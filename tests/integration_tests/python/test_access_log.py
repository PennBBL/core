import time
import pytest

from api.web.request import AccessType

from api.access_log import create_entry, bulk_log_access

class MockRequest:
    def __init__(self, method, path):
        self.method = method
        self.path = path
        self.client_addr = '127.0.0.1'


# NOTE these tests assume they are not running in parallel w/ other tests
# by relying on the last entry in the logs

def test_access_log_succeeds(data_builder, as_admin, log_db):
    project = data_builder.create_project()
    session = data_builder.create_session()
    acquisition = data_builder.create_acquisition()
    file_name = 'one.csv'

    ###
    # Test login action is logged
    ###

    api_key = as_admin.get('/users/self').json()['api_key']['key']

    log_records_count_before = log_db.access_log.count({})

    r = as_admin.post('/login', json={
        'auth_type': 'api-key',
        'code': api_key
    })
    assert r.ok
    admin_id = as_admin.get('/users/self').json()['_id']
    log_records_count_after = log_db.access_log.count({})
    assert log_records_count_before+1 == log_records_count_after

    most_recent_log = log_db.access_log.find({}).sort([('_id', -1)]).limit(1)[0]
    assert most_recent_log['access_type'] == AccessType.user_login.value
    assert str(most_recent_log['origin']['id']) == admin_id


    ###
    # Test logout action is logged
    ###

    log_records_count_before = log_db.access_log.count({})

    r = as_admin.post('/logout')
    assert r.ok

    log_records_count_after = log_db.access_log.count({})
    assert log_records_count_before+1 == log_records_count_after

    most_recent_log = log_db.access_log.find({}).sort([('_id', -1)]).limit(1)[0]
    assert most_recent_log['access_type'] == AccessType.user_logout.value
    assert str(most_recent_log['origin']['id']) == admin_id


    ###
    # Test project access is logged
    ###

    log_records_count_before = log_db.access_log.count({})

    r = as_admin.get('/projects/' + project)
    assert r.ok

    log_records_count_after = log_db.access_log.count({})
    assert log_records_count_before+1 == log_records_count_after

    most_recent_log = log_db.access_log.find({}).sort([('_id', -1)]).limit(1)[0]

    assert most_recent_log['context']['project']['id'] == project
    assert most_recent_log['access_type'] == AccessType.view_container.value
    assert str(most_recent_log['origin']['id']) == admin_id


    ###
    # Test session access is logged
    ###

    log_records_count_before = log_db.access_log.count({})

    r = as_admin.get('/sessions/' + session)
    assert r.ok

    log_records_count_after = log_db.access_log.count({})
    assert log_records_count_before+1 == log_records_count_after

    most_recent_log = log_db.access_log.find({}).sort([('_id', -1)]).limit(1)[0]

    assert most_recent_log['context']['session']['id'] == session
    assert most_recent_log['access_type'] == AccessType.view_container.value
    assert str(most_recent_log['origin']['id']) == admin_id


    ###
    # Test acquisition access is logged
    ###

    log_records_count_before = log_db.access_log.count({})

    r = as_admin.get('/acquisitions/' + acquisition)
    assert r.ok

    log_records_count_after = log_db.access_log.count({})
    assert log_records_count_before+1 == log_records_count_after

    most_recent_log = log_db.access_log.find({}).sort([('_id', -1)]).limit(1)[0]

    assert most_recent_log['context']['acquisition']['id'] == acquisition
    assert most_recent_log['access_type'] == AccessType.view_container.value
    assert str(most_recent_log['origin']['id']) == admin_id


    ###
    # Add subject info
    ###

    subject_code = 'Test subject code'
    r = as_admin.put('/sessions/' + session, json={
        'subject': {'code': subject_code}}
    )
    assert r.ok


    ###
    # Test subject access is logged
    ###

    log_records_count_before = log_db.access_log.count({})

    r = as_admin.get('/sessions/' + session + '/subject')
    assert r.ok
    subject = r.json()['_id']

    log_records_count_after = log_db.access_log.count({})
    assert log_records_count_before+1 == log_records_count_after

    most_recent_log = log_db.access_log.find({}).sort([('_id', -1)]).limit(1)[0]

    assert most_recent_log['context']['session']['id'] == session
    assert most_recent_log['context']['subject']['label'] == subject_code
    assert most_recent_log['access_type'] == AccessType.view_subject.value
    assert str(most_recent_log['origin']['id']) == admin_id


    ###
    # Test subject access is logged on new subject route
    ###

    log_records_count_before = log_db.access_log.count({})

    r = as_admin.get('/subjects/' + subject)
    assert r.ok

    log_records_count_after = log_db.access_log.count({})
    assert log_records_count_before+1 == log_records_count_after

    most_recent_log = log_db.access_log.find({}).sort([('_id', -1)]).limit(1)[0]

    assert most_recent_log['context']['subject']['label'] == subject_code
    assert most_recent_log['access_type'] == AccessType.view_subject.value
    assert most_recent_log['origin']['id'] == admin_id


    # Upload files
    r = as_admin.post('/projects/' + project + '/files', files={
        'file': (file_name, 'test-content')
    })
    assert r.ok


    ###
    # Test file download is logged
    ###

    log_records_count_before = log_db.access_log.count({})

    r = as_admin.get('/projects/' + project + '/files/' + file_name)
    assert r.ok

    file_ = r.raw.read(10)
    time.sleep(1)

    log_records_count_after = log_db.access_log.count({})
    assert log_records_count_before+1 == log_records_count_after

    most_recent_log = log_db.access_log.find({}).sort([('_id', -1)]).limit(1)[0]

    assert most_recent_log['context']['project']['id'] == project
    assert most_recent_log['context']['file']['name'] == file_name
    assert most_recent_log['access_type'] == AccessType.download_file.value
    assert str(most_recent_log['origin']['id']) == admin_id


    ###
    # Test file ticket download is logged once
    ###

    log_records_count_before = log_db.access_log.count({})

    r = as_admin.get('/projects/' + project + '/files/' + file_name, params={'ticket': ''})
    assert r.ok

    ticket_id = r.json()['ticket']

    r = as_admin.get('/projects/' + project + '/files/' + file_name, params={'ticket': ticket_id})
    assert r.ok

    file_ = r.raw.read(10)
    time.sleep(1)

    log_records_count_after = log_db.access_log.count({})
    assert log_records_count_before+1 == log_records_count_after

    most_recent_log = log_db.access_log.find({}).sort([('_id', -1)]).limit(1)[0]

    assert most_recent_log['context']['project']['id'] == project
    assert most_recent_log['context']['file']['name'] == file_name
    assert most_recent_log['context']['ticket_id'] == ticket_id
    assert most_recent_log['access_type'] == AccessType.download_file.value
    assert str(most_recent_log['origin']['id']) == admin_id


    # Upload another file
    r = as_admin.post('/sessions/' + session + '/files', files={
        'file': (file_name, 'test-content')
    })
    assert r.ok


    ###
    # Test container bulk download
    ###

    log_records_count_before = log_db.access_log.count({})
    r = as_admin.post('/download', json={'optional': True, 'nodes':[{'level': 'project', '_id': project}]})
    assert r.ok
    ticket_id = r.json()['ticket']
    file_count = r.json()['file_cnt']
    r = as_admin.get('/download', params={'ticket':ticket_id})
    assert r.ok

    log_records_count_after = log_db.access_log.count({})
    assert log_records_count_before + file_count == log_records_count_after

    most_recent_logs = log_db.access_log.find({}).sort([('_id', -1)]).limit(file_count)
    for l in most_recent_logs:
        assert l['context']['file']['name'] == file_name
        assert l['access_type'] == AccessType.download_file.value
        assert str(l['origin']['id']) == admin_id

    ###
    # Test search bulk download
    ###

    log_records_count_before = log_db.access_log.count({})
    r = as_admin.post('/download', params={'bulk':True},
                      json={"files":[{"container_name":"project","container_id":project,"filename":file_name},
                                     {"container_name":"session","container_id":session,"filename":file_name}]})
    assert r.ok
    ticket_id = r.json()['ticket']
    file_count = r.json()['file_cnt']
    r = as_admin.get('/download', params={'ticket':ticket_id})
    assert r.ok

    log_records_count_after = log_db.access_log.count({})
    assert log_records_count_before + file_count == log_records_count_after

    most_recent_logs = log_db.access_log.find({}).sort([('_id', -1)]).limit(file_count)
    for l in most_recent_logs:
        assert l['context']['file']['name'] == file_name
        assert l['access_type'] == AccessType.download_file.value
        assert str(l['origin']['id']) == admin_id


    ###
    # Test file info access is logged
    ###

    log_records_count_before = log_db.access_log.count({})

    r = as_admin.get('/projects/' + project + '/files/' + file_name + '/info')
    assert r.ok
    assert r.json()['name'] == file_name

    log_records_count_after = log_db.access_log.count({})
    assert log_records_count_before+1 == log_records_count_after

    most_recent_log = log_db.access_log.find({}).sort([('_id', -1)]).limit(1)[0]

    assert most_recent_log['context']['project']['id'] == project
    assert most_recent_log['context']['file']['name'] == file_name
    assert most_recent_log['access_type'] == AccessType.view_file.value
    assert str(most_recent_log['origin']['id']) == admin_id


    ###
    # Test file replacement is logged
    ###

    log_records_count_before = log_db.access_log.count({})

    # Replace existing file
    r = as_admin.post('/projects/' + project + '/files', files={
        'file': (file_name, 'different-content')
    })
    assert r.ok

    log_records_count_after = log_db.access_log.count({})
    assert log_records_count_before+1 == log_records_count_after

    most_recent_log = log_db.access_log.find({}).sort([('_id', -1)]).limit(1)[0]

    assert most_recent_log['context']['project']['id'] == project
    assert most_recent_log['context']['file']['name'] == file_name
    assert most_recent_log['access_type'] == AccessType.replace_file.value
    assert str(most_recent_log['origin']['id']) == admin_id


    ###
    # Test file delete is logged
    ###

    log_records_count_before = log_db.access_log.count({})

    r = as_admin.delete('/projects/' + project + '/files/' + file_name)
    assert r.ok

    log_records_count_after = log_db.access_log.count({})
    assert log_records_count_before+1 == log_records_count_after

    most_recent_log = log_db.access_log.find({}).sort([('_id', -1)]).limit(1)[0]

    assert most_recent_log['context']['project']['id'] == project
    assert most_recent_log['context']['file']['name'] == file_name
    assert most_recent_log['access_type'] == AccessType.delete_file.value
    assert str(most_recent_log['origin']['id']) == admin_id


    ###
    # Test acquisition delete is logged
    ###

    log_records_count_before = log_db.access_log.count({})

    r = as_admin.delete('/acquisitions/' + acquisition)
    assert r.ok

    log_records_count_after = log_db.access_log.count({})
    assert log_records_count_before+1 == log_records_count_after

    most_recent_log = log_db.access_log.find({}).sort([('_id', -1)]).limit(1)[0]

    assert most_recent_log['context']['acquisition']['id'] == acquisition
    assert most_recent_log['access_type'] == AccessType.delete_container.value
    assert str(most_recent_log['origin']['id']) == admin_id


    ###
    # Test session delete is logged
    ###

    log_records_count_before = log_db.access_log.count({})

    r = as_admin.delete('/sessions/' + session)
    assert r.ok

    log_records_count_after = log_db.access_log.count({})
    assert log_records_count_before+1 == log_records_count_after

    most_recent_log = log_db.access_log.find({}).sort([('_id', -1)]).limit(1)[0]

    assert most_recent_log['context']['session']['id'] == session
    assert most_recent_log['access_type'] == AccessType.delete_container.value
    assert str(most_recent_log['origin']['id']) == admin_id


    ###
    # Test project delete is logged
    ###

    log_records_count_before = log_db.access_log.count({})

    r = as_admin.delete('/projects/' + project)
    assert r.ok

    log_records_count_after = log_db.access_log.count({})
    assert log_records_count_before+1 == log_records_count_after

    most_recent_log = log_db.access_log.find({}).sort([('_id', -1)]).limit(1)[0]

    assert most_recent_log['context']['project']['id'] == project
    assert most_recent_log['access_type'] == AccessType.delete_container.value
    assert str(most_recent_log['origin']['id']) == admin_id



