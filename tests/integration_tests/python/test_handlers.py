import datetime
import os

from api.config import release_version_file_path

def test_roothandler(as_public):
    r = as_public.get('')
    assert r.ok
    assert '<title>SciTran API</title>' in r.text


def test_schemahandler(as_public):
    r = as_public.get('/schemas/non/existent.json')
    assert r.status_code == 404

    r = as_public.get('/schemas/definitions/user.json')
    assert r.ok
    schema = r.json()
    assert all(attr in schema['definitions'] for attr in ('email', 'firstname', 'lastname'))


def test_devicehandler(as_user, as_root, as_drone, api_db):
    # get all devices
    r = as_user.get('/devices')
    assert r.ok

    # test that drone is listed
    drone_id = as_drone.headers['X-SciTran-Method'] + '_' + as_drone.headers['X-SciTran-Name']
    assert sum(device['_id'] == drone_id for device in r.json()) == 1

    # try to get non-existent device
    r = as_user.get('/devices/these_arent_the_droids_you_are_looking_for')
    assert r.status_code == 404

    # get device
    r = as_user.get('/devices/' + drone_id)
    assert r.ok

    # get device self
    r = as_drone.get('/devices/self')
    assert r.ok

    # get device status list
    # NOTE unprotected handler method - shouldn't it require_login?
    r = as_user.get('/devices/status')
    assert r.ok

    # try to update drone w/o perms (require_drone)
    r = as_user.post('/devices')
    assert r.status_code == 403

    # update drone - set check-in interval
    r = as_drone.post('/devices', json={'interval': 60})
    assert r.ok

    # inject test device for status checks
    api_db.devices.insert({
        '_id': 'test_drone',
        'last_seen': datetime.datetime.now(),
        'method': 'test',
        'name': 'drone',
        'errors': [],
    })

    # no check-in interval => unknown
    assert as_user.get('/devices/status').json()['test_drone']['status'] == 'unknown'

    # check-in interval set => ok
    api_db.devices.update({'_id': 'test_drone'}, {'$set': {'interval': 60}})
    assert as_user.get('/devices/status').json()['test_drone']['status'] == 'ok'

    # check-in interval set + last_seen too old => missing
    api_db.devices.update({'_id': 'test_drone'},
        {'$set': {'last_seen': datetime.datetime.now() - datetime.timedelta(seconds=61)}})
    assert as_user.get('/devices/status').json()['test_drone']['status'] == 'missing'

    # has errors => error
    api_db.devices.update({'_id': 'test_drone'}, {'$set': {'errors': ['does not compute']}})
    assert as_user.get('/devices/status').json()['test_drone']['status'] == 'error'

    # clean up
    api_db.devices.remove({'_id': 'test_drone'})


def test_config_version(as_user, api_db):
    # get database version when no version document exists, It hasn;t been set yet in the tests
    r = as_user.get('/version')
    assert r.status_code == 404
    api_db.singletons.insert_one({"_id":"version","database":3})

    # Start with non-existent file
    try:
        os.remove(release_version_file_path)
    except:
        pass

    # get database schema version
    r = as_user.get('/version')
    assert r.ok
    assert r.json()['database'] == 3
    assert r.json()['release'] == ''

    # Check api version when api_version.txt does not exist
    with open(release_version_file_path, 'w') as f:
        f.write('2.1.0')

    r = as_user.get('/version')
    assert r.ok
    assert r.json()['database'] == 3
    assert r.json()['release'] == '2.1.0'

    api_db.singletons.find_one_and_delete({'_id':'version'})
    os.remove(release_version_file_path)
