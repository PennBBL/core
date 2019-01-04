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
    api_db.project_rules.delete_many({'alg': 'dcm2niix'})
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

def test_52(data_builder, api_db, as_admin, file_form, database, default_payload):
    # Create a valid gear
    gear_doc = default_payload['gear']
    gear_doc['gear']['name'] = 'test-52-upgrade-gear'
    gear_doc['category'] = 'analysis'
    gear_id = api_db.gears.insert_one(gear_doc).inserted_id
    assert gear_id

    # Create project
    session = data_builder.create_session()

    # Create job with existing gear
    job_data = {
        'gear_id': str(gear_id),
        'inputs': {},
        'config': { 'two-digit multiple of ten': 20 },
    }

    job1_id = api_db.jobs.insert_one(job_data).inserted_id
    if '_id' in job_data:
        del job_data['_id']
    assert job1_id

    # Create analysis
    analysis_id = api_db.analyses.insert_one({
        'job': str(job1_id),
        'inputs': []
    }).inserted_id
    assert analysis_id

    # Create job with invalid gear id
    job_data['gear_id'] = '000000000000000000000000'
    job2_id = api_db.jobs.insert_one(job_data).inserted_id
    assert job2_id

    # Perform the upgrade
    database.upgrade_to_52()

    job1 = api_db.jobs.find_one({'_id': job1_id})
    gear_info = job1['gear_info']
    assert gear_info['name'] == 'test-52-upgrade-gear'
    assert gear_info['version'] == '0.0.1'
    assert gear_info['category'] == 'analysis'

    job2 = api_db.jobs.find_one({'_id': job2_id})
    assert 'gear_info' not in job2

    analysis = api_db.analyses.find_one({'_id': analysis_id})
    gear_info = analysis['gear_info']
    assert gear_info['id'] == str(gear_id)
    assert gear_info['name'] == 'test-52-upgrade-gear'
    assert gear_info['version'] == '0.0.1'
    assert gear_info['category'] == 'analysis'

    api_db.gears.delete_one({'_id': gear_id})
    api_db.analyses.delete_one({'_id': analysis_id})
    api_db.jobs.delete_one({'_id': job1_id})
    api_db.jobs.delete_one({'_id': job2_id})

def test_53(randstr, default_payload, as_root, api_db, database):
    # Create gear with multiple versions
    gear_name = randstr()
    gear_payload = default_payload['gear']
    gear_payload['gear']['name'] = gear_name
    gear_payload['gear']['version'] = '0.0.1'
    r = as_root.post('/gears/' + gear_name, json=gear_payload)
    assert r.ok
    gear_id_1 = r.json()['_id']

    gear_payload['gear']['version'] = '0.0.2'
    r = as_root.post('/gears/' + gear_name, json=gear_payload)
    assert r.ok
    gear_id_2 = r.json()['_id']

    # Create old-style rule ('alg' instead of 'gear_id')
    rule_id = bson.ObjectId()
    api_db.project_rules.insert_one({
        '_id': rule_id,
        'alg': gear_name,
        'project_id': 'site',
        'any': [],
        'all': [],
    })

    # Verify that upgrade switches to gear_id_2
    database.upgrade_to_53()
    rule = api_db.project_rules.find_one({'_id': rule_id})
    assert 'alg' not in rule
    assert 'gear_id' in rule
    assert rule['gear_id'] == gear_id_2

