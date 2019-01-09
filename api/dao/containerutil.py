import bson.objectid
import copy

from .. import config
from ..auth import has_access
from ..types import Origin

from ..web.errors import APINotFoundException, APIPermissionException


# Ordering optimized for global request frequency
CONT_TYPES = [
    'acquisition',
    'session',
    'subject',
    'project',
    'group',
    'analysis',
    'collection',
]
SINGULAR_TO_PLURAL = {
    'acquisition': 'acquisitions',
    'analysis':    'analyses',
    'collection':  'collections',
    'device':      'devices',
    'group':       'groups',
    'job':         'jobs',
    'project':     'projects',
    'session':     'sessions',
    'subject':     'subjects',
    'user':        'users',
    'query':       'queries',
}
PLURAL_TO_SINGULAR = {p: s for s, p in SINGULAR_TO_PLURAL.iteritems()}
PLURAL_CONT_TYPES = [ SINGULAR_TO_PLURAL[_type] for _type in CONT_TYPES ]

CONTAINER_HIERARCHY = [
    'groups',
    'projects',
    'subjects',
    'sessions',
    'acquisitions'
]

# Generate {child: parent} and {parent: child} maps from ordered hierarchy list
CHILD_FROM_PARENT = {p: CONTAINER_HIERARCHY[ind+1] for ind, p in enumerate(CONTAINER_HIERARCHY[:-1] )}
PARENT_FROM_CHILD = {c: CONTAINER_HIERARCHY[ind]   for ind, c in enumerate(CONTAINER_HIERARCHY[1:]  )}


def propagate_changes(cont_name, cont_ids, query, update, include_refs=False):
    """
    Propagates changes down the heirarchy tree recursively.

    cont_name and cont_ids refer to top level containers (which will not be modified here)
    """

    containers = ['groups', 'projects', 'subjects', 'sessions', 'acquisitions']
    if not isinstance(cont_ids, list):
        cont_ids = [cont_ids]
    if query is None:
        query = {}

    if include_refs:
        analysis_query = copy.deepcopy(query)
        analysis_query.update({'parent.type': singularize(cont_name), 'parent.id': {'$in': cont_ids}})
        analysis_update = copy.deepcopy(update)
        analysis_update.get('$set', {}).pop('permissions', None)
        config.db.analyses.update_many(analysis_query, analysis_update)

        # Update job parents by destination
        job_query = { 'parents.{}'.format(singularize(cont_name)) : {'$in': cont_ids} }
        config.db.jobs.update_many(job_query, analysis_update)

    if cont_name in containers[:-1]:
        child_cont = containers[containers.index(cont_name) + 1]
        child_ids = [c['_id'] for c in config.db[child_cont].find({singularize(cont_name): {'$in': cont_ids}}, [])]

        if child_ids:
            child_query = copy.deepcopy(query)
            child_query['_id'] = {'$in': child_ids}
            config.db[child_cont].update_many(child_query, update)
            # Recurse to the next hierarchy level
            propagate_changes(child_cont, child_ids, query, update, include_refs=include_refs)


def attach_raw_subject(session, subject, additional_fields=None):
    raw_subject_fields = ['firstname', 'lastname', 'sex', 'race', 'ethnicity']
    if additional_fields:
        raw_subject_fields += additional_fields
    subject_raw = {k: copy.deepcopy(v) for k, v in subject.iteritems() if v is not None and k in raw_subject_fields}
    if subject_raw:
        if session.get('info'):
            session['info']['subject_raw'] = subject_raw
        else:
            session['info'] = {'subject_raw': subject_raw}


