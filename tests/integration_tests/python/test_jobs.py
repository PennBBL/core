import copy

import bson
import datetime

def test_jobs_access(as_user):
    r = as_user.get('/jobs/next')
    assert r.status_code == 403

    r = as_user.get('/jobs/stats')
    assert r.status_code == 403

    r = as_user.get('/jobs/pending')
    assert r.status_code == 403

    r = as_user.post('/jobs/reap')
    assert r.status_code == 403

    r = as_user.get('/jobs/test-job')
    assert r.status_code == 403

    r = as_user.get('/jobs/test-job/config.json')
    assert r.status_code == 403


def test_jobs(data_builder, default_payload, as_public, as_user, as_admin, as_root, api_db, file_form):

    # Dupe of test_queue.py
    gear_doc = default_payload['gear']['gear']
    gear_doc['inputs'] = {
        'dicom': {
            'base': 'file'
        }
    }
    gear = data_builder.create_gear(gear=gear_doc)
    invalid_gear = data_builder.create_gear(gear={'custom': {'flywheel': {'invalid': True}}})
    project = data_builder.create_project()
    session = data_builder.create_session()
    acquisition = data_builder.create_acquisition()
    assert as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('test.zip')).ok

    # Create ad-hoc analysis
    r = as_admin.post('/sessions/' + session + '/analyses', json={
        'label': 'offline',
        'inputs': [{'type': 'acquisition', 'id': acquisition, 'name': 'test.zip'}]
    })
    assert r.ok
    analysis = r.json()['_id']
    # Manually upload outputs
    r = as_admin.post('/analyses/' + analysis + '/files', files=file_form('output1.csv', 'output2.csv', meta=[
        {'name': 'output1.csv', 'info': {'foo': 'foo'}},
        {'name': 'output2.csv', 'info': {'bar': 'bar'}},
    ]))
    assert r.ok

    job_data = {
        'gear_id': gear,
        'inputs': {
            'dicom': {
                'type': 'acquisition',
                'id': acquisition,
                'name': 'test.zip'
            }
        },
        'config': { 'two-digit multiple of ten': 20 },
        'destination': {
            'type': 'acquisition',
            'id': acquisition
        },
        'tags': [ 'test-tag' ]
    }

    # try to add job with analysis as explicit destination
    job_data['destination'] = {
        'type': 'analysis',
        'id': analysis
    }
    r = as_admin.post('/jobs/add', json=job_data)
    assert r.status_code == 400


    job_data['destination'] = {
        'type': 'acquisition',
        'id': acquisition
    }

    # try to add job w/ non-existent gear
    job0 = copy.deepcopy(job_data)
    job0['gear_id'] = '000000000000000000000000'
    r = as_admin.post('/jobs/add', json=job0)
    assert r.status_code == 404

    # try to add job without login
    r = as_public.post('/jobs/add', json=job_data)
    assert r.status_code == 403

    # add job with explicit destination
    r = as_admin.post('/jobs/add', json=job_data)
    assert r.ok
    job1_id = r.json()['_id']

    # get job
    r = as_root.get('/jobs/' + job1_id)
    assert r.ok

    job = r.json()
    assert job['gear_info']['name']
    assert job['gear_info']['version'] == '0.0.1'

    # get job log (empty)
    r = as_admin.get('/jobs/' + job1_id + '/logs')
    assert r.ok
    assert r.json()['logs'] == []

    # try to add job log w/o root
    # needed to use as_user because root = true for as_admin
    job_logs = [{'fd': 1, 'msg': 'Hello'}, {'fd': 2, 'msg': 'World'}]
    r = as_user.post('/jobs/' + job1_id + '/logs', json=job_logs)
    assert r.status_code == 403

    # try to add job log to non-existent job
    r = as_root.post('/jobs/000000000000000000000000/logs', json=job_logs)
    assert r.status_code == 404

    # get job log as text w/o logs
    r = as_admin.get('/jobs/' + job1_id + '/logs/text')
    assert r.ok
    assert r.text == '<span class="fd--1">No logs were found for this job.</span>'

    # get job log as html w/o logs
    r = as_admin.get('/jobs/' + job1_id + '/logs/html')
    assert r.ok
    assert r.text == '<span class="fd--1">No logs were found for this job.</span>'

    # add job log
    r = as_root.post('/jobs/' + job1_id + '/logs', json=job_logs)
    assert r.ok

    # try to get job log of non-existent job
    r = as_admin.get('/jobs/000000000000000000000000/logs')
    assert r.status_code == 404

    # get job log (non-empty)
    r = as_admin.get('/jobs/' + job1_id + '/logs')
    assert r.ok
    assert len(r.json()['logs']) == 2

    # add same logs again (for testing text/html logs)
    r = as_root.post('/jobs/' + job1_id + '/logs', json=job_logs)
    assert r.ok

    # get job log as text
    r = as_admin.get('/jobs/' + job1_id + '/logs/text')
    assert r.ok
    assert r.text == 2 * ''.join(log['msg'] for log in job_logs)

    # get job log as html
    r = as_admin.get('/jobs/' + job1_id + '/logs/html')
    assert r.ok
    assert r.text == 2 * ''.join('<span class="fd-{fd}">{msg}</span>\n'.format(**log) for log in job_logs)

    # get job config
    r = as_root.get('/jobs/' + job1_id + '/config.json')
    assert r.ok

    # try to cancel job w/o permission (different user)
    r = as_user.put('/jobs/' + job1_id, json={'state': 'cancelled'})
    assert r.status_code == 403

    # try to update job (user may only cancel)
    api_db.jobs.update_one({'_id': bson.ObjectId(job1_id)}, {'$set': {'origin.id': 'user@user.com'}})
    r = as_user.put('/jobs/' + job1_id, json={'test': 'invalid'})
    assert r.status_code == 403

    # try to add job whos implicit destination is an analysis
    analyis_input_job_data = {
        'gear_id': gear,
        'inputs': {
            'dicom': {
                'type': 'analysis',
                'id': analysis,
                'name': 'output1.csv'
            }
        },
        'config': { 'two-digit multiple of ten': 20 },
        'tags': [ 'test-tag' ]
    }
    r = as_admin.post('/jobs/add', json=analyis_input_job_data)
    assert r.status_code == 400

    # add job with implicit destination
    job2 = copy.deepcopy(job_data)
    del job2['destination']
    r = as_admin.post('/jobs/add', json=job2)
    assert r.ok

    # add job with invalid gear
    job3 = copy.deepcopy(job_data)
    job3['gear_id'] = invalid_gear

    r = as_admin.post('/jobs/add', json=job3)
    assert r.status_code == 400

    # get next job - with nonexistent tag
    r = as_root.get('/jobs/next', params={'tags': 'fake-tag'})
    assert r.status_code == 400

    # get next job - with excluding tag
    r = as_root.get('/jobs/next', params={'tags': '!test-tag'})
    assert r.status_code == 400

    # get next job - with excluding tag overlap
    r = as_root.get('/jobs/next', params={'tags': ['test-tag', '!test-tag']})
    assert r.status_code == 400

    # get next job with peek
    r = as_root.get('/jobs/next', params={'tags': 'test-tag', 'peek': True})
    assert r.ok
    next_job_id_peek = r.json()['id']

    # get next job
    r = as_root.get('/jobs/next', params={'tags': ['test-tag', '!fake-tag']})
    assert r.ok
    next_job_id = r.json()['id']
    assert next_job_id == next_job_id_peek

    # set next job to failed
    r = as_root.put('/jobs/' + next_job_id, json={'state': 'failed'})
    assert r.ok

    # retry failed job
    r = as_root.post('/jobs/' + next_job_id + '/retry')
    assert r.ok

    # get next job as admin
    r = as_admin.get('/jobs/next', params={'tags': 'test-tag'})
    assert r.ok
    next_job_id = r.json()['id']

    # set next job to failed
    r = as_root.put('/jobs/' + next_job_id, json={'state': 'failed'})
    assert r.ok

    # retry failed job w/o root
    r = as_admin.post('/jobs/' + next_job_id + '/retry')
    assert r.ok

    # set as_user perms to ro
    r = as_user.get('/users/self')
    assert r.ok
    uid = r.json()['_id']

    r = as_admin.post('/projects/' + project + '/permissions', json={
        '_id': uid,
        'access': 'ro'
    })
    assert r.ok

    # try to add job without rw
    r = as_user.post('/jobs/add', json=job_data)
    assert r.status_code == 403

    # set as_user perms to rw
    r = as_admin.put('/projects/' + project + '/permissions/' + uid, json={
        'access': 'rw'
    })
    assert r.ok

    # add job with rw
    r = as_user.post('/jobs/add', json=job_data)
    assert r.ok
    job_rw_id = r.json()['_id']

    # get next job as admin
    r = as_admin.get('/jobs/next', params={'tags': 'test-tag'})
    assert r.ok
    job_rw_id = r.json()['id']

    # try to add job with no inputs and no destination
    gear_doc = default_payload['gear']['gear']
    gear_doc['inputs'] = {}
    gear2 = data_builder.create_gear(gear=gear_doc)

    job5 = copy.deepcopy(job_data)
    job5['gear_id'] = gear2
    job5.pop('inputs')
    job5.pop('destination')

    r = as_admin.post('/jobs/add', json=job5)
    assert r.status_code == 400

    # try to add job with input type that is not file nor api-key
    gear_doc = default_payload['gear']['gear']
    gear_doc['inputs'] = {
        'dicom': {
            'base': 'made-up'
        }
    }
    gear3 = str(api_db.gears.insert(gear_doc))

    job6 = copy.deepcopy(job_data)
    job6['gear_id'] = gear3

    r = as_admin.post('/jobs/add', json=job6)
    assert r.status_code == 500

    assert as_root.delete('/gears/' + gear3).ok

    # Attempt to set a malformed file reference as input
    job7 = copy.deepcopy(job_data)
    job7['inputs'] = {
        'dicom': {
                # missing type
                'id': acquisition,
                'name': 'test.zip'
        }
    }
    r = as_admin.post('/jobs/add', json=job7)
    assert r.status_code == 400

    # Insert non-running job into database
    job_instance = {
        "_id" : bson.ObjectId("5a007cdb0f352600d94c845f"),
        "inputs" : [{
            "input": 'dicom',
            'type': 'acquisition',
            'id': acquisition,
            'name': 'test.zip'
        }],
        # Set attempt to 5 so that job isn't retried, throwing off the usage report tests
        "attempt" : 5,
        "tags" : [
            "ad-hoc"
        ],
        "destination" : {
            "type" : "acquisition",
            "id" : acquisition
        },
        "modified" : datetime.datetime(1980, 1, 1),
        "created" : datetime.datetime(1980, 1, 1),
        "produced_metadata" : {},
        "saved_files" : [],
        "state" : "running",
        "gear_id" : gear3,
        "batch" : None,
    }
    api_db.jobs.insert_one(job_instance)
    r = as_root.post('/jobs/reap')
    assert r.ok
    assert r.json().get('orphaned') == 1
    r = as_admin.get('/jobs/'+str(job_instance['_id'])+'/logs')
    assert r.ok
    assert "The job did not report in for a long time and was canceled." in [log["msg"] for log in r.json()['logs']]
    api_db.jobs.delete_one({"_id": bson.ObjectId("5a007cdb0f352600d94c845f")})

    r = as_admin.get('/jobs/stats')
    assert r.ok
    r = as_admin.get('/jobs/pending')
    assert r.ok
    r = as_admin.get('/jobs/pending', params={'tags': 'auto,unused'})
    assert r.ok
    r = as_admin.get('/jobs/stats', params={'all': '1'})
    assert r.ok
    r = as_admin.get('/jobs/stats', params={'tags': 'auto,unused', 'last': '2'})
    assert r.ok