def test_54(randstr, api_db, database):
    # Create hierarchy
    group = 'g1'
    api_db.groups.insert_one({'_id': group})
    project_1 = bson.ObjectId()
    api_db.projects.insert_one({'_id': project_1, 'group': group})
    project_2 = bson.ObjectId()
    api_db.projects.insert_one({'_id': project_2, 'group': group})
    session_1 = bson.ObjectId()
    api_db.sessions.insert_one({'_id': session_1, 'project': project_1, 'group': group})
    session_2 = bson.ObjectId()
    api_db.sessions.insert_one({'_id': session_2, 'project': project_2, 'group': group})
    acquisition = bson.ObjectId()
    api_db.acquisitions.insert_one({'_id': acquisition, 'session': session_1})
    analysis = bson.ObjectId()
    api_db.analyses.insert_one({'_id': analysis, 'parent': {'type': 'session', 'id': session_2}})

    # Create Apikey, also make sure other apikeys follow old schema
    cursor = api_db.apikeys.find({})
    for key in cursor:
        api_db.apikeys.update_one({'_id': key['_id']}, {'$set': {'uid': key['origin']['id']}, '$unset': {'origin': ""}})
    apikey = bson.ObjectId()
    api_db.apikeys.insert_one({'_id': apikey, 'uid': 'Me@some.com', 'type': 'user'})

    database.upgrade_to_54()

    project_1_parents = api_db.projects.find_one({'_id': project_1})['parents']
    project_2_parents = api_db.projects.find_one({'_id': project_2})['parents']
    session_1_parents = api_db.sessions.find_one({'_id': session_1})['parents']
    session_2_parents = api_db.sessions.find_one({'_id': session_2})['parents']
    acquisition_parents = api_db.acquisitions.find_one({'_id': acquisition})['parents']
    analysis_parents = api_db.analyses.find_one({'_id': analysis})['parents']
    apikey_origin = api_db.apikeys.find_one({'_id': apikey})['origin']

    assert project_1_parents['group'] == group
    assert project_2_parents['group'] == group
    assert session_1_parents['group'] == group
    assert session_2_parents['group'] == group
    assert acquisition_parents['group'] == group
    assert analysis_parents['group'] == group

    assert session_1_parents['project'] == project_1
    assert session_2_parents['project'] == project_2
    assert acquisition_parents['project'] == project_1
    assert analysis_parents['project'] == project_2

    assert acquisition_parents['session'] == session_1
    assert analysis_parents['session'] == session_2

    assert apikey_origin['id'] == 'Me@some.com'
    assert apikey_origin['type'] == 'user'

    api_db.groups.delete_one({'_id': group})
    api_db.projects.delete_one({'_id': project_1})
    api_db.projects.delete_one({'_id': project_2})
    api_db.sessions.delete_one({'_id': session_1})
    api_db.sessions.delete_one({'_id': session_2})
    api_db.acquisitions.delete_one({'_id': acquisition})
    api_db.analyses.delete_one({'_id': analysis})
    api_db.apikeys.delete_one({'_id': apikey})


