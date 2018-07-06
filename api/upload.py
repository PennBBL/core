import bson
import datetime
import json
import os
import uuid

import fs.errors
import fs.path

from .web import base
from .web.errors import FileFormException
from . import config
from . import files
from . import placer as pl
from . import util
from .dao import hierarchy

Strategy = util.Enum('Strategy', {
    'targeted'       : pl.TargetedPlacer,       # Upload 1 files to a container.
    'targeted_multi' : pl.TargetedMultiPlacer,  # Upload N files to a container.
    'engine'         : pl.EnginePlacer,         # Upload N files from the result of a successful job.
    'token'          : pl.TokenPlacer,          # Upload N files to a saved folder based on a token.
    'packfile'       : pl.PackfilePlacer,       # Upload N files as a new packfile to a container.
    'label'          : pl.LabelPlacer,
    'uid'            : pl.UIDPlacer,
    'uidmatch'       : pl.UIDMatchPlacer,
    'reaper'         : pl.UIDReaperPlacer,
    'analysis'       : pl.AnalysisPlacer,       # Upload N files to an analysis as input and output (no db updates - deprecated)
    'analysis_job'   : pl.AnalysisJobPlacer,    # Upload N files to an analysis as output from job results
    'gear'           : pl.GearPlacer
})


def process_upload(request, strategy, access_logger, container_type=None, id_=None, origin=None, context=None, response=None,
                   metadata=None, file_fields=None, tempdir=None):
    """
    Universal file upload entrypoint.

    Format:
        Multipart form upload with N file fields, each with their desired filename.
        For technical reasons, no form field names can be repeated. Instead, use (file1, file2) and so forth.

        Depending on the type of upload, a non-file form field called "metadata" may/must also be sent.
        If present, it is expected to be a JSON string matching the schema for the upload strategy.

        Currently, the JSON returned may vary by strategy.

        Some examples:
        curl -F file1=@science.png   -F file2=@rules.png url
        curl -F metadata=<stuff.json -F file=@data.zip   url
        http --form POST url metadata=@stuff.json file@data.zip

    Features:
                                               | targeted |  reaper   | engine | packfile
        Must specify a target container        |     X    |           |    X   |
        May create hierarchy on demand         |          |     X     |        |     X

        May  send metadata about the files     |     X    |     X     |    X   |     X
        MUST send metadata about the files     |          |     X     |        |     X

        Creates a packfile from uploaded files |          |           |        |     X
    """
    log = request.logger

    if not isinstance(strategy, Strategy):
        raise Exception('Unknown upload strategy')

    if id_ is not None and container_type == None:
        raise Exception('Unspecified container type')

    allowed_container_types = ('project', 'subject', 'session', 'acquisition',
                               'gear', 'analysis',
                               'collection')
    if container_type is not None and container_type not in allowed_container_types:
        raise Exception('Unknown container type')

    timestamp = datetime.datetime.utcnow()

    container = None
    if container_type and id_:
        container = hierarchy.get_container(container_type, id_)

    # Check if filename should be basename or full path
    use_filepath = request.GET.get('filename_path', '').lower() in ('1', 'true')
    if use_filepath:
        name_fn = util.sanitize_path
    else:
        name_fn = os.path.basename

    # The vast majority of this function's wall-clock time is spent here.
    # Tempdir is deleted off disk once out of scope, so let's hold onto this reference.
    file_processor = files.FileProcessor(config.fs, local_tmp_fs=(strategy == Strategy.token), tempdir_name=tempdir)
    if not file_fields:
        form = file_processor.process_form(request, use_filepath=use_filepath)
        # Non-file form fields may have an empty string as filename, check for 'falsy' values
        file_fields = extract_file_fields(form)

        if 'metadata' in form:
            try:
                metadata = json.loads(form['metadata'].value)
            except Exception:
                raise FileFormException('wrong format for field "metadata"')
            if isinstance(metadata, dict):
                for f in metadata.get(container_type, {}).get('files', []):
                    f['name'] = name_fn(f['name'])
            elif isinstance(metadata, list):
                for f in metadata:
                    f['name'] = name_fn(f['name'])

    placer_class = strategy.value
    placer = placer_class(container_type, container, id_, metadata, timestamp, origin, context, file_processor, access_logger)
    placer.check()

    # Browsers, when sending a multipart upload, will send files with field name "file" (if sinuglar)
    # or "file1", "file2", etc (if multiple). Following this convention is probably a good idea.
    # Here, we accept any

    # TODO: Change schemas to enabled targeted uploads of more than one file.
    # Ref docs from placer.TargetedPlacer for details.
    if strategy == Strategy.targeted and len(file_fields) > 1:
        raise FileFormException("Targeted uploads can only send one file")

    for field in file_fields:
        if hasattr(field, 'file'):
            field.file.close()
            field.hash = util.format_hash(files.DEFAULT_HASH_ALG, field.hasher.hexdigest())

        if not hasattr(field, 'hash'):
            field.hash = ''
        # Augment the cgi.FieldStorage with a variety of custom fields.
        # Not the best practice. Open to improvements.
        # These are presumbed to be required by every function later called with field as a parameter.
        field.path = field.filename
        if not file_processor.temp_fs.exists(field.path):
            # tempdir_exists = os.path.exists(tempdir.name)
            raise Exception("file {} does not exist, files in tmpdir: {}".format(
                field.path,
                file_processor.temp_fs.listdir('/'),
            ))
        field.size = int(file_processor.temp_fs.getsize(field.path))
        field.uuid = str(uuid.uuid4())
        field.mimetype = util.guess_mimetype(field.filename)  # TODO: does not honor metadata's mime type if any
        field.modified = timestamp

        # create a file-attribute map commonly used elsewhere in the codebase.
        # Stands in for a dedicated object... for now.
        file_attrs = make_file_attrs(field, origin)

        placer.process_file_field(field, file_attrs)

    # Respond either with Server-Sent Events or a standard json map
    if placer.sse and not response:
        raise Exception("Programmer error: response required")
    elif placer.sse:
        # Returning a callable will bypass webapp2 processing and allow
        # full control over the response.
        def sse_handler(environ, start_response): # pylint: disable=unused-argument
            write = start_response('200 OK', [
                ('Content-Type', 'text/event-stream; charset=utf-8'),
                ('Connection', 'keep-alive')
            ])

            # Instead of handing the iterator off to response.app_iter, send it ourselves.
            # This prevents disconnections from leaving the API in a partially-complete state.
            #
            # Timing out between events or throwing an exception will result in undefinied behaviour.
            # Right now, in our environment:
            # - Timeouts may result in nginx-created 500 Bad Gateway HTML being added to the response.
            # - Exceptions add some error json to the response, which is not SSE-sanitized.
            for item in placer.finalize():
                try:
                    write(item)
                except Exception: # pylint: disable=broad-except
                    log.info('SSE upload progress failed to send; continuing')

            return ''

        return sse_handler
    else:
        return placer.finalize()


