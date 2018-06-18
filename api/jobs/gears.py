"""
Gears
"""

from __future__ import absolute_import

import bson.objectid
import datetime
from jsonschema import Draft4Validator, ValidationError
import gears as gear_tools
import pymongo

from .. import config
from ..dao import dbutil
from .jobs import Job

from ..web.errors import APIValidationException, APINotFoundException

log = config.log

def get_gears(pagination=None):
    """
    Fetch the install-global gears from the database
    """

    if pagination:
        pagination['pipe_key'] = lambda key: 'original.' + key

    pipe = [
        {'$sort': {
            'gear.name': 1,
            'created': -1,
        }},
        {'$group': {
            '_id': { 'name': '$gear.name' },
            'original': { '$first': '$$CURRENT' }
        }}
    ]

    page = dbutil.paginate_pipe(config.db.gears, pipe, pagination)
    page['results'] = [r['original'] for r in page['results']]
    return page['results'] if pagination is None else page

def get_gear(_id):
    return config.db.gears.find_one({'_id': bson.ObjectId(_id)})

def get_gear_by_name(name):

    # Find a gear from the list by name
    gear_doc = list(config.db.gears.find({'gear.name': name}).sort('created', pymongo.DESCENDING))

    if len(gear_doc) == 0 :
        raise APINotFoundException('Unknown gear ' + name)

    return gear_doc[0]

def get_invocation_schema(gear):
    return gear_tools.derive_invocation_schema(gear['gear'])

def add_suggest_info_to_files(gear, files):
    """
    Given a list of files, add information to each file that details those that would work well for each input on a gear.
    """

    invocation_schema = get_invocation_schema(gear)

    schemas = {}
    for x in gear['gear']['inputs']:
        input_ = gear['gear']['inputs'][x]
        if input_.get('base') == 'file':
            schema = gear_tools.isolate_file_invocation(invocation_schema, x)
            schemas[x] = Draft4Validator(schema)

    for f in files:
        f['suggested'] = {}
        for x in schemas:
            f['suggested'][x] = schemas[x].is_valid(f)

    return files

def suggest_for_files(gear, files, context=None):

    invocation_schema = get_invocation_schema(gear)
    schemas = {}
    suggested_inputs = {}

    for x in gear['gear']['inputs']:
        input_ = gear['gear']['inputs'][x]
        if input_.get('base') == 'context':
            if x in context:
                suggested_inputs[x] = [{
                    'base': 'context',
                    'found': True,
                    'value': context[x]['value']
                }]
            else:
                suggested_inputs[x] = [{
                    'base': 'context',
                    'found': False
                }]
        else:
            schema = gear_tools.isolate_file_invocation(invocation_schema, x)
            schemas[x] = Draft4Validator(schema)

    for input_name, schema in schemas.iteritems():
        suggested_inputs[input_name] = []
        for f in files:
            if schema.is_valid(f):
                suggested_inputs[input_name].append({
                    'base': 'file',
                    'name': f.get('name')
                })

    return suggested_inputs

def validate_gear_config(gear, config_):
    if len(gear.get('manifest', {}).get('config', {})) > 0:
        invocation = gear_tools.derive_invocation_schema(gear['manifest'])
        ci = gear_tools.isolate_config_invocation(invocation)
        validator = Draft4Validator(ci)

        try:
            validator.validate(config_)
        except ValidationError as err:
            key = None
            if len(err.relative_path) > 0:
                key = err.relative_path[0]

            raise APIValidationException({
                'reason': 'config did not match manifest',
                'error': err.message.replace("u'", "'"),
                'key': key
            })
    return True

def fill_gear_default_values(gear, config_):
    """
    Given a gear and a config map, fill any missing keys using defaults from the gear's config
    """

    if config_ is None:
        config_ = {}

    for k,v in gear['gear'].get('config', {}).iteritems():
        if 'default' in v:
            config_.setdefault(k, v['default'])

    return config_

def count_file_inputs(geardoc):
    return len([inp for inp in geardoc['gear']['inputs'].values() if inp['base'] == 'file'])

def insert_gear(doc):
    gear_tools.validate_manifest(doc['gear'])

    # This can be mongo-escaped and re-used later
    if doc.get("invocation-schema"):
        del(doc["invocation-schema"])

    now = datetime.datetime.utcnow()

    doc['created']  = now
    doc['modified'] = now

    result = config.db.gears.insert(doc)

    if config.get_item('queue', 'prefetch'):
        log.info('Queuing prefetch job for gear %s', doc['gear']['name'])

        job = Job(str(doc['_id']), {}, destination={}, tags=['prefetch'], request={
            'inputs': [
                {
                    'type': 'http',
                    'uri': doc['exchange']['rootfs-url'],
                    'vu': 'vu0:x-' + doc['exchange']['rootfs-hash']
                }
            ],
            'target': {
                'command': ['uname', '-a'],
                'env': {
                    'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
                },
            },
            'outputs': [ ],
        })
        job.insert()

    return result


def remove_gear(_id):
    result = config.db.gears.delete_one({"_id": bson.ObjectId(_id)})

    if result.deleted_count != 1:
        raise Exception("Deleted failed " + str(result.raw_result))

def upsert_gear(doc):
    check_for_gear_insertion(doc)

    return insert_gear(doc)

def check_for_gear_insertion(doc):
    gear_tools.validate_manifest(doc['gear'])

    # Remove previous gear if name & version combo already exists

    conflict = config.db.gears.find_one({
        'gear.name': doc['gear']['name'],
        'gear.version': doc['gear']['version']
    })

    if conflict is not None:
        raise Exception('Gear "' + doc['gear']['name'] + '" version "' + doc['gear']['version'] + '" already exists, consider changing the version string.')