def test_55(api_db, data_builder, database):
    """Test subject collection pullout upgrade."""
    group = data_builder.create_group()
    project = bson.ObjectId(data_builder.create_project())
    now = datetime.datetime.utcnow()
    sessions = []
    def create_session(subject_doc):
        subject_doc.setdefault('_id', bson.ObjectId())
        session = bson.ObjectId()
        sessions.append(session)
        now_ = now + datetime.timedelta(seconds=len(sessions))
        api_db.sessions.insert_one({
            '_id': session,
            'group': group,
            'project': project,
            'parents': {'group': group,
                        'project': project},
            'subject': subject_doc,
            'created': now_,
            'modified': now_,
            'permissions': [{'_id': 'admin@user.com', 'access': 'admin'}],
            'public': True,
        })
        return session

    # missing code (expect separate subjects, regardless of id match)
    missing_subject = create_session({})
    missing_subject_code_1 = create_session({'code': ''})
    missing_subject_code_2 = create_session({'code': None})
    missing_subject_code_id = bson.ObjectId()
    missing_subject_code_3 = create_session({'_id': missing_subject_code_id})
    missing_subject_code_4 = create_session({'_id': missing_subject_code_id})

    # same proj/code, different id (expect merge)
    different_subject_id_1 = create_session({'code': 'id-mismatch', '_id': bson.ObjectId()})
    different_subject_id_2 = create_session({'code': 'id-mismatch', '_id': bson.ObjectId()})

    # same proj/code, same id (expect merge, keep id)
    matching_subject_id = bson.ObjectId()
    matching_subject_id_1 = create_session({'code': 'id-match', '_id': matching_subject_id})
    matching_subject_id_2 = create_session({'code': 'id-match', '_id': matching_subject_id})

    # test that age is moved to session
    test_age = create_session({'age': 123})

    # test merge of subject fields
    create_session({'code': 'merge'})
    session_bob_id = create_session({'code': 'merge', 'key': 'value1', 'firstname': 'Bob'})  # session.info.subject_raw.key: value1, firstname: Bob, session.info.subject_raw.firstname: Bob
    create_session({'code': 'merge', 'key': 'value1', 'firstname': 'Bob'})  # noop
    create_session({'code': 'merge', 'key': 'value2'})  # key: value2, session.info.subject_raw.key = value2
    session_mary_id = create_session({'code': 'merge', 'key': 'value2', 'firstname': 'Mary'})  # firstname: Mary, , session.info.subject_raw.firstname: Mary
    create_session({'code': 'merge'})                   # noop
    create_session({'code': 'merge', 'key': None})      # noop
    create_session({'code': 'merge', 'key': ''})        # noop
    # test on the most recently created session
    test_merge = create_session({'code': 'merge', 'key': 'value3'})  # key: value3, session.info.subject_raw.key: value3

    # test merge of deep subject fields (eg. info, expect same behavior as above)
    create_session({'code': 'deep-merge'})
    create_session({'code': 'deep-merge', 'info': {'key': 'value1'}})  # info.key: value1
    create_session({'code': 'deep-merge', 'info': {'key': 'value1'}})  # noop
    create_session({'code': 'deep-merge', 'info': {'key': 'value2'}})  # info.key: value2, info.key_history: ['value1']
    create_session({'code': 'deep-merge'})                             # noop
    create_session({'code': 'deep-merge', 'info': {'key': None}})      # noop
    create_session({'code': 'deep-merge', 'info': {'key': ''}})        # noop
    # test on the most recently created session
    test_deep_merge = create_session({'code': 'deep-merge', 'info': {'key': 'value3'}})  # info.key: value3, info.key_history: ['value1', 'value2']

    # test both at the same time
    create_session({'code': 'multi-merge'})
    value1_session_id = create_session({'code': 'multi-merge', 'info': {'key': 'value1'}})                  # info.key: value1
    create_session({'code': 'multi-merge', 'top_key': 'value1'})                        # top_key: value1, info.key: value1
    value2_session_id = create_session({'code': 'multi-merge', 'info': {'key': 'value2'}, 'top_key': 'value2'}) # top_key: value2, info.top_key: [value1], info.key: value2, info.key_history: ['value1']
    create_session({'code': 'multi-merge'})                                             # noop
    create_session({'code': 'multi-merge', 'top_key': None })                           # noop
    create_session({'code': 'multi-merge', 'top_key': 'value3'})                        # top_key: value3, info.top_key: [value1, value2], info.key: value2, info.key_history: ['value1']
    # test on the most recently created session
    test_multi_merge = create_session({'code': 'multi-merge', 'info': {'key': 'value3'}})  # top_key: value3, info.top_key: [value1, value2], info.key: value3, info.key_history: ['value1', 'value2']

    database.upgrade_to_55()

    def get_subject(session_id):
        session = api_db.sessions.find_one({'_id': session_id})
        return api_db.subjects.find_one({'_id': session['subject']})

    # verify that migrated subjects have, project, permissions, created, modified & parents
    subject = get_subject(missing_subject)
    assert subject['project'] == project
    assert subject['permissions'] == [{'_id': 'admin@user.com', 'access': 'admin'}]
    assert subject['created'] == min(s['created'] for s in api_db.sessions.find({'subject': subject['_id']}))
    assert subject['modified'] == max(s['modified'] for s in api_db.sessions.find({'subject': subject['_id']}))
    assert subject['parents'] == {'group': group, 'project': project}

    # verify separate subjects were created for those w/o code (no 2 [i,j] have the same id)
    separate_subjects = [missing_subject, missing_subject_code_1, missing_subject_code_2, missing_subject_code_3, missing_subject_code_4]
    for i, session_i in enumerate(separate_subjects):
        subject_i = get_subject(session_i)
        for j, session_j in enumerate(separate_subjects[i + 1:]):
            assert subject_i['_id'] != get_subject(session_j)['_id']

    # verify subjects were merged on proj/code match
    assert get_subject(different_subject_id_1)['_id'] == get_subject(different_subject_id_2)['_id']
    assert get_subject(matching_subject_id_1)['_id'] == get_subject(matching_subject_id_2)['_id'] == matching_subject_id

    # verify subject.age is moved to session.age
    assert api_db.sessions.find_one({'_id': test_age}).get('age') == 123

    # verify merging works as expected
    merge_subject = get_subject(test_merge)

    assert merge_subject['key'] == 'value3'
    assert merge_subject['firstname'] == 'Mary'


    # Verify important subject info is kept at session level
    session_bob = api_db.sessions.find_one({'_id': session_bob_id})
    assert session_bob['info']['subject_raw']['firstname'] == 'Bob'
    session_mary = api_db.sessions.find_one({'_id': session_mary_id})
    assert session_mary['info']['subject_raw']['firstname'] == 'Mary'


    # verify merging works in nested docs like info
    deep_merge_subject = get_subject(test_deep_merge)
    assert deep_merge_subject['info']['key'] == 'value3'  # Not a protected EM4
                                                          # key so it isn't saved at the session level

    key_values = set(['value1', 'value2', 'value3', ''])
    deep_merge_sessions = api_db.sessions.find({'subject': bson.ObjectId(deep_merge_subject['_id'])})
    deep_merge_sessions_with_value = [s for s in deep_merge_sessions if s.get('info',{}).get('subject_raw', {}).get('info', {}).get('key') is not None]
    assert set([s['info']['subject_raw'].get('info', {}).get('key') for s in deep_merge_sessions_with_value]) == key_values

    # verify merging works in both nested and unnested
    multi_merge_subject = get_subject(test_multi_merge)
    value1_session = api_db.sessions.find_one({'_id': value1_session_id})
    value2_session = api_db.sessions.find_one({'_id': value2_session_id})
    value3_session = api_db.sessions.find_one({'_id': test_multi_merge})
    assert multi_merge_subject['top_key'] == 'value3'
    assert value3_session['info']['subject_raw']['info']['key'] == 'value3'
    assert value2_session['info']['subject_raw']['info']['key'] == 'value2'
    assert value1_session['info']['subject_raw']['info']['key'] == 'value1'
    assert multi_merge_subject['info']['key'] == 'value3'

    data_builder.delete_group(group, recursive=True)


