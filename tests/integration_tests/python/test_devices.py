import datetime

import bson


def test_devices(as_public, as_user, as_admin, as_root, as_drone, api_db):
    # try to get all devices w/o logging in
    r = as_public.get('/devices')
    assert r.status_code == 403

    # get all devices
    r = as_user.get('/devices?join_keys=true')
    assert r.ok

    # bw-comp: verify test bootstrapper exists and has uid
    assert r.json()
    drone = r.json()[0]
    drone_id = drone['_id']

    # bw-comp: verify test bootstrapper has api key after first get
    assert as_admin.get('/devices/' + drone_id).ok
    assert api_db.apikeys.count({'uid': bson.ObjectId(drone_id), 'type': 'device'}) == 1

    # verify users don't have access to device keys, but admins do
    assert 'key' not in drone
    r = as_admin.get('/devices?join_keys=true')
    assert r.ok
    assert 'key' in r.json()[0]

    # try to get devices w/o logging in
    r = as_public.get('/devices/' + drone_id)
    assert r.status_code == 403

    # try to get non-existent device
    r = as_user.get('/devices/000000000000000000000000')
    assert r.status_code == 404

    # get device
    r = as_user.get('/devices/' + drone_id)
    assert r.ok

    # bw-comp: verify devices using secret have type instead of method
    drone = r.json()
    assert 'type' in drone
    assert 'method' not in drone

    # verify users don't have access to device keys, but admins do
    assert 'key' not in drone
    r = as_admin.get('/devices/' + drone_id)
    assert r.ok
    assert 'key' in r.json()

    # try to do device check-in as user
    r = as_root.put('/devices/self')
    assert r.status_code == 403

    # do empty device check-in (implicit last_seen update)
    r = as_drone.put('/devices/self')
    assert r.ok

    # verify last_seen was updated
    r = as_user.get('/devices/' + drone_id)
    assert r.ok
    drone_ = r.json()
    assert drone_['last_seen'] > drone['last_seen']
    del drone['last_seen']
    del drone_['last_seen']
    assert drone_ == drone

    # try to get device statuses w/o logging in
    r = as_public.get('/devices/status')
    assert r.status_code == 403

    # get device statuses
    r = as_user.get('/devices/status')
    assert r.ok
    assert drone_id in r.json()

    # try to create device w/o root
    r = as_admin.post('/devices')
    assert r.status_code == 403

    # create device
    r = as_root.post('/devices', json={'type': 'test'})
    assert r.ok
    device_id = r.json()['_id']
    assert api_db.apikeys.count({'uid': bson.ObjectId(device_id), 'type': 'device'}) == 1
    r = as_admin.get('/devices/' + device_id)
    assert r.ok
    device_key = r.json()['key']

    # no check-in interval or last_seen not set => unknown
    assert as_user.get('/devices/status').json()[device_id]['status'] == 'unknown'

    # update device - self-set check-in interval (also implicitly updates last_seen)
    as_device = as_public
    as_device.headers.update({'Authorization': 'scitran-user {}'.format(device_key)})
    r = as_device.put('/devices/self', json={'interval': 60})
    assert r.ok

    # check-in interval set + last_seen new => ok
    assert as_user.get('/devices/status').json()[device_id]['status'] == 'ok'

    # check-in interval set + last_seen old => missing
    api_db.devices.update({'_id': bson.ObjectId(device_id)},
        {'$set': {'last_seen': datetime.datetime.now() - datetime.timedelta(seconds=61)}})
    assert as_user.get('/devices/status').json()[device_id]['status'] == 'missing'

    # has errors => error
    r = as_device.put('/devices/self', json={'errors': ['does. not. compute.']})
    assert r.ok
    assert as_user.get('/devices/status').json()[device_id]['status'] == 'error'

    # delete device
    r = as_root.delete('/devices/' + device_id)
    assert r.ok

    r = as_user.get('/devices/' + device_id)
    assert r.status_code == 404
