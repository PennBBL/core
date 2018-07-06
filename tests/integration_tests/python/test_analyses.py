import cStringIO
import os
import tarfile

import bson


def test_online_analysis(data_builder, as_admin, as_drone, file_form, api_db):
    gear = data_builder.create_gear(gear={'inputs': {'csv': {'base': 'file'}}})
    group = data_builder.create_group()
    project = data_builder.create_project()
    session = data_builder.create_session()
    acquisition = data_builder.create_acquisition()
    assert as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('input.csv')).ok

    # Try to create job-based analysis with invalid fileref
    r = as_admin.post('/sessions/' + session + '/analyses', json={
        'label': 'online',
        'job': {'gear_id': gear,
                'inputs': {'csv': {'type': 'acquisition', 'id': acquisition, 'name': 'nosuch.csv'}}}
    })
    assert r.status_code == 404

    # Try to create job-based analysis with invalid gear id
    r = as_admin.post('/sessions/' + session + '/analyses', json={
        'label': 'online',
        'job': {'gear_id': '000000000000000000000000',
                'inputs': {'csv': {'type': 'acquisition', 'id': acquisition, 'name': 'input.csv'}}}
    })
    assert r.status_code == 404

    # Try to create job-based analysis at group level
    r = as_admin.post('/groups/' + group + '/analyses', json={
        'label': 'online',
        'job': {'gear_id': gear,
                'inputs': {'csv': {'type': 'acquisition', 'id': acquisition, 'name': 'input.csv'}}}
    })
    # No endpoint to make group analyses but the handler/dao layer specifically allows it
    assert r.status_code == 404

    # Create analysis job at project level
    r = as_admin.post('/projects/' + project + '/analyses', json={
        'label': 'online',
        'job': {'gear_id': gear,
                'inputs': {'csv': {'type': 'acquisition', 'id': acquisition, 'name': 'input.csv'}}}
    })
    assert r.ok
    analysis = r.json()['_id']

    # Test that permission updates don't make it to analyses
    r = as_admin.post('/projects/' + project + '/permission', json={
        '_id': 'user@user.com',
        'access': 'ro'})

    # Verify job was created with it
    r = as_admin.get('/analyses/' + analysis)
    assert r.ok
    job = r.json().get('job')
    assert job
    assert not r.json().get('permissions')

    # Engine upload
    r = as_drone.post('/engine',
        params={'level': 'analysis', 'id': analysis, 'job': job},
        files=file_form('output.csv', meta={'type': 'tabular data'}))
    assert r.ok

    check_files(as_admin, analysis, 'files', 'output.csv')
    api_db.analyses.delete_one({'_id': bson.ObjectId(analysis)})

    # Create job-based analysis at acquisition level
    r = as_admin.post('/acquisitions/' + acquisition + '/analyses', json={
        'label': 'online',
        'job': {'gear_id': gear,
                'inputs': {'csv': {'type': 'acquisition', 'id': acquisition, 'name': 'input.csv'}}}
    })
    assert r.ok
    analysis = r.json()['_id']

    # Verify job was created with it
    r = as_admin.get('/analyses/' + analysis)
    assert r.ok
    job = r.json().get('job')
    assert job

    # Engine upload
    r = as_drone.post('/engine',
        params={'level': 'analysis', 'id': analysis, 'job': job},
        files=file_form('output.csv', meta={'type': 'tabular data'}))
    assert r.ok

    check_files(as_admin, analysis, 'files', 'output.csv')
    api_db.analyses.delete_one({'_id': bson.ObjectId(analysis)})

    # Create job-based analysis
    r = as_admin.post('/sessions/' + session + '/analyses', json={
        'label': 'online',
        'job': {'gear_id': gear,
                'inputs': {'csv': {'type': 'acquisition', 'id': acquisition, 'name': 'input.csv'}}}
    })
    assert r.ok
    analysis = r.json()['_id']

    # Verify job was created with it
    r = as_admin.get('/analyses/' + analysis)
    assert r.ok
    job = r.json().get('job')
    assert job

    # Verify that gear info was stored
    gear_info = r.json().get('gear_info')
    assert gear_info.get('id') == gear
    assert gear_info.get('name')
    assert gear_info.get('version') == '0.0.1'

    check_files(as_admin, analysis, 'inputs', 'input.csv')

    # Try manual upload - not allowed for job-based analysis
    r = as_admin.post('/analyses/' + analysis + '/files', files=file_form('output.csv'))
    assert r.status_code == 400

    # Engine upload
    r = as_drone.post('/engine',
        params={'level': 'analysis', 'id': analysis, 'job': job},
        files=file_form('output.csv', meta={'type': 'tabular data'}))
    assert r.ok

    check_files(as_admin, analysis, 'files', 'output.csv')

    # Force retry the job
    r = as_drone.get('/jobs/next')
    assert r.ok
    r = as_drone.get('/jobs/next')
    assert r.ok
    r = as_drone.get('/jobs/next')
    assert r.ok

    # set job to failed
    r = as_drone.put('/jobs/' + job, json={'state': 'failed'})
    assert r.ok

    r = as_admin.post('/jobs/' + job + '/retry', params={'ignoreState': True, 'root': True})
    assert r.ok
    retried_job_id = r.json()['_id']

    r = as_drone.get('/jobs/next')
    assert r.ok

    # Verify job was created with it
    r = as_admin.get('/analyses/' + analysis)
    assert r.ok
    print job
    assert r.json().get('job') == retried_job_id

    # Engine upload
    r = as_drone.post('/engine',
        params={'level': 'analysis', 'id': analysis, 'job': retried_job_id},
        files=file_form('output.csv', meta={'type': 'tabular data'}))
    assert r.ok
    check_files(as_admin, analysis, 'files', 'output.csv')

    # Verify job was created with it
    r = as_admin.get('/analyses/' + analysis)
    assert r.ok
    print job
    assert r.json().get('job') == retried_job_id

    r = as_admin.get('/jobs/' + retried_job_id)
    assert r.ok
    print r.json()['saved_files']
    assert r.json()['saved_files'] != []

    check_files(as_admin, analysis, 'files', 'output.csv')

    api_db.analyses.delete_one({'_id': bson.ObjectId(analysis)})