def test_access_log_fails(data_builder, as_admin, log_db):
    project = data_builder.create_project()
    file_name = 'one.csv'

    log_db.command('collMod', 'access_log', validator={'$and': [{'foo': {'$exists': True}}]}, validationLevel='strict')

    # Upload files
    r = as_admin.post('/projects/' + project + '/files', files={
        'file': (file_name, 'test-content')
    })
    assert r.ok

    ###
    # Test file delete request fails and does not delete file
    ###

    r = as_admin.delete('/projects/' + project + '/files/' + file_name)
    assert r.status_code == 500

    log_db.command('collMod', 'access_log', validator={}, validationLevel='strict')

    r = as_admin.get('/projects/' + project)
    assert r.ok
    assert r.json()['files']

def test_create_entry_validation():
    # Could be a unit test?
    req = MockRequest('GET', '/test')
    origin = { 'type': 'user', 'id': 'admin@user.com' }

    try:
        # Invalid access type
        create_entry(req, 'view_subject', origin, { 'group': { 'id': 'test' } })
        pytest.fail('Expected exception!')
    except Exception:
        pass

    try:
        # Missing context
        create_entry(req, AccessType.view_subject, origin, context=None)
        pytest.fail('Expected exception!')
    except Exception:
        pass

    try:
        # Missing file entry
        create_entry(req, AccessType.view_file, origin, context={ 'group': { 'id': 'test' }})
        pytest.fail('Expected exception!')
    except Exception:
        pass

    #Valid
    create_entry(req, AccessType.view_file, origin, context={ 'group': { 'id': 'test' }, 'file': {'name': 'test.txt'} })


