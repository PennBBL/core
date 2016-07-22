import bson.objectid

from .. import config
from ..auth import INTEGER_ROLES

CONT_TYPES = ['acquisition', 'analysis', 'collection', 'group', 'project', 'session']

def getPerm(name):
    return INTEGER_ROLES[name]

def add_id_to_subject(subject, pid):
    """
    Add a mongo id field to given subject object (dict)

    Use the same _id as other subjects in the session's project with the same code
    If no _id is found, generate a new _id
    """
    result = None
    if subject is None:
        subject = {}
    if subject.get('_id') is not None:
        # Ensure _id is bson ObjectId
        subject['_id'] = bson.ObjectId(str(subject['_id']))
        return subject

    # Attempt to match with another session in the project
    if subject.get('code') is not None and pid is not None:
        query = {'subject.code': subject['code'],
                 'project': pid,
                 'subject._id': {'$exists': True}}
        result = config.db.sessions.find_one(query)

    if result is not None:
        subject['_id'] = result['subject']['_id']
    else:
        subject['_id'] = bson.ObjectId()
    return subject


class ContainerReference(object):
    # pylint: disable=redefined-builtin
    # TODO: refactor to resolve pylint warning

    def __init__(self, type, id):
        if type not in CONT_TYPES:
            raise Exception('Container type must be one of {}'.format(CONT_TYPES))

        if not isinstance(type, basestring):
            raise Exception('Container type must be of type str')
        if not isinstance(id, basestring):
            raise Exception('Container id must be of type str')

        self.type = type
        self.id   = id

    @classmethod
    def from_dictionary(cls, d):
        return cls(
            type = d['type'],
            id   = d['id']
        )

    @classmethod
    def from_filereference(cls, fr):
        return cls(
            type = fr.type,
            id   = fr.id
        )

    def get(self):
        result = config.db[self.type + 's'].find_one({'_id': bson.ObjectId(self.id)})
        if result is None:
            raise Exception("No such " + self.type + " " + self.id + " in database")
        return result

    def find_file(self, filename):
        cont = self.get()
        for f in cont.get('files', []):
            if f['name'] == filename:
                return f
        return None

    def check_access(self, userID, perm_name):
        perm = getPerm(perm_name)
        for p in self.get()['permissions']:
            if p['_id'] == userID and getPerm(p['access']) > perm:
                return

        raise Exception("User " + userID + " does not have " + perm_name + " access to " + self.type + " " + self.id)

class FileReference(ContainerReference):
    def __init__(self, type, id, name):
        super(FileReference, self).__init__(type, id)
        self.name = name

    @classmethod
    def from_dictionary(cls, d):
        return cls(
            type = d['type'],
            id   = d['id'],
            name = d['name']
        )

def create_filereference_from_dictionary(d):
    return FileReference.from_dictionary(d)

def create_containerreference_from_dictionary(d):
    return ContainerReference.from_dictionary(d)

def create_containerreference_from_filereference(fr):
    return ContainerReference.from_filereference(fr)