def test_offline_analysis(data_builder, as_admin, file_form, api_db):
    session = data_builder.create_session()
    acquisition = data_builder.create_acquisition()
    assert as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('input.csv')).ok

    # Try to create ad-hoc analysis with invalid fileref
    r = as_admin.post('/sessions/' + session + '/analyses', json={
        'label': 'offline',
        'inputs': [{'type': 'acquisition', 'id': acquisition, 'name': 'nosuch.csv'}]
    })
    assert r.status_code == 404

    # Try to create ad-hoc analysis with invalid session fileref
    r = as_admin.post('/sessions/' + session + '/analyses', json={
        'label': 'offline',
        'inputs': [{'type': 'session', 'id': session, 'name': 'input.csv'}]
    })
    assert r.status_code == 404

    # Create ad-hoc analysis
    r = as_admin.post('/sessions/' + session + '/analyses', json={
        'label': 'offline',
        'inputs': [{'type': 'acquisition', 'id': acquisition, 'name': 'input.csv'}]
    })
    assert r.ok
    analysis = r.json()['_id']

    check_files(as_admin, analysis, 'inputs', 'input.csv')

    # Manual upload
    r = as_admin.post('/analyses/' + analysis + '/files', files=file_form('output1.csv', 'output2.csv', meta=[
        {'name': 'output1.csv', 'info': {'foo': 'foo'}},
        {'name': 'output2.csv', 'info': {'bar': 'bar'}},
    ]))
    assert r.ok

    check_files(as_admin, analysis, 'files', 'output1.csv', 'output2.csv')

    # Verify that repeated uploads are rejected
    r = as_admin.post('/analyses/' + analysis + '/files', files=file_form('output3.csv', meta=[
        {'name': 'output3.csv', 'info': {'baz': 'baz'}},
    ]))
    assert r.status_code == 400

    api_db.analyses.delete_one({'_id': bson.ObjectId(analysis)})


def test_legacy_analysis(data_builder, as_admin, file_form, api_db):
    session = data_builder.create_session()

    # Create legacy analysis (upload both inputs and outputs in the same fileform)
    r = as_admin.post('/sessions/' + session + '/analyses', files=file_form('input.csv', 'output.csv', meta={
        'label': 'legacy',
        'inputs': [{'name': 'input.csv', 'info': {'foo': 'foo'}}],
        'outputs': [{'name': 'output.csv', 'info': {'bar': 'bar'}}],
    }))
    assert r.ok
    analysis = r.json()['_id']

    check_files(as_admin, analysis, 'inputs', 'input.csv')
    check_files(as_admin, analysis, 'files', 'output.csv')
    api_db.analyses.delete_one({'_id': bson.ObjectId(analysis)})


