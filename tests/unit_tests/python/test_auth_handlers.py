import pytest

from api.dao import noop
from api.auth.containerauth import any_referer
from api.web.errors import APIPermissionException

from pprint import pprint

class MockRequestHandler(object):
    def __init__(self, method, uid, public_request=False, user_is_admin=False):
        self.method = method
        self.uid = uid
        self.public_request = public_request
        self.user_is_admin = user_is_admin

def verify_has_access(method, uid, referer, **kwargs):
    handler = MockRequestHandler(method, uid, **kwargs)
    f = referer(handler)(noop)
    try:
        f(method)
    except APIPermissionException:
        pytest.fail('Expected request to succeed')

def verify_has_no_access(method, uid, referer, **kwargs):
    handler = MockRequestHandler(method, uid, **kwargs)
    f = referer(handler)(noop)
    try:
        f(method)
        pytest.fail('Expected request to fail with APIPermissionException')
    except APIPermissionException:
        pass

def curry_referer(referer, **kwargs):
    def fn(handler):
        return referer(handler, **kwargs)
    return fn

public_data_view = { 'public': True }
private_data_view = {}

def test_any_referer_with_site():
    uid = 'user@user.com'

    # Public access
    referer = curry_referer(any_referer, container=public_data_view, parent_container='site')
    verify_has_access('GET', uid, referer)
    verify_has_no_access('PUT', uid, referer)
    verify_has_access('GET', uid, referer, user_is_admin=True)
    verify_has_access('PUT', uid, referer, user_is_admin=True)

    # Private access
    referer = curry_referer(any_referer, container=private_data_view, parent_container='site')
    verify_has_no_access('GET', uid, referer)
    verify_has_no_access('PUT', uid, referer)
    verify_has_access('GET', uid, referer, user_is_admin=True)
    verify_has_access('PUT', uid, referer, user_is_admin=True)

def test_any_referer_with_user():
    uid = 'user@user.com'
    uid2 = 'user2@user.com'

    parent_container = {'cont_name': 'user', '_id': uid}

    # Public access, different user
    referer = curry_referer(any_referer, container=public_data_view, parent_container=parent_container)
    verify_has_access('GET', uid2, referer)
    verify_has_no_access('PUT', uid2, referer)

    # Public access, same user
    verify_has_access('GET', uid, referer)
    verify_has_access('PUT', uid, referer)

    # Private access, different user
    referer = curry_referer(any_referer, container=private_data_view, parent_container=parent_container)
    verify_has_no_access('GET', uid2, referer)
    verify_has_no_access('PUT', uid2, referer)

    # Private access, same user
    verify_has_access('GET', uid, referer)
    verify_has_access('PUT', uid, referer)

    # Private access, superuser
    verify_has_access('GET', uid2, referer, user_is_admin=True)
    verify_has_access('PUT', uid2, referer, user_is_admin=True)

def test_any_referer_with_group():
    uid = 'user@user.com'
    uid2 = 'user2@user.com'
    uid3 = 'user3@user.com'
    uid4 = 'user4@user.com'

    parent_container = {
        'cont_name': 'group', 
        'permissions': [
            { '_id': uid,  'access': 'admin' },
            { '_id': uid2, 'access': 'rw' },
            { '_id': uid3, 'access': 'ro' }
        ]
    }

    # Public access, admin user
    referer = curry_referer(any_referer, container=public_data_view, parent_container=parent_container)
    verify_has_access('GET', uid, referer)
    verify_has_access('PUT', uid, referer)

    # Public access, rw user
    verify_has_access('GET', uid2, referer)
    verify_has_no_access('PUT', uid2, referer)

    # Public access, ro user
    verify_has_access('GET', uid3, referer)
    verify_has_no_access('PUT', uid3, referer)

    # Public access, public user
    verify_has_access('GET', uid4, referer)
    verify_has_no_access('PUT', uid4, referer)

    # Public access, superuser
    verify_has_access('GET', uid4, referer, user_is_admin=True)
    verify_has_access('PUT', uid4, referer, user_is_admin=True)

    # Private access, admin user
    referer = curry_referer(any_referer, container=private_data_view, parent_container=parent_container)
    verify_has_access('GET', uid, referer)
    verify_has_access('PUT', uid, referer)

    # Private access, rw user
    verify_has_access('GET', uid2, referer)
    verify_has_no_access('PUT', uid2, referer)

    # Private access, ro user
    verify_has_access('GET', uid3, referer)
    verify_has_no_access('PUT', uid3, referer)

    # Private access, public user
    verify_has_no_access('GET', uid4, referer)
    verify_has_no_access('PUT', uid4, referer)

    # Private access, superuser
    verify_has_access('GET', uid4, referer, user_is_admin=True)
    verify_has_access('PUT', uid4, referer, user_is_admin=True)

def test_any_referer_with_container():
    uid = 'user@user.com'
    uid2 = 'user2@user.com'
    uid3 = 'user3@user.com'
    uid4 = 'user4@user.com'

    parent_container = {
        'cont_name': 'project', 
        'permissions': [
            { '_id': uid,  'access': 'admin' },
            { '_id': uid2, 'access': 'rw' },
            { '_id': uid3, 'access': 'ro' }
        ]
    }

    # Public access, admin user
    referer = curry_referer(any_referer, container=public_data_view, parent_container=parent_container)
    verify_has_access('GET', uid, referer)
    verify_has_access('PUT', uid, referer)

    # Public access, rw user
    verify_has_access('GET', uid2, referer)
    verify_has_access('PUT', uid2, referer)

    # Public access, ro user
    verify_has_access('GET', uid3, referer)
    verify_has_no_access('PUT', uid3, referer)

    # Public access, public user
    verify_has_access('GET', uid4, referer)
    verify_has_no_access('PUT', uid4, referer)

    # Public access, superuser
    verify_has_access('GET', uid4, referer, user_is_admin=True)
    verify_has_access('PUT', uid4, referer, user_is_admin=True)

    # Private access, admin user
    referer = curry_referer(any_referer, container=private_data_view, parent_container=parent_container)
    verify_has_access('GET', uid, referer)
    verify_has_access('PUT', uid, referer)

    # Private access, rw user
    verify_has_access('GET', uid2, referer)
    verify_has_access('PUT', uid2, referer)

    # Private access, ro user
    verify_has_access('GET', uid3, referer)
    verify_has_no_access('PUT', uid3, referer)

    # Private access, public user
    verify_has_no_access('GET', uid4, referer)
    verify_has_no_access('PUT', uid4, referer)

    # Private access, superuser
    verify_has_access('GET', uid4, referer, user_is_admin=True)
    verify_has_access('PUT', uid4, referer, user_is_admin=True)