def test_failed_job_output(data_builder, default_payload, as_user, as_admin, as_drone, api_db, file_form):
    # create gear
    gear_doc = default_payload['gear']['gear']
    gear_doc['inputs'] = {
        'dicom': {
            'base': 'file'
        }
    }
    gear = data_builder.create_gear(gear=gear_doc)
    gear2 = data_builder.create_gear()
    project = data_builder.create_project()
    session = data_builder.create_session()
    acquisition = data_builder.create_acquisition()
    r = as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('test.zip'))
    assert r.ok

    # create rule for text files
    r = as_admin.post('/projects/' + project + '/rules', json={
        'gear_id': gear2,
        'name': 'text-trigger',
        'any': [],
        'not': [],
        'all': [{'type': 'file.type', 'value': 'text'}]
    })
    assert r.ok

    # create job
    r = as_admin.post('/jobs/add', json={
        'gear_id': gear,
        'inputs': {
            'dicom': {
                'type': 'acquisition',
                'id': acquisition,
                'name': 'test.zip'
            }
        },
        'config': {},
        'destination': {
            'type': 'acquisition',
            'id': acquisition
        }
    })
    assert r.ok
    job = r.json()['_id']
    api_db.jobs.update_one({'_id': bson.ObjectId(job)}, {'$set': {'state': 'running'}})

    # prepare completion (send success status before engine upload)
    r = as_drone.post('/jobs/' + job + '/prepare-complete', json={'success': False, 'elapsed': -1})
    assert r.ok

    # verify that job ticket has been created
    job_ticket = api_db.job_tickets.find_one({'job': job})
    assert job_ticket['success'] == False

    # engine upload
    r = as_drone.post('/engine',
        params={'level': 'acquisition', 'id': acquisition, 'job': job, 'job_ticket': job_ticket['_id']},
        files=file_form('result.txt', meta={
            'project': {
                'label': 'engine project',
                'info': {'test': 'p'}
            },
            'session': {
                'label': 'engine session',
                'subject': {'code': 'engine subject'},
                'info': {'test': 's'}
            },
            'acquisition': {
                'label': 'engine acquisition',
                'timestamp': '2016-06-20T21:57:36+00:00',
                'info': {'test': 'a'},
                'files': [{
                    'name': 'result.txt',
                    'type': 'text',
                    'info': {'test': 'f0'}
                }]
            }
        })
    )
    assert r.ok

    # verify job was transitioned to failed state
    job_doc = as_admin.get('/jobs/' + job).json()
    assert job_doc['state'] == 'failed'

    # verify metadata wasn't applied
    acq = as_admin.get('/acquisitions/' + acquisition).json()
    assert 'test' not in acq.get('info', {})

    # verify uploaded file got marked w/ 'from_failed_job'
    result_file = acq['files'][-1]
    assert 'from_failed_job' in result_file
    assert result_file['from_failed_job'] == True

    # verify that no jobs were spawned for failed files
    jobs = [j for j in api_db.jobs.find({'gear_id': gear2})]
    assert len(jobs) == 0

    # try to accept failed output - user has no access to destination
    r = as_user.post('/jobs/' + job + '/accept-failed-output')
    assert r.status_code == 403

    # accept failed output
    r = as_admin.post('/jobs/' + job + '/accept-failed-output')
    assert r.ok

    # verify job is marked w/ 'failed_output_accepted'
    job_doc = as_admin.get('/jobs/' + job).json()
    assert 'failed_output_accepted' in job_doc
    assert job_doc['failed_output_accepted'] == True

    # verify metadata was applied on hierarchy
    acq = as_admin.get('/acquisitions/' + acquisition).json()
    assert 'test' in acq.get('info', {})

    # verify uploaded file isn't marked anymore
    result_file = acq['files'][-1]
    assert 'from_failed_job' not in result_file

    # verify that a job was spawned for accepted files
    jobs = [j for j in api_db.jobs.find({'gear_id': gear2})]
    assert len(jobs) == 1