def test_bulk_access(data_builder, as_admin, log_db):
    project = data_builder.create_project(label='Test Project')

    log_records_count_before = log_db.access_log.count({})

    admin_id = as_admin.get('/users/self').json()['_id']

    req = MockRequest('GET', '/test/bulk_log_access')
    origin = { 'type': 'user', 'id': admin_id }

    entries = [
        (AccessType.view_container, {
            'group': { 'id': 'test', 'label': 'Test Group' }
        }),
        (AccessType.view_file, {
            'group': { 'id': 'test', 'label': 'Test Group' },
            'project': { 'id': project, 'label': 'Test Project' },
            'file': { 'name': 'example.csv' }
        })
    ]

    bulk_log_access(req, origin, entries)

    log_records_count_after = log_db.access_log.count({})
    assert log_records_count_before+2 == log_records_count_after

    most_recent_logs = log_db.access_log.find({}).sort([('timestamp', -1)]).limit(2)

    from pprint import pprint
    pprint(most_recent_logs)
    if most_recent_logs[0]['access_type'] == 'view_file':
        log1 = most_recent_logs[1]
        log2 = most_recent_logs[0]
    else:
        log1 = most_recent_logs[0]
        log2 = most_recent_logs[1]

    assert log1['access_type'] == AccessType.view_container.value
    assert log1['origin']['id'] == admin_id
    assert log1['request_method'] == 'GET'
    assert log1['request_path'] == '/test/bulk_log_access'
    assert log1['context']['group']['id'] == 'test'

    assert log2['access_type'] == AccessType.view_file.value
    assert log2['origin']['id'] == admin_id
    assert log2['request_method'] == 'GET'
    assert log2['request_path'] == '/test/bulk_log_access'
    assert log2['context']['file']['name'] == 'example.csv'


