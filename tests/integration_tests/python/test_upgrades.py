import datetime
import os
import sys

import bson
import copy
import pytest
import pytz


@pytest.fixture(scope='function')
def database(mocker):
    bin_path = os.path.join(os.getcwd(), 'bin')
    mocker.patch('sys.path', [bin_path] + sys.path)
    import database
    return database


def test_42(data_builder, api_db, as_admin, database):
    # Mimic old-style archived flag
    session = data_builder.create_session()
    session2 = data_builder.create_session()
    api_db.sessions.update_one({'_id': bson.ObjectId(session)}, {'$set': {'archived': True}})
    api_db.sessions.update_one({'_id': bson.ObjectId(session2)}, {'$set': {'archived': False}})

    # Verfiy archived session is not hidden anymore
    assert session  in [s['_id'] for s in as_admin.get('/sessions').json()]

    # Verify upgrade creates new-style hidden tag
    database.upgrade_to_42()
    session_data = as_admin.get('/sessions/' + session).json()
    assert 'archived' not in session_data
    assert 'hidden' in session_data['tags']

    # Verify archived was removed when false as well
    session_data = as_admin.get('/sessions/' + session2).json()
    assert 'archived' not in session_data


def test_43(data_builder, api_db, as_admin, file_form, database):
    # Create session and upload file for later use as analysis input
    session = data_builder.create_session()
    r = as_admin.post('/sessions/' + session + '/files', files=file_form('input.txt'))
    assert r.ok

    # Create ad-hoc analysis with input ref, then upload output
    r = as_admin.post('/sessions/' + session + '/analyses', json={
        'label': 'offline',
        'inputs': [{'type': 'session', 'id': session, 'name': 'input.txt'}]
    })
    assert r.ok
    analysis_id = r.json()['_id']
    r = as_admin.post('/analyses/' + analysis_id + '/files', files=file_form('output.txt', meta=[{'name': 'output.txt'}]))
    assert r.ok

    # Mimic old-style analysis input/output tags
    analysis = api_db.analyses.find_one({'_id': bson.ObjectId(analysis_id)}, ['inputs', 'files'])
    for f in analysis['inputs']:
        f['input'] = True
    for f in analysis['files']:
        f['output'] = True
    api_db.analyses.update_one({'_id': bson.ObjectId(analysis_id)},
                               {'$set': {'files': analysis['inputs'] + analysis['files']},
                                '$unset': {'inputs': ''}})

    # Verify upgrade gets rid of tags and separates inputs/files
    database.upgrade_to_43()
    analysis = as_admin.get('/analyses/' + analysis_id).json()
    assert 'inputs' in analysis
    assert len(analysis['inputs']) == 1
    assert 'input' not in analysis['inputs'][0]

    assert 'files' in analysis
    assert len(analysis['files']) == 1
    assert 'output' not in analysis['files'][0]