def test_job_state_transition_from_ticket(data_builder, default_payload, as_admin, as_drone, api_db, file_form):
    # create gear
    gear_doc = default_payload['gear']['gear']
    gear_doc['inputs'] = {'dicom': {'base': 'file'}}
    gear = data_builder.create_gear(gear=gear_doc)

    # create acq with file (for input)
    acquisition = data_builder.create_acquisition()
    r = as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('test.zip'))
    assert r.ok

    # create job
    r = as_admin.post('/jobs/add', json={
        'gear_id': gear,
        'config': {},
        'inputs': {'dicom': {'type': 'acquisition', 'id': acquisition, 'name': 'test.zip'}},
        'destination': {'type': 'acquisition', 'id': acquisition}
    })
    assert r.ok
    job = r.json()['_id']
    api_db.jobs.update_one({'_id': bson.ObjectId(job)}, {'$set': {'state': 'running'}})

    # prepare completion (send success status before engine upload)
    r = as_drone.post('/jobs/' + job + '/prepare-complete', json={'success': True, 'elapsed': 3})
    assert r.ok
    job_ticket = r.json()['ticket']

    # engine upload (should trigger state transition based on ticket)
    r = as_drone.post('/engine',
        params={'level': 'acquisition', 'id': acquisition, 'job': job, 'job_ticket': job_ticket},
        files=file_form('result.txt', meta={
            'acquisition': {'files': [{'name': 'result.txt', 'type': 'text'}]}
        })
    )
    assert r.ok

    # verify job was transitioned to complete state
    job_doc = as_admin.get('/jobs/' + job).json()
    assert job_doc['state'] == 'complete'

    # test with success: False
    api_db.jobs.update_one({'_id': bson.ObjectId(job)}, {'$set': {'state': 'running'}})
    api_db.job_tickets.update_one({'_id': bson.ObjectId(job_ticket)}, {'$set': {'success': False}})
    r = as_drone.post('/engine',
        params={'level': 'acquisition', 'id': acquisition, 'job': job, 'job_ticket': job_ticket},
        files=file_form('result.txt', meta={
            'acquisition': {'files': [{'name': 'result.txt', 'type': 'text'}]}
        })
    )
    assert r.ok
    job_doc = as_admin.get('/jobs/' + job).json()
    assert job_doc['state'] == 'failed'

    # create session, analysis and job
    session = data_builder.create_session()
    r = as_admin.post('/sessions/' + session + '/analyses', json={
        'label': 'online',
        'job': {'gear_id': gear,
                'inputs': {'dicom': {'type': 'acquisition', 'id': acquisition, 'name': 'test.zip'}}}
    })
    assert r.ok
    analysis = r.json()['_id']

    r = as_admin.get('/analyses/' + analysis)
    assert r.ok
    job = r.json().get('job')
    api_db.jobs.update_one({'_id': bson.ObjectId(job)}, {'$set': {'state': 'running'}})

    # prepare completion (send success status before engine upload)
    r = as_drone.post('/jobs/' + job + '/prepare-complete', json={'success': True, 'elapsed': 3})
    assert r.ok
    job_ticket = r.json()['ticket']

    r = as_drone.post('/engine',
        params={'level': 'analysis', 'id': analysis, 'job': job, 'job_ticket': job_ticket},
        files=file_form('result.txt', meta={'type': 'text'}))
    assert r.ok

    # verify job was transitioned to complete state
    job_doc = as_admin.get('/jobs/' + job).json()
    assert job_doc['state'] == 'complete'

    # test with success: False
    api_db.jobs.update_one({'_id': bson.ObjectId(job)}, {'$set': {'state': 'running'}})
    api_db.job_tickets.update_one({'_id': bson.ObjectId(job_ticket)}, {'$set': {'success': False}})
    r = as_drone.post('/engine',
        params={'level': 'analysis', 'id': analysis, 'job': job, 'job_ticket': job_ticket},
        files=file_form('result.txt', meta={'type': 'text'}))
    assert r.ok
    job_doc = as_admin.get('/jobs/' + job).json()
    assert job_doc['state'] == 'failed'


