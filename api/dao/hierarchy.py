import bson
import copy
import datetime
import dateutil.parser
import difflib
import pymongo
import re

from .. import util
from .. import config
from .basecontainerstorage import ContainerStorage
from ..auth import has_access
from ..web.errors import APIStorageException, APINotFoundException, APIPermissionException, APIEditionException
from ..web.request import AccessType
from . import containerutil


log = config.log

PROJECTION_FIELDS = ['group', 'name', 'label', 'timestamp', 'permissions', 'public']

class TargetContainer(object):

    def __init__(self, container, level):
        self.container = container
        self.level = level
        self.dbc = config.db[level]
        self.id_ = container['_id']
        self.file_prefix = 'files'


# TODO: already in code elsewhere? Location?
def get_container(cont_name, _id):
    cont_name = containerutil.pluralize(cont_name)
    if cont_name != 'groups':
        _id = bson.ObjectId(_id)

    return config.db[cont_name].find_one({
        '_id': _id,
    })

def is_edition(edition, cont_name, _id, container=None):
    if container is None:
        container = get_container(cont_name, _id)
    if cont_name != 'groups':
        group = container.get('parents', {}).get('group')
    else:
        group = _id
    if group:
        editions = get_container('groups', group).get('edition', [])
        return edition in editions
    else:
        return True

def confirm_edition(edition, cont_name, _id, container=None):
    if not is_edition(edition, cont_name, _id, container):
        raise APIEditionException('This action is reserved for {} edition groups'.format(edition))

def get_parent_tree(cont_name, _id):
    """
    Given a contanier and an id, returns that container and its parent tree.

    For example, given `sessions`, `<session_id>`, it will return:
    {
        'session':  <session>,
        'project':  <project>,
        'group':    <group>
    }
    """

    cont_name = containerutil.singularize(cont_name)

    if cont_name not in ['acquisition', 'session', 'subject', 'project', 'group', 'analysis']:
        raise ValueError('Can only construct tree from group, project, subject, session, analysis or acquisition level')

    analysis_id     = None
    acquisition_id  = None
    session_id      = None
    subject_id      = None
    project_id      = None
    group_id        = None
    tree            = {}

    if cont_name == 'analysis':
        analysis_id = bson.ObjectId(_id)
        analysis = get_container('analysis', analysis_id)
        tree['analysis'] = analysis
        if analysis['parent']['type'] == 'session':
            session_id = analysis['parent']['id']
    if cont_name == 'acquisition':
        acquisition_id = bson.ObjectId(_id)
        acquisition = get_container('acquisition', acquisition_id)
        tree['acquisition'] = acquisition
        session_id = acquisition['session']
    if cont_name == 'session' or session_id:
        if not session_id:
            session_id = bson.ObjectId(_id)
        session = get_container('session', session_id)
        tree['session'] = session
        subject_id = session['subject']
    if cont_name == 'subject' or subject_id:
        if not subject_id:
            subject_id = bson.ObjectId(_id)
        subject = get_container('subject', subject_id)
        tree['subject'] = subject
        project_id = subject['project']
    if cont_name == 'project' or project_id:
        if not project_id:
            project_id = bson.ObjectId(_id)
        project = get_container('project', project_id)
        tree['project'] = project
        group_id = project['group']
    if cont_name == 'group' or group_id:
        if not group_id:
            group_id = _id
        tree['group'] = get_container('group', group_id)

    return tree

