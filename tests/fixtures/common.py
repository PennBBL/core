import binascii
import bson
import copy
import datetime
import json
import logging
import os

import attrdict
import bson
import pytest

SCITRAN_CORE_DRONE_SECRET = os.environ['SCITRAN_CORE_DRONE_SECRET']
SCITRAN_ADMIN_API_KEY = None
SCITRAN_USER_API_KEY = binascii.hexlify(os.urandom(10))


@pytest.fixture(scope='session')
def file_form():

    def file_form(*files, **kwargs):
        """Return multipart/form-data for file upload requests"""
        data = {}
        for i, file_ in enumerate(files):
            if isinstance(file_, str):
                file_ = (file_, 'test\ndata\n')
            data['file' + str(i + 1)] = file_
        if len(files) == 1:
            data['file'] = data.pop('file1')
        meta = kwargs.pop('meta', None)
        if meta:
            data['metadata'] = ('', json.dumps(meta))
        return data

    return file_form


@pytest.fixture(scope='module')
def log(request):
    """Return logger for the test module for easy logging from tests"""
    log = logging.getLogger(request.module.__name__)
    log.addHandler(logging.StreamHandler())
    return log


@pytest.fixture(scope='function')
def randstr(request):

    def randstr():
        """Return random string prefixed with test module and function name"""
        # NOTE Useful for generating required unique document fields in data_builder
        # or in tests directly by using the fixture. Uses hex strings as each of
        # those fields (user._id, group._id, gear.gear.name) support [a-z0-9]

        def clean(test_name):
            return test_name.lower().replace('test_', '').rstrip('_').replace('_', '-')

        module = clean(request.module.__name__)
        function = clean(request.function.__name__)
        prefix = module + '-' + function
        return prefix[:21] + '-' + binascii.hexlify(os.urandom(5))

    return randstr


@pytest.yield_fixture(scope='function')
def data_builder(as_root, api_db, randstr):
    """Yield DataBuilder instance (per test)"""
    # NOTE currently there's only a single data_builder for simplicity which
    # uses as_root - every resource is created/owned by the admin user
    data_builder = DataBuilder(as_root, api_db, randstr=randstr)
    yield data_builder
    data_builder.teardown()


@pytest.fixture(scope='function')
def default_payload():
    """Return default test resource creation payloads"""
    return attrdict.AttrDict({
        'user': {'firstname': 'test', 'lastname': 'user'},
        'group': {},
        'project': {'public': True},
        'subject': {'public': True},
        'session': {'public': True},
        'acquisition': {'public': True},
        'collection': {},
        'gear': {
            'exchange': {
                'git-commit': 'aex',
                'rootfs-hash': 'sha384:oy',
                'rootfs-url': 'https://test.test'
            },
            'gear': {
                'author': 'test',
                'config': {},
                'description': 'test',
                'inputs': {
                    'text': {
                        'base': 'file',
                        'name': {'pattern': '^.*.txt$'},
                        'size': {'maximum': 100000}
                    }
                },
                'label': 'test',
                'license': 'BSD-2-Clause',
                'source': 'https://test.test',
                'url': 'https://test.test',
                'version': '0.0.1',
            },
        },
        'job': {'inputs': {}},
    })


@pytest.fixture(scope='session')
def merge_dict():
    def merge_dict(a, b):
        """Merge two dicts into the first recursively"""
        for key, value in b.iteritems():
            if key in a and isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_dict(a[key], b[key])
            else:
                a[key] = b[key]
    return merge_dict


@pytest.fixture(scope='session')
def bootstrap_users(session, api_db):
    """Create admin and non-admin users with api keys"""
    global SCITRAN_ADMIN_API_KEY
    _session = session()
    r = _session.post('/users', json={'email': 'admin@user.com', 'firstname': 'Test', 'lastname': 'Admin'})
    assert r.ok
    if callable(r.json):
        SCITRAN_ADMIN_API_KEY = r.json()['key']
    else:
        SCITRAN_ADMIN_API_KEY = r.json['key']
    _session.headers.update({'Authorization': 'scitran-user {}'.format(SCITRAN_ADMIN_API_KEY)})
    data_builder = DataBuilder(_session, api_db)
    data_builder.create_user(email='user@user.com', api_key=SCITRAN_USER_API_KEY)
    yield data_builder
    api_db.users.delete_many({})
    api_db.singletons.delete_one({'_id': 'bootstrap'})


@pytest.fixture(scope='session')
def as_drone(session):
    """Return ApiAccessor with drone access"""
    _session = session()
    _session.headers.update({
        'X-SciTran-Method': 'bootstrapper',
        'X-SciTran-Name': 'Bootstrapper',
        'X-SciTran-Auth': SCITRAN_CORE_DRONE_SECRET,
    })
    return _session

@pytest.fixture(scope='session')
def as_root(session, bootstrap_users):
    """Return requests session using admin api key and root=true"""
    _session = session()
    _session.headers.update({'Authorization': 'scitran-user {}'.format(SCITRAN_ADMIN_API_KEY)})
    _session.params.update({'root': 'true'})
    return _session


