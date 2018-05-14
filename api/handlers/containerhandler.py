import bson
import copy
import datetime
import dateutil

from .. import config
from .. import util
from .. import validators
from ..auth import containerauth, always_ok
from ..dao import containerstorage, containerutil, noop
from ..dao.containerstorage import AnalysisStorage
from ..dao.hierarchy import confirm_edition
from ..jobs.jobs import Job
from ..jobs.queue import Queue
from ..web import base
from ..web.errors import APIPermissionException, APIValidationException, InputValidationException
from ..web.request import log_access, AccessType

PROJECT_BLACKLIST = ['Unknown', 'Unsorted']

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
        'subjects': True,
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
        'subjects': {
            'storage': containerstorage.SubjectStorage(),
            'permchecker': containerauth.default_container,
            'parent_storage': containerstorage.ProjectStorage(),
            'storage_schema_file': 'subject.json',
            'payload_schema_file': 'subject.json',
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

        inflate_job_info = cont_name in ['projects', 'sessions', 'subjects', 'acquisitions']
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
        container = self._get_container(cid)

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
            query = {containerutil.singularize(par_cont_name): par_id}
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
        if cont_name == 'subjects':
            if 'project' not in payload:
                # The new POST /subjects reuses json schema used for "embedded" subject creation,
                # but requires project in the payload, too
                raise APIValidationException('project required')
            subject_code = payload.get('code') or payload.get('label')
            if not subject_code:
                raise APIValidationException('label or code required')

            if self.storage.get_all_el({
                'project': bson.ObjectId(payload['project']),
                'code': subject_code,
                }, None, {'_id': 1}):
                raise APIValidationException('subject code "{}" already exists in project {}'.format(subject_code, payload['project']))


        # Load the parent container in which the new container will be created
        # to check permissions.
        parent_container, parent_id_property = self._get_parent_container(payload)
        # Always add the id of the parent to the container
        payload[parent_id_property] = parent_container['_id']
        # Confirm that ad hoc container creation is happening in lab groups
        if cont_name not in ['acquisitions', 'projects']:
            config.log.debug('Confirming group edition')
            confirm_edition('lab', containerutil.pluralize(parent_id_property), parent_container['_id'], parent_container)
        # If the new container is a session add the group of the parent project in the payload
        if cont_name == 'sessions':
            payload['group'] = parent_container['group']
        # Optionally inherit permissions of a project from the parent group. The default behaviour
        # for projects is to give admin permissions to the requestor.
        # The default for other containers is to inherit.
        if self.is_true('inherit') and cont_name == 'projects':
            payload['permissions'] = parent_container.get('permissions')
        elif cont_name =='projects':
            payload['permissions'] = [{'_id': self.uid, 'access': 'admin'}] if self.uid else []

            # Unsorted projects are reserved for reaper uploads
            if payload['label'] in PROJECT_BLACKLIST:
                self.abort(400, 'The project "{}" can\'t be created as it is integral within the API'.format(payload['label']))
        else:
            payload['permissions'] = parent_container.get('permissions', [])
        # Created and modified timestamps are added here to the payload
        payload['created'] = payload['modified'] = datetime.datetime.utcnow()
        if payload.get('timestamp'):
            payload['timestamp'] = dateutil.parser.parse(payload['timestamp'])
        permchecker = self._get_permchecker(parent_container=parent_container)

        # Handle embedded subjects for backwards-compatibility
        if cont_name == 'sessions':
            self._handle_embedded_subject(payload, parent_container)

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

        if cont_name == 'subjects':
            # Check for code collision if changing code/label or moving to a new project
            # TODO: Minor duplication of code below, resolve when ability to edit subject
            # via session is resolved
            current_project, _ = self._get_parent_container(container)
            target_project, _ = self._get_parent_container(payload)
            project_id = (target_project or current_project)['_id'] # It's current project or the new project it is moving to
            subject_code = payload.get('code') or payload.get('label') or container.get('code') or container.get('label') # It's current label or the new label it is moving to

            # Check for subject code collision 1st when changing project and/or subject code
            if subject_code and self.storage.get_all_el({
                'project': project_id,
                'code': subject_code,
                '_id': {'$ne': container['_id']} # Make sure that if neither code nor project changed, we allow it
                }, None, {'_id': 1}):
                raise APIValidationException('subject code "{}" already exists in project {}'.format(subject_code, project_id))



        # Handle embedded subjects for backwards-compatibility
        if cont_name == 'sessions':
            current_project, _ = self._get_parent_container(container)
            target_project, _ = self._get_parent_container(payload)
            project_id = (target_project or current_project)['_id']

            current_subject = container['subject']
            payload_subject = payload.get('subject', {})
            target_subject_id = payload_subject.get('_id')
            target_subject_code = payload_subject.get('code') or payload_subject.get('label')
            subject_code = target_subject_code or container['subject'].get('code')
            subject_storage = containerstorage.SubjectStorage()

            # Check for subject code collision 1st when changing project and/or subject code
            if ((target_project and project_id != current_project['_id']) or
                (target_subject_code and subject_code != current_subject.get('code'))):

                if subject_storage.get_all_el({'project': project_id, 'code': subject_code}, None, {'_id': 1}):
                    raise APIValidationException('subject code "{}" already exists in project {}'.format(subject_code, project_id))

            # Handle changing subject id (moving session to another subject)
            if target_subject_id:
                target_subject = subject_storage.get_container(target_subject_id)

                # If payload also contains project, verify that the target_subject is in it
                if target_project and project_id != target_subject['project']:
                    raise APIValidationException('subject {} is not in project {}'.format(target_subject_id, project_id))

                # Make sure session.project is also updated
                if not target_project:
                    payload['project'] = target_subject['project']
                    target_project, _ = self._get_parent_container(payload)

            # Handle changing project (moving session and subject to another project)
            # * Copy subject into target project if there are other sessions on it
            # * Move if this is the only session on it (else branch)
            elif (target_project and project_id != current_project['_id']) and config.db.sessions.count({'subject': container['subject']['_id']}) > 1:
                subject = copy.deepcopy(container['subject'])
                subject.pop('parents')
                subject.update(payload_subject)   # Still apply any embedded subject changes
                subject['_id'] = bson.ObjectId()  # Causes new subject creation via extract_subject
                payload['subject'] = subject

            # Enable embedded subject updates via session updates: match on subject._id
            else:
                payload.setdefault('subject', {})['_id'] = container['subject']['_id']

            self._handle_embedded_subject(payload, target_project or current_project)

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
        self.config = self.container_handler_configurations[cont_name]
        self.storage = self.config['storage']
        container = self._get_container(_id)

        # Support subject info modification via PUT /sessions/<sess>/subject/info
        # Can be removed after all clients use PUT /subjects/<subj>/info instead
        if 'subject' in kwargs:
            if cont_name != 'sessions':
                raise InputValidationException('Indirect subject info modification only allowed via sessions.')
            _id = container['subject']['_id']
            self.config = self.container_handler_configurations['subjects']
            self.storage = self.config['storage']
            container = self._get_container(_id)

        permchecker = self._get_permchecker(container)
        payload = self.request.json_body
        validators.validate_data(payload, 'info_update.json', 'input', 'POST')
        permchecker(noop)('PUT', _id=_id)
        self.storage.modify_info(_id, payload)
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

        payload = self.request.json_body
        validators.validate_data(payload.get('templates', []), 'project-template.json', 'input', 'POST')
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
        unset_payload = {'templates': ''}

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
        # NOTE not using storage.parent_id_property (keep using project as session's parent for compatibility)
        parent_id_property = containerutil.singularize(parent_storage.cont_name)
        parent_id = payload.get(parent_id_property)
        if parent_id:
            parent_storage.dbc = config.db[parent_storage.cont_name]
            parent_container = parent_storage.get_container(parent_id)
            if parent_container is None:
                self.abort(404, 'Element {} not found in container {}'.format(parent_id, parent_storage.cont_name))
            parent_container['cont_name'] = containerutil.singularize(parent_storage.cont_name)
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

    def _handle_embedded_subject(self, session, project):
        """Extract, validate, perm-check and exec subject creation/updates embedded in session payloads."""
        subject = containerutil.extract_subject(session, project)
        subject_schema = validators.schema_uri('mongo', 'subject.json')
        subject_validator = validators.decorator_from_schema_path(subject_schema)
        # NOTE using the session's permchecker which should be ultimately identical to the subject's
        permchecker = self._get_permchecker(session, project)
        # method = 'PUT' if config.db.subjects.find_one({'_id': subject['_id']}) else 'POST'
        # NOTE checking perms for method 'POST' for backwards-compatibility
        #  * allows "PUT subject" via "POST session"
        #  * otherwise PUT would require admin
        method = 'POST'
        subject_validator(permchecker(noop))(method, payload=subject)
        containerstorage.SubjectStorage().create_or_update_el(subject)
