import bson
import datetime

from .. import config, util
from ..web.errors import APIAuthProviderException

log = config.log


class APIKey(object):
    """
    Abstract API key class
    """

    key_type = None

    @staticmethod
    def _preprocess_key(key):
        """
        Convention for API keys is that they can have arbitrary information, separated by a :,
        before the actual key. Generally, this will have a connection string in it.
        Strip this preamble, if any, before processing the key.
        """

        return key.split(":")[-1] # Get the last segment of the string after any : separators

    @staticmethod
    def validate(key):
        """
        AuthN for user accounts via api key.

        401s via APIAuthProviderException on failure.
        """
        key = APIKey._preprocess_key(key)

        timestamp = datetime.datetime.utcnow()
        api_key = config.db.apikeys.find_one_and_update({'_id': key}, {'$set': {'last_used': timestamp}})

        if api_key:

            # Some api keys may have additional requirements that must be met
            try:
                APIKeyTypes[api_key['type']].check(api_key)
            except KeyError:
                log.warning('Unknown API key type ({})'.format(api_key.get('type')))
                APIAuthProviderException('Invalid API key')

            return api_key

        else:
            raise APIAuthProviderException('Invalid API key')

    @classmethod
    def generate_api_key(cls, uid):
        if not isinstance(uid, bson.ObjectId):
            uid = bson.ObjectId(uid)
        return {
            '_id': util.create_nonce(),
            'created': datetime.datetime.utcnow(),
            'type': cls.key_type,
            'last_used': None,
            'origin': {'type': cls.key_type, 'id': uid}
        }

    @classmethod
    def generate(cls, uid):
        """
        Generates API key, replaces existing API key if it exists
        """
        api_key = cls.generate_api_key(uid)
        config.db.apikeys.delete_many({'origin.id': uid, 'type': cls.key_type})
        config.db.apikeys.insert_one(api_key)
        return api_key['_id']

    @classmethod
    def get(cls, uid):
        return config.db.apikeys.find_one({'origin.id': uid, 'type': cls.key_type})

    @classmethod
    def check(cls, api_key):
        pass


class DeviceApiKey(APIKey):
    key_type = 'device'


class UserApiKey(APIKey):
    key_type = 'user'


class JobApiKey(APIKey):
    """
    API key that grants API access as a specified user during execution of a job
    Job must be in 'running' state to use API key
    """

    key_type = 'job'

    # pylint: disable=arguments-differ
    @classmethod
    def generate(cls, uid, job_id, scope=None):
        """
        Returns an API key for user for use by a specific job.
        Re-uses such a key if it already exists.
        """

        job_id = str(job_id)

        existing_key = config.db.apikeys.find_one({
            'origin.id': uid,
            'job': job_id,
        })

        if existing_key is not None:
            return existing_key['_id']

        else:
            api_key = cls.generate_api_key(uid)
            api_key['job'] = job_id
            if scope:
                api_key['scope'] = scope
            else:
                api_key['origin']['via'] = {'type': api_key['origin']['type'],
                                            'id': job_id}
                api_key['origin']['type'] = 'user'

            config.db.apikeys.insert_one(api_key)
            return api_key['_id']

    @classmethod
    def remove(cls, job_id):
        config.db.apikeys.delete_many({'type': cls.key_type, 'job': str(job_id)})

    @classmethod
    def check(cls, api_key):
        job_id = api_key['job']
        if config.db.jobs.count({'_id': bson.ObjectId(job_id), 'state': 'running'}) != 1:
            raise APIAuthProviderException('Use of API key requires job to be in progress')


APIKeyTypes = {
    'device': DeviceApiKey,
    'user': UserApiKey,
    'job': JobApiKey,
}
