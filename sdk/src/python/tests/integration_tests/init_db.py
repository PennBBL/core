import binascii
import os
import datetime

SCITRAN_PERSISTENT_DB_URI = os.environ.get('SCITRAN_PERSISTENT_DB_URI')
SCITRAN_ADMIN_API_KEY = binascii.hexlify(os.urandom(10)).decode('utf-8')

def create_user(db, _id, api_key, **kwargs):
    payload = {
        '_id': _id, 
        'email': _id,
        'created': datetime.datetime.utcnow(),
        'modified': datetime.datetime.utcnow(),
        'firstname': 'test', 
        'lastname': 'user'
    }
    payload.update(kwargs)

    # Create user
    print('Create user...')
    db.users.replace_one({'_id': _id}, payload, upsert=True)

    # Insert API Key
    print('Create API Key...')
    db.apikeys.replace_one({'_id': api_key}, {
        '_id': api_key,
        'created': datetime.datetime.utcnow(),
        'last_seen': None,
        'type': 'user',
        'origin': {'type': 'user', 'id': _id}
    }, upsert=True)

def init_db():
    # Import on demand
    import pymongo
    import requests

    if not SCITRAN_PERSISTENT_DB_URI:
        raise Exception('Cannot initialize database without SCITRAN_PERSISTENT_DB_URI!')

    db = pymongo.MongoClient(SCITRAN_PERSISTENT_DB_URI).get_default_database()
    create_user(db, 'admin@user.com', SCITRAN_ADMIN_API_KEY, role='site-admin')