def is_session_compliant(session, templates):
    """
    Given a project-level session template and a session,
    returns True/False if the session is in compliance with the template
    """

    def check_req(cont, req_k, req_v):
        """
        Return True if container satisfies specific requirement.
        """

        # If looking at classification, translate to list rather than dictionary
        if req_k == 'classification':
            cont_v = []
            for v in cont.get('classification', {}).itervalues():
                cont_v.extend(v)
        else:
            cont_v = cont.get(req_k)

        if cont_v:
            if isinstance(req_v, dict):
                for k,v in req_v.iteritems():
                    if not check_req(cont_v, k, v):
                        return False
            elif isinstance(cont_v, list):
                found_in_list = False
                for v in cont_v:
                    if re.search(req_v, v, re.IGNORECASE):
                        found_in_list = True
                        break
                if not found_in_list:
                    return False
            else:
                # Assume regex for now
                if not re.search(req_v, cont_v, re.IGNORECASE):
                    return False
        else:
            return False
        return True


    def check_cont(cont, reqs):
        """
        Return True if container satisfies requirements.
        Return False otherwise.
        """
        for req_k, req_v in reqs.iteritems():
            if req_k == 'files':
                for fr in req_v:
                    fr_temp = fr.copy() #so subsequent calls don't have their minimum missing
                    min_count = fr_temp.pop('minimum')
                    count = 0
                    for f in cont.get('files', []):
                        if 'deleted' in f or not check_cont(f, fr_temp):
                            # Didn't find a match, on to the next one
                            continue
                        else:
                            count += 1
                            if count >= min_count:
                                break
                    if count < min_count:
                        return False

            else:
                if not check_req(cont, req_k, req_v):
                    return False
        return True

    def check_session_for_single_template(session, template):

        s_requirements = template.get('session')
        a_requirements = template.get('acquisitions')

        label = s_requirements.pop('label', s_requirements.pop('code', None))
        if label:
            m = re.match(label, session['label'])
            if not m:
                return False

        if s_requirements:
            if not check_cont(session, s_requirements):
                return False

        if a_requirements:
            if not session.get('_id'):
                # New session, won't have any acquisitions. Compliance check fails
                return False
            acquisitions = list(config.db.acquisitions.find({'session': session['_id'], 'deleted': {'$exists': False}}))
            for req in a_requirements:
                req_temp = copy.deepcopy(req)
                min_count = req_temp.pop('minimum')
                count = 0
                for a in acquisitions:
                    if not check_cont(a, req_temp):
                        # Didn't find a match, on to the next one
                        continue
                    else:
                        count += 1
                        if count >= min_count:
                            break
                if count < min_count:
                    return False
        return True

    for template in templates:
        if check_session_for_single_template(session, template):
            return True
    return False


def update_fileinfo(cont_name, _id, fileinfo):
    """
    Used when the file object itself is not intended to be replaced, but the metadata is updated
    Saved state is `saved` when metadata update is completed successfully, `ignored` if the file is not found
    """
    cont_name = containerutil.pluralize(cont_name)
    _id = bson.ObjectId(_id)

    container_before = config.db[cont_name].find_one({'_id': _id, 'files.name': fileinfo['name']})
    if not container_before:
        return None, None, 'ignored'

    container_after = update_file(cont_name, _id, fileinfo)
    return container_before, container_after, 'saved'