def extract_subject(session, project):
    """
    Extract subject from session payload (dict), add _id if needed and leave reference on the session.
    Enables backwards-compatibilty for all endpoints receiving subject-related input embedded into sessions.
    Implements similar extraction as the separate-subjects-collection DB upgrade, with the difference being
     * subject _ids are matched (or generated) if not provided in the input
     * project and permissions on the subject are populated from the 2nd arg `project` as they might not
       be populated on the session at the time of the call

    Example:
        extract_subject(session={'subject': {'_id': SUBJ, code': CODE}},
                        project={'_id': PROJ, 'permissions': PERM})
        --> session['subject'] = SUBJ
        --> return {'_id': SUBJ, 'code': CODE, 'project': PROJ, 'permissions': PERM}

    Subject _id selection:
     * use original session['subject']['_id'] if provided (cast ObjectId)
     * assign existing subject's _id with the same code in the same project if any
     * generate new ObjectId otherwise (ie. treat as new subject)
    """
    subject = session.pop('subject', {})
    subject.update({'project': bson.ObjectId(str(project['_id'])), 'permissions': project['permissions']})
    if subject.get('_id'):
        subject['_id'] = bson.ObjectId(str(subject['_id']))
        query = {'_id': subject['_id'], 'project': project['_id'], 'deleted': {'$exists': True}}
        result = config.db.subjects.find_one(query)
        # If a subject with that id exists and is deleted, create a new one
        if result:
            subject['_id'] = bson.ObjectId()
    elif subject.get('master_code'):
        query = {'master_code': subject['master_code'], 'project': project['_id'], 'deleted': {'$exists': False}}
        result = config.db.subjects.find_one(query)
        if result:
            subject['_id'] = result['_id']
    elif subject.get('code'):
        # If a non-deleted subject with that code doesn't exist in the project, create a new id
        query = {'code': subject['code'], 'project': project['_id'], 'deleted': {'$exists': False}}
        result = config.db.subjects.find_one(query)
        if result:
            subject['_id'] = result['_id']
    if not subject.get('_id'):
        subject['_id'] = bson.ObjectId()
    session['subject'] = subject['_id']
    if subject.get('age'):
        session['age'] = subject.pop('age')
    attach_raw_subject(session, subject)
    return subject


def get_stats(cont, cont_type):
    """
    Add a session, subject, non-compliant session and attachment count to a project or collection
    """

    if cont_type not in ['projects', 'collections']:
        return cont

    # Get attachment count from file array length
    cont['attachment_count'] = len(cont.get('files', []))

    # Get session and non-compliant session count
    match_q = {}
    if cont_type == 'projects':
        match_q = {'project': cont['_id'], 'deleted': {'$exists': False}}
    elif cont_type == 'collections':
        result = config.db.acquisitions.find({'collections': cont['_id'], 'deleted': {'$exists': False}}, {'session': 1})
        session_ids = list(set([s['session'] for s in result]))
        match_q = {'_id': {'$in': session_ids}}

    pipeline = [
        {'$match': match_q},
        {'$project': {'_id': 1, 'non_compliant':  {'$cond': [{'$eq': ['$satisfies_template', False]}, 1, 0]}}},
        {'$group': {'_id': 1, 'noncompliant_count': {'$sum': '$non_compliant'}, 'total': {'$sum': 1}}}
    ]

    result = list(config.db.sessions.aggregate(pipeline))

    if len(result) > 0:
        cont['session_count'] = result[0].get('total', 0)
        cont['noncompliant_session_count'] = result[0].get('noncompliant_count', 0)
    else:
        # If there are no sessions, return zero'd out stats
        cont['session_count'] = 0
        cont['noncompliant_session_count'] = 0
        cont['subject_count'] = 0
        return cont

    # Get subject count
    match_q['subject'] = {'$ne': None}
    pipeline = [
        {'$match': match_q},
        {'$group': {'_id': '$subject'}},
        {'$group': {'_id': 1, 'count': { '$sum': 1 }}}
    ]

    result = list(config.db.sessions.aggregate(pipeline))

    if len(result) > 0:
        cont['subject_count'] = result[0].get('count', 0)
    else:
        cont['subject_count'] = 0

    return cont

def sanitize_info(info):
    """
    Modifies an info key to only include known top-level keys
    """
    formalized_keys = ['BIDS']
    sanitized_info = {}
    for k in formalized_keys:
        if k in info:
            sanitized_info[k] = info[k]
    return sanitized_info


def get_referring_analyses(cont_name, cont_id, filename=None):
    """
    Get all (non-deleted) analyses that reference any file from the container as their input.
    If filename is given, only return analyses that have that specific file as their input.
    """
    query = {
        'destination.type': 'analysis',
        'inputs.type': singularize(cont_name),
        'inputs.id': str(cont_id),
    }
    if filename:
        query['inputs.name'] = filename
    jobs = config.db.jobs.find(query, {'destination.id': True})
    analysis_ids = [bson.ObjectId(job['destination']['id']) for job in jobs]
    analyses = config.db.analyses.find({'_id': {'$in': analysis_ids}, 'deleted': {'$exists': False}})
    return list(analyses)


def container_has_original_data(container, child_cont_name=None):
    """
    Given a container, creates a list of all origin types
    for all files in the container and it's children, if provided.
    If the set only includes user and job uploaded files, the container
    is not considered to have "original data".
    """

    for f in container.get('files', []):
        if f['origin']['type'] not in [str(Origin.user), str(Origin.job)]:
            return True
    if child_cont_name:
        for c in container.get(child_cont_name, []):
            for f in c.get('files', []):
                if f['origin']['type'] not in [str(Origin.user), str(Origin.job)]:
                    return True
    return False