def test_analysis_job_creation_errors(data_builder, default_payload, as_admin, file_form):
    project = data_builder.create_project()
    session = data_builder.create_session()
    gear_doc = default_payload['gear']['gear']
    gear_doc['inputs'] = {
        'csv': {
            'base': 'file'
        }
    }
    gear = data_builder.create_gear(gear=gear_doc)

    # Add project file
    r = as_admin.post('/projects/' + project + '/files', files=file_form('job_1.csv'))
    assert r.ok

    # ensure analysis with improper gear id is not created
    r = as_admin.post('/sessions/' + session + '/analyses', json={
        'label': 'with-job',
        'job': {
            # no gear id
            'inputs': {
                'csv': {'type': 'project', 'id': project, 'name': 'job_1.csv'}
            }
        }
    })
    assert r.status_code == 400
    assert len(as_admin.get('/sessions/' + session).json().get('analyses', [])) == 0

    # ensure analysis with improper inputs is not created
    r = as_admin.post('/sessions/' + session + '/analyses', json={
        'label': 'with-job',
        'job': {
            'gear_id': gear,
            'inputs': {
                'made-up': {'type': 'project', 'id': project, 'name': 'job_1.csv'}
            }
        }
    })
    assert r.status_code == 400
    assert len(as_admin.get('/sessions/' + session).json().get('analyses', [])) == 0