def upsert_fileinfo(cont_name, _id, fileinfo, access_logger, ignore_hash_replace=False, logger=config.log):
    """
    Used when a file object is added as well as any relevant metadata.

    If the file does not exist, the file is `saved` as normal
    If the file already exists, this file will increment the version of the existing file and is considered `replaced`
    UNLESS: the upload method would prefer to ignore identical file objects (matching hash), the the file is `ignored`
    """

    cont_name = containerutil.pluralize(cont_name)
    _id = bson.ObjectId(_id)

    container_before = config.db[cont_name].find_one({'_id': _id})

    container_after = None
    saved_state = 'saved'

    # Look to see if file with the same name already exists in the container
    for f in container_before.get('files',[]):

        # File already exists, respond accordingly
        if f['name'] == fileinfo['name']:

            # If the existing file is deleted, always replace (But this is not considered a "replaced" saved state)
            if 'deleted' in f:
                remove_file(cont_name, _id, fileinfo['name'])
                container_after = add_file(cont_name, _id, fileinfo)
                saved_state = 'saved'
                logger.info('File id=%s, name=<%s> replaced deleted file on %s=%s', fileinfo['_id'], fileinfo['name'], cont_name, _id)


            # Files from a failed job should never replaced existing files that are "accepted" (unless they are deleted)
            elif fileinfo.get('from_failed_job') and not f.get('from_failed_job'):
                saved_state = 'ignored'
                logger.info('File id=%s, name=<%s> was from a failed job, and ignored because accepted file exists on %s=%s', fileinfo['_id'], fileinfo['name'], cont_name, _id)

            # The file object is the same as an existing file and the caller has chosen to ignore in this situation
            elif ignore_hash_replace and hashes_equal_or_empty(f.get('hash'), fileinfo['hash']):
                saved_state = 'ignored'
                logger.info('File id=%s, name=<%s> was ignored because its hash <%s> matches the existing hash <%s> on %s=%s',
                    fileinfo['_id'], fileinfo['name'], fileinfo['hash'], f.get('hash'), cont_name, _id)

            # No special circumstances, proceed with a replace
            else:
                container_after = replace_file(cont_name, _id, f, fileinfo, access_logger)
                saved_state = 'replaced'
                logger.info('File id=%s, name=<%s> replaced existing file (id=%s) on %s=%s', fileinfo['_id'], fileinfo['name'], f.get('_id'), cont_name, _id)

            break


    else:

        # File was not already in container, add as normal
        container_after = add_file(cont_name, _id, fileinfo)
        logger.info('File id=%s, name=<%s> was added to %s=%s', fileinfo['_id'], fileinfo['name'], cont_name, _id)


    return container_before, container_after, saved_state

def hashes_equal_or_empty(hash1, hash2):
    """Compare two hashes. They are equal if they both EXIST and are identical"""
    return hash1 and hash2 and hash1 == hash2

def add_file(cont_name, _id, fileinfo):
    fileinfo['created'] = datetime.datetime.utcnow()
    return config.db[cont_name].find_one_and_update(
        {'_id': _id},
        {'$push': {'files': fileinfo}},
        return_document=pymongo.collection.ReturnDocument.AFTER
    )


def update_file(cont_name, _id, fileinfo):
    update_set = {'files.$.modified': datetime.datetime.utcnow()}

    for k,v in fileinfo.iteritems():
        update_set['files.$.' + k] = v

    return config.db[cont_name].find_one_and_update(
        {'_id': _id, 'files.name': fileinfo['name']},
        {'$set': update_set},
        return_document=pymongo.collection.ReturnDocument.AFTER
    )


def replace_file(cont_name, _id, existing_fileinfo, fileinfo, access_logger):

    access_logger(AccessType.replace_file, cont_name=cont_name, cont_id=_id, filename=fileinfo['name'])

    # Keep created date the same, add "replaced" timestamp
    fileinfo['created'] = existing_fileinfo['created']
    fileinfo['replaced'] = datetime.datetime.utcnow()

    return config.db[cont_name].find_one_and_update(
        {'_id': _id, 'files.name': fileinfo['name']},
        {'$set': {'files.$': fileinfo}},
        return_document=pymongo.collection.ReturnDocument.AFTER
    )



def remove_file(cont_name, _id, filename):
    return config.db[cont_name].find_one_and_update(
        {'_id': _id, 'files.name': filename},
        {'$pull': {'files': {'name': filename}}},
        return_document=pymongo.collection.ReturnDocument.AFTER
    )


def _group_id_fuzzy_match(group_id, project_label, unsorted_projects):
    existing_group_ids = [g['_id'] for g in config.db.groups.find(None, ['_id'])]
    if group_id.lower() in existing_group_ids:
        return group_id.lower(), project_label
    group_id_matches = difflib.get_close_matches(group_id, existing_group_ids, cutoff=0.8)
    if len(group_id_matches) == 1:
        group_id = group_id_matches[0]
    else:
        if group_id != '' or project_label != '':
            project_label = group_id + '_' + project_label
            if unsorted_projects:
                project_label = 'Unsorted'
        group_id = 'unknown'
    return group_id, project_label