class ContainerReference(object):
    # pylint: disable=redefined-builtin
    # TODO: refactor to resolve pylint warning

    def __init__(self, type, id):
        type = singularize(type)
        id = str(id)

        if type not in CONT_TYPES:
            raise Exception('Container type must be one of {}'.format(CONT_TYPES))

        self.type = type
        self.id = id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__dict__ == other.__dict__

    @classmethod
    def from_dictionary(cls, d):
        return cls(
            type = d['type'],
            id = d['id']
        )

    @classmethod
    def from_filereference(cls, fr):
        return cls(
            type = fr.type,
            id = fr.id
        )

    def get(self):
        collection = pluralize(self.type)
        result = config.db[collection].find_one({'_id': bson.ObjectId(self.id), 'deleted': {'$exists': False}})
        if result is None:
            raise APINotFoundException('No such {} {} in database'.format(self.type, self.id))
        if 'parent' in result:
            parent_collection = pluralize(result['parent']['type'])
            parent = config.db[parent_collection].find_one({'_id': bson.ObjectId(result['parent']['id'])})
            if parent is None:
                raise APINotFoundException('Cannot find parent {} {} of {} {}'.format(
                    result['parent']['type'], result['parent']['id'], self.type, self.id))
            result['permissions'] = parent['permissions']
        return result

    def find_file(self, filename):
        cont = self.get()
        for f in cont.get('files', []):
            if f['name'] == filename:
                return f
        return None

    def file_uri(self, filename):
        collection = pluralize(self.type)
        cont = self.get()
        if 'parent' in cont:
            par_coll, par_id = pluralize(cont['parent']['type']), cont['parent']['id']
            return '/{}/{}/{}/{}/files/{}'.format(par_coll, par_id, collection, self.id, filename)
        return '/{}/{}/files/{}'.format(collection, self.id, filename)

    def check_access(self, uid, perm_name, cont=None):
        if cont is None:
            cont = self.get()
        if has_access(uid, cont, perm_name):
            return
        else:
            raise APIPermissionException('User {} does not have {} access to {} {}'.format(uid, perm_name, self.type, self.id))


class FileReference(ContainerReference):
    # pylint: disable=redefined-builtin
    # TODO: refactor to resolve pylint warning

    def __init__(self, type, id, name):
        super(FileReference, self).__init__(type, id)
        self.name = name

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__dict__ == other.__dict__

    @classmethod
    def from_dictionary(cls, d):
        return cls(
            type = d['type'],
            id = d['id'],
            name = d['name']
        )

    def get_file(self, container=None):
        if not container:
            container = super(FileReference, self).get()

        for file in container.get('files', []):
            if file['name'] == self.name and not file.get('deleted'):
                return file

        raise APINotFoundException('No such file {} on {} {} in database'.format(self.name, self.type, self.id))


def create_filereference_from_dictionary(d):
    return FileReference.from_dictionary(d)

def create_containerreference_from_dictionary(d):
    return ContainerReference.from_dictionary(d)

def create_containerreference_from_filereference(fr):
    return ContainerReference.from_filereference(fr)

def container_search(query, projection=None, collections=PLURAL_CONT_TYPES, early_return=True, **kwargs):
    """ Perform search across multiple collections.

    Args:
        query (dict): The filter specifying elements which must be present for a document to be included in the result set.
        projection (dict, optional): A list of field names that should be returned in the result set, or a dict specifying fields to include or exclude.
        collections (list, optional): The list of collections to search across, by default all of the containers specified in CONT_TYPES, in no particular order.
        early_return (bool, optional): Whether to return after the first match is found or keep searching. Default is true (return immediately)
        **kwargs: Additional arguments to pass to the underlying `find` calls

    Returns:
        list: A list of tuples of (collection_name, results)
    """
    results = []

    for coll_name in collections:
        coll = config.db.get_collection(coll_name)
        coll_results = list(coll.find(query, projection, **kwargs))

        if coll_results:
            results.append( (coll_name, coll_results) )
            if early_return:
                break

    return results


def pluralize(cont_name):
    if cont_name in SINGULAR_TO_PLURAL:
        return SINGULAR_TO_PLURAL[cont_name]
    elif cont_name in PLURAL_TO_SINGULAR:
        return cont_name
    raise ValueError('Could not pluralize unknown container name {}'.format(cont_name))

def singularize(cont_name):
    if cont_name in PLURAL_TO_SINGULAR:
        return PLURAL_TO_SINGULAR[cont_name]
    elif cont_name in SINGULAR_TO_PLURAL:
        return cont_name
    raise ValueError('Could not singularize unknown container name {}'.format(cont_name))
