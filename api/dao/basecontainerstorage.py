import copy
import bson
import datetime
import pymongo.errors

from . import consistencychecker
from . import containerutil
from . import dbutil
from .. import config
from .. import util

from ..types import Origin
from ..web.errors import APIStorageException, APIConflictException, APINotFoundException

log = config.log

# TODO: Find a better place to put this until OOP where we can just call cont.children
CHILD_MAP = {
    'groups':   'projects',
    'projects': 'sessions',
    'sessions': 'acquisitions'
}

PARENT_MAP = {v: k for k,v in CHILD_MAP.iteritems()}

# All "containers" are required to return these fields
# 'All' includes users
BASE_DEFAULTS = {
    '_id':      None,
    'created':  None,
    'modified': None
}

# All containers that inherit from 'container' in the DM
CONTAINER_DEFAULTS = BASE_DEFAULTS.copy()
CONTAINER_DEFAULTS.update({
    'permissions':  [],
    'files':        [],
    'notes':        [],
    'tags':         [],
    'info':         {}
})


class ContainerStorage(object):
    """
    This class provides access to mongodb collection elements (called containers).
    It is used by ContainerHandler istances for get, create, update and delete operations on containers.
    Examples: projects, sessions, acquisitions and collections
    """

    def __init__(self, cont_name, use_object_id=False, use_delete_tag=False, parent_cont_name=None, child_cont_name=None, list_projection=None):
        self.cont_name = cont_name
        self.parent_cont_name = parent_cont_name
        self.child_cont_name = child_cont_name
        self.use_object_id = use_object_id
        self.use_delete_tag = use_delete_tag
        self.dbc = config.db[cont_name]
        self.list_projection = list_projection

    @classmethod
    def factory(cls, cont_name):
        """
        Factory method to aid in the creation of a ContainerStorage instance
        when cont_name is dynamic.
        """
        cont_storage_name = containerutil.singularize(cont_name).capitalize() + 'Storage'
        for subclass in cls.__subclasses__():
            if subclass.__name__ == cont_storage_name:
                return subclass()
        return cls(containerutil.pluralize(cont_name))

    @classmethod
    def get_top_down_hierarchy(cls, cont_name, cid):
        parent_to_child = {
            'groups': 'projects',
            'projects': 'sessions',
            'sessions': 'acquisitions'
        }

        parent_tree = {
            cont_name: [cid]
        }
        parent_name = cont_name
        while parent_to_child.get(parent_name):
            # Parent storage
            storage = ContainerStorage.factory(parent_name)
            child_name = parent_to_child[parent_name]
            parent_tree[child_name] = []

            # For each parent id, find all of its children and add them to the list of child ids in the parent tree
            for parent_id in parent_tree[parent_name]:
                parent_tree[child_name] = parent_tree[child_name] + [cont["_id"] for cont in storage.get_children_legacy(parent_id, projection={'_id':1})]

            parent_name = child_name
        return parent_tree

    @classmethod
    def filter_container_files(cls, cont):
        if cont is not None and cont.get('files', []):
            cont['files'] = [f for f in cont['files'] if 'deleted' not in f]
            for f in cont['files']:
                f.pop('measurements', None)

    def format_id(self, _id):
        if self.use_object_id:
            try:
                _id = bson.ObjectId(_id)
            except bson.errors.InvalidId as e:
                raise APIStorageException(e.message)
        return _id


    def _fill_default_values(self, cont):
        if cont:
            defaults = BASE_DEFAULTS.copy()
            if self.cont_name not in ['groups', 'users']:
                defaults = CONTAINER_DEFAULTS.copy()
            for k,v in defaults.iteritems():
                cont.setdefault(k, v)


    def get_container(self, _id, projection=None, get_children=False):
        cont = self.get_el(_id, projection=projection)
        if cont is None:
            raise APINotFoundException('Could not find {} {}'.format(self.cont_name, _id))
        if get_children:
            children = self.get_children(_id, projection=projection)
            cont[containerutil.pluralize(self.child_cont_name)] = children
        return cont

    def get_children_legacy(self, _id, projection=None, uid=None):
        """
        A get_children method that returns sessions from the project level rather than subjects.
        Will be removed when Subject completes it's transition to a stand alone collection.
        """
        try:
            child_name = CHILD_MAP[self.cont_name]
        except KeyError:
            raise APIStorageException('Children cannot be listed from the {0} level'.format(self.cont_name))
        if not self.use_object_id:
            query = {containerutil.singularize(self.cont_name): _id}
        else:
            query = {containerutil.singularize(self.cont_name): bson.ObjectId(_id)}

        if uid:
            query['permissions'] = {'$elemMatch': {'_id': uid}}
        if not projection:
            projection = {'info': 0, 'files.info': 0, 'subject': 0, 'tags': 0}
        return ContainerStorage.factory(child_name).get_all_el(query, None, projection)


    def get_children(self, _id, query=None, projection=None, uid=None):
        child_name = self.child_cont_name
        if not child_name:
            raise APIStorageException('Children cannot be listed from the {0} level'.format(self.cont_name))
        if not query:
            query = {}

        query[containerutil.singularize(self.cont_name)] = self.format_id(_id)

        if uid:
            query['permissions'] = {'$elemMatch': {'_id': uid}}
        if not projection:
            projection = {'info': 0, 'files.info': 0, 'subject': 0, 'tags': 0}

        return ContainerStorage.factory(child_name).get_all_el(query, None, projection)


    def get_parent_tree(self, _id, cont=None, projection=None, add_self=False):
        parents = []

        curr_storage = self

        if not cont:
            cont = self.get_container(_id, projection=projection)

        if add_self:
            # Add the referenced container to the list
            cont['cont_type'] = self.cont_name
            parents.append(cont)

        # Walk up the hierarchy until we cannot go any further
        while True:

            try:
                parent = curr_storage.get_parent(cont['_id'], cont=cont, projection=projection)

            except (APINotFoundException, APIStorageException):
                # We got as far as we could, either we reached the top of the hierarchy or we hit a dead end with a missing parent
                break

            curr_storage = ContainerStorage.factory(curr_storage.parent_cont_name)
            parent['cont_type'] = curr_storage.cont_name
            parents.append(parent)

            if curr_storage.parent_cont_name:
                cont = parent
            else:
                break

        return parents

    def get_parent(self, _id, cont=None, projection=None):
        if not cont:
            cont = self.get_container(_id, projection=projection)

        if self.parent_cont_name:
            ps = ContainerStorage.factory(self.parent_cont_name)
            parent = ps.get_container(cont[self.parent_cont_name], projection=projection)
            return parent

        else:
            raise APIStorageException('The container level {} has no parent.'.format(self.cont_name))


    def _from_mongo(self, cont):
        pass

    def _to_mongo(self, payload):
        pass

    # pylint: disable=unused-argument
    def exec_op(self, action, _id=None, payload=None, query=None, user=None,
                public=False, projection=None, recursive=False, r_payload=None,
                replace_metadata=False, unset_payload=None, pagination=None):
        """
        Generic method to exec a CRUD operation from a REST verb.
        """

        check = consistencychecker.get_container_storage_checker(action, self.cont_name)
        data_op = payload or {'_id': _id}
        check(data_op)
        if action == 'GET' and _id:
            return self.get_el(_id, projection=projection, fill_defaults=True)
        if action == 'GET':
            return self.get_all_el(query, user, projection, fill_defaults=True, pagination=pagination)
        if action == 'DELETE':
            return self.delete_el(_id)
        if action == 'PUT':
            return self.update_el(_id, payload, unset_payload=unset_payload, recursive=recursive, r_payload=r_payload, replace_metadata=replace_metadata)
        if action == 'POST':
            return self.create_el(payload)
        raise ValueError('action should be one of GET, POST, PUT, DELETE')

    def create_el(self, payload):
        self._to_mongo(payload)
        try:
            result = self.dbc.insert_one(payload)
        except pymongo.errors.DuplicateKeyError:
            raise APIConflictException('Object with id {} already exists.'.format(payload['_id']))
        return result

    def update_el(self, _id, payload, unset_payload=None, recursive=False, r_payload=None, replace_metadata=False):
        replace = None
        if replace_metadata:
            replace = {}
            if payload.get('info') is not None:
                replace['info'] = util.mongo_sanitize_fields(payload.pop('info'))
            if payload.get('subject') is not None and payload['subject'].get('info') is not None:
                replace['subject.info'] = util.mongo_sanitize_fields(payload['subject'].pop('info'))

        update = {}

        if payload is not None:
            self._to_mongo(payload)
            update['$set'] = util.mongo_dict(payload)

        if unset_payload is not None:
            update['$unset'] = util.mongo_dict(unset_payload)

        if replace is not None:
            update['$set'].update(replace)

        _id = self.format_id(_id)

        if recursive and r_payload is not None:
            containerutil.propagate_changes(self.cont_name, _id, {}, {'$set': util.mongo_dict(r_payload)})

        return self.dbc.update_one({'_id': _id}, update)

    def replace_el(self, _id, payload):
        payload['_id'] = self.format_id(_id)
        return self.dbc.replace_one({'_id': _id}, payload)


    def delete_el(self, _id):
        _id = self.format_id(_id)
        self.cleanup_ancillary_data(_id)
        if self.use_delete_tag:
            return self.dbc.update_one({'_id': _id}, {'$set': {'deleted': datetime.datetime.utcnow()}})
        return self.dbc.delete_one({'_id':_id})

    def cleanup_ancillary_data(self, _id):
        """Optional cleanup of other data that may be associated with this container"""
        pass

    def get_el(self, _id, projection=None, fill_defaults=False):
        _id = self.format_id(_id)
        cont = self.dbc.find_one({'_id': _id, 'deleted': {'$exists': False}}, projection)
        self._from_mongo(cont)
        if fill_defaults:
            self._fill_default_values(cont)
        self.filter_container_files(cont)
        return cont

    def get_all_el(self, query, user, projection, fill_defaults=False, pagination=None):
        if query is None:
            query = {}
        if user:
            if query.get('permissions'):
                query['$and'] = [{'permissions': {'$elemMatch': user}}, {'permissions': query.pop('permissions')}]
            else:
                query['permissions'] = {'$elemMatch': user}
        query['deleted'] = {'$exists': False}

        # if projection includes files.info, add new key `info_exists` and allow reserved info keys through
        if projection and ('info' in projection or 'files.info' in projection or 'subject.info' in projection):
            projection = copy.deepcopy(projection)
            replace_info_with_bool = True
            projection.pop('subject.info', None)
            projection.pop('files.info', None)
            projection.pop('info', None)

            # Replace with None if empty (empty projections only return ids)
            if not projection:
                projection = None
        else:
            replace_info_with_bool = False

        page = dbutil.paginate_find(self.dbc, {'filter': query, 'projection': projection}, pagination)
        results = page['results']

        for cont in results:
            self.filter_container_files(cont)
            self._from_mongo(cont)
            if fill_defaults:
                self._fill_default_values(cont)

            if replace_info_with_bool:
                info = cont.pop('info', {})
                cont['info_exists'] = bool(info)
                cont['info'] = containerutil.sanitize_info(info)

                if cont.get('subject'):
                    s_info = cont['subject'].pop('info', {})
                    cont['subject']['info_exists'] = bool(s_info)
                    cont['subject']['info'] = containerutil.sanitize_info(s_info)

                for f in cont.get('files', []):
                    f_info = f.pop('info', {})
                    f['info_exists'] = bool(f_info)
                    f['info'] = containerutil.sanitize_info(f_info)

        return results if pagination is None else page

    def modify_info(self, _id, payload, modify_subject=False):

        # Support modification of subject info
        # Can be removed when subject becomes a standalone container
        info_key = 'subject.info' if modify_subject else 'info'

        update = {}
        set_payload = payload.get('set')
        delete_payload = payload.get('delete')
        replace_payload = payload.get('replace')

        if (set_payload or delete_payload) and replace_payload is not None:
            raise APIStorageException('Cannot set or delete AND replace info fields.')

        if replace_payload is not None:
            update = {
                '$set': {
                    info_key: util.mongo_sanitize_fields(replace_payload)
                }
            }

        else:
            if set_payload:
                update['$set'] = {}
                for k,v in set_payload.items():
                    update['$set'][info_key + '.' + util.mongo_sanitize_fields(str(k))] = util.mongo_sanitize_fields(v)
            if delete_payload:
                update['$unset'] = {}
                for k in delete_payload:
                    update['$unset'][info_key + '.' + util.mongo_sanitize_fields(str(k))] = ''

        _id = self.format_id(_id)
        query = {'_id': _id }

        if not update.get('$set'):
            update['$set'] = {'modified': datetime.datetime.utcnow()}
        else:
            update['$set']['modified'] = datetime.datetime.utcnow()

        return self.dbc.update_one(query, update)

    @staticmethod
    def join_avatars(containers):
        """
        Given a list of containers, adds avatar and name context to each member of the permissions and notes lists
        """

        # Get list of all users, hash by uid
        # TODO: This is not an efficient solution if there are hundreds of inactive users
        users_list = ContainerStorage.factory('users').get_all_el({}, None, None)
        users = {user['_id']: user for user in users_list}

        for container in containers:
            permissions = container.get('permissions', [])
            notes = container.get('notes', [])

            for item in permissions + notes:
                uid = item.get('user', item['_id'])
                user = users[uid]
                item['avatar'] = user.get('avatar')
                item['firstname'] = user.get('firstname', '')
                item['lastname'] = user.get('lastname', '')

    @staticmethod
    def join_origins(container):
        """Given a container, coalesce and merge origins for all of its files."""

        # Create a map of each type of origin to hold the join
        container['join-origin'] = {
            Origin.user.name:   {},
            Origin.device.name: {},
            Origin.job.name:    {}
        }

        for f in container.get('files', []):
            origin = f.get('origin')

            if origin is None:
                # Backfill origin maps if none provided from DB
                f['origin'] = {'type': str(Origin.unknown), 'id': None}

            else:
                j_type = f['origin']['type']
                j_id   = str(f['origin']['id'])
                j_id_b = bson.ObjectId(j_id) if bson.ObjectId.is_valid(j_id) else j_id

                # Join from database if we haven't for this origin before
                if j_type != 'unknown' and container['join-origin'][j_type].get(j_id) is None:
                    j_types = containerutil.pluralize(j_type)
                    join_doc = config.db[j_types].find_one({'_id': j_id_b})

                    # Alias job.gear_info.name as job.gear_name until UI starts using gear_info.name directly
                    if join_doc is not None and j_type == 'job':
                        join_doc['gear_name'] = join_doc['gear_info']['name']

                    # Save to join table
                    container['join-origin'][j_type][j_id] = join_doc

    def get_list_projection(self):
        """
        Return a copy of the list projection to use with this container, or None.
        It is safe to modify the returned copy.
        """
        if self.list_projection:
            return self.list_projection.copy()
        return None