def test_job_context(data_builder, default_payload, as_admin, as_root, file_form):
    # Dupe of test_queue.py
    gear_doc = default_payload['gear']['gear']
    gear_doc['inputs'] = {
        'zip': {
            'base': 'file'
        },
        'test_context_value': {
            'base': 'context'
        }
    }
    gear = data_builder.create_gear(gear=gear_doc)
    project = data_builder.create_project()
    session = data_builder.create_session()
    acquisition = data_builder.create_acquisition()
    assert as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('test.zip')).ok

    job_data = {
        'gear_id': gear,
        'inputs': {
            'zip': {
                'type': 'acquisition',
                'id': acquisition,
                'name': 'test.zip'
            }
        },
        'tags': [ 'test-tag' ]
    }

    # add job without context value
    r = as_admin.post('/jobs/add', json=job_data)
    assert r.ok
    job1_id = r.json()['_id']

    # get job
    r = as_root.get('/jobs/' + job1_id)
    assert r.ok
    r_job = r.json()
    r_inputs = r_job['config']['inputs']
    assert 'test_context_value' in r_inputs
    assert r_inputs['test_context_value']['base'] == 'context'
    assert r_inputs['test_context_value']['found'] == False

    # Set context at project level
    r = as_admin.post('/projects/' + project + '/info', json={
        'set': {
            'test_context_value': 3,
            'context': {
                'test_context_value': 'project_context_value'
            }
        }
    })
    assert r.ok

    # add job with project context value
    r = as_admin.post('/jobs/add', json=job_data)
    assert r.ok
    job2_id = r.json()['_id']

    # get job
    r = as_root.get('/jobs/' + job2_id)
    assert r.ok
    r_job = r.json()
    r_inputs = r_job['config']['inputs']
    assert 'test_context_value' in r_inputs
    assert r_inputs['test_context_value']['base'] == 'context'
    assert r_inputs['test_context_value']['found'] == True
    assert r_inputs['test_context_value']['value'] == 'project_context_value'

    # Override context at session level
    r = as_admin.post('/sessions/' + session + '/info', json={
        'set': {
            'context': {
                'test_context_value': {
                    'session_value': 3
                }
            }
        }
    })
    assert r.ok

    # add job with session context value
    r = as_admin.post('/jobs/add', json=job_data)
    assert r.ok
    job3_id = r.json()['_id']

    # get job
    r = as_root.get('/jobs/' + job3_id)
    assert r.ok
    r_job = r.json()
    r_inputs = r_job['config']['inputs']
    assert 'test_context_value' in r_inputs
    assert r_inputs['test_context_value']['base'] == 'context'
    assert r_inputs['test_context_value']['found'] == True
    assert r_inputs['test_context_value']['value'] == { 'session_value': 3 }


