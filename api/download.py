import os
import bson
import copy
import pytz
import tarfile
import datetime
import cStringIO

from tarfile import TarInfo

import fs.path
import fs.errors
from fs.time import datetime_to_epoch
import requests
from requests import exceptions as req_exceptions

from .web import base
from .web.request import AccessType
from . import config, files, util, validators
from .dao.containerutil import pluralize

BYTES_IN_MEGABYTE = float(1<<20)

def _filter_check(property_filter, property_values):
    minus = set(property_filter.get('-', []) + property_filter.get('minus', []))
    plus = set(property_filter.get('+', []) + property_filter.get('plus', []))
    if "null" in plus and not property_values:
        return True
    if "null" in minus and property_values:
        return False
    elif not minus.isdisjoint(property_values):
        return False
    if plus and plus.isdisjoint(property_values):
        return False
    return True


class Download(base.RequestHandler):
    BLOCKSIZE = 512
    CHUNKSIZE = 2 ** 20

    def __init__(self, *args, **kwargs):
        self.session = requests.Session()
        super(Download, self).__init__(*args, **kwargs)

    def _append_targets(self, targets, cont_name, container, prefix, total_size, total_cnt, filters):
        inputs = [('input', f) for f in container.get('inputs', [])]
        outputs = [('output', f) for f in container.get('files', []) if not f.get('deleted')]
        for file_group, f in inputs + outputs:
            if filters:
                filtered = True
                for filter_ in filters:
                    type_as_list = [f['type']] if f.get('type') else []
                    if (
                        _filter_check(filter_.get('tags', {}), f.get('tags', [])) and
                        _filter_check(filter_.get('types', {}), type_as_list)
                        ):
                        filtered = False
                        break
                if filtered:
                    continue

            file_path = files.get_file_path(f)
            if file_path:  # silently skip missing files
                if cont_name == 'analyses':
                    targets.append((file_path, '{}/{}/{}'.format(prefix, file_group, f['name']), cont_name, str(container.get('_id')), f['size'], f['modified']))
                else:
                    targets.append((file_path, '{}/{}'.format(prefix, f['name']), cont_name, str(container.get('_id')), f['size'], f['modified']))
                total_size += f['size']
                total_cnt += 1
            else:
                self.log.warn("Expected {} to exist but it is missing. File will be skipped in download.".format(file_path))
        return total_size, total_cnt

    def _bulk_preflight_archivestream(self, file_refs):
        arc_prefix =  self.get_param('prefix', 'scitran')
        file_cnt = 0
        total_size = 0
        targets = []

        for fref in file_refs:

            cont_id     = fref.get('container_id', '')
            filename    = fref.get('filename', '')
            cont_name   = fref.get('container_name','')

            if cont_name not in ['project', 'session', 'acquisition', 'analysis']:
                self.abort(400, 'Bulk download only supports files in projects, sessions, analyses and acquisitions')
            cont_name   = pluralize(fref.get('container_name',''))


            file_obj = None
            try:
                # Try to find the file reference in the database (filtering on user permissions)
                bid = bson.ObjectId(cont_id)
                query = {'_id': bid}
                if not self.user_is_admin:
                    query['permissions._id'] = self.uid
                file_obj = config.db[cont_name].find_one(
                    query,
                    {'files': { '$elemMatch': {
                        'name': filename
                    }}
                })['files'][0]
            except Exception: # pylint: disable=broad-except
                # self.abort(404, 'File {} on Container {} {} not found'.format(filename, cont_name, cont_id))
                # silently skip missing files/files user does not have access to
                self.log.warn("Expected file {} on Container {} {} to exist but it is missing. File will be skipped in download.".format(filename, cont_name, cont_id))
                continue

            file_path = files.get_file_path(file_obj)
            if file_path:  # silently skip missing files
                targets.append((file_path, cont_name+'/'+cont_id+'/'+file_obj['name'], cont_name, cont_id, file_obj['size'], file_obj['modified']))
                total_size += file_obj['size']
                file_cnt += 1

        if len(targets) > 0:
            filename = arc_prefix + '_'+datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S') + '.tar'
            ticket = util.download_ticket(self.request.client_addr, self.origin, 'batch', targets, filename, total_size)
            config.db.downloads.insert_one(ticket)
            return {'ticket': ticket['_id'], 'file_cnt': file_cnt, 'size': total_size}
        else:
            self.abort(404, 'No files requested could be found')


    def _preflight_archivestream(self, req_spec, collection=None):
        arc_prefix = self.get_param('prefix', 'scitran')
        file_cnt = 0
        total_size = 0
        targets = []
        filename = None

        ids_of_paths = {}
        base_query = {'deleted': {'$exists': False}}
        if not self.user_is_admin:
            base_query['permissions._id'] = self.uid

        for item in req_spec['nodes']:

            item_id = bson.ObjectId(item['_id'])
            base_query['_id'] = item_id

            if item['level'] == 'project':
                project = config.db.projects.find_one(base_query, ['group', 'label', 'files'])
                if not project:
                    # silently(while logging it) skip missing objects/objects user does not have access to
                    self.log.warn("Expected project {} to exist but it is missing. Node will be skipped".format(item_id))
                    continue

                prefix = '/'.join([arc_prefix, project['group'], project['label']])
                total_size, file_cnt = self._append_targets(targets, 'projects', project, prefix, total_size, file_cnt, req_spec.get('filters'))

                subjects = config.db.subjects.find({'project': item_id, 'deleted': {'$exists': False}}, ['code', 'files'])
                subject_dict = {subject['_id']: subject for subject in subjects}
                subject_prefixes = {}
                for subject in subject_dict.itervalues():
                    if not subject.get('code'):
                        subject['code'] = 'unknown_subject'
                    subject_prefix = self._path_from_container(prefix, subject, ids_of_paths, subject['code'])
                    subject_prefixes[subject['_id']] = subject_prefix
                    total_size, file_cnt = self._append_targets(targets, 'subjects', subject, subject_prefix, total_size, file_cnt, req_spec.get('filters'))

                sessions = config.db.sessions.find({'subject': {'$in': subject_dict.keys()}, 'deleted': {'$exists': False}}, ['label', 'files', 'uid', 'timestamp', 'timezone', 'subject'])
                session_dict = {session['_id']: session for session in sessions}
                session_prefixes = {}
                for session in session_dict.itervalues():
                    session_prefix = self._path_from_container(subject_prefixes[session['subject']], session, ids_of_paths, session['_id'])
                    session_prefixes[session['_id']] = session_prefix
                    total_size, file_cnt = self._append_targets(targets, 'sessions', session, session_prefix, total_size, file_cnt, req_spec.get('filters'))

                acquisitions = config.db.acquisitions.find({'session': {'$in': session_dict.keys()}, 'deleted': {'$exists': False}}, ['label', 'files', 'session', 'uid', 'timestamp', 'timezone'])
                for acq in acquisitions:
                    session = session_dict[acq['session']]
                    acq_prefix = self._path_from_container(session_prefixes[session['_id']], acq, ids_of_paths, acq['_id'])
                    total_size, file_cnt = self._append_targets(targets, 'acquisitions', acq, acq_prefix, total_size, file_cnt, req_spec.get('filters'))

            elif item['level'] == 'subject':
                subject = config.db.subjects.find_one(base_query, ['project', 'code', 'files'])
                if not subject:
                    # silently(while logging it) skip missing objects/objects user does not have access to
                    self.log.warn("Expected subject {} to exist but it is missing. Node will be skipped".format(item_id))
                    continue
                if not subject.get('code'):
                    subject['code'] = 'unknown_subject'

                project = config.db.projects.find_one({'_id': subject['project']}, ['group', 'label'])
                prefix = self._path_from_container(project['group'] + '/' + project['label'], subject, ids_of_paths, subject["code"])
                total_size, file_cnt = self._append_targets(targets, 'subjects', subject, prefix, total_size, file_cnt, req_spec.get('filters'))

                sessions = config.db.sessions.find({'subject': item_id, 'deleted': {'$exists': False}}, ['label', 'files', 'uid', 'timestamp', 'timezone', 'subject'])
                session_dict = {session['_id']: session for session in sessions}
                session_prefixes = {}
                for session in session_dict.itervalues():
                    session_prefix = self._path_from_container(prefix, session, ids_of_paths, session['_id'])
                    session_prefixes[session['_id']] = session_prefix
                    total_size, file_cnt = self._append_targets(targets, 'sessions', session, session_prefix, total_size, file_cnt, req_spec.get('filters'))

                acquisitions = config.db.acquisitions.find({'session': {'$in': session_dict.keys()}, 'deleted': {'$exists': False}}, ['label', 'files', 'session', 'uid', 'timestamp', 'timezone'])
                for acq in acquisitions:
                    session = session_dict[acq['session']]
                    acq_prefix = self._path_from_container(session_prefixes[session['_id']], acq, ids_of_paths, acq['_id'])
                    total_size, file_cnt = self._append_targets(targets, 'acquisitions', acq, acq_prefix, total_size, file_cnt, req_spec.get('filters'))

            elif item['level'] == 'session':
                session = config.db.sessions.find_one(base_query, ['project', 'label', 'files', 'uid', 'timestamp', 'timezone', 'subject'])
                if not session:
                    # silently(while logging it) skip missing objects/objects user does not have access to
                    self.log.warn("Expected session {} to exist but it is missing. Node will be skipped".format(item_id))
                    continue

                project = config.db.projects.find_one({'_id': session['project']}, ['group', 'label'])
                subject = config.db.subjects.find_one({'_id': session['subject']})
                if not subject.get('code'):
                    subject['code'] = 'unknown_subject'
                prefix = self._path_from_container(self._path_from_container(project['group'] + '/' + project['label'], subject, ids_of_paths, subject["code"]), session, ids_of_paths, session['_id'])
                total_size, file_cnt = self._append_targets(targets, 'sessions', session, prefix, total_size, file_cnt, req_spec.get('filters'))

                # If the param `collection` holding a collection id is not None, filter out acquisitions that are not in the collection
                a_query = {'session': item_id, 'deleted': {'$exists': False}}
                if collection:
                    a_query['collections'] = bson.ObjectId(collection)
                acquisitions = config.db.acquisitions.find(a_query, ['label', 'files', 'uid', 'timestamp', 'timezone'])

                for acq in acquisitions:
                    acq_prefix = self._path_from_container(prefix, acq, ids_of_paths, acq['_id'])
                    total_size, file_cnt = self._append_targets(targets, 'acquisitions', acq, acq_prefix, total_size, file_cnt, req_spec.get('filters'))

            elif item['level'] == 'acquisition':
                acq = config.db.acquisitions.find_one(base_query, ['session', 'label', 'files', 'uid', 'timestamp', 'timezone'])
                if not acq:
                    # silently(while logging it) skip missing objects/objects user does not have access to
                    self.log.warn("Expected acquisition {} to exist but it is missing. Node will be skipped".format(item_id))
                    continue

                session = config.db.sessions.find_one({'_id': acq['session']}, ['project', 'label', 'uid', 'timestamp', 'timezone', 'subject'])
                subject = config.db.subjects.find_one({'_id': session['subject']})
                if not subject.get('code'):
                    subject['code'] = 'unknown_subject'

                project = config.db.projects.find_one({'_id': session['project']}, ['group', 'label'])
                prefix = self._path_from_container(self._path_from_container(self._path_from_container(project['group'] + '/' + project['label'], subject, ids_of_paths, subject['code']), session, ids_of_paths, session["_id"]), acq, ids_of_paths, acq['_id'])
                total_size, file_cnt = self._append_targets(targets, 'acquisitions', acq, prefix, total_size, file_cnt, req_spec.get('filters'))

            elif item['level'] == 'analysis':
                analysis_query = copy.deepcopy(base_query)
                perm_query = analysis_query.pop('permissions._id', None)
                analysis = config.db.analyses.find_one(analysis_query, ['parent', 'label', 'inputs', 'files', 'uid', 'timestamp'])
                analysis_query = {
                    'deleted': {'$exists': False},
                    "_id": analysis.get('parent', {}).get('id'),
                    "permissions._id": perm_query
                }
                if perm_query is None:
                    analysis_query.pop('permissions._id')
                if analysis:
                    parent = config.db[pluralize(analysis.get('parent', {}).get('type'))].find_one(analysis_query)
                if not analysis or not parent:
                    # silently(while logging it) skip missing objects/objects user does not have access to
                    self.log.warn("Expected anaylysis {} to exist but it is missing. Node will be skipped".format(item_id))
                    continue
                prefix = self._path_from_container("", analysis, ids_of_paths, util.sanitize_string_to_filename(analysis['label']))
                filename = 'analysis_' + util.sanitize_string_to_filename(analysis['label']) + '.tar'
                total_size, file_cnt = self._append_targets(targets, 'analyses', analysis, prefix, total_size, file_cnt, req_spec.get('filters'))

        if len(targets) > 0:
            if not filename:
                filename = arc_prefix + '_' + datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S') + '.tar'
            ticket = util.download_ticket(self.request.client_addr, self.origin, 'batch', targets, filename, total_size)
            config.db.downloads.insert_one(ticket)
            return {'ticket': ticket['_id'], 'file_cnt': file_cnt, 'size': total_size, 'filename': filename}
        else:
            self.abort(404, 'No requested containers could be found')

    def _path_from_container(self, prefix, container, ids_of_paths, _id):
        """
        Returns the full path of a container instead of just a subpath, it must be provided with a prefix though
        """
        def _find_new_path(path, ids_of_paths, _id):
            """
            Checks to see if the full path is used
            """
            if _id in ids_of_paths.keys():
                # If the id is already associated with a path, use that instead of modifying it
                return ids_of_paths[_id]
            used_paths = [ids_of_paths[id_] for id_ in ids_of_paths if id_ != _id]
            i = 0
            modified_path = path
            while modified_path in used_paths:
                modified_path = path + '_' + str(i)
                i += 1
            return modified_path

        path = ''
        if not path and container.get('label'):
            path = util.sanitize_string_to_filename(container['label'])
        if not path and container.get('timestamp'):
            timezone = container.get('timezone')
            if timezone:
                path = pytz.timezone('UTC').localize(container['timestamp']).astimezone(pytz.timezone(timezone)).strftime('%Y%m%d_%H%M')
            else:
                path = container['timestamp'].strftime('%Y%m%d_%H%M')
        if not path and container.get('uid'):
            path = container['uid']
        if not path and container.get('code'):
            path = container['code']

        path = path.encode('ascii', errors='ignore')

        if not path:
            path = 'untitled'

        path = prefix + '/' + path
        path = _find_new_path(path, ids_of_paths, _id)
        ids_of_paths[_id] = path
        return path

    def stream_file_signed_url(self, signed_url, tarinfo_buf, file_info):
        response = self.session.get(signed_url, stream=True)
        f_iter = response.iter_content(chunk_size=self.CHUNKSIZE)
        try:
            yield tarinfo_buf
            chunk = ''
            for chunk in f_iter:
                yield chunk
            if len(chunk) % self.BLOCKSIZE != 0:
                yield (self.BLOCKSIZE - (len(chunk) % self.BLOCKSIZE)) * b'\0'
        except (req_exceptions.ChunkedEncodingError,
                req_exceptions.ConnectionError,
                req_exceptions.ContentDecodingError):
            msg = ("Error happened during sending file content in archive stream, file path: %s, "
                   "container: %s/%s, archive path: %s" % file_info)
            self.log.critical(msg)
            self.abort(500, msg)

    def stream_regular_file(self, filepath, tarinfo_buf, file_info):
        try:
            file_system = files.get_fs_by_file_path(filepath)
            with file_system.open(filepath, 'rb') as fd:
                f_iter = iter(lambda: fd.read(self.CHUNKSIZE), '')  # pylint: disable=cell-var-from-loop
                try:
                    yield tarinfo_buf
                    chunk = ''
                    for chunk in f_iter:
                        yield chunk
                    if len(chunk) % self.BLOCKSIZE != 0:
                        yield (self.BLOCKSIZE - (len(chunk) % self.BLOCKSIZE)) * b'\0'

                except (IOError, fs.errors.OperationFailed):
                    msg = ("Error happened during sending file content in archive stream, file path: %s, "
                           "container: %s/%s, archive path: %s" % file_info)
                    self.log.critical(msg)
                    self.abort(500, msg)
        except (fs.errors.ResourceNotFound, fs.errors.OperationFailed, IOError):
            self.log.critical("Couldn't find the file during creating archive stream: %s, "
                              "container: %s/%s, archive path: %s" % file_info)
            tarinfo = TarInfo()
            tarinfo.name = file_info[3] + '.MISSING'
            yield tarinfo.tobuf()

    def archivestream(self, ticket):
        stream = cStringIO.StringIO()

        with tarfile.open(mode='w|', fileobj=stream):
            for filepath, arcpath, cont_name, cont_id, f_size, f_modified in ticket['target']:
                tarinfo = TarInfo()
                tarinfo.name = arcpath.lstrip('/')
                tarinfo.size = f_size
                tarinfo.mtime = datetime_to_epoch(f_modified)
                tarinfo_buf = tarinfo.tobuf()
                signed_url = None
                try:
                    signed_url = files.get_signed_url(filepath, config.fs)
                except fs.errors.ResourceNotFound:
                    pass

                if signed_url:
                    content_generator = self.stream_file_signed_url(signed_url, tarinfo_buf, (filepath, cont_name, cont_id, arcpath))
                else:
                    content_generator = self.stream_regular_file(filepath, tarinfo_buf, (filepath, cont_name, cont_id, arcpath))

                for chunk in content_generator:
                    yield chunk

                self.log_user_access(AccessType.download_file, cont_name=cont_name, cont_id=cont_id, filename=os.path.basename(arcpath), origin_override=ticket['origin'], download_ticket=ticket['_id']) # log download
        yield stream.getvalue()  # get tar stream trailer
        stream.close()

    def symlinkarchivestream(self, ticket):
        for filepath, arcpath, cont_name, cont_id, _, _ in ticket['target']:
            t = tarfile.TarInfo(name=arcpath)
            t.type = tarfile.SYMTYPE
            t.linkname = fs.path.relpath(filepath)
            yield t.tobuf()
            self.log_user_access(AccessType.download_file, cont_name=cont_name, cont_id=cont_id, filename=os.path.basename(arcpath), origin_override=ticket['origin'], download_ticket=ticket['_id']) # log download
        stream = cStringIO.StringIO()
        with tarfile.open(mode='w|', fileobj=stream) as _:
            pass
        yield stream.getvalue() # get tar stream trailer
        stream.close()

    def download(self):
        """Download files or create a download ticket"""
        ticket_id = self.get_param('ticket')
        if ticket_id:
            ticket = config.db.downloads.find_one({'_id': ticket_id})
            if not ticket:
                self.abort(404, 'no such ticket')
            if ticket['ip'] != self.request.client_addr:
                self.abort(400, 'ticket not for this source IP')
            if self.get_param('symlinks'):
                self.response.app_iter = self.symlinkarchivestream(ticket)
            else:
                self.response.app_iter = self.archivestream(ticket)
            self.response.headers['Content-Type'] = 'application/octet-stream'
            self.response.headers['Content-Disposition'] = 'attachment; filename=' + ticket['filename'].encode('ascii', errors='ignore')
        else:

            req_spec = self.request.json_body

            if self.is_true('bulk'):
                return self._bulk_preflight_archivestream(req_spec.get('files', []))
            else:
                payload_schema_uri = validators.schema_uri('input', 'download.json')
                validator = validators.from_schema_path(payload_schema_uri)
                validator(req_spec, 'POST')
                return self._preflight_archivestream(req_spec, collection=self.get_param('collection'))

    def summary(self):
        """Return a summary of what has been/will be downloaded based on a given query"""
        res = {}
        req = self.request.json_body
        cont_query = {
            'projects': {'_id': {'$in': []}},
            'subjects': {'_id': {'$in': []}},
            'sessions': {'_id': {'$in': []}},
            'acquisitions': {'_id': {'$in': []}},
            'analyses': {'_id': {'$in': []}}
        }
        for node in req:
            node['_id'] = bson.ObjectId(node['_id'])
            level = node['level']

            containers = {'projects': 0, 'subjects': 0, 'sessions': 0, 'acquisitions': 0, 'analyses': 0}

            if level == 'project':
                subjects = config.db.subjects.find({'project': node['_id'], 'deleted': {'$exists': False}}, {'_id': 1})
                subject_ids = [s['_id'] for s in subjects]
                sessions = config.db.sessions.find({'subject': {'$in': subject_ids}, 'deleted': {'$exists': False}}, {'_id': 1})
                session_ids = [s['_id'] for s in sessions]
                acquisitions = config.db.acquisitions.find({'session': {'$in': session_ids}, 'deleted': {'$exists': False}}, {'_id': 1})
                acquisition_ids = [a['_id'] for a in acquisitions]

                cont_query['projects']['_id']['$in'].append(node['_id'])
                cont_query['subjects']['_id']['$in'].extend(subject_ids)
                cont_query['sessions']['_id']['$in'].extend(session_ids)
                cont_query['acquisitions']['_id']['$in'].extend(acquisition_ids)

                for cont_name in ('projects', 'subjects', 'sessions', 'acquisitions'):
                    containers[cont_name] = 1

            elif level == 'subject':
                sessions = config.db.sessions.find({'subject': node['_id'], 'deleted': {'$exists': False}}, {'_id': 1})
                session_ids = [s['_id'] for s in sessions]
                acquisitions = config.db.acquisitions.find({'session': {'$in': session_ids}, 'deleted': {'$exists': False}}, {'_id': 1})
                acquisition_ids = [a['_id'] for a in acquisitions]

                cont_query['subjects']['_id']['$in'].append(node['_id'])
                cont_query['sessions']['_id']['$in'].extend(session_ids)
                cont_query['acquisitions']['_id']['$in'].extend(acquisition_ids)

                for cont_name in ('subjects', 'sessions', 'acquisitions'):
                    containers[cont_name] = 1

            elif level == 'session':
                acquisitions = config.db.acquisitions.find({'session': node['_id'], 'deleted': {'$exists': False}}, {'_id': 1})
                acquisition_ids = [a['_id'] for a in acquisitions]

                cont_query['sessions']['_id']['$in'].append(node['_id'])
                cont_query['acquisitions']['_id']['$in'].extend(acquisition_ids)

                for cont_name in ('sessions', 'acquisitions'):
                    containers[cont_name] = 1

            elif level == 'acquisition':
                cont_query['acquisitions']['_id']['$in'].append(node['_id'])
                containers['acquisitions'] = 1

            elif level == 'analysis':
                cont_query['analyses']['_id']['$in'].append(node['_id'])
                containers['analyses'] = 1

            else:
                self.abort(400, "{} not a recognized level".format(level))

            containers = [cont for cont in containers if containers[cont] == 1]

        for cont_name in containers:
            # Aggregate file types
            pipeline = [
                {'$match': cont_query[cont_name]},
                {'$unwind': '$files'},
                {'$match': {'files.deleted': {'$exists': False}}},
                {'$project': {'_id': '$_id', 'type': '$files.type','mbs': {'$divide': ['$files.size', BYTES_IN_MEGABYTE]}}},
                {'$group': {
                    '_id': '$type',
                    'count': {'$sum' : 1},
                    'mb_total': {'$sum':'$mbs'}
                }}
            ]

            try:
                result = config.db[cont_name].aggregate(pipeline)
            except Exception as e: # pylint: disable=broad-except
                self.log.warning(e)
                self.abort(500, "Failure to load summary")

            for doc in result:
                type_ = doc['_id']
                if res.get(type_):
                    res[type_]['count'] += doc.get('count',0)
                    res[type_]['mb_total'] += doc.get('mb_total',0)
                else:
                    res[type_] = doc
        return res
