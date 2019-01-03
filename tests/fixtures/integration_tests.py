import copy
import os

import attrdict
import fs.move
import fs.path
import pymongo
import pytest
import requests

from api import config, files, util

# load required envvars w/ the same name
SCITRAN_PERSISTENT_DB_LOG_URI = os.environ['SCITRAN_PERSISTENT_DB_LOG_URI']
SCITRAN_PERSISTENT_DB_URI = os.environ['SCITRAN_PERSISTENT_DB_URI']
SCITRAN_SITE_API_URL = os.environ['SCITRAN_SITE_API_URL']


@pytest.fixture(scope='session')
def session():
    """Return session Object which used by as_{drone, admin, public, user} fixtures"""
    def session():
        return BaseUrlSession()
    return session


@pytest.fixture(scope='session')
def api_db():
    """Return mongo client for the api db"""
    return pymongo.MongoClient(SCITRAN_PERSISTENT_DB_URI).get_database()


@pytest.fixture(scope='session')
def log_db():
    """Return mongo client for the log db"""
    return pymongo.MongoClient(SCITRAN_PERSISTENT_DB_LOG_URI).get_database()


@pytest.fixture(scope='function')
def with_user(data_builder, randstr, as_public):
    """Return AttrDict with new user, api-key and api-accessor"""
    api_key = randstr()
    user = data_builder.create_user(api_key=api_key, role='user')
    session = copy.deepcopy(as_public)
    session.headers.update({'Authorization': 'scitran-user ' + api_key})
    return attrdict.AttrDict(user=user, api_key=api_key, session=session)


@pytest.yield_fixture(scope='function')
def legacy_cas_file(as_admin, api_db, data_builder, randstr, file_form):
    """Yield legacy CAS file"""
    project = data_builder.create_project()
    file_name = '%s.csv' % randstr()
    file_content = randstr()
    as_admin.post('/projects/' + project + '/files', files=file_form((file_name, file_content)))

    file_info = api_db['projects'].find_one(
        {'files.name': file_name}
    )['files'][0]
    file_id = file_info['_id']
    file_hash = file_info['hash']
    # verify cas backward compatibility
    api_db['projects'].find_one_and_update(
        {'files.name': file_name},
        {'$unset': {'files.$._id': ''}}
    )

    file_path = unicode(util.path_from_hash(file_hash))
    target_dir = fs.path.dirname(file_path)
    if not config.local_fs.exists(target_dir):
        config.local_fs.makedirs(target_dir)
    fs.move.move_file(src_fs=config.fs, src_path=util.path_from_uuid(file_id), dst_fs=config.local_fs, dst_path=file_path)

    yield (project, file_name, file_content)

    # clean up
    config.local_fs.remove(file_path)
    config.local_fs.removetree(target_dir)
    api_db['projects'].delete_one({'_id': project})


class BaseUrlSession(requests.Session):
    """Requests session subclass using core api's base url"""
    def __init__(self, *args, **kwargs):
        super(BaseUrlSession, self).__init__(*args, **kwargs)
        self.headers.update({ 'X-Accept-Feature': 'beta' })

    def request(self, method, url, **kwargs):
        return super(BaseUrlSession, self).request(method, SCITRAN_SITE_API_URL + url, **kwargs)