def test_57(randstr, api_db, database, data_builder):
    # Create hierarchy
    group_id = data_builder.create_group()
    project_id = data_builder.create_project()
    subject_id = bson.ObjectId()
    subject = {'_id': subject_id, 'project': bson.ObjectId(project_id), 'code': 'Subject_1'}
    api_db.subjects.insert_one(subject)
    session_id = bson.ObjectId()
    api_db.sessions.insert_one({'_id': session_id, 'subject': subject_id, 'project': bson.ObjectId(project_id),
                                'parents': {}})
    acquisition_id = bson.ObjectId()
    api_db.acquisitions.insert_one({'session': session_id, '_id': acquisition_id,
                                    'parents': {'session': session_id}})

    assert api_db.sessions.find_one({'_id': session_id})

    assert api_db.sessions.find_one({'_id': session_id})['parents'] == {}
    assert api_db.acquisitions.find_one({'_id': acquisition_id})['parents'] == {'session': session_id}

    database.upgrade_to_57()

    subject_parents = api_db.subjects.find_one({'_id': subject_id})['parents']
    session_parents = api_db.sessions.find_one({'_id': session_id})['parents']
    acquisition_parents = api_db.acquisitions.find_one({'_id': acquisition_id})['parents']

    assert subject_parents['group'] == group_id
    assert session_parents['group'] == group_id
    assert acquisition_parents['group'] == group_id

    assert subject_parents['project'] == bson.ObjectId(project_id)
    assert session_parents['project'] == bson.ObjectId(project_id)
    assert acquisition_parents['project'] == bson.ObjectId(project_id)

    assert acquisition_parents['session'] == session_id

    api_db.subjects.delete_one({'_id': subject_id})
    api_db.sessions.delete_one({'_id': session_id})
    api_db.acquisitions.delete_one({'_id': acquisition_id})