def test_job_api_key(data_builder, default_payload, as_public, as_admin, as_root, api_db, file_form):

    acquisition = data_builder.create_acquisition()
    assert as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('test.zip')).ok

    # Add job with gear that uses api-key base type and get config
    gear_doc = default_payload['gear']['gear']
    gear_doc['inputs'] = {
        'dicom': {
            'base': 'file'
        },
        'api_key': {
            'base': 'api-key'
        }
    }
    gear = data_builder.create_gear(gear=gear_doc)

    job_data = {
        'gear_id': gear,
        'inputs': {
            'dicom': {
                'type': 'acquisition',
                'id': acquisition,
                'name': 'test.zip'
            }
        },
        'config': { 'two-digit multiple of ten': 20 },
        'destination': {
            'type': 'acquisition',
            'id': acquisition
        },
        'tags': [ 'test-tag' ]
    }


    job1 = copy.deepcopy(job_data)
    job1['gear_id'] = gear

    r = as_admin.post('/jobs/add', json=job1)
    assert r.status_code == 200
    job_id = r.json()['_id']

    # get next job as admin
    r = as_root.get('/jobs/next')
    assert r.ok

    # get config
    r = as_root.get('/jobs/'+ job_id +'/config.json')
    assert r.ok
    config = r.json()

    assert type(config['inputs']['dicom']) is dict
    assert config['destination']['id'] == acquisition
    assert type(config['config']) is dict
    api_key = config['inputs']['api_key']['key']

    # ensure api_key works
    as_job_key = as_public
    as_job_key.headers.update({'Authorization': 'scitran-user ' + api_key})
    r = as_job_key.get('/users/self')
    assert r.ok

    # complete job and ensure API key no longer works
    r = as_root.put('/jobs/' + job_id, json={'state': 'complete'})
    assert r.ok

    r = as_job_key.get('/users/self')
    assert r.status_code == 401

    ##
    # Ensure API key is generated for retried job
    ##

    job2 = copy.deepcopy(job_data)
    job2['gear_id'] = gear

    r = as_admin.post('/jobs/add', json=job2)
    assert r.status_code == 200
    job_id = r.json()['_id']

    # get next job as admin
    r = as_root.get('/jobs/next')
    assert r.ok

    # get config
    r = as_root.get('/jobs/'+ job_id +'/config.json')
    assert r.ok
    config = r.json()

    assert type(config['inputs']['dicom']) is dict
    assert config['destination']['id'] == acquisition
    assert type(config['config']) is dict
    api_key = config['inputs']['api_key']['key']

    # ensure api_key works
    as_job_key = as_public
    as_job_key.headers.update({'Authorization': 'scitran-user ' + api_key})
    r = as_job_key.get('/users/self')
    assert r.ok

    # Make sure there are no jobs that are pending
    assert api_db.jobs.count({'state': 'pending'}) == 0

    # set job as one that should be orphaned
    api_db.jobs.update_one({'_id': bson.ObjectId(job_id)}, {'$set': {'modified': datetime.datetime(1980, 1, 1)}})

    # reap orphans
    r = as_root.post('/jobs/reap')

    # Make sure there is only one job that is pending
    assert api_db.jobs.count({'state': 'pending'}) == 1

    # get next job as admin
    r = as_root.get('/jobs/next')
    assert r.ok
    retried_job = r.json()
    retried_job_id = retried_job['id']
    assert retried_job['previous_job_id'] is not None

    # Ensure the attempt is bumped and the config uri is for the new job
    assert retried_job['attempt'] == 2
    found_config_uri = False
    for i in retried_job['request']['inputs']:
        if i['uri'] == '/jobs/' + retried_job_id + '/config.json':
            found_config_uri = True
            break
    assert found_config_uri

    # get config
    r = as_root.get('/jobs/'+ retried_job_id +'/config.json')
    assert r.ok
    config = r.json()

    assert type(config['inputs']['dicom']) is dict
    assert config['destination']['id'] == acquisition
    assert type(config['config']) is dict
    api_key = config['inputs']['api_key']['key']

    # ensure api_key works
    as_job_key = as_public
    as_job_key.headers.update({'Authorization': 'scitran-user ' + api_key})
    r = as_job_key.get('/users/self')
    assert r.ok

    # complete job and ensure API key no longer works
    r = as_root.put('/jobs/' + retried_job_id, json={'state': 'complete'})
    assert r.ok

    r = as_job_key.get('/users/self')
    assert r.status_code == 401


def test_job_tagging(data_builder, default_payload, as_admin, as_root, api_db, file_form):
    # Dupe of test_queue.py
    gear_doc = default_payload['gear']['gear']
    gear_name = 'gear-name'
    gear_doc['name'] = gear_name
    gear = data_builder.create_gear(gear=gear_doc)

    project = data_builder.create_project()
    session = data_builder.create_session()
    acquisition = data_builder.create_acquisition()

    # Test the gear name tag with auto job rule
    rule = {
        'gear_id': gear,
        'name': 'job-trigger-rule',
        'any': [],
        'not': [],
        'all': [
            {'type': 'file.type', 'value': 'tabular data'}],
        'disabled': False
    }

    # add project rule
    r = as_admin.post('/projects/' + project + '/rules', json=rule)
    assert r.ok
    rule_id = r.json()['_id']

    # create job
    # print gear_doc
    assert as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('test.csv')).ok

    # Verify that job was created
    rule_jobs = [job for job in api_db.jobs.find({'gear_id': gear})]
    assert len(rule_jobs) == 1
    assert gear_name in rule_jobs[0].get('tags', [])

    # Test the gear name tag with manually adding the job
    job_data = {
        'gear_id': gear,
        'inputs': {
            'text': {
                'type': 'acquisition',
                'id': acquisition,
                'name': 'test.csv'
            }
        },
        'config': { 'two-digit multiple of ten': 20 },
        'destination': {
            'type': 'acquisition',
            'id': acquisition
        },
        # No gear name in tags
        'tags': [ 'test-tag' ]
    }

    # add job with explicit destination
    r = as_admin.post('/jobs/add', json=job_data)
    assert r.ok
    manual_job_id = r.json()['_id']

    # get job
    r = as_root.get('/jobs/' + manual_job_id)
    assert r.ok

    # Make sure that the job has the tag of the gear name
    manual_job = r.json()
    assert gear_name in manual_job['tags']

    # Test the gear name tag with job-based analysis
    r = as_admin.post('/sessions/' + session + '/analyses', json={
        'label': 'online',
        'job': job_data
    })
    assert r.ok
    analysis_id = r.json()['_id']

    # Verify job was created with it
    r = as_admin.get('/analyses/' + analysis_id)
    assert r.ok
    analysis_job_id = r.json().get('job')

    # get job
    r = as_root.get('/jobs/' + analysis_job_id)
    assert r.ok

    # Make sure that the job has the tag of the gear name
    analysis_job = r.json()
    assert gear_name in analysis_job['tags']