def test_analysis_download(data_builder, as_admin, as_root, file_form, api_db):
    project = data_builder.create_project()
    session = data_builder.create_session()

    # Create legacy analysis
    r = as_admin.post('/sessions/' + session + '/analyses', files=file_form('input.csv', 'output.csv', meta={
        'label': 'legacy',
        'inputs': [{'name': 'input.csv', 'info': {'foo': 'foo'}}],
        'outputs': [{'name': 'output.csv', 'info': {'bar': 'bar'}}],
    }))
    assert r.ok
    analysis = r.json()['_id']

    as_admin.post('/projects/' + project + '/permissions', json={'_id': 'user@user.com', 'access': 'admin'})

    # Get download ticket for analysis via /download
    r = as_admin.get('/download', params={'ticket': ''}, json={'optional': True, 'nodes': [{'level':'analysis','_id': analysis}]})
    assert r.ok
    ticket = r.json()['ticket']

    # Verify both inputs and outputs are present
    r = as_admin.get('/download', params={'ticket': ticket})
    assert r.ok
    with tarfile.open(mode='r', fileobj=cStringIO.StringIO(r.content)) as tar:
        assert set(m.name for m in tar.getmembers()) == set(['legacy/input/input.csv', 'legacy/output/output.csv'])

    # Test with root
    r = as_root.get('/download', params={'ticket': ''}, json={'optional': True, 'nodes': [{'level':'analysis','_id': analysis}]})
    assert r.ok
    ticket = r.json()['ticket']

    # Verify both inputs and outputs are present
    r = as_root.get('/download', params={'ticket': ticket})
    assert r.ok
    with tarfile.open(mode='r', fileobj=cStringIO.StringIO(r.content)) as tar:
        assert set(m.name for m in tar.getmembers()) == set(['legacy/input/input.csv', 'legacy/output/output.csv'])


def test_analysis_inflate_job(data_builder, file_form, as_admin):
    gear = data_builder.create_gear(gear={'inputs': {'csv': {'base': 'file'}}})
    session = data_builder.create_session()
    acquisition = data_builder.create_acquisition()
    assert as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('input.csv')).ok

    # Create job-based analysis
    r = as_admin.post('/sessions/' + session + '/analyses', json={
        'label': 'inflate',
        'job': {'gear_id': gear,
                'inputs': {'csv': {'type': 'acquisition', 'id': acquisition, 'name': 'input.csv'}}}
    })
    assert r.ok
    analysis = r.json()['_id']

    # Verify ?inflate_jobs=true works for one analysis
    r = as_admin.get('/analyses/' + analysis + '?inflate_job=true')
    assert r.ok
    assert 'id' in r.json().get('job', {})

    # Verify ?inflate_jobs=true works for multiple analyses
    r = as_admin.get('/sessions/' + session + '/analyses?inflate_job=true')
    assert r.ok
    assert all('id' in a.get('job', {}) for a in r.json())


def test_analysis_join_origin(data_builder, file_form, as_admin, as_drone):
    gear = data_builder.create_gear(gear={'inputs': {'csv': {'base': 'file'}}})
    session = data_builder.create_session()
    acquisition = data_builder.create_acquisition()
    assert as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('input.csv')).ok

    # Create job-based analysis
    r = as_admin.post('/sessions/' + session + '/analyses', json={
        'label': 'inflate',
        'job': {'gear_id': gear,
                'inputs': {'csv': {'type': 'acquisition', 'id': acquisition, 'name': 'input.csv'}}}
    })
    assert r.ok
    analysis = r.json()['_id']

    # Get the job that was created with it
    r = as_admin.get('/analyses/' + analysis)
    assert r.ok
    job = r.json().get('job')

    # Engine upload
    r = as_drone.post('/engine',
        params={'level': 'analysis', 'id': analysis, 'job': job},
        files=file_form('output.csv', meta={'type': 'tabular data'}))
    assert r.ok

    # Verify ?join=origin works for one analysis
    r = as_admin.get('/analyses/' + analysis + '?join=origin')
    assert r.ok
    assert 'join-origin' in r.json()

    # Verify ?join=origin works for multiple analyses
    r = as_admin.get('/sessions/' + session + '/analyses?join=origin')
    assert r.ok
    assert all('join-origin' in a for a in r.json())

    # Verify ?join=origin_job_gear_name works for one analysis
    r = as_admin.get('/analyses/' + analysis + '?join=origin&join=origin_job_gear_name')
    assert r.ok
    assert 'gear_name' in r.json()['join-origin']['job'][job]

    # Verify ?join=origin_job_gear_name works for multiple analyses
    r = as_admin.get('/sessions/' + session + '/analyses?join=origin&join=origin_job_gear_name')
    assert r.ok
    assert all('gear_name' in a['join-origin']['job'][job] for a in r.json())