def test_58(api_db, database, data_builder, as_admin, file_form):
    acquisition = data_builder.create_acquisition()
    r = as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('test_file1.csv'))
    assert r.ok
    r = as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('test_file2.csv'))
    assert r.ok
    r = as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('test_file3.csv'))
    assert r.ok

    r = as_admin.post('/acquisitions/' + acquisition + '/files/test_file1.csv/classification', json={
        'modality': '',
        'replace': {
            'Custom': ['Random']
        }
    })
    assert r.ok
    r = as_admin.post('/acquisitions/' + acquisition + '/files/test_file2.csv/classification', json={
        'modality': 'MR',
        'replace': {
            'Custom': ['PET']
        }
    })
    assert r.ok
    r = as_admin.post('/acquisitions/' + acquisition + '/files/test_file3.csv/classification', json={
        'modality': '',
        'replace': {
            'Custom': ['PET']
        }
    })
    assert r.ok

    database.upgrade_to_58()

    r = as_admin.get('/acquisitions/' + acquisition)
    assert r.ok
    files = r.json()['files']

    assert files[0]['name'] == 'test_file1.csv'
    assert files[0]['modality'] == ''
    assert files[0]['classification'] == {'Custom': ['Random']}

    assert files[1]['name'] == 'test_file2.csv'
    assert files[1]['modality'] == 'MR'
    assert files[1]['classification'] == {'Custom': ['PET']}

    assert files[2]['name'] == 'test_file3.csv'
    assert files[2]['modality'] == 'PET'
    assert files[2]['classification'] == {'Custom': ['PET']}