def test_job_reap_ticketed_jobs(data_builder, default_payload, as_drone, as_admin, as_root, api_db, file_form):
    acquisition = data_builder.create_acquisition()
    assert as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('test.zip')).ok

    # Add job with gear that uses api-key base type and get config
    gear_doc = default_payload['gear']['gear']
    gear_doc['inputs'] = {
        'dicom': {
            'base': 'file'
        },
        'api_key': {
            'base': 'api-key'
        }
    }
    gear = data_builder.create_gear(gear=gear_doc)

    job = {
        'gear_id': gear,
        'inputs': {
            'dicom': {
                'type': 'acquisition',
                'id': acquisition,
                'name': 'test.zip'
            }
        },
        'config': { 'two-digit multiple of ten': 20 },
        'destination': {
            'type': 'acquisition',
            'id': acquisition
        },
        'tags': [ 'test-tag' ]
    }

    r = as_admin.post('/jobs/add', json=job)
    assert r.status_code == 200
    job_id = r.json()['_id']

    r = as_admin.post('/jobs/add', json=job)
    assert r.status_code == 200
    job_id2 = r.json()['_id']

    # transition jobs to running
    r = as_drone.put('/jobs/' + job_id, json={'state': 'running'})
    assert r.ok

    r = as_drone.put('/jobs/' + job_id2, json={'state': 'running'})
    assert r.ok

    # Make sure there are no jobs that are pending
    assert api_db.jobs.count({'state': 'pending'}) == 0

    # prepare completion (send success status before engine upload)
    r = as_drone.post('/jobs/' + job_id + '/prepare-complete', json={'success': True, 'elapsed': 10})
    assert r.ok

    # verify that job ticket has been created
    job_ticket = api_db.job_tickets.find_one({'job': job_id})
    assert job_ticket['success'] == True

    # set job as one that should be orphaned
    api_db.jobs.update_one({'_id': bson.ObjectId(job_id)}, {'$set': {'modified': datetime.datetime(1980, 1, 1)}})
    api_db.jobs.update_one({'_id': bson.ObjectId(job_id2)}, {'$set': {'modified': datetime.datetime(1980, 1, 1)}})

    # reap orphans
    r = as_root.post('/jobs/reap')

    # Make sure that exactly 1 job got restarted
    assert api_db.jobs.count({'state': 'pending'}) == 1

    # Ensure that our job is still running
    r = as_admin.get('/jobs/' + job_id)
    assert r.ok
    assert r.json()['state'] == 'running'

    # Ensure that our other job got marked as failed
    r = as_admin.get('/jobs/' + job_id2)
    assert r.ok
    assert r.json()['state'] == 'failed'

def test_job_requests(randstr, default_payload, data_builder, as_admin, as_drone, file_form):
    acquisition = data_builder.create_acquisition()
    assert as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('test.zip')).ok

    # Create gears
    gear_doc = default_payload['gear']['gear']
    gear_doc['name'] = randstr()
    gear_doc['inputs'] = {
        'dicom': {
            'base': 'file',
            'optional': True
        }
    }
    gear = data_builder.create_gear(gear=gear_doc)
    gear_doc['name'] = randstr()
    not_url_gear = data_builder.create_gear(gear=gear_doc, exchange={'rootfs-url': '/api/gears/temp/5b840961bef39f0018b73e64'})

    job = {
        'gear_id': gear,
        'inputs': {
            'dicom': {
                'type': 'acquisition',
                'id': acquisition,
                'name': 'test.zip'
            }
        },
        'config': { 'two-digit multiple of ten': 20 },
        'destination': {
            'type': 'acquisition',
            'id': acquisition
        },
        'tags': [ 'test-tag' ]
    }

    # Create jobs
    r = as_admin.post('/jobs/add', json=job)
    assert r.ok
    job_id = r.json()['_id']

    job['gear_id'] = not_url_gear

    r = as_admin.post('/jobs/add', json=job)
    assert r.ok
    not_url_job_id = r.json()['_id']

    # Start jobs
    r = as_drone.put('/jobs/' + job_id, json={'state': 'running'})
    assert r.ok

    r = as_drone.put('/jobs/' + not_url_job_id, json={'state': 'running'})
    assert r.ok

    # Check request inputs all have types
    r = as_admin.get('/jobs/' + job_id)
    assert r.ok
    job_request_inputs = r.json()['request']['inputs']
    for request_input in job_request_inputs:
        assert request_input.get('type')
    r = as_admin.get('/jobs/' + not_url_job_id)
    assert r.ok
    not_url_job_request_inputs = r.json()['request']['inputs']
    for request_input in not_url_job_request_inputs:
        assert request_input.get('type')


