import os
import cgi
import json
import six
import hashlib
import uuid

import fs.move
import fs.subfs
import fs.tempfs
import fs.path
import fs.errors

from . import config, util

DEFAULT_HASH_ALG = 'sha384'

class FileProcessor(object):
    def __init__(self, presistent_fs, local_tmp_fs=False):
        self._tempdir_name = str(uuid.uuid4())
        self._presistent_fs = presistent_fs
        self._presistent_fs.makedirs(fs.path.join('tmp', self._tempdir_name), recreate=True)
        if not local_tmp_fs:
            self._temp_fs = fs.subfs.SubFS(presistent_fs, fs.path.join('tmp', self._tempdir_name))
        else:
            self._temp_fs = fs.tempfs.TempFS('tmp')

    def store_temp_file(self, src_path, dst_path, dst_fs=None):
        if not isinstance(src_path, unicode):
            src_path = six.u(src_path)
        if not isinstance(dst_path, unicode):
            dst_path = six.u(dst_path)
        dst_dir = fs.path.dirname(dst_path)
        if not dst_fs:
            dst_fs = self.persistent_fs
        self._presistent_fs.makedirs(dst_dir, recreate=True)
        if isinstance(self._temp_fs, fs.tempfs.TempFS):
            fs.move.move_file(self._temp_fs, src_path, dst_fs, dst_path)
        else:
            self._presistent_fs.move(src_path=fs.path.join('tmp', self._tempdir_name, src_path), dst_path=dst_path)

    def process_form(self, request, use_filepath=False):
        """
        Some workarounds to make webapp2 process forms in an intelligent way.
        Normally webapp2/WebOb Reqest.POST would copy the entire request stream
        into a single file on disk.
        https://github.com/Pylons/webob/blob/cb9c0b4f51542a7d0ed5cc5bf0a73f528afbe03e/webob/request.py#L787
        https://github.com/moraes/webapp-improved/pull/12
        We pass request.body_file (wrapped wsgi input stream)
        to our custom subclass of cgi.FieldStorage to write each upload file
        to a separate file on disk, as it comes in off the network stream from the client.
        Then we can rename these files to their final destination,
        without copying the data gain.

        Returns (tuple):
            form: SingleFileFieldStorage instance
            tempdir: tempdir the file was stored in.

        Keep tempdir in scope until you don't need it anymore; it will be deleted on GC.
        """

        # Copied from WebOb source:
        # https://github.com/Pylons/webob/blob/cb9c0b4f51542a7d0ed5cc5bf0a73f528afbe03e/webob/request.py#L790
        env = request.environ.copy()
        env.setdefault('CONTENT_LENGTH', '0')
        env['QUERY_STRING'] = ''
        field_storage_class = get_single_file_field_storage(self._temp_fs, use_filepath=use_filepath)

        form = field_storage_class(
            fp=request.body_file, environ=env, keep_blank_values=True
        )

        return form

    def hash_file_formatted(self, filepath, f_system, hash_alg=None, buffer_size=65536):
        """
        Return the scitran-formatted hash of a file, specified by path.
        """

        if not isinstance(filepath, unicode):
            filepath = six.u(filepath)

        hash_alg = hash_alg or DEFAULT_HASH_ALG
        hasher = hashlib.new(hash_alg)

        with f_system.open(filepath, 'rb') as f:
            while True:
                data = f.read(buffer_size)
                if not data:
                    break
                hasher.update(data)

        return util.format_hash(hash_alg, hasher.hexdigest())

    @property
    def temp_fs(self):
        return self._temp_fs

    @property
    def persistent_fs(self):
        return self._presistent_fs

    def __exit__(self, exc, value, tb):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        # Cleaning up
        if isinstance(self._temp_fs, fs.tempfs.TempFS):
            # The TempFS cleans up automatically on close
            self._temp_fs.close()
        else:
            # Otherwise clean up manually
            self._presistent_fs.removetree(fs.path.join('tmp', self._tempdir_name))