def test_analysis_join_avatars(as_admin, data_builder):
    session = data_builder.create_session()
    r = as_admin.post('/sessions/' + session + '/analyses', json={'label': 'join-avatars'})
    assert r.ok
    analysis = r.json()['_id']

    r = as_admin.post('/analyses/' + analysis + '/notes', json={'text': 'test'})
    assert r.ok

    r = as_admin.get('/analyses/' + analysis + '?join_avatars=true')
    assert r.ok
    assert 'avatar' in r.json()['notes'][0]

    r = as_admin.get('/sessions/' + session + '/analyses?join_avatars=true')
    assert r.ok
    assert 'avatar' in r.json()[0]['notes'][0]


def check_files(as_admin, analysis_id, filegroup, *filenames):
    # Verify that filegroup has all files, inflated
    r = as_admin.get('/analyses/' + analysis_id)
    assert r.ok
    analysis = r.json()
    assert set(f['name'] for f in analysis.get(filegroup, [])) == set(filenames)
    assert all('size' in f for f in analysis.get(filegroup, []))

    # Verify that filegroup download works
    r = as_admin.get('/analyses/' + analysis_id + '/' + filegroup, params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']
    r = as_admin.get('/download', params={'ticket': ticket})
    assert r.ok
    dirname = 'input' if filegroup == 'inputs' else 'output'
    with tarfile.open(mode='r', fileobj=cStringIO.StringIO(r.content)) as tar:
        assert set(m.name for m in tar.getmembers()) == set('/'.join([analysis['label'], dirname, fn]) for fn in filenames)


def test_moving_session_moves_analyses(data_builder, as_admin):
    project_1 = data_builder.create_project()
    project_2 = data_builder.create_project()
    session = data_builder.create_session(project=project_1)
    acquisition = data_builder.create_acquisition(session=session)

    # Create ad-hoc analysis on session
    r = as_admin.post('/sessions/' + session + '/analyses', json={
        'label': 'session_offline'
    })
    assert r.ok
    session_analysis = r.json()['_id']

    # Create ad-hoc analysis on acquisition
    r = as_admin.post('/acquisitions/' + acquisition + '/analyses', json={
        'label': 'acquisition_offline'
    })
    assert r.ok
    acquisition_analysis = r.json()['_id']

    # Test that session analysis has current parents
    r = as_admin.get('/analyses/' + session_analysis)
    assert r.ok
    parents = r.json()['parents']
    assert parents['project'] == project_1

    # Test that acquisition analysis has current parents
    r = as_admin.get('/analyses/' + acquisition_analysis)
    assert r.ok
    parents = r.json()['parents']
    assert parents['project'] == project_1

    # Move session
    r = as_admin.put('/sessions/' + session, json={'project': project_2})
    assert r.ok

    # Test session analysis parents updated
    r = as_admin.get('/analyses/' + session_analysis)
    assert r.ok
    parents = r.json()['parents']
    assert parents['project'] == project_2

    # Test that acquisition parents are up to date
    r = as_admin.get('/acquisitions/' + acquisition)
    assert r.ok
    assert r.json()['session'] == session
    assert r.json()['parents']['session'] == session
    assert r.json()['parents']['project'] == project_2

    # Test acquisition analysis parents updated
    r = as_admin.get('/analyses/' + acquisition_analysis)
    assert r.ok
    parents = r.json()['parents']
    assert parents['project'] == project_2
