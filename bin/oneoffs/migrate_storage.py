#!/usr/bin/env python
"""
Migrate storage backend from legacy storage to PyFilesystem
"""

import argparse
import datetime
import logging
import os
import pprint
import time
import uuid
import sys
import pymongo
from functools import wraps

import fs.move
import fs.path

from fs import open_fs, errors

from api import util

from google.cloud.exceptions import GoogleCloudError

log = logging.getLogger('migrate_storage')

def main(*argv):
    """
    Remove CAS logic, generate UUID for the files and move the files from the lagacy storage to the new one.
    """
    argv = argv or sys.argv[1:]
    args = parse_args(argv)


    date_format = '%Y-%m-%d %H:%M:%S'
    log_format = '%(asctime)s %(levelname)4.4s %(message)s'
    logging.basicConfig(datefmt=date_format,
                        format=log_format,
                        level=getattr(logging, args.log_level.upper()))

    global db, target_fs, local_fs, local_fs2, data_path
    db_uri = os.environ['SCITRAN_PERSISTENT_DB_URI']
    data_path = os.environ['SCITRAN_PERSISTENT_DATA_PATH']
    log.info('Using mongo URI: %s', db_uri)
    log.info('Using data path: %s', data_path)
    db = pymongo.MongoClient(db_uri).get_default_database()
    local_fs = open_fs('osfs://' + data_path)

    ### Temp fix for 3-way split storages, see api.config.local_fs2 for details
    data_path2 = os.path.join(data_path, 'v1')
    if os.path.exists(data_path2):
        log.warning('Path %s exists - enabling 3-way split storage support', data_path2)
        local_fs2 = open_fs('osfs://' + data_path2)
    else:
        local_fs2 = None
    ###

    fs_url = os.environ.get('SCITRAN_PERSISTENT_FS_URL', 'osfs://' + os.path.join(data_path, 'v1'))
    log.info('Migrate files from %s to %s', data_path, fs_url)
    target_fs = open_fs(fs_url)

    try:
        if not (args.containers or args.gears):
            migrate_containers()
            migrate_gears()

        if args.containers:
            migrate_containers()

        if args.gears:
            migrate_gears()

        if args.delete_files:
            log.info('Delete legacy files')
            local_fs.removetree(u'/')

        cleanup_empty_folders()
    except MigrationError:
        log.critical('Migration failed')
        exit(1)

    log.info('Migration completed successfully')


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--containers', action='store_true', help='Migrate containers')
    parser.add_argument('--gears', action='store_true', help='Migrate gears')
    parser.add_argument('--delete-files', action='store_true', help='Delete files from legacy storage')
    parser.add_argument('--log-level', default='info', metavar='PATH', help='log level [info]')

    return parser.parse_args(argv)


def get_src_fs_by_file_path(file_path):
    if local_fs.isfile(file_path):
        return local_fs
    ### Temp fix for 3-way split storages, see api.config.local_fs2 for details
    elif local_fs2 and local_fs2.isfile(file_path):
        return local_fs2
    ###
    else:
        raise fs.errors.ResourceNotFound('File not found: %s' % file_path)


def get_files_by_prefix(document, prefix):
    for key in prefix.split('.'):
        document = document.get(key, {})
    return document


def show_progress(current_index, total_files):
    if current_index % (total_files / 10 + 1) == 0:
        log.info('Processed %s files of total %s files ...' % (current_index, total_files))


def cleanup_empty_folders():
    log.info('Cleanup empty folders')

    for _dirpath, _, _ in os.walk(data_path, topdown=False):
        if not (os.listdir(_dirpath) or data_path == _dirpath):
            os.rmdir(_dirpath)


def get_containers_files(containers_prefixes):
    _files = []

    for container, prefix in containers_prefixes:
        cursor = db.get_collection(container).find({})
        for document in cursor:
            for f in get_files_by_prefix(document, prefix):
                f_dict = {
                    'container_id': document.get('_id'),
                    'container': container,
                    'fileinfo': f,
                    'prefix': prefix
                }
                _files.append(f_dict)

    return _files