def _find_or_create_destination_project(group_id, project_label, timestamp, user, unsorted_projects):
    group_id, project_label = _group_id_fuzzy_match(group_id, project_label, unsorted_projects)
    group = config.db.groups.find_one({'_id': group_id})

    if project_label == '':
        project_label = 'Unsorted' if unsorted_projects else 'Unknown'

    project_regex = '^'+re.escape(project_label)+'$'
    project = config.db.projects.find_one({'group': group['_id'], 'label': {'$regex': project_regex, '$options': 'i'}, 'deleted': {'$exists': False}})

    if project:
        # If the project already exists, check the user's access
        if user:
            confirm_edition('lab', 'projects', project['_id'], project)
            if not has_access(user, project, 'rw'):
                raise APIPermissionException('User {} does not have read-write access to project {}'.format(user, project['label']))
        return project

    elif unsorted_projects:
        # Check if there is an Unsorted project in the group to upload to
        project_label = 'Unsorted'
        project = config.db.projects.find_one({'group': group['_id'], 'label': project_label, 'deleted': {'$exists': False}})
        if project:
            if user and not has_access(user, project, 'rw'):
                raise APIPermissionException('User {} does not have read-write access to project {}'.format(user, project['label']))
            return project

    if not project:
        # if the project doesn't exit, check the user's access at the group level, should be admin
        if user:
            confirm_edition('lab', 'groups', group_id, group)
            if not has_access(user, group, 'admin'):
                raise APIPermissionException('User {} does not have read-write access to group {}'.format(user, group_id))

        project = {
                'group': group['_id'],
                'label': project_label,
                'permissions': group['permissions'],
                'public': False,
                'created': timestamp,
                'modified': timestamp
        }

        if unsorted_projects:
            project['description'] = 'This project was automatically created because unsortable data was detected. \
                                      Please move sessions to the appropriate project.'

        result = ContainerStorage.factory('project').create_el(project)
        project['_id'] = result.inserted_id

    return project

def _create_query(cont, cont_type, parent_type, parent_id, upload_type):
    if upload_type in ('label', 'uid'):
        match_key = '_id' if cont_type == 'subject' else upload_type
        return {
            parent_type: bson.ObjectId(parent_id),
            match_key: cont[match_key],
            'deleted': {'$exists': False},
        }
    else:
        raise NotImplementedError('upload type {} is not handled by _create_query'.format(upload_type))

def _upsert_container(cont, cont_type, parent, parent_type, upload_type, timestamp):
    cont['modified'] = timestamp
    cont_name = containerutil.pluralize(cont_type)

    if cont.get('timestamp'):
        cont['timestamp'] = dateutil.parser.parse(cont['timestamp'])

        if cont_type == 'acquisition':
            session_operations = {'$min': dict(timestamp=cont['timestamp'])}
            if cont.get('timezone'):
                session_operations['$set'] = {'timezone': cont['timezone']}
            config.db.sessions.update_one({'_id': parent['_id']}, session_operations)

    query = _create_query(cont, cont_type, parent_type, parent['_id'], upload_type)

    if config.db[cont_name].find_one(query) is not None:
        return _update_container_nulls(query, cont, cont_type)

    else:
        insert_vals = {
            parent_type:    parent['_id'],
            'permissions':  parent['permissions'],
            'public':       parent.get('public', False),
            'created':      timestamp
        }
        if cont_type == 'session':
            insert_vals['group'] = parent['group']
        cont.update(insert_vals)
        if cont_name in ['acquisitions', 'sessions', 'subjects', 'projects', 'analyses']:
            cont['parents'] = ContainerStorage.factory(cont_name).get_parents(cont)
        insert_id = config.db[cont_name].insert(cont)
        cont['_id'] = insert_id
        return cont