def test_45(data_builder, randstr, api_db, as_admin, database, file_form):

    # Set up files with measurements

    assert True

    containers = [
        ('collections',  data_builder.create_collection()),
        ('projects',     data_builder.create_project()),
        ('sessions',     data_builder.create_session()),
        ('acquisitions', data_builder.create_acquisition())
    ]

    for c in containers:
        assert as_admin.post('/{}/{}/files'.format(c[0], c[1]), files=file_form('test.csv')).ok
        assert as_admin.post('/{}/{}/files'.format(c[0], c[1]), files=file_form('test2.csv')).ok
        api_db[c[0]].update_one({'_id': bson.ObjectId(c[1])},
            {'$set': { # Mangoes ...
                'files.0.measurements': ['diffusion', 'functional'],
                'files.1.measurements': ['diffusion', 'functional']
            }})


    # Set up rules referencing measurements

    rule = {
        'all' : [
            {'type' : 'file.measurements', 'value' : 'diffusion'},
            {'type' : 'container.has-measurements', 'value' : 'tests', 'regex': True}
        ],
        'any' : [
            {'type' : 'file.measurements', 'value' : 'diffusion'},
            {'type' : 'container.has-measurements', 'value' : 'tests', 'regex': True}
        ],
        'name' : 'Run dcm2niix on dicom',
        'alg' : 'dcm2niix',
        'project_id' : 'site'
    }

    api_db.project_rules.insert(copy.deepcopy(rule))
    api_db.project_rules.insert(copy.deepcopy(rule))


    # Set up session templates referencing measurements

    t_project1 = data_builder.create_project()
    t_project2 = data_builder.create_project()

    template = {
        'session': {'subject': {'code': '^compliant$'}},
        'acquisitions': [{
            'minimum': 1,
            'files': [{
                'minimum': 2,
                'measurements': 'diffusion'
            }]
        }]
    }

    assert as_admin.post('/projects/' + t_project1 + '/template', json=template).ok
    assert as_admin.post('/projects/' + t_project2 + '/template', json=template).ok


    ### RUN UPGRADE

    database.upgrade_to_45()

    ####


    # Ensure files were updated
    for c in containers:
        files = as_admin.get('/{}/{}'.format(c[0], c[1])).json()['files']
        for f in files:
            assert f['classification'] == {'Contrast': ['Diffusion', 'T2*'], 'Intent': ['Functional', 'Structural'], 'Custom': ['diffusion', 'functional']}


    # Ensure rules were updated
    rule_after = {
        'all' : [
            {'type' : 'file.classification', 'value' : 'diffusion'},
            {'type' : 'container.has-classification', 'value' : 'tests', 'regex': True}
        ],
        'any' : [
            {'type' : 'file.classification', 'value' : 'diffusion'},
            {'type' : 'container.has-classification', 'value' : 'tests', 'regex': True}
        ],
        'name' : 'Run dcm2niix on dicom',
        'alg' : 'dcm2niix'
    }

    rules = as_admin.get('/site/rules').json()
    for r in rules:
        r.pop('_id')
        assert r == rule_after


    # Ensure templates were updated
    template_after = {
        'session': {'subject': {'code': '^compliant$'}},
        'acquisitions': [{
            'minimum': 1,
            'files': [{
                'minimum': 2,
                'classification': 'diffusion'
            }]
        }]
    }
    for p in [t_project1, t_project2]:
        assert as_admin.get('/projects/' + p).json()['template'] == template_after

    ### CLEANUP

    api_db.modalities.delete_many({})


def test_47_and_48(api_db, data_builder, as_admin, file_form, database):
    # Create old device
    last_seen = datetime.datetime.utcnow().replace(microsecond=0)
    api_db.devices.insert_one({
        '_id': 'method_name',
        'method': 'method',
        'name': 'name',
        'last_seen': last_seen,
        'errors': [],
    })

    api_db.devices.insert_one({
        '_id': 'device_without_method',
        'last_seen': last_seen
    })

    # Create acq with files
    # * one with with above device as it's origin
    # * the other pointing to a device that doesn't exist
    acq_id = data_builder.create_acquisition()
    as_admin.post('/acquisitions/' + acq_id + '/files', files=file_form('a.txt'))
    as_admin.post('/acquisitions/' + acq_id + '/files', files=file_form('b.txt'))
    files = api_db.acquisitions.find_one({'_id': bson.ObjectId(acq_id)})['files']
    files[0]['origin'] = {'type': 'device', 'id': 'method_name'}
    files[1]['origin'] = {'type': 'device', 'id': 'missing_one'}
    api_db.acquisitions.update_one({'_id': bson.ObjectId(acq_id)}, {'$set': {'files': files}})

    # Test that devices are switched over to ObjectId via 47
    database.upgrade_to_47()
    device = api_db.devices.find_one({'type': 'method', 'name': 'name'})

    assert device
    device_id = device.get('_id')
    assert isinstance(device_id, bson.ObjectId)
    assert device == {
        '_id': device_id,
        'label': 'method_name',
        'type': 'method',
        'name': 'name',
        'last_seen': last_seen,
        'errors': [],
    }

    device = api_db.devices.find_one({'type': 'device_without_method'})
    assert device
    assert device['label'] == 'device_without_method'
    assert device['type'] == 'device_without_method'


    # Verify that ObjectId casting is no longer 500-ing with `join=origin`, even without
    # upgrade 48 fixing device origins.
    r = as_admin.get('/acquisitions/' + acq_id + '?join=origin')
    assert r.ok

    # Test that device origins get fixed via 48
    database.upgrade_to_48()
    device_id_str = str(device_id)
    files = api_db.acquisitions.find_one({'_id': bson.ObjectId(acq_id)})['files']
    assert files[0]['origin'] == {'type': 'device', 'id': device_id_str}

    # Look for id of new device
    added_device_id_str = files[1]['origin']['id']
    assert files[1]['origin'] == {'type': 'device', 'id': added_device_id_str}
    added_device = api_db.devices.find_one({'label': 'missing_one'})
    assert added_device['type'] == 'unknown'
    added_device['_id'] = added_device_id_str

    # Verify that `join=origin` now works as intended
    r = as_admin.get('/acquisitions/' + acq_id + '?join=origin')
    assert r.ok
    assert r.json()['join-origin']['device'] == {
        device_id_str: {
            '_id': device_id_str,
            'label': 'method_name',
            'type': 'method',
            'name': 'name',
            'last_seen': pytz.timezone('UTC').localize(last_seen).isoformat(),
            'errors': [],
        },
        added_device_id_str: added_device
    }