def get_single_file_field_storage(file_system, use_filepath=False):
    # pylint: disable=attribute-defined-outside-init

    # We dynamically create this class because we
    # can't add arguments to __init__.
    # This is due to the FieldStorage we create
    # in turn creating a FieldStorage for different
    # parts of the form, with a hardcoded set of args
    # https://github.com/python/cpython/blob/1e3e162ff5c0cc656559c43914439ab3e5734f00/Lib/cgi.py#L696
    # https://github.com/python/cpython/blob/1e3e162ff5c0cc656559c43914439ab3e5734f00/Lib/cgi.py#L728

    class SingleFileFieldStorage(cgi.FieldStorage):
        bufsize = 2 ** 20

        def make_file(self, binary=None):

            self.hasher = hashlib.new(DEFAULT_HASH_ALG)
            # Sanitize form's filename (read: prevent malicious escapes, bad characters, etc)
            if use_filepath:
                self.filename = util.sanitize_path(self.filename)
            else:
                self.filename = os.path.basename(self.filename)
            if not isinstance(self.filename, unicode):
                self.filename = six.u(self.filename)
            # If the filepath doesn't exist, make it IF the opted in to use full path as name
            if  self.filename and os.path.dirname(self.filename) and not file_system.exists(os.path.dirname(self.filename)):
                file_system.makedirs(os.path.dirname(self.filename))
            self.open_file = file_system.open(self.filename, 'wb')
            return self.open_file

        # override private method __write of superclass FieldStorage
        # _FieldStorage__file is the private variable __file of the same class
        def _FieldStorage__write(self, line):
            # pylint: disable=access-member-before-definition
            if self._FieldStorage__file is not None:
                # Always write fields of type "file" to disk for consistent renaming behavior
                if self.filename:
                    self.file = self.make_file('')
                    self.file.write(self._FieldStorage__file.getvalue())
                    self.hasher.update(self._FieldStorage__file.getvalue())
                self._FieldStorage__file = None

            self.file.write(line)

            # NOTE: In case of metadata, we don't have a file name and we also don't have a hasher,
            # so skipping the hasher.update
            if self.filename:
                self.hasher.update(line)

    return SingleFileFieldStorage

class FileStoreException(Exception):
    pass

# File extension --> scitran file type detection hueristics.
# Listed in precendence order.
with open(os.path.join(os.path.dirname(__file__), 'filetypes.json')) as fd:
    TYPE_MAP = json.load(fd)

KNOWN_FILETYPES = {ext: filetype for filetype, extensions in TYPE_MAP.iteritems() for ext in extensions}

def guess_type_from_filename(filename):
    particles = filename.split('.')[1:]
    extentions = ['.' + '.'.join(particles[i:]) for i in range(len(particles))]
    for ext in extentions:
        filetype = KNOWN_FILETYPES.get(ext.lower())
        if filetype:
            break
    else:
        filetype = None
    return filetype


def get_valid_file(file_info):
    """
    Get the file path and the filesystem where the file exists.

    First try to serve the file from the current filesystem and
    if the file is not found (likely has not migrated yet) and the instance
    still supports the legacy storage, attempt to serve from there.

    :param file_info: dict, contains the _id and the hash of the file
    :return: (<file's path>, <filesystem>)
    """

    file_path = get_file_path(file_info)
    return file_path, get_fs_by_file_path(file_path)


def get_file_path(file_info):
    """
    Get the file path. If the file has id then returns path_from_uuid otherwise path_from_hash.

    :param file_info: dict, contains the _id and the hash of the file
    :return: <file's path>
    """
    file_id = file_info.get('_id', '')
    file_hash = file_info.get('hash', '')
    file_uuid_path = None
    file_hash_path = None

    if file_hash:
        file_hash_path = util.path_from_hash(file_hash)

    if file_id:
        file_uuid_path = util.path_from_uuid(file_id)

    file_path = file_uuid_path or file_hash_path
    return file_path


def get_signed_url(file_path, file_system, **kwargs):
    try:
        if hasattr(file_system, 'get_signed_url'):
            return file_system.get_signed_url(file_path, **kwargs)
    except fs.errors.NoURL:
        return None


def get_fs_by_file_path(file_path):
    """
    Get the filesystem where the file exists by a valid file path.
    Attempt to serve file from current storage in config.

    If file is not found (likely has not migrated yet) and the instance
    still supports the legacy storage, attempt to serve from there.
    """

    if config.fs.isfile(file_path):
        return config.fs
    elif config.support_legacy_fs and config.local_fs.isfile(file_path):
        return config.local_fs

    ### Temp fix for 3-way split storages, see api.config.local_fs2 for details
    elif config.support_legacy_fs and config.local_fs2 and config.local_fs2.isfile(file_path):
        return config.local_fs2
    ###

    else:
        raise fs.errors.ResourceNotFound('File not found: %s' % file_path)