def test_scoped_job_api_key(randstr, data_builder, default_payload, as_public, as_admin, as_root, file_form):
    gear_doc = default_payload['gear']['gear']

    rw_gear_name = randstr()
    gear_doc['name'] = rw_gear_name
    gear_doc['inputs'] = {
        "api_key": {
          "base": "api-key"
        }
    }
    rw_gear = data_builder.create_gear(gear=gear_doc)
    gear_name = randstr()
    gear_doc['name'] = gear_name
    gear_doc['inputs'] = {
        "api_key": {
          "base": "api-key",
          "read-only": True
        }
    }
    ro_gear = data_builder.create_gear(gear=gear_doc)

    group = data_builder.create_group()
    project = data_builder.create_project(public=False)
    session = data_builder.create_session(public=False)
    acquisition = data_builder.create_acquisition(public=False)
    # Create ad-hoc analysis
    r = as_admin.post('/sessions/' + session + '/analyses', json={
        'label': 'offline_1',
    })
    assert r.ok
    analysis = r.json()['_id']

    # Test the gear name tag with auto job rule
    rule = {
        'gear_id': rw_gear,
        'name': 'job-trigger-rule',
        'any': [],
        'not': [],
        'all': [
            {'type': 'file.type', 'value': 'tabular data'}],
        'disabled': False
    }

    # Try to add rule with gear that requires read-write api-key
    r = as_admin.post('/projects/' + project + '/rules', json=rule)
    assert r.status_code == 400

    rule['gear_id'] = ro_gear

    # add project rule
    r = as_admin.post('/projects/' + project + '/rules', json=rule)
    assert r.ok
    rule_id = r.json()['_id']

    # create job
    assert as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('test.csv')).ok

    # get next job as admin
    r = as_root.get('/jobs/next')
    assert r.ok
    job_id = r.json()['id']

    # get config
    r = as_root.get('/jobs/' + job_id + '/config.json')
    assert r.ok
    config = r.json()

    assert config['destination']['id'] == acquisition
    assert type(config['config']) is dict
    api_key = config['inputs']['api_key']['key']
    # print api_key
    # ensure api_key works
    as_job_key = as_public
    as_job_key.headers.update({'Authorization': 'scitran-user ' + api_key.split(':')[-1]})

    r = as_job_key.get('/projects/' + project)
    assert r.ok

    # ensure api_key can access public projects
    project_2 = data_builder.create_project(public=True)
    r = as_job_key.get('/projects/' + project_2)
    assert r.ok

    # ensure api_key can't access other non public projects
    project_3 = data_builder.create_project(public=False)
    r = as_job_key.get('/projects/' + project_3)
    assert r.status_code == 403

    # Test getting lists of containers
    session_2 = data_builder.create_session(project=project_3, public=False)
    acquisition_2 = data_builder.create_acquisition(session=session_2, public=False)
    assert as_admin.post('/acquisitions/' + acquisition_2 + '/files', files=file_form('test.csv')).ok
    # Create ad-hoc analysis
    r = as_admin.post('/sessions/' + session_2 + '/analyses', json={
        'label': 'offline_2',
    })
    assert r.ok
    analysis_2 = r.json()['_id']

    # test get_all
    r = as_job_key.get('/projects')
    assert r.ok
    assert len(r.json()) == 2

    r = as_job_key.get('/sessions')
    assert r.ok
    print r.json()
    assert len(r.json()) == 1
    assert session == r.json()[0]['_id']

    r = as_job_key.get('/acquisitions')
    assert r.ok
    assert len(r.json()) == 1
    assert acquisition == r.json()[0]['_id']

    r = as_job_key.get('/sessions/' + session + '/analyses')
    assert r.ok
    assert len(r.json()) == 1
    assert analysis == r.json()[0]['_id']

    r = as_job_key.get('/sessions/' + session_2 + '/analyses')
    assert r.status_code == 403

    # Download file in scope
    r = as_job_key.get('/acquisitions/' + acquisition + '/files/test.csv')
    assert r.ok

    # Try getting file from outside of scope
    r = as_job_key.get('/acquisitions/' + acquisition_2 + '/files/test.csv')
    assert r.status_code == 403

    # Try creating containers
    # r = as_job_key.post('/projects', json={'label': 'NewLabel', 'group': group})
    # assert r.status_code == 403
    r = as_job_key.post('/sessions', json={'label': 'NewLabel', 'project': project})
    assert r.status_code == 403
    r = as_job_key.post('/acquisitions', json={'label': 'NewLabel', 'session': session})
    assert r.status_code == 403
    # Create ad-hoc analysis
    r = as_job_key.post('/sessions/' + session + '/analyses', json={
        'label': 'offline_2'
    })
    assert r.status_code == 403

    # Try uploading a file
    r = as_job_key.post('/acquisitions/' + acquisition + '/files', files=file_form('test_1.csv'))
    assert r.status_code == 403

    # Try to modify different containers and sublists
    r = as_job_key.put('/projects/' + project, json={'label': 'NewLabel'})
    assert r.status_code == 403
    r = as_job_key.put('/sessions/' + session, json={'label': 'NewLabel'})
    assert r.status_code == 403
    r = as_job_key.put('/acquisitions/' + acquisition, json={'label': 'NewLabel'})
    assert r.status_code == 403
    r = as_job_key.put('/sessions/' + session + '/analyses/' + analysis, json={'label': 'NewLabel'})
    assert r.status_code == 403

    # Try modifying the info of a file in the scope
    r = as_job_key.post('/acquisitions/' + acquisition + '/files/test.csv/info', json={
        'set': {'Key': 'Value'}
    })
    assert r.status_code == 403

    # complete job and ensure API key no longer works
    r = as_root.put('/jobs/' + job_id, json={'state': 'complete'})
    assert r.ok

    r = as_job_key.get('/projects/' + project)
    assert r.status_code == 401