def get_gears_files():
    cursor = db.get_collection('gears').find({})
    _files = []

    for document in cursor:
        if document.get('exchange', {}).get('git-commit', '') == 'local':
            f_dict = {
                'gear_id': document['_id'],
                'gear_name': document['gear']['name'],
                'exchange': document['exchange']
            }
            _files.append(f_dict)

    return _files


def retry(exception_to_check, tries=4, delay=3, backoff=2):
    """Retry calling the decorated function using an exponential backoff.

    :param exception_to_check: the exception to check. may be a tuple of
        exceptions to check
    :type exception_to_check: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    """

    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exception_to_check:
                    f_to_migrate = args[0]
                    msg = "Couldn't upload %s/%s/%s to target storage, retrying in %ds (%s)..." % \
                          (f_to_migrate['container'], f_to_migrate['container_id'], f_to_migrate['fileinfo']['name'], mdelay, tries-mtries+1)
                    log.warning(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            try:
                return f(*args, **kwargs)
            except exception_to_check as e:
                if hasattr(e, 'response') and hasattr(e.response, 'text'):
                    log.error(e.response.text)
                raise MigrationError

        return f_retry

    return deco_retry


@retry(GoogleCloudError, tries=4)
def migrate_file(f):
    file_id = f['fileinfo'].get('_id', '')
    if file_id:
        file_path = util.path_from_uuid(file_id)
        if not target_fs.isfile(file_path):
            log.debug('    file aready has id field, just copy to target storage')
            src_fs = get_src_fs_by_file_path(file_path)
            log.debug('    file found in %s' % src_fs)

            dst_dir = fs.path.dirname(file_path)
            target_fs.makedirs(dst_dir, recreate=True)
            fs.move.copy_file(src_fs=src_fs, src_path=file_path, dst_fs=target_fs, dst_path=file_path)
        else:
            log.debug('    file is aready present in target storage, skipping')
    else:
        file_id = str(uuid.uuid4())
        log.debug('    generated uuid: %s', file_id)
        f_old_path = util.path_from_hash(f['fileinfo']['hash'])
        log.debug('    file old path: %s', f_old_path)
        f_new_path = util.path_from_uuid(file_id)
        log.debug('    file new path: %s', f_new_path)

        log.debug('    copy file to target storage')
        dst_dir = fs.path.dirname(f_new_path)
        target_fs.makedirs(dst_dir, recreate=True)
        fs.move.copy_file(src_fs=local_fs, src_path=f_old_path, dst_fs=target_fs, dst_path=f_new_path)

        update_set = {
            f['prefix'] + '.$.modified': datetime.datetime.utcnow(),
            f['prefix'] + '.$._id': file_id
        }

        # Update the file with the newly generated UUID
        updated_doc = db[f['container']].find_one_and_update(
            {'_id': f['container_id'],
             f['prefix'] + '.name': f['fileinfo']['name'],
             f['prefix'] + '.hash': f['fileinfo']['hash']},
            {'$set': update_set}
        )

        if not updated_doc:
            log.info('Probably the following file has been updated during the migration '
                     'and its hash is changed, cleaning up from the new filesystem')
            target_fs.remove(f_new_path)


def migrate_analysis_file(f, migrated_files):
    match = [cf for cf in migrated_files if
             cf['fileinfo']['hash'] == f['fileinfo']['hash'] and cf['fileinfo'].get('_id')]
    # The file is already migrated
    if len(match) > 0 and not f['fileinfo'].get('_id'):
        log.debug('    file was already migrated, just set a reference')
        update_set = {
            f['prefix'] + '.$.modified': match[0]['fileinfo']['modified'],
            f['prefix'] + '.$._id': match[0]['fileinfo']['_id']
        }

        # Update the file with the newly generated UUID
        db[f['container']].find_one_and_update(
            {'_id': f['container_id'],
             f['prefix'] + '.name': f['fileinfo']['name'],
             f['prefix'] + '.hash': f['fileinfo']['hash']},
            {'$set': update_set}
        )
    else:
        log.debug('    migrate file normally')
        migrate_file(f)


def migrate_containers():
    log.info('Migrate container (projects, acquisitions, sessions, subject, collections) files...')

    container_files = get_containers_files([('projects', 'files'),
                                            ('acquisitions', 'files'),
                                            ('sessions', 'files'),
                                            ('sessions', 'subject.files'),
                                            ('collections', 'files'),
                                            ('analyses', 'files')])

    for i, f in enumerate(container_files):
        log.debug('  [%s/%s] %s/%s/%s', i+1, len(container_files), f['container'], f['container_id'],
                  f['fileinfo']['name'])
        migrate_file(f)
        show_progress(i + 1, len(container_files))

    log.info('Migrate analysis files...')
    # Refresh the list of container files
    migrated_files = get_containers_files([('projects', 'files'),
                                           ('acquisitions', 'files'),
                                           ('sessions', 'files'),
                                           ('sessions', 'subject.files'),
                                           ('collections', 'files'),
                                           ('analyses', 'files')])
    analysis_files = get_containers_files([('analyses', 'inputs')])

    for i, f in enumerate(analysis_files):
        log.debug('  [%s/%s] %s/%s/%s', i+1, len(container_files), f['container'], f['container_id'],
                  f['fileinfo']['name'])
        migrate_analysis_file(f, migrated_files)
        show_progress(i + 1, len(analysis_files))


def migrate_gear_files(f):
    file_id = f['exchange'].get('rootfs-id', '')
    if file_id:
        file_path = util.path_from_uuid(file_id)
        if not target_fs.isfile(file_path):
            log.debug('    file aready has id field, just copy to target storage')
            src_fs = get_src_fs_by_file_path(file_path)
            log.debug('    file found in %s' % src_fs)

            dst_dir = fs.path.dirname(file_path)
            target_fs.makedirs(dst_dir, recreate=True)
            fs.move.copy_file(src_fs=src_fs, src_path=file_path, dst_fs=target_fs, dst_path=file_path)
        else:
            log.debug('    file is aready present in target storage, skipping')
    else:
        file_id = str(uuid.uuid4())
        file_hash = 'v0-' + f['exchange']['rootfs-hash'].replace(':', '-')
        f_old_path = util.path_from_hash(file_hash)
        log.debug('    file old path: %s', f_old_path)
        f_new_path = util.path_from_uuid(file_id)
        log.debug('    file new path: %s', f_new_path)

        log.debug('    copy file to target storage')

        dst_dir = fs.path.dirname(f_new_path)
        target_fs.makedirs(dst_dir, recreate=True)
        fs.move.copy_file(src_fs=local_fs, src_path=f_old_path, dst_fs=target_fs, dst_path=f_new_path)

        update_set = {
            'modified': datetime.datetime.utcnow(),
            'exchange.rootfs-id': file_id
        }

        # Update the gear with the newly generated UUID
        db['gears'].find_one_and_update(
            {'_id': f['gear_id']},
            {'$set': update_set}
        )


def migrate_gears():
    log.info('Migrate gears...')

    _files = get_gears_files()

    for i, f in enumerate(_files):
        log.debug('  [%s/%s] gears/%s/%s', i+1, len(_files), f['gear_id'], f['gear_name'])
        migrate_gear_files(f)
        show_progress(i + 1, len(_files))


class MigrationError(Exception):
    pass


if __name__ == '__main__':
    try:
        main()
    except Exception:
        log.critical('Unhandled exception', exc_info=True)
        exit(1)
    exit(0)
