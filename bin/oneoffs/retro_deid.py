#!/usr/bin/env python
"""
Retroactively de-identify EFiles, PFiles and PFile headers as follows:

* Scan mongo for files matching the relevant name patterns (~extensions)
* Iterate over file candidates on storage (skip one on error and continue):
   * Copy each file to /tmp and de-identify it in place
   * Calculate new hash and skip if unchanged (meaning it's already de-identified)
   * Copy de-identified file from /tmp to storage
   * Update de-identified file's hash in mongo (potentially on multiple mongo entries)
* Write list of PHI files found on storage into a text file (no deletion)

"""

import argparse
import datetime
import gzip
import hashlib
import itertools
import logging
import os
import re
import shutil
import struct
import sys

from backports import tempfile
import pymongo


TYPE_RE = {'efile': re.compile(r'E\d{5}S\d{3}P\d{5}\.7$'),
           'pfile': re.compile(r'(?P<aux>P\d{5})\.7\.gz$'),
           'pfile_header': re.compile(r'(?P<aux>P\d{5})\.7\.hdr$')}

log = logging.getLogger('retro.deid')


def main(*argv):
    argv = argv or sys.argv[1:] or ['--help']
    args = parse_args(argv)
    date_format = '%Y-%m-%d %H:%M:%S'
    log_format = '%(asctime)s %(levelname)4.4s %(message)s'
    logging.basicConfig(datefmt=date_format,
                        format=log_format,
                        level=getattr(logging, args.log_level.upper()))
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filehandler = logging.FileHandler('{}_retro_deid.log'.format(timestamp))
    filehandler.setFormatter(logging.Formatter(fmt=log_format, datefmt=date_format))
    log.addHandler(filehandler)

    if 'SCITRAN_PERSISTENT_FS_URL' in os.environ:
        log.critical('retro_deid.py is incompatible with object storage (SCITRAN_PERSISTENT_FS_URL)')
        sys.exit(1)

    if not any((args.efile, args.pfile, args.pfile_header)):
        log.info('No types selected, exiting.')
        sys.exit(0)

    log.info('Selected types: [ EFiles:%s | PFiles:%s | PFile headers:%s ]',
             args.efile, args.pfile, args.pfile_header)

    db_uri = os.environ['SCITRAN_PERSISTENT_DB_URI']
    data_path = os.environ.get('SCITRAN_PERSISTENT_DATA_PATH', '/var/scitran/data')
    log.info('Using mongo URI: %s', db_uri)
    log.info('Using data path: %s', data_path)
    db = pymongo.MongoClient(db_uri).get_default_database()

    user_desc = '{}:{}'.format(os.getuid(), os.getgid())
    data_desc = '{}:{}'.format(os.stat(data_path).st_uid, os.stat(data_path).st_gid)
    if user_desc != data_desc:
        log.warning('Running as %s instead of %s (%s)', user_desc, data_desc, data_path)

    version = (db.singletons.find_one({'_id': 'version'}) or {}).get('database', 0)
    file_groups = {'analyses': 'files' if version < 43 else 'inputs'}

    log.info('Scanning mongo for matching files (including deleted containers)...')
    references = []
    for cont_type in ('projects', 'sessions', 'acquisitions', 'collections', 'analyses'):
        for cont in db[cont_type].find():
            for f in cont.get(file_groups.get(cont_type, 'files'), []):
                for type_name, type_re in TYPE_RE.iteritems():
                    if getattr(args, type_name) and type_re.match(f['name']):
                        references.append({
                            'cont_type': cont_type,
                            'cont_id': cont['_id'],
                            'type': type_name,
                            'name': f['name'],
                            'hash': f['hash']})

    if not references:
        log.info('No matching files found in mongo, exiting.')
        sys.exit(0)

    key = lambda ref: ref['hash']
    references.sort(key=key)
    hash_count = len(set(ref['hash'] for ref in references))
    log.info('Found %d unique files across %d mongo references.', hash_count, len(references))

    scan_filename = timestamp + '_scan_files.txt'
    log.info('Writing scan results to "%s"', scan_filename)
    with open(scan_filename, 'w') as f:
        f.write('# retro_deid.py {}\n'.format(' '.join(argv)))
        f.write('\n'.join('{} {}/{}/{}'.format(ref['hash'], ref['cont_type'], ref['cont_id'], ref['name'])
                          for ref in references))
        f.write('\n')

    if args.scan_only:
        sys.exit(0)

    log.info('De-identifying %d files...', hash_count)
    phi_paths = []
    progress = 0
    for orig_hash, refs in itertools.groupby(references, key=key):
        progress += 1
        refs = list(refs)
        log.info('[%d/%d] %s', progress, hash_count, orig_hash)

        with tempfile.TemporaryDirectory() as temp_dir:
            orig_path = os.path.join(data_path, path_from_hash(orig_hash))
            temp_path = os.path.join(temp_dir, orig_hash)
            try:
                shutil.copy(orig_path, temp_path)
            except (IOError, OSError) as exc:
                log.error('  %s', exc)
                log.warning('  Cannot copy file from storage - skipping')
                continue

            gzipped = refs[0]['name'].endswith('.gz')
            if gzipped:
                extracted_path = os.path.join(temp_dir, refs[0]['name']).replace('.gz', '')
                try:
                    with gzip.open(temp_path, 'rb') as f_in, open(extracted_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out, 2**30)
                except (MemoryError, Exception) as exc:
                    log.error('  %s', exc)
                    log.warning('  Cannot extract file - skipping')
                extracted_orig_hash = hash_from_contents(extracted_path)
                temp_path = extracted_path

            loader = EFile if refs[0]['type'] == 'efile' else PFile
            try:
                loader(temp_path, de_identify=True)
            except Exception as exc:
                log.error('  %s', exc)
                log.warning('  Cannot open/de-identify file - skipping')
                continue

            if gzipped:
                extracted_deid_hash = hash_from_contents(temp_path)
                if extracted_deid_hash == extracted_orig_hash:
                    log.info('  File already de-identified - skipping')
                    continue

                compressed_path = temp_path + '.gz'
                try:
                    with open(temp_path, 'rb') as f_in, gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out, 2**30)
                except (MemoryError, Exception) as exc:
                    log.error('  %s', exc)
                    log.warning('  Cannot compress file - skipping')
                temp_path = compressed_path
                deid_hash = hash_from_contents(temp_path)
            else:
                deid_hash = hash_from_contents(temp_path)
                if deid_hash == orig_hash:
                    log.info('  File already de-identified - skipping')
                    continue

            log.info('  De-id hash: %s', deid_hash)
            log.info('  Adding de-identified file to storage')
            deid_path = os.path.join(data_path, path_from_hash(deid_hash))
            if not args.dry_run:
                if not os.path.isdir(os.path.dirname(deid_path)):
                    os.makedirs(os.path.dirname(deid_path))
                shutil.copy(temp_path, deid_path)

            for ref in refs:
                file_group = file_groups.get(ref['cont_type'], 'files')
                log.info('  Updating file hash and size in mongo for %s/%s/%s/%s',
                         ref['cont_type'], ref['cont_id'], file_group, ref['name'])
                if not args.dry_run:
                    cont = db[ref['cont_type']].find_one({'_id': ref['cont_id']})
                    for f in cont.get(file_group, []):
                        if f['name'] == ref['name'] and f['hash'] == orig_hash:
                            f['hash'] = deid_hash
                            f['size'] = os.path.getsize(deid_path)  # EFile size can change
                            db[ref['cont_type']].update_one(
                                {'_id': ref['cont_id']},
                                {'$set': {file_group: cont[file_group]}})
                            break
                    else:
                        log.warning('  Cannot find file with original hash in mongo: it was replaced or removed.')

            phi_paths.append(orig_path)

    if phi_paths:
        phi_filename = timestamp + '_phi_paths.txt'
        log.info('Writing list of PHI files found on storage to "%s"', phi_filename)
        with open(phi_filename, 'w') as f:
            f.write('# retro_deid.py {}\n'.format(' '.join(argv)))
            f.write('\n'.join(sorted(phi_paths)))
            f.write('\n')
    else:
        log.info('No matching PHI files are referenced on storage from mongo.')

    log.info('Done.')