def test_60(api_db, data_builder, database):
    """Test subject collection pullout upgrade."""
    group = data_builder.create_group()
    project = bson.ObjectId(data_builder.create_project())
    now = datetime.datetime.utcnow()
    sessions = []
    def create_session(subject_doc, deleted=False):
        subject_doc.setdefault('_id', bson.ObjectId())
        session = bson.ObjectId()
        sessions.append(session)
        now_ = now + datetime.timedelta(seconds=len(sessions))
        session_obj = {
            '_id': session,
            'group': group,
            'project': project,
            'parents': {'group': group,
                        'project': project},
            'subject': subject_doc,
            'created': now_,
            'modified': now_,
            'permissions': [{'_id': 'admin@user.com', 'access': 'admin'}],
            'public': True,
        }
        if deleted:
            session_obj['deleted'] = now_
        api_db.sessions.insert_one(session_obj)
        return session

    # Create the sessions
    not_deleted = create_session({'code': 'not deleted', 'firstname': 'Person 1'})
    half_deleted_id = bson.ObjectId()
    not_half_deleted = create_session({'code': 'half deleted', '_id': half_deleted_id, 'firstname': 'Person 2'})
    half_deleted = create_session({'code': 'half deleted', '_id': half_deleted_id, 'firstname': 'Person 3'}, deleted=True)
    full_deleted = create_session({'code': 'deleted', 'firstname': 'Person 4'}, deleted=True)

    # Test subject id mismatch
    subject_same_id = bson.ObjectId()
    same_id = create_session({'code': 'code A', '_id': subject_same_id, 'firstname': 'Person 3'}, deleted=False)
    same_id_2 = create_session({'code': 'code A2', '_id': subject_same_id, 'firstname': 'Person 3'}, deleted=False)
    same_id_deleted = create_session({'code': 'code B', '_id': subject_same_id, 'firstname': 'Person 3'}, deleted=True)

    codeless_id = bson.ObjectId()
    codeless = create_session({'code': '', '_id': subject_same_id, 'firstname': 'Person 5'}, deleted=False)
    codeless_2 = create_session({'code': '', '_id': subject_same_id, 'firstname': 'Person 6'}, deleted=False)
    codeless_deleted = create_session({'code': '', '_id': subject_same_id, 'firstname': 'Person 7'}, deleted=True)

    database.upgrade_to_55()

    def get_subject(session_id):
        session = api_db.sessions.find_one({'_id': session_id})
        return api_db.subjects.find_one({'_id': session['subject']})

    # verify that upgrade 55 did what is expected
    not_deleted_subject = get_subject(not_deleted)
    print not_deleted_subject
    assert not_deleted_subject['project'] == project
    assert not_deleted_subject['permissions'] == [{'_id': 'admin@user.com', 'access': 'admin'}]
    assert not not_deleted_subject.get('created')
    assert not not_deleted_subject.get('modified')
    assert not_deleted_subject['firstname'] == 'Person 1'

    not_half_deleted_subject = get_subject(not_half_deleted)
    assert not_half_deleted_subject['firstname'] == 'Person 2'

    session = api_db.sessions.find_one({'_id': half_deleted})
    half_deleted_subject = api_db.subjects.find_one({'_id': session['subject']['_id']})
    assert half_deleted_subject['firstname'] == 'Person 2' # Not Person 3

    session = api_db.sessions.find_one({'_id': full_deleted})
    full_deleted_subject = api_db.subjects.find_one({'_id': session['subject']['_id']})
    assert not full_deleted_subject

    session = api_db.sessions.find_one({'_id': same_id})
    same_id_subject = api_db.subjects.find_one({'_id': session['subject']})
    assert same_id_subject
    assert same_id_subject['code'] == 'code A'

    database.upgrade_to_60()

    not_deleted_subject = get_subject(not_deleted)
    assert not_deleted_subject['project'] == project
    assert not_deleted_subject['permissions'] == [{'_id': 'admin@user.com', 'access': 'admin'}]
    assert not_deleted_subject['created'] == min([s['created'] for s in api_db.sessions.find({'subject': not_deleted_subject['_id']})] +
                                                 [not_deleted_subject['_id'].generation_time.replace(tzinfo=None)])
    assert not_deleted_subject['modified'] == max([s['modified'] for s in api_db.sessions.find({'subject': not_deleted_subject['_id']})] +
                                                  [not_deleted_subject['_id'].generation_time.replace(tzinfo=None)])
    assert not_deleted_subject['firstname'] == 'Person 1'

    not_half_deleted_subject = get_subject(not_half_deleted)
    assert not_half_deleted_subject['firstname'] == 'Person 2'
    assert half_deleted_subject['code'] == 'half deleted'

    half_deleted_subject = get_subject(half_deleted)
    assert half_deleted_subject['firstname'] == 'Person 3'
    assert half_deleted_subject['code'] == 'half deleted-deleted'

    full_deleted_subject = get_subject(full_deleted)
    assert full_deleted_subject['firstname'] == 'Person 4'

    session = api_db.sessions.find_one({'_id': same_id})
    same_id_subject = api_db.subjects.find_one({'_id': session['subject']})
    assert same_id_subject
    assert same_id_subject['code'] == 'code A'

    session = api_db.sessions.find_one({'_id': same_id_deleted})
    same_id_deleted_subject = api_db.subjects.find_one({'_id': session['subject']})
    assert same_id_deleted_subject
    assert same_id_deleted_subject['code'] == 'code B'

    session = api_db.sessions.find_one({'_id': codeless})
    codeless_subject = api_db.subjects.find_one({'_id': session['subject']})
    assert codeless_subject
    assert codeless_subject['firstname'] == 'Person 5'

    session = api_db.sessions.find_one({'_id': codeless_deleted})
    codeless_deleted_subject = api_db.subjects.find_one({'_id': session['subject']})
    assert codeless_deleted_subject
    assert codeless_deleted_subject['firstname'] == 'Person 7'

    data_builder.delete_group(group, recursive=True)

