import bson
import datetime
import dateutil

from .. import config
from .. import util
from .. import validators
from ..auth import containerauth, always_ok
from ..dao import containerstorage, containerutil, noop
from ..dao.containerstorage import AnalysisStorage
from ..jobs.jobs import Job
from ..jobs.queue import Queue
from ..web import base
from ..web.errors import APIPermissionException
from ..web.request import log_access, AccessType


class ContainerHandler(base.RequestHandler):
    """
    This class handle operations on a generic container

    The pattern used is:
    1) load the storage class used to interact with mongo
    2) configure the permissions checker and the json payload validators
    3) validate the input payload
    4) augment the payload when appropriate
    5) exec the request (using the mongo validator and the permissions checker)
    6) check the result
    7) augment the result when needed
    8) return the result

    Specific behaviors (permissions checking logic for authenticated and not superuser users, storage interaction)
    are specified in the container_handler_configurations
    """
    use_object_id = {
        'groups': False,
        'projects': True,
        'sessions': True,
        'acquisitions': True
    }

    # This configurations are used by the ContainerHandler class to load the storage,
    # the permissions checker and the json schema validators used to handle a request.
    #
    # "children_cont" represents the children container.
    # "list projection" is used to filter data in mongo.
    # "use_object_id" implies that the container ids are converted to ObjectId
    container_handler_configurations = {
        'projects': {
            'storage': containerstorage.ProjectStorage(),
            'permchecker': containerauth.default_container,
            'parent_storage': containerstorage.GroupStorage(),
            'storage_schema_file': 'project.json',
            'payload_schema_file': 'project.json',
            'propagated_properties': ['public'],
            'children_cont': 'sessions'
        },
        'sessions': {
            'storage': containerstorage.SessionStorage(),
            'permchecker': containerauth.default_container,
            'parent_storage': containerstorage.ProjectStorage(),
            'storage_schema_file': 'session.json',
            'payload_schema_file': 'session.json',
            'children_cont': 'acquisitions'
        },
        'acquisitions': {
            'storage': containerstorage.AcquisitionStorage(),
            'permchecker': containerauth.default_container,
            'parent_storage': containerstorage.SessionStorage(),
            'storage_schema_file': 'acquisition.json',
            'payload_schema_file': 'acquisition.json'
        }
    }

    def __init__(self, request=None, response=None):
        super(ContainerHandler, self).__init__(request, response)
        self.storage = None
        self.config = None

    @log_access(AccessType.view_container)
    def get(self, cont_name, **kwargs):
        _id = kwargs.get('cid')
        self.config = self.container_handler_configurations[cont_name]
        self.storage = self.config['storage']
        container = self._get_container(_id)

        permchecker = self._get_permchecker(container)
        # This line exec the actual get checking permissions using the decorator permchecker
        result = permchecker(self.storage.exec_op)('GET', _id)
        if result is None:
            self.abort(404, 'Element not found in container {} {}'.format(self.storage.cont_name, _id))
        if not self.superuser_request and not self.is_true('join_avatars'):
            self._filter_permissions(result, self.uid)
        if self.is_true('join_avatars'):
            self.storage.join_avatars([result])

        inflate_job_info = cont_name == 'sessions'
        if not self.is_enabled('Slim-Containers'):
            result['analyses'] = AnalysisStorage().get_analyses(None, cont_name, _id, inflate_job_info)
        self.handle_origin(result)
        util.add_container_type(self.request, result)
        return result

    def _filter_permissions(self, result, uid):
        """
        if the user is not admin only her permissions are returned.
        """
        user_perm = util.user_perm(result.get('permissions', []), uid)
        if user_perm.get('access') != 'admin':
            result['permissions'] = [user_perm] if user_perm else []

    def get_subject(self, cid):
        self.config = self.container_handler_configurations['sessions']
        self.storage = self.config['storage']
        container= self._get_container(cid)

        permchecker = self._get_permchecker(container)
        result = permchecker(self.storage.exec_op)('GET', cid)
        self.log_user_access(AccessType.view_subject, cont_name='sessions', cont_id=cid)
        return result.get('subject', {})


    def get_jobs(self, cid):
        # Only enabled for sessions container type per url rule in api.py
        self.config = self.container_handler_configurations["sessions"]
        self.storage = self.config['storage']
        cont = self._get_container(cid, projection={'files': 0, 'metadata': 0}, get_children=True)

        permchecker = self._get_permchecker(cont)

        permchecker(noop)('GET', cid)

        analyses = AnalysisStorage().get_analyses(None, 'session', cont['_id'])
        acquisitions = cont.get('acquisitions', [])

        # Get query params
        states = self.request.GET.getall('states')
        tags = self.request.GET.getall('tags')
        join_cont = 'containers' in self.request.params.getall('join')
        join_gears = 'gears' in self.request.params.getall('join')

        cont_refs = [containerutil.ContainerReference(cont_type, str(cont_id)) for cont_type, cont_id in
                        [('session', cont['_id'])] +
                        [('analysis', an['_id']) for an in analyses] +
                        [('acquisition', aq['_id']) for aq in acquisitions]
                    ]
        jobs = Queue.search(cont_refs, states=states, tags=tags)

        unique_jobs = {}
        gear_ids = set()
        for job in jobs:
            if job['_id'] not in unique_jobs:
                unique_jobs[job['_id']] = Job.load(job)
                if job.get('gear_id') and job['gear_id'] not in gear_ids:
                    gear_ids.add(job['gear_id'])

        response = {'jobs': sorted(unique_jobs.values(), key=lambda job: job.created)}
        if join_gears:
            gears = config.db.gears.find({'_id': {'$in': [bson.ObjectId(gear_id) for gear_id in gear_ids]}})
            response['gears'] = {str(gear['_id']): gear for gear in gears}
        if join_cont:
            # create a map of analyses and acquisitions by _id
            containers = {str(cont['_id']): cont for cont in analyses + acquisitions}
            for container in containers.itervalues():
                # No need to return perm arrays
                container.pop('permissions', None)
            response['containers'] = containers
        return response

    def get_all(self, cont_name, par_cont_name=None, par_id=None):
        self.config = self.container_handler_configurations[cont_name]
        self.storage = self.config['storage']

        projection = self.storage.get_list_projection()

        if self.is_true('permissions'):
            if not projection:
                projection = None

        # select which permission filter will be applied to the list of results.
        if self.superuser_request:
            permchecker = always_ok
        elif self.public_request:
            permchecker = containerauth.list_public_request
        else:
            permchecker = containerauth.list_permission_checker(self)
        # if par_cont_name (parent container name) and par_id are not null we return only results
        # within that container
        if par_cont_name:
            if not par_id:
                self.abort(500, 'par_id is required when par_cont_name is provided')
            if self.use_object_id.get(par_cont_name):
                if not bson.ObjectId.is_valid(par_id):
                    self.abort(400, 'not a valid object id')
                par_id = bson.ObjectId(par_id)
            query = {par_cont_name[:-1]: par_id}
        else:
            query = {}
        # this request executes the actual reqeust filtering containers based on the user permissions
        page = permchecker(self.storage.exec_op)('GET', query=query, public=self.public_request, projection=projection, pagination=self.pagination)
        results = page['results']
        # return only permissions of the current user unless superuser or getting avatars
        if not self.superuser_request and not self.is_true('join_avatars'):
            self._filter_all_permissions(results, self.uid)
        # the "count" flag add a count for each container returned
        if self.is_true('counts'):
            self._add_results_counts(results, cont_name)

        for result in results:
            self.handle_origin(result)
            if self.is_true('stats'):
                containerutil.get_stats(result, cont_name)

        if self.is_true('join_avatars'):
            self.storage.join_avatars(results)

        return self.format_page(page)

    def _filter_all_permissions(self, results, uid):
        for result in results:
            user_perm = util.user_perm(result.get('permissions', []), uid)
            result['permissions'] = [user_perm] if user_perm else []
        return results

    def _add_results_counts(self, results, cont_name):
        dbc_name = self.config.get('children_cont')
        el_cont_name = cont_name[:-1]
        dbc = config.db[dbc_name]
        counts =  dbc.aggregate([
            {'$match': {el_cont_name: {'$in': [res['_id'] for res in results]}}},
            {'$group': {'_id': '$' + el_cont_name, 'count': {"$sum": 1}}}
            ])
        counts = {elem['_id']: elem['count'] for elem in counts}
        for elem in results:
            elem[dbc_name[:-1] + '_count'] = counts.get(elem['_id'], 0)

    def get_all_for_user(self, cont_name, uid):
        self.config = self.container_handler_configurations[cont_name]
        self.storage = self.config['storage']
        projection = self.storage.get_list_projection()
        # select which permission filter will be applied to the list of results.
        if self.superuser_request or self.user_is_admin:
            permchecker = always_ok
        elif self.public_request:
            self.abort(403, 'this request is not allowed')
        else:
            permchecker = containerauth.list_permission_checker(self)
        query = {}
        user = {
            '_id': uid
        }
        results = permchecker(self.storage.exec_op)('GET', query=query, user=user, projection=projection)
        if results is None:
            self.abort(404, 'Element not found in container {} {}'.format(self.storage.cont_name, uid))
        self._filter_all_permissions(results, uid)
        return results

    def post(self, cont_name):
        self.config = self.container_handler_configurations[cont_name]
        self.storage = self.config['storage']
        mongo_validator, payload_validator = self._get_validators()

        payload = self.request.json_body
        #validate the input payload
        payload_validator(payload, 'POST')
        # Load the parent container in which the new container will be created
        # to check permissions.
        parent_container, parent_id_property = self._get_parent_container(payload)
        # Always add the id of the parent to the container
        payload[parent_id_property] = parent_container['_id']
        # If the new container is a session add the group of the parent project in the payload
        if cont_name == 'sessions':
            payload['group'] = parent_container['group']
            payload['subject'] = containerutil.add_id_to_subject(payload.get('subject'), payload.get('project'))
        # Optionally inherit permissions of a project from the parent group. The default behaviour
        # for projects is to give admin permissions to the requestor.
        # The default for other containers is to inherit.
        if self.is_true('inherit') and cont_name == 'projects':
            payload['permissions'] = parent_container.get('permissions')
        elif cont_name =='projects':
            payload['permissions'] = [{'_id': self.uid, 'access': 'admin'}] if self.uid else []
        else:
            payload['permissions'] = parent_container.get('permissions', [])
        # Created and modified timestamps are added here to the payload
        payload['created'] = payload['modified'] = datetime.datetime.utcnow()
        if payload.get('timestamp'):
            payload['timestamp'] = dateutil.parser.parse(payload['timestamp'])
        permchecker = self._get_permchecker(parent_container=parent_container)
        # This line exec the actual request validating the payload that will create the new container
        # and checking permissions using respectively the two decorators, mongo_validator and permchecker
        result = mongo_validator(permchecker(self.storage.exec_op))('POST', payload=payload)
        if result.acknowledged:
            return {'_id': result.inserted_id}
        else:
            self.abort(404, 'Element not added in container {}'.format(self.storage.cont_name))

    @validators.verify_payload_exists
    def put(self, cont_name, **kwargs):
        _id = kwargs.pop('cid')
        self.config = self.container_handler_configurations[cont_name]
        self.storage = self.config['storage']
        container = self._get_container(_id)
        mongo_validator, payload_validator = self._get_validators()

        payload = self.request.json_body
        payload_validator(payload, 'PUT')

        # Check if any payload keys are any propogated property, add to r_payload
        rec = False
        r_payload = {}
        prop_keys = set(payload.keys()).intersection(set(self.config.get('propagated_properties', [])))
        if prop_keys:
            rec = True
            for key in prop_keys:
                r_payload[key] = payload[key]

        # Check if we are updating the parent container of the element (ie we are moving the container)
        # In this case, we will check permissions on it.
        target_parent_container, parent_id_property = self._get_parent_container(payload)
        if target_parent_container:
            if cont_name in ['sessions', 'acquisitions']:
                payload[parent_id_property] = bson.ObjectId(payload[parent_id_property])
                parent_perms = target_parent_container.get('permissions', [])
                payload['permissions'] = parent_perms

            if cont_name == 'sessions':
                payload['group'] = target_parent_container['group']
                # Propagate permissions down to acquisitions
                rec = True
                r_payload['permissions'] = parent_perms


        payload['modified'] = datetime.datetime.utcnow()
        if payload.get('timestamp'):
            payload['timestamp'] = dateutil.parser.parse(payload['timestamp'])
        if cont_name == 'sessions':
            if payload.get('subject') is not None and payload['subject'].get('_id') is not None:
                # Ensure subject id is a bson object
                payload['subject']['_id'] = bson.ObjectId(str(payload['subject']['_id']))
        permchecker = self._get_permchecker(container, target_parent_container)

        # Specifies wether the metadata fields should be replaced or patched with payload value
        replace_metadata = self.get_param('replace_metadata', default=False)
        # This line exec the actual request validating the payload that will update the container
        # and checking permissions using respectively the two decorators, mongo_validator and permchecker
        result = mongo_validator(permchecker(self.storage.exec_op))('PUT',
                    _id=_id, payload=payload, recursive=rec, r_payload=r_payload, replace_metadata=replace_metadata)

        if result.modified_count == 1:
            return {'modified': result.modified_count}
        else:
            self.abort(404, 'Element not updated in container {} {}'.format(self.storage.cont_name, _id))

    def modify_info(self, cont_name, **kwargs):
        _id = kwargs.pop('cid')

        # Support subject info modification in new style
        # Will be removed when subject becomes stand-alone container
        modify_subject = True if 'subject' in kwargs else False
        if modify_subject and cont_name != 'sessions':
            self.abort(400, 'Subject info modification only allowed via session.')

        self.config = self.container_handler_configurations[cont_name]
        self.storage = self.config['storage']
        container = self._get_container(_id)
        permchecker = self._get_permchecker(container)
        payload = self.request.json_body

        validators.validate_data(payload, 'info_update.json', 'input', 'POST')

        permchecker(noop)('PUT', _id=_id)
        self.storage.modify_info(_id, payload, modify_subject=modify_subject)

        return

    @log_access(AccessType.delete_container)
    def delete(self, cont_name, **kwargs):
        _id = kwargs.pop('cid')
        self.config = self.container_handler_configurations[cont_name]
        self.storage = self.config['storage']

        if cont_name == 'sessions':
            get_children = True
        else:
            get_children = False
        container = self._get_container(_id, get_children=get_children)
        container['cont_name'] = containerutil.singularize(cont_name)

        if cont_name in ['sessions', 'acquisitions']:
            container['has_original_data'] = containerutil.container_has_original_data(container, child_cont_name=self.config.get('children_cont'))
        if cont_name == 'acquisitions':
            analyses = containerutil.get_referring_analyses(cont_name, _id)
            if analyses:
                analysis_ids = [str(a['_id']) for a in analyses]
                errors = {'reason': 'analysis_conflict'}
                raise APIPermissionException('Cannot delete acquisition {} referenced by analyses {}'.format(_id, analysis_ids), errors=errors)

        target_parent_container, _ = self._get_parent_container(container)
        permchecker = self._get_permchecker(container, target_parent_container)
        permchecker(noop)('DELETE', _id)
        if self.is_true('check'):
            # User only wanted to check permissions, respond with 200
            return

        # This line exec the actual delete checking permissions using the decorator permchecker
        result = self.storage.exec_op('DELETE', _id)
        if result.modified_count == 1:
            deleted_at = config.db[cont_name].find_one({'_id': bson.ObjectId(_id)})['deleted']
            # Don't overwrite deleted timestamp for already deleted children
            query = {'deleted': {'$exists': False}}
            update = {'$set': {'deleted': deleted_at}}
            containerutil.propagate_changes(cont_name, bson.ObjectId(_id), query, update, include_refs=True)
            return {'deleted': 1}
        else:
            self.abort(404, 'Element not removed from container {} {}'.format(self.storage.cont_name, _id))


    def get_groups_with_project(self):
        """
        method to return the list of groups for which there are projects accessible to the user
        """
        group_ids = list(set((p['group'] for p in self.get_all('projects'))))
        return list(config.db.groups.find({'_id': {'$in': group_ids}}, ['label']))

    def set_project_template(self, **kwargs):
        project_id = kwargs.pop('cid')
        self.config = self.container_handler_configurations['projects']
        self.storage = self.config['storage']
        container = self._get_container(project_id)

        template = self.request.json_body
        validators.validate_data(template, 'project-template.json', 'input', 'POST')
        payload = {'template': template}
        payload['modified'] = datetime.datetime.utcnow()

        permchecker = self._get_permchecker(container)
        result = permchecker(self.storage.exec_op)('PUT', _id=project_id, payload=payload)
        return {'modified': result.modified_count}

    def delete_project_template(self, **kwargs):
        project_id = kwargs.pop('cid')
        self.config = self.container_handler_configurations['projects']
        self.storage = self.config['storage']
        container = self._get_container(project_id)

        payload = {'modified': datetime.datetime.utcnow()}
        unset_payload = {'template': ''}

        permchecker = self._get_permchecker(container)
        result = permchecker(self.storage.exec_op)('PUT', _id=project_id, payload=payload, unset_payload=unset_payload)
        return {'modified': result.modified_count}


    def calculate_project_compliance(self, **kwargs):
        project_id = kwargs.pop('cid', None)
        self.log.debug("project_id is {}".format(project_id))
        self.config = self.container_handler_configurations['projects']
        self.storage = self.config['storage']
        return {'sessions_changed': self.storage.recalc_sessions_compliance(project_id=project_id)}

    def _get_validators(self):
        mongo_schema_uri = validators.schema_uri('mongo', self.config.get('storage_schema_file'))
        mongo_validator = validators.decorator_from_schema_path(mongo_schema_uri)
        payload_schema_uri = validators.schema_uri('input', self.config.get('payload_schema_file'))
        payload_validator = validators.from_schema_path(payload_schema_uri)
        return mongo_validator, payload_validator

    def _get_parent_container(self, payload):
        if not self.config.get('parent_storage'):
            return None, None
        parent_storage = self.config['parent_storage']
        parent_id_property = parent_storage.cont_name[:-1]
        parent_id = payload.get(parent_id_property)
        if parent_id:
            parent_storage.dbc = config.db[parent_storage.cont_name]
            parent_container = parent_storage.get_container(parent_id)
            if parent_container is None:
                self.abort(404, 'Element {} not found in container {}'.format(parent_id, parent_storage.cont_name))
            parent_container['cont_name'] = parent_storage.cont_name[:-1]
        else:
            parent_container = None
        return parent_container, parent_id_property

    def _get_container(self, _id, projection=None, get_children=False):
        container = self.storage.get_container(_id, projection=projection, get_children=get_children)
        if container is not None:
            files = container.get('files', [])
            if files:
                container['files'] = [f for f in files if 'deleted' not in f]
            return container
        else:
            self.abort(404, 'Element {} not found in container {}'.format(_id, self.storage.cont_name))

    def _get_permchecker(self, container=None, parent_container=None):
        if self.superuser_request:
            return always_ok
        elif self.public_request:
            return containerauth.public_request(self, container)
        else:
            permchecker = self.config['permchecker']
            return permchecker(self, container, parent_container)
