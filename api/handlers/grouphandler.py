import datetime
import bson

from ..web import base
from .. import util
from .. import validators
from ..auth import groupauth, require_admin
from ..dao import containerstorage


GROUP_ID_BLACKLIST = [ 'unknown', 'site' ]


class GroupHandler(base.RequestHandler):

    def __init__(self, request=None, response=None):
        super(GroupHandler, self).__init__(request, response)
        self.storage = containerstorage.GroupStorage()

    def get(self, _id):
        group = self._get_group(_id)
        permchecker = groupauth.default(self, group)
        result = permchecker(self.storage.exec_op)('GET', _id)
        if not self.superuser_request and not self.is_true('join_avatars'):
            self._filter_permissions([result], self.uid)
        if self.is_true('join_avatars'):
            self.storage.join_avatars([result])
        util.add_container_type(self.request, result)
        return result

    @require_admin
    def delete(self, _id):
        if _id in GROUP_ID_BLACKLIST:
            self.abort(400, 'The group "{}" can\'t be deleted as it is integral within the API'.format(_id))
        group = self._get_group(_id)
        permchecker = groupauth.default(self, group)
        result = permchecker(self.storage.exec_op)('DELETE', _id)
        if result.deleted_count == 1:
            return {'deleted': result.deleted_count}
        else:
            self.abort(404, 'Group {} not removed'.format(_id))
        return result

    def handle_projects(self, result):
        """
        If parameter join=projects, return project id, label, permissions, and description
        """
        result['projects'] = self.storage.get_children(result.get('_id'), projection={'permissions': 1, 'label': 1, 'description': 1, 'group': 1}, uid=self.uid)
        self._filter_permissions(result['projects'], self.uid)
        return result

    def get_all(self, uid=None):
        if uid:
            uid = bson.ObjectId(uid)
        projection = {'label': 1, 'created': 1, 'modified': 1, 'permissions': 1, 'tags': 1}
        permchecker = groupauth.list_permission_checker(self, uid)
        page = permchecker(self.storage.exec_op)('GET', projection=projection, pagination=self.pagination)
        results = page['results']
        if not self.superuser_request and not self.is_true('join_avatars') and not self.user_is_admin:
            self._filter_permissions(results, self.uid)
        if self.is_true('join_avatars'):
            self.storage.join_avatars(results)
        if 'projects' in self.request.params.getall('join'):
            for result in results:
                self.handle_projects(result)
        return self.format_page(page)

    @validators.verify_payload_exists
    def put(self, _id):
        group = self._get_group(_id)
        permchecker = groupauth.default(self, group)
        payload = self.request.json_body
        mongo_schema_uri = validators.schema_uri('mongo', 'group.json')
        mongo_validator = validators.decorator_from_schema_path(mongo_schema_uri)
        payload_schema_uri = validators.schema_uri('input', 'group-update.json')
        payload_validator = validators.from_schema_path(payload_schema_uri)
        payload_validator(payload, 'PUT')
        payload['modified'] = datetime.datetime.utcnow()
        result = mongo_validator(permchecker(self.storage.exec_op))('PUT', _id=_id, payload=payload)
        if result.modified_count == 1:
            return {'modified': result.modified_count}
        else:
            self.abort(404, 'Group {} not updated'.format(_id))

    def post(self):
        permchecker = groupauth.default(self, None)
        payload = self.request.json_body
        mongo_schema_uri = validators.schema_uri('mongo', 'group.json')
        mongo_validator = validators.decorator_from_schema_path(mongo_schema_uri)
        payload_schema_uri = validators.schema_uri('input', 'group-new.json')
        payload_validator = validators.from_schema_path(payload_schema_uri)
        payload_validator(payload, 'POST')
        if payload['_id'] in GROUP_ID_BLACKLIST:
            self.abort(400, 'The group "{}" can\'t be created as it is integral within the API'.format(payload['_id']))
        payload['created'] = payload['modified'] = datetime.datetime.utcnow()
        payload['permissions'] = [{'_id': self.uid, 'access': 'admin'}] if self.uid else []
        result = mongo_validator(permchecker(self.storage.exec_op))('POST', payload=payload)
        if result.acknowledged:
            if result.upserted_id:
                return {'_id': result.upserted_id}
            else:
                self.response.status_int = 201
                return {'_id': payload['_id']}
        else:
            self.abort(404, 'Group {} not updated'.format(payload['_id']))

    def _get_group(self, _id):
        group = self.storage.get_container(_id)
        if group is not None:
            return group
        else:
            self.abort(404, 'Group {} not found'.format(_id))

    def _filter_permissions(self, results, uid):
        """
        if the user is not admin only her permission is returned.
        """
        for result in results:
            user_perm = util.user_perm(result.get('permissions', []), uid)
            if user_perm.get('access') != 'admin':
                result['permissions'] = [user_perm] if user_perm else []
        return results