class Upload(base.RequestHandler):

    def _create_upload_ticket(self):
        if not hasattr(config.fs, 'get_signed_url'):
            self.abort(405, 'Signed URLs are not supported with the current storage backend')

        payload = self.request.json_body
        metadata = payload.get('metadata', None)
        filenames = payload.get('filenames', None)

        if metadata is None or not filenames:
            self.abort(400, 'metadata and at least one filename are required')

        tempdir = str(uuid.uuid4())
        # Upload into a temp folder, so we will be able to cleanup
        signed_urls = {}
        for filename in filenames:
            signed_urls[filename] = files.get_signed_url(fs.path.join('tmp', tempdir, filename),
                                                         config.fs,
                                                         purpose='upload')

        ticket = util.upload_ticket(self.request.client_addr, self.origin, tempdir, filenames, metadata)
        return {'ticket': config.db.uploads.insert_one(ticket).inserted_id,
                'urls': signed_urls}

    def _check_upload_ticket(self, ticket_id):
        ticket = config.db.uploads.find_one({'_id': ticket_id})
        if not ticket:
            self.abort(404, 'no such ticket')
        if ticket['ip'] != self.request.client_addr:
            self.abort(403, 'ticket not for this resource or source IP')
        return ticket

    def upload(self, strategy):
        """Receive a sortable reaper upload."""

        if not self.user_is_admin:
            user = self.uid
            if not user:
                self.abort(403, 'Uploading requires login')

        if strategy in ['label', 'uid', 'uid-match', 'reaper']:
            strategy = strategy.replace('-', '')
            strategy = getattr(Strategy, strategy)

        context = {'uid': self.uid if not self.user_is_admin else None}

        # Request for upload ticket
        if self.get_param('ticket') == '':
            return self._create_upload_ticket()

        # Check ticket id and skip permissions check if it clears
        ticket_id = self.get_param('ticket')
        if ticket_id:
            ticket = self._check_upload_ticket(ticket_id)
            file_fields = []
            for filename in ticket['filenames']:
                file_fields.append(
                    util.dotdict({
                        'filename': filename
                    })
                )

            return process_upload(self.request, strategy, self.log_user_access, metadata=ticket['metadata'], origin=self.origin,
                                  context=context, file_fields=file_fields, tempdir=ticket['tempdir'])
        else:
            return process_upload(self.request, strategy, self.log_user_access, origin=self.origin, context=context)

    def engine(self):
        """Handles file uploads from the engine"""

        if not self.user_is_admin:
            self.abort(402, 'uploads must be from an authorized drone')
        level = self.get_param('level')
        if level is None:
            self.abort(400, 'container level is required')
        if level not in ['analysis', 'acquisition', 'session', 'subject', 'project']:
            self.abort(400, 'container level must be analysis, acquisition, session, subject or project.')
        cid = self.get_param('id')
        if not cid:
            self.abort(400, 'container id is required')
        else:
            cid = bson.ObjectId(cid)

        context = {
            'job_id': self.get_param('job'),
            'job_ticket_id': self.get_param('job_ticket'),
        }

        # Request for upload ticket
        if self.get_param('upload_ticket') == '':
            return self._create_upload_ticket()

        # Check ticket id and skip permissions check if it clears
        ticket_id = self.get_param('upload_ticket')
        if ticket_id:
            ticket = self._check_upload_ticket(ticket_id)
            file_fields = []
            for filename in ticket['filenames']:
                file_fields.append(
                    util.dotdict({
                        'filename': filename
                    })
                )

            strategy = Strategy.analysis_job if level == 'analysis' else Strategy.engine
            return process_upload(self.request, strategy, self.log_user_access, metadata=ticket['metadata'], origin=self.origin,
                                  context=context, file_fields=file_fields, tempdir=ticket['tempdir'],
                                  container_type=level, id_=cid)

        else:
            strategy = Strategy.analysis_job if level == 'analysis' else Strategy.engine
            return process_upload(self.request, strategy, self.log_user_access, container_type=level, id_=cid,
                                  origin=self.origin, context=context)

    def clean_packfile_tokens(self):
        """Clean up expired upload tokens and invalid token directories.
        Ref placer.TokenPlacer and FileListHandler.packfile_start for context.
        """

        if not self.user_is_admin:
            self.abort(402, 'uploads must be from an authorized drone')

        # Race condition: we could delete tokens & directories that are currently processing.
        # For this reason, the modified timeout is long.
        result = config.db['tokens'].delete_many({
            'type': 'packfile',
            'modified': {'$lt': datetime.datetime.utcnow() - datetime.timedelta(hours=1)},
        })

        removed = result.deleted_count
        if removed > 0:
            self.log.info('Removed %s expired packfile tokens', removed)

        # Next, find token directories and remove any that don't map to a token.

        # This logic is used by:
        #   TokenPlacer.check
        #   PackfilePlacer.check
        #   upload.clean_packfile_tokens
        #
        # It must be kept in sync between each instance.
        folder = fs.path.join('tokens', 'packfile')

        util.mkdir_p(folder, config.fs)
        try:
            paths = config.fs.listdir(folder)
        except fs.errors.ResourceNotFound:
            # Non-local storages are used without 0-blobs for "folders" (mkdir_p is a noop)
            paths = []

        cleaned = 0

        for token in paths:
            path = fs.path.join(folder, token)

            result = None
            try:
                result = config.db['tokens'].find_one({
                    '_id': token
                })
            except bson.errors.InvalidId:
                # Folders could be an invalid mongo ID, in which case they're definitely expired :)
                pass

            if result is None:
                self.log.info('Cleaning expired token directory %s', token)
                config.fs.removetree(path)
                cleaned += 1

        return {
            'removed': {
                'tokens': removed,
                'directories': cleaned,
            }
        }

def extract_file_fields(form):
    """Returns a list of file fields in the form, handling multiple values"""
    result = []
    for fieldname in form:
        field = form[fieldname]
        if isinstance(field, list):
            for field_entry in field:
                if field_entry.filename:
                    result.append(field_entry)

        elif field.filename:
            result.append(field)

    return result

def make_file_attrs(field, origin):
    # create a file-attribute map commonly used elsewhere in the codebase.
    # Stands in for a dedicated object... for now.
    file_attrs = {
        '_id': field.uuid,
        'name': field.filename,
        'modified': field.modified,
        'size': field.size,
        'mimetype': field.mimetype,
        'hash': field.hash,
        'origin': origin,

        'type': None,
        'modality': None,
        'classification': {},
        'tags': [],
        'info': {}
    }

    file_attrs['type'] = files.guess_type_from_filename(file_attrs['name'])
    return file_attrs