def parse_args(argv):
    """Return parsed CLI arguments"""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--efile', action='store_true', help='Include EFiles [false]')
    parser.add_argument('--pfile', action='store_true', help='Include PFiles [false]')
    parser.add_argument('--pfile-header', action='store_true', help='Include PFile headers [false]')

    parser.add_argument('--scan-only', action='store_true', help='Print matching files and exit')
    parser.add_argument('--dry-run', action='store_true', help='Print what this script would do and exit')
    parser.add_argument('--log-level', default='info', metavar='PATH', help='log level [info]')

    return parser.parse_args(argv)


def path_from_hash(file_hash):
    """Return file path (relative to DATA_PATH) from formatted hash"""
    hash_version, hash_alg, actual_hash = file_hash.split('-')
    first_stanza = actual_hash[0:2]
    second_stanza = actual_hash[2:4]
    return os.path.join(hash_version, hash_alg, first_stanza, second_stanza, file_hash)


def hash_from_contents(file_path, hash_alg='sha384', buffer_size=65536):
    """Return formatted file hash from contents"""
    hasher = hashlib.new(hash_alg)
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            hasher.update(data)
    return '-'.join(('v0', hash_alg, hasher.hexdigest()))


class EFile(object):
    """EFile class"""

    DEID_RE = re.compile(r'(patient (id|name) =).*')

    def __init__(self, filepath, de_identify=False):
        if de_identify:
            lines = open(filepath).readlines()
            with open(filepath, 'w') as f:
                for line in lines:
                    f.write(EFile.DEID_RE.sub(r'\1', line))