def _get_targets(project_obj, session, acquisition, type_, timestamp):
    target_containers = []
    if not session:
        return target_containers

    subject = containerutil.extract_subject(session, project_obj)
    subject_files = dict_fileinfos(subject.pop('files', []))
    subject_obj = _upsert_container(subject, 'subject', project_obj, 'project', type_, timestamp)
    target_containers.append(
        (TargetContainer(subject_obj, 'subject'), subject_files)
    )

    session_files = dict_fileinfos(session.pop('files', []))
    session_obj = _upsert_container(session, 'session', project_obj, 'project', type_, timestamp)
    target_containers.append(
        (TargetContainer(session_obj, 'session'), session_files)
    )

    if not acquisition:
        return target_containers
    acquisition_files = dict_fileinfos(acquisition.pop('files', []))
    acquisition_obj = _upsert_container(acquisition, 'acquisition', session_obj, 'session', type_, timestamp)
    target_containers.append(
        (TargetContainer(acquisition_obj, 'acquisition'), acquisition_files)
    )
    return target_containers


def find_existing_hierarchy(metadata, type_='uid', user=None):
    #pylint: disable=unused-argument
    project = metadata.get('project', {})
    session = metadata.get('session', {})
    acquisition = metadata.get('acquisition', {})

    # Fail if some fields are missing
    try:
        acquisition_uid = acquisition['uid']
        session_uid = session['uid']
    except Exception as e:
        log.error(metadata)
        raise APIStorageException(str(e))

    # Confirm session and acquisition exist
    session_obj = config.db.sessions.find_one({'uid': session_uid, 'deleted': {'$exists': False}}, ['project', 'permissions'])

    if session_obj is None:
        raise APINotFoundException('Session with uid {} does not exist'.format(session_uid))
    if user and not has_access(user, session_obj, 'rw'):
        raise APIPermissionException('User {} does not have read-write access to session {}'.format(user, session_uid))

    a = config.db.acquisitions.find_one({'uid': acquisition_uid, 'deleted': {'$exists': False}}, ['_id'])
    if a is None:
        raise APINotFoundException('Acquisition with uid {} does not exist'.format(acquisition_uid))

    now = datetime.datetime.utcnow()
    project_files = dict_fileinfos(project.pop('files', []))
    project_obj = config.db.projects.find_one({'_id': session_obj['project'], 'deleted': {'$exists': False}}, projection=PROJECTION_FIELDS + ['name'])
    target_containers = _get_targets(project_obj, session, acquisition, type_, now)
    target_containers.append(
        (TargetContainer(project_obj, 'project'), project_files)
    )
    return target_containers


def upsert_bottom_up_hierarchy(metadata, type_='uid', user=None):
    group = metadata.get('group', {})
    project = metadata.get('project', {})
    session = metadata.get('session', {})
    acquisition = metadata.get('acquisition', {})

    # Fail if some fields are missing
    try:
        _ = group['_id']
        _ = project['label']
        _ = acquisition['uid']
        session_uid = session['uid']
    except Exception as e:
        log.error(metadata)
        raise APIStorageException(str(e))

    session_obj = config.db.sessions.find_one({'uid': session_uid, 'deleted': {'$exists': False}})

    if session_obj: # skip project creation, if session exists

        if user:
            confirm_edition('lab', 'sessions', session_obj['_id'], session_obj)
            if not has_access(user, session_obj, 'rw'):
                raise APIPermissionException('User {} does not have read-write access to session {}'.format(user, session_uid))

        now = datetime.datetime.utcnow()
        project_files = dict_fileinfos(project.pop('files', []))
        project_obj = config.db.projects.find_one({'_id': session_obj['project'], 'deleted': {'$exists': False}}, projection=PROJECTION_FIELDS + ['name'])
        target_containers = _get_targets(project_obj, session, acquisition, type_, now)
        target_containers.append(
            (TargetContainer(project_obj, 'project'), project_files)
        )
        return target_containers
    else:
        return upsert_top_down_hierarchy(metadata, type_=type_, user=user, unsorted_projects=True)