@pytest.fixture(scope='session')
def as_admin(session, bootstrap_users):
    _session = session()
    _session.headers.update({'Authorization': 'scitran-user {}'.format(SCITRAN_ADMIN_API_KEY)})
    return _session


@pytest.fixture(scope='session')
def as_user(session, bootstrap_users):
    _session = session()
    _session.headers.update({'Authorization': 'scitran-user {}'.format(SCITRAN_USER_API_KEY)})
    return _session


@pytest.fixture(scope='function')
def as_public(session):
    """Return ApiAccessor without authentication"""
    return session()


class DataBuilder(object):
    child_to_parent = {
        'project':     'group',
        'session':     'project',
        'acquisition': 'session',
    }
    parent_to_child = {parent: child for child, parent in child_to_parent.items()}

    def __init__(self, session, api_db, randstr=lambda: binascii.hexlify(os.urandom(10))):
        self.api_db = api_db
        self.session = session
        self.randstr = randstr
        self.resources = []

    def __getattr__(self, name):
        """Return resource specific create_* or delete_* method"""
        if name.startswith('create_') or name.startswith('delete_'):
            method, resource = name.split('_', 1)
            if resource not in _default_payload:
                raise Exception('Unknown resource type {} (from {})'.format(resource, name))
            def resource_method(*args, **kwargs):
                return getattr(self, method)(resource, *args, **kwargs)
            return resource_method
        raise AttributeError

    def create(self, resource, **kwargs):
        """Create resource in api and return it's _id"""

        # merge any kwargs on top of the default payload
        payload = copy.deepcopy(_default_payload[resource])
        _merge_dict(payload, kwargs)

        # add missing required unique fields using randstr
        # such fields are: [user._id, group._id, gear.gear.name]
        if resource == 'user' and 'email' not in payload:
            payload['email'] = self.randstr() + '@user.com'
        if resource == 'group' and '_id' not in payload:
            payload['_id'] = self.randstr()
        if resource == 'gear' and 'name' not in payload['gear']:
            payload['gear']['name'] = self.randstr()
        if resource == 'collection' and 'label' not in payload:
            payload['label'] = self.randstr()

        # add missing label fields using randstr
        # such fields are: [project.label, session.label, acquisition.label]
        if resource in self.child_to_parent and 'label' not in payload:
            payload['label'] = self.randstr()

        # add missing parent container when creating child container
        if resource in self.child_to_parent:
            parent = self.child_to_parent[resource]
            if parent not in payload:
                payload[parent] = self.get_or_create(parent)

        # add missing gear when creating job
        if resource == 'job' and 'gear_id' not in payload:

            # create file inputs for each job input on gear
            gear_inputs = {}
            for i in payload.get('inputs', {}).keys():
                gear_inputs[i] = {'base': 'file'}

            gear_doc = copy.deepcopy(_default_payload['gear']['gear'])
            gear_doc['inputs'] = gear_inputs
            payload['gear_id'] = self.create('gear', gear=gear_doc)

        # put together the create url to post to
        create_url = '/' + resource + 's'
        if resource == 'gear':
            create_url += '/' + payload['gear']['name']
        if resource == 'job':
            create_url += '/add'

        # handle user api keys (they are set via mongo directly)
        if resource == 'user':
            user_api_key = payload.pop('api_key', None)

        # create resource
        r = self.session.post(create_url, json=payload)
        if callable(r.json):
            r_json = r.json()
        else:
            r_json = r.json
        if not r.ok:
            raise Exception(
                'DataBuilder failed to create {}: {}\n'
                'Payload was:\n{}'.format(resource, r_json['message'], payload))
        _id = r_json['_id']

        # inject api key if it was provided
        if resource == 'user' and user_api_key:
            self.api_db.apikeys.insert_one({
                '_id': user_api_key,
                'created': datetime.datetime.utcnow(),
                'last_seen': None,
                'type': 'user',
                'origin': {'type': 'user', 'id': bson.ObjectId(_id)}
            })

        self.resources.append((resource, _id))
        return _id

    def get_or_create(self, resource):
        """Return first _id from self.resources for type `resource` (Create if not found)"""
        for resource_, _id in self.resources:
            if resource == resource_:
                return _id
        return self.create(resource)

    def teardown(self):
        """Delete resources created with this DataBuilder from self.resources"""
        for resource, _id in reversed(self.resources):
            self.delete(resource, _id)

    def delete(self, resource, _id, recursive=False):
        """Delete resource from mongodb by _id"""
        if bson.ObjectId.is_valid(_id):
            _id = bson.ObjectId(_id)
        if resource == 'project':
            # Subjects are implicitly created via sessions.
            # Remove them even with recursive=False
            self.api_db.subjects.delete_many({resource: _id})
        if recursive and resource in self.parent_to_child:
            child_cont = self.parent_to_child[resource]
            for child in self.api_db[child_cont + 's'].find({resource: _id}, {'_id': 1}):
                self.delete(child_cont, child['_id'], recursive=recursive)
        if resource == 'gear':
            self.api_db.jobs.remove({'gear_id': str(_id)})
        if resource == 'user':
            self.api_db.apikeys.delete_one({'origin.id': _id})
        self.api_db[resource + 's'].remove({'_id': _id})


_default_payload = default_payload()
_merge_dict = merge_dict()