class PFileError(Exception):
    pass


class PFile(object):
    """PFile class"""

    VERSION_ATTR_OFFSETS = {
        ('\x19\x04\xd0A', '\x00\x00\xd8A'): {  # v26, v27
            'logo': (0x6e, '10s', True),
            'patient_name': (195184, '65s', True),
            'patient_id': (195249, '65s', True),
            'patient_dob': (195331, '9s', True),
        },
        ('\x00\x00\xc0A', 'V\x0e\xa0A'): {  # v23, v24, v25
            'logo': (34, '10s', True),
            'patient_name': (144344, '65s', True),
            'patient_id': (144409, '65s', True),
            'patient_dob': (144491, '9s', True),
        },
        ('J\x0c\xa0A',): {  # v22
            'logo': (34, '10s', True),
            'patient_name': (144336, '65s', True),
            'patient_id': (144401, '65s', True),
            'patient_dob': (144483, '9s', True),
        },
        ('\x00\x000A',): {  # v12
            'logo': (34, '10s', True),
            'patient_name': (62062, '65s', True),
            'patient_id': (62127, '65s', True),
            'patient_dob': (62209, '9s', True),
        },
    }

    def __init__(self, filepath, de_identify=False):
        attrs, offsets = self.parse(filepath)

        if de_identify:
            with open(filepath, 'r+b') as fd:
                for attr in ('patient_name', 'patient_id', 'patient_dob'):
                    offset, fmt = offsets[attr][:2]
                    fd.seek(offset)
                    fd.write(struct.pack(fmt, '\0'))
                    attrs[attr] = ''

    @classmethod
    def parse(cls, filepath):
        """Return parsed attribute values and their offsets for the specific version"""
        attrs = {}
        offsets = {}
        with open(filepath, 'rb') as fd:
            version_bytes = fd.read(4)
            for versions, offsets in cls.VERSION_ATTR_OFFSETS.iteritems():
                if version_bytes in versions:
                    logo = cls.unpacked_bytes(fd, *offsets['logo'])
                    if logo not in ('GE_MED_NMR', 'INVALIDNMR'):
                        raise PFileError(fd.name + ' is not a valid PFile')
                    break
            else:
                raise PFileError(fd.name + ' is not a valid PFile or of an unsupported version')
            for attr, offset in offsets.iteritems():
                attrs[attr] = cls.unpacked_bytes(fd, *offset)
        return attrs, offsets

    @staticmethod
    def unpacked_bytes(fd, offset, fmt, split=False):
        fd.seek(offset)
        r = struct.unpack(fmt, fd.read(struct.calcsize(fmt)))[0]
        if split:
            r = r.split('\0', 1)[0]
        return r


if __name__ == '__main__':
    try:
        main()
    except Exception:
        log.critical('Unhandled exception', exc_info=True)
        sys.exit(1)
    sys.exit(0)