def upsert_top_down_hierarchy(metadata, type_='label', user=None, unsorted_projects=False):
    group = metadata['group']
    project = metadata['project']
    session = metadata.get('session')
    acquisition = metadata.get('acquisition')

    now = datetime.datetime.utcnow()
    project_files = dict_fileinfos(project.pop('files', []))
    project_obj = _find_or_create_destination_project(group['_id'], project['label'], now, user, unsorted_projects)
    if unsorted_projects and project_obj['label'] == 'Unsorted':
        session['label'] = 'gr-{}_proj-{}_ses-{}'.format(group['_id'], project['label'], session['uid'])
    target_containers = _get_targets(project_obj, session, acquisition, type_, now)
    target_containers.append(
        (TargetContainer(project_obj, 'project'), project_files)
    )
    return target_containers


def dict_fileinfos(infos):
    dict_infos = {}
    for info in infos:
        dict_infos[info['name']] = info
    return dict_infos


def update_container_hierarchy(metadata, cid, container_type):
    c_metadata = metadata.get(container_type)

    if c_metadata is None:
        c_metadata = {}

    now = datetime.datetime.utcnow()
    if c_metadata.get('timestamp'):
        c_metadata['timestamp'] = dateutil.parser.parse(c_metadata['timestamp'])
    c_metadata['modified'] = now
    c_obj = _update_container_nulls({'_id': cid}, c_metadata, container_type)
    if c_obj is None:
        raise APIStorageException('container does not exist')
    if container_type in ['session', 'acquisition']:
        _update_hierarchy(c_obj, container_type, metadata)
    return c_obj

def _update_hierarchy(container, container_type, metadata):
    project_id = container.get('project') # for sessions
    now = datetime.datetime.utcnow()

    if container_type == 'acquisition':
        session = metadata.get('session', {})
        session_obj = None
        if session.keys():
            session['modified'] = now
            if session.get('timestamp'):
                session['timestamp'] = dateutil.parser.parse(session['timestamp'])
            session_obj = _update_container_nulls({'_id': container['session']},  session, 'session')
        if session_obj is None:
            session_obj = get_container('session', container['session'])
        project_id = session_obj['project']

    if project_id is None:
        raise APIStorageException('Failed to find project id in session obj')
    project = metadata.get('project', {})
    if project.keys():
        project['modified'] = now
        _update_container_nulls({'_id': project_id}, project, 'project')

def _update_container_nulls(base_query, update, container_type):
    coll_name = containerutil.pluralize(container_type)
    cont = config.db[coll_name].find_one(base_query)
    if cont is None:
        raise APIStorageException('Failed to find {} object using the query: {}'.format(container_type, base_query))

    if container_type == 'session' and type(update.get('subject')) is dict:
        subject_update = update.pop('subject')
        containerutil.attach_raw_subject(update, subject_update)
        subject_update['modified'] = update['modified']
        _update_container_nulls({'_id': cont['subject']}, subject_update, 'subject')

    bulk = config.db[coll_name].initialize_unordered_bulk_op()

    if update.get('metadata') and not cont.get('metadata'):
        # If we are trying to update metadata fields and the container metadata does not exist or is empty,
        # metadata can all be updated at once for efficiency
        m_update = util.mongo_sanitize_fields(update.pop('metadata'))
        bulk.find(base_query).update_one({'$set': {'metadata': m_update}})

    update_dict = util.mongo_dict(update)
    for k, v in update_dict.items():
        q = copy.deepcopy(base_query)
        if k == 'tags':
            u = {'$addToSet': {k: {'$each': v}}}
        else:
            q['$or'] = [{k: {'$exists': False}}, {k: None}]
            u = {'$set': {k: v}}
        bulk.find(q).update_one(u)
    bulk.execute()
    return config.db[coll_name].find_one(base_query)