def test_50(data_builder, api_db, as_admin, file_form, database):
    acquisition = data_builder.create_acquisition()
    r = as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('test_file1.csv'))
    r = as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('test_file2.csv'))
    r = as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('test_file3.csv'))
    assert r.ok

    # Clean up modality
    r = as_admin.delete('/modalities/MR')

    payload = {
        '_id': 'MR',
        'classification': {
            'Intent': ["Structural", "Functional", "Localizer"],
            'Measurement': ["B0", "B1", "T1", "T2"]
        }
    }
    r = as_admin.post('/modalities', json=payload)
    assert r.ok

    r = as_admin.post('/acquisitions/' + acquisition + '/files/test_file1.csv/classification', json={
        'modality': 'MR',
        'replace': {
            'Intent': ['Structural'],
            'Measurement': ['T1'],
            'Custom': ['anatomy_t1w', 'foobar']
        }
    })
    assert r.ok

    r = as_admin.post('/acquisitions/' + acquisition + '/files/test_file2.csv/classification', json={
        'modality': 'MR',
        'replace': {
            'Intent': ['Functional'],
            'Measurement': ['T2'],
            'Custom': ['functional']
        }
    })
    assert r.ok

    database.upgrade_to_50()

    # Confirm that measurements is set and classification is updated
    r_acquisition = api_db.acquisitions.find_one({'_id': bson.ObjectId(acquisition)})
    f = r_acquisition['files'][0]
    assert f['name'] == 'test_file1.csv'
    assert f['classification'] == {
        'Intent': ['Structural'],
        'Measurement': ['T1'],
        'Custom': ['foobar']
    }
    assert f['measurements'] == ['anatomy_t1w']

    f = r_acquisition['files'][1]
    assert f['name'] == 'test_file2.csv'
    assert f['classification'] == {
        'Intent': ['Functional'],
        'Measurement': ['T2']
    }
    assert f['measurements'] == ['functional']

    f = r_acquisition['files'][2]
    assert f['name'] == 'test_file3.csv'
    assert f['classification'] == {}
    assert 'measurements' not in f

    # Assert that changing modality resets measurements
    r = as_admin.put('/acquisitions/' + acquisition + '/files/test_file1.csv', json={
        'modality': None
    })
    assert r.ok

    # Assert that changing classification resets measurements
    r = as_admin.post('/acquisitions/' + acquisition + '/files/test_file2.csv/classification', json={
        'add': {
            'Custom': ['myvalue']
        }
    })
    assert r.ok

    r_acquisition = api_db.acquisitions.find_one({'_id': bson.ObjectId(acquisition)})
    f = r_acquisition['files'][0]
    assert f['name'] == 'test_file1.csv'
    assert f['classification'] == {
        'Custom': ['foobar']
    }
    assert 'measurements' not in f

    f = r_acquisition['files'][1]
    assert f['name'] == 'test_file2.csv'
    assert f['classification'] == {
        'Intent': ['Functional'],
        'Measurement': ['T2'],
        'Custom': ['myvalue']
    }
    assert 'measurements' not in f

    # Clean up modality
    r = as_admin.delete('/modalities/MR')
    assert r.ok
