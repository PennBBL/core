from ..types import Origin
from ..web.errors import APIPermissionException

PERMISSIONS = [
    {
        'rid': 'ro',
        'name': 'Read-Only',
    },
    {
        'rid': 'rw',
        'name': 'Read-Write',
    },
    {
        'rid': 'admin',
        'name': 'Admin',
    },
]

INTEGER_PERMISSIONS = {r['rid']: i for i, r in enumerate(PERMISSIONS)}

def _get_access(uid, container, scope=None):
    if scope:
        if _check_scope(scope, container):
            return INTEGER_PERMISSIONS[scope['access']]
        else:
            return -1
    permissions_list = container.get('permissions', [])
    for perm in permissions_list:
        if perm['_id'] == uid:
            return INTEGER_PERMISSIONS[perm['access']]
    return -1

def _check_scope(scope, container, parent_container=None):
    if container and container.get('parents'):
        return scope['id'] in container['parents'].itervalues() or scope['id'] == container['_id']
    elif parent_container and parent_container.get('parents'):
        return scope['id'] in parent_container['parents'].itervalues() or scope['id'] == parent_container['_id']

def has_access(uid, container, perm):
    return _get_access(uid, container) >= INTEGER_PERMISSIONS[perm]


def always_ok(exec_op):
    """
    This decorator leaves the original method unchanged.
    It is used as permissions checker when the request is a superuser_request
    """
    return exec_op

def require_login(handler_method):
    """
    A decorator to ensure the request is not a public request.

    Accepts superuser and non-superuser requests.
    Accepts drone and user requests.
    """
    def check_login(self, *args, **kwargs):
        if self.public_request:
            raise APIPermissionException('Login required.')
        return handler_method(self, *args, **kwargs)
    return check_login

def require_developer(handler_method):
    """
    a decorator to ensure the request is made as a developer.

    Accepts drone, site-admin, and developer requests.
    """
    def check_developer(self, *args, **kwargs):
        if not self.user_is_developer:
            raise APIPermissionException('Developer role required.')
        return handler_method(self, *args, **kwargs)
    return check_developer

def require_admin(handler_method):
    """
    A decorator to ensure the request is made as superuser.

    Accepts drone and user requests.
    """
    def check_admin(self, *args, **kwargs):
        if not self.user_is_admin:
            raise APIPermissionException('Admin user required.')
        return handler_method(self, *args, **kwargs)
    return check_admin

def require_superuser(handler_method):
    """
    A decorator to ensure the request is made as superuser.

    Accepts drone and user requests.
    """
    def check_superuser(self, *args, **kwargs):
        if not self.superuser_request:
            raise APIPermissionException('Superuser required.')
        return handler_method(self, *args, **kwargs)
    return check_superuser

def require_drone(handler_method):
    """
    A decorator to ensure the request is made as a drone.

    Will also ensure superuser, which is implied with a drone request.
    """
    def check_drone(self, *args, **kwargs):
        if self.origin.get('type', '') != Origin.device:
            raise APIPermissionException('Drone request required.')
        if not self.superuser_request:
            raise APIPermissionException('Superuser required.')
        return handler_method(self, *args, **kwargs)
    return check_drone