def test_62(api_db, data_builder, database, default_payload, as_admin, file_form):
    # Create a valid gear
    gear_doc = default_payload['gear']
    gear_doc['gear']['name'] = 'test-62-upgrade-gear'
    gear_doc['category'] = 'utility'
    gear_id = api_db.gears.insert_one(gear_doc).inserted_id
    assert gear_id

    # Create hierarchy
    group = data_builder.create_group()
    project = data_builder.create_project(group=group)
    subject = data_builder.create_subject(project=project, label='1000')
    session = data_builder.create_session(project=project, subject={'_id': subject})
    acquisition = data_builder.create_acquisition(session=session)

    dest_containers = [group, project, subject, session]
    input_containers = dest_containers + [acquisition]

    r = as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('input.txt'))
    assert r.ok

    # Ensure that indexes get deleted
    api_db.jobs.create_index('group')
    api_db.jobs.create_index('project')

    # Valid job document
    job_src = {
        'gear_id': str(gear_id),
        'inputs': [{
            'input': 'text',
            'type': 'acquisition',
            'id': acquisition,
            'name': 'input.txt'
        }],
        'destination': {
            'type': 'session',
            'id': session
        }
    }

    # Job with empty destination
    job_data = copy.deepcopy(job_src)
    del job_data['destination']
    job_empty_dest = api_db.jobs.insert_one(job_data).inserted_id

    # Job with non-existent destination
    job_data = copy.deepcopy(job_src)
    job_data['destination']['id'] = 'ffffffffffffffffffffffff'
    job_invalid_dest = api_db.jobs.insert_one(job_data).inserted_id

    # Job with empty inputs
    job_data = copy.deepcopy(job_src)
    job_data['inputs'] = []
    job_empty_input = api_db.jobs.insert_one(job_data).inserted_id

    # Job with non-existent input
    job_data = copy.deepcopy(job_src)
    job_data['inputs'][0]['id'] = 'ffffffffffffffffffffffff'
    job_invalid_input = api_db.jobs.insert_one(job_data).inserted_id

    # Valid job with inputs & destination
    job_data = copy.deepcopy(job_src)
    job_valid = api_db.jobs.insert_one(job_data).inserted_id

    try:
        database.upgrade_to_62()

        # Validate empty destination
        job_data = api_db.jobs.find_one({'_id': job_empty_dest})
        assert 'parents' not in job_data
        for cid in input_containers:
            assert cid in job_data['related_container_ids']

        # Job with non-existent destination
        job_data = api_db.jobs.find_one({'_id': job_invalid_dest})
        assert 'parents' not in job_data
        for cid in input_containers:
            assert cid in job_data['related_container_ids']

        # Job with empty inputs
        job_data = api_db.jobs.find_one({'_id': job_empty_input})
        assert job_data['parents']['group'] == group
        assert job_data['parents']['project'] == bson.ObjectId(project)
        assert job_data['parents']['subject'] == bson.ObjectId(subject)
        assert job_data['parents']['session'] == bson.ObjectId(session)
        for cid in dest_containers:
            assert cid in job_data['related_container_ids']

        # Job with non-existent input
        job_data = api_db.jobs.find_one({'_id': job_invalid_input})
        assert job_data['parents']['group'] == group
        assert job_data['parents']['project'] == bson.ObjectId(project)
        assert job_data['parents']['subject'] == bson.ObjectId(subject)
        assert job_data['parents']['session'] == bson.ObjectId(session)
        for cid in dest_containers:
            assert cid in job_data['related_container_ids']

        # Valid job with inputs & destination
        job_data = api_db.jobs.find_one({'_id': job_valid})
        assert job_data['parents']['group'] == group
        assert job_data['parents']['project'] == bson.ObjectId(project)
        assert job_data['parents']['subject'] == bson.ObjectId(subject)
        assert job_data['parents']['session'] == bson.ObjectId(session)
        for cid in input_containers:
            assert cid in job_data['related_container_ids']

        # Validate that indexes are deleted
        for _, index in api_db.jobs.index_information().items():
            assert ('group', 1) not in index['key']
            assert ('project', 1) not in index['key']

    finally:
        api_db.jobs.delete_many({'_id': {'$in': [
            job_empty_dest, job_invalid_dest, job_empty_input, job_invalid_input, job_valid]}})

def test_63(api_db, database):
    api_db.users.insert({'_id': 'user1', 'firstname': 'upgrade_test', 'root': False})
    api_db.users.insert({'_id': 'user2', 'firstname': 'upgrade_test', 'root': True})
    api_db.users.insert({'_id': 'user3', 'firstname': 'upgrade_test'})

    database.upgrade_to_63()

    assert api_db.users.find_one({'_id': 'user1'}).get('roles') == ['user']
    assert set(api_db.users.find_one({'_id': 'user2'}).get('roles')) == set(['developer', 'site-admin'])
    assert api_db.users.find_one({'_id': 'user3'}).get('roles') == ['user']

    api_db.users.delete_many({'firstname': 'upgrade_test'})
