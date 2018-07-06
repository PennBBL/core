import bson


def test_site_rules(randstr, data_builder, as_admin, as_user, as_public):
    gear = data_builder.create_gear(gear={'version': '0.0.1'})
    gear_2 = data_builder.create_gear(gear={'version': '0.0.1'})

    rule = {
        'gear_id': gear,
        'name': 'csv-job-trigger-rule',
        'any': [],
        'not': [],
        'all': [
            {'type': 'file.type', 'value': 'tabular data'},
        ]
    }

    # GET ALL
    # attempt to get site rules without login
    r = as_public.get('/site/rules')
    assert r.status_code == 403

    # get empty list of site rules
    r = as_admin.get('/site/rules')
    assert r.ok
    assert r.json() == []


    # POST
    # attempt to add site rule without admin
    r = as_user.post('/site/rules', json=rule)
    assert r.status_code == 403

    # attempt to add site rule with empty payload
    r = as_admin.post('/site/rules', json={})
    assert r.status_code == 400
    assert 'Empty Payload' in r.json()['message']

    # attempt to add site rule without any conditions
    r = as_admin.post('/site/rules', json={
        'gear_id': gear,
        'name': 'no-conditions-rule',
        'any': [],
        'not': [],
        'all': []
    })
    assert r.status_code == 400
    assert 'conditions' in r.json()['message']

    # attempt to add site rule with invalid regex
    invalid_pattern = '^(?non-image$).+'
    r = as_admin.post('/site/rules', json={
        'gear_id': gear,
        'name': 'invalid-regex-rule',
        'any': [],
        'not': [],
        'all': [
            {'type': 'file.classification', 'value': invalid_pattern, 'regex': True},
        ]
    })
    assert r.status_code == 422
    assert invalid_pattern in r.json()['patterns']

    # try to add rule with id in the payload
    r = as_admin.post('/site/rules', json={
        'gear_id': gear,
        'name': 'invalid-regex-rule',
        '_id': 'foo',
        'any': [],
        'not': [],
        'all': [
            {'type': 'file.classification', 'value': 'Functional'},
        ]
    })
    assert r.status_code == 400

    # add site rule
    r = as_admin.post('/site/rules', json=rule)
    assert r.ok
    rule_id = r.json()['_id']

    r = as_admin.get('/site/rules')
    assert r.ok
    assert len(r.json()) == 1

    # GET ALL
    # attempt to get site rules without login
    r = as_public.get('/site/rules')
    assert r.status_code == 403

    # test rule is returned in list
    r = as_admin.get('/site/rules')
    assert r.ok
    assert r.json()[0]['_id'] == rule_id


    # GET ONE
    # attempt to get specific site rule without login
    r = as_public.get('/site/rules/' + rule_id)
    assert r.status_code == 403

    # attempt to get non-existent site rule
    r = as_admin.get('/site/rules/000000000000000000000000')
    assert r.status_code == 404

    # get specific site rule
    r = as_admin.get('/site/rules/' + rule_id)
    assert r.ok
    assert r.json()['gear_id'] == gear


    # PUT
    update = {'gear_id': gear_2}

    # attempt to modify site rule without admin
    r = as_user.put('/site/rules/' + rule_id, json=update)
    assert r.status_code == 403

    # attempt to modify non-existent site rule
    r = as_admin.put('/site/rules/000000000000000000000000', json=update)
    assert r.status_code == 404

    # attempt to modify site rule with empty payload
    r = as_admin.put('/site/rules/' + rule_id, json={})
    assert r.status_code == 400

    # attempt to modify site rule into invalid rule
    r = as_admin.put('/site/rules/' + rule_id, json={
        'all': []
    })
    assert r.status_code == 400

    # attempt to modify site rule with invalid regex
    r = as_admin.put('/site/rules/' + rule_id, json={
        'all': [
            {'type': 'file.classification', 'value': invalid_pattern, 'regex': True},
        ]
    })
    assert r.status_code == 422
    assert invalid_pattern in r.json()['patterns']

    # modify site rule
    r = as_admin.put('/site/rules/' + rule_id, json=update)
    assert r.ok
    r = as_admin.get('/site/rules/' + rule_id)
    assert r.ok
    assert r.json()['gear_id'] == gear_2


    # DELETE
    # attempt to delete rule without admin
    r = as_user.delete('/site/rules/' + rule_id)
    assert r.status_code == 403

    # attempt to delete non-existent site rule
    r = as_admin.delete('/site/rules/000000000000000000000000')
    assert r.status_code == 404

    # delete site rule
    r = as_admin.delete('/site/rules/' + rule_id)
    assert r.ok

    r = as_admin.get('/site/rules/' + rule_id)
    assert r.status_code == 404


def test_site_rules_copied_to_new_projects(randstr, data_builder, file_form, as_admin, as_root):
    gear_1 = data_builder.create_gear(gear={'version': '0.0.1'})
    rule_1 = {
        'gear_id': gear_1,
        'name': 'csv-job-trigger-rule',
        'any': [],
        'not': [],
        'all': [
            {'type': 'file.type', 'value': 'tabular data'},
        ]
    }

    gear_2 = data_builder.create_gear(gear={'version': '0.0.1'})
    rule_2 = {
        'gear_id': gear_2,
        'name': 'text-job-trigger-rule',
        'any': [],
        'not': [],
        'all': [
            {'type': 'file.type', 'value': 'text'},
        ]
    }

    # Add rules to site level
    r = as_admin.post('/site/rules', json=rule_1)
    assert r.ok
    rule_id_1 = r.json()['_id']

    r = as_admin.post('/site/rules', json=rule_2)
    assert r.ok
    rule_id_2 = r.json()['_id']

    # Ensure rules exist
    r = as_admin.get('/site/rules')
    assert r.ok
    assert len(r.json()) == 2


    # Create new project via POST
    group = data_builder.create_group()
    r = as_admin.post('/projects', json={
        'group': group,
        'label': 'project_1'
    })
    assert r.ok
    project_id = r.json()['_id']

    r = as_admin.get('/projects/'+project_id+'/rules')
    assert r.ok
    assert len(r.json()) == 2

    # Create new project via upload
    r = as_admin.post('/upload/label', files=file_form(
        'acquisition.csv',
        meta={
            'group': {'_id': group},
            'project': {
                'label': 'test_project',
            },
            'session': {
                'label': 'test_session_label',
                'subject': {
                    'code': 'test_subject_code'
                },
            },
            'acquisition': {
                'label': 'test_acquisition_label',
                'files': [{'name': 'acquisition.csv'}]
            }
        })
    )
    assert r.ok

    # Find newly created project id
    projects = as_root.get('/projects').json()
    for p in projects:
        if p['label'] == 'test_project':
            project_2 = p['_id']
            break

    # Find newly created project id using exhaustive
    projects = as_admin.get('/projects', params={'exhaustive': True}).json()
    for p in projects:
        if p['label'] == 'test_project':
            project_2 = p['_id']
            break

    assert project_2
    r = as_admin.get('/projects/'+project_2+'/rules')
    assert r.ok
    assert len(r.json()) == 2

    # Cleanup site rules
    r = as_admin.delete('/site/rules/' + rule_id_1)
    assert r.ok
    r = as_admin.delete('/site/rules/' + rule_id_2)
    assert r.ok

    # delete group and children recursively (created by upload)
    data_builder.delete_group(group, recursive=True)


def test_project_rules(randstr, data_builder, file_form, as_root, as_admin, with_user, api_db):
    # create versioned gear to cover code selecting latest gear
    gear_config = {'param': {'type': 'string', 'pattern': '^default|custom$', 'default': 'default'}}
    gear = data_builder.create_gear(gear={'version': '0.0.1', 'config': gear_config})
    project = data_builder.create_project()

    bad_payload = {'test': 'rules'}

    # try to get all project rules of non-existent project
    r = as_admin.get('/projects/000000000000000000000000/rules')
    assert r.status_code == 404

    # try to get single project rule of non-existent project
    r = as_admin.get('/projects/000000000000000000000000/rules/000000000000000000000000')
    assert r.status_code == 404

    # try to get project rules w/o permissions
    r = with_user.session.get('/projects/' + project + '/rules')
    assert r.status_code == 403

    # get project rules (yet empty list)
    r = as_admin.get('/projects/' + project + '/rules')
    assert r.ok
    assert r.json() == []

    # upload file w/o any rules
    r = as_admin.post('/projects/' + project + '/files', files=file_form('test1.csv'))
    assert r.ok

    # try to add rule to non-existent project
    r = as_admin.post('/projects/000000000000000000000000/rules', json=bad_payload)
    assert r.status_code == 404

    # add read-only perms for user
    r = as_admin.post('/projects/' + project + '/permissions', json={
        '_id': with_user.user, 'access': 'ro'})
    assert r.ok

    # try to add rule w/ read-only project perms
    r = with_user.session.post('/projects/' + project + '/rules', json=bad_payload)
    assert r.status_code == 403

    rule_json = {
        'gear_id': '000000000000000000000000',
        'name': 'csv-job-trigger-rule',
        'any': [],
        'not': [],
        'all': [
            {'type': 'file.type', 'value': 'tabular data'},
        ]
    }

    # try to add project rule w/ invalid rule-item (invalid type)
    # NOTE this is a legacy rule
    rule_json['all'] = [{'type': 'invalid', 'value': 'test'}]
    r = as_admin.post('/projects/' + project + '/rules', json=rule_json)
    assert r.status_code == 400
    assert "'invalid' is not one of" in r.json()['message']

    # try to add project rule w/ invalid rule-item (missing value)
    # NOTE this is a legacy rule
    rule_json['all'] = [{'type': 'file.name'}]
    r = as_admin.post('/projects/' + project + '/rules', json=rule_json)
    assert r.status_code == 400
    assert "'value' is a required property" in r.json()['message']

    # set valid rule-item
    rule_json['all'] = [{'type': 'file.type', 'value': 'tabular data'}]

    # try to add project rule w/ non-existent gear
    # NOTE this is a legacy rule
    r = as_admin.post('/projects/' + project + '/rules', json=rule_json)
    assert r.status_code == 404

    # try to add project rule w/ invalid config
    # NOTE this is a legacy rule
    rule_json['gear_id'] = gear
    rule_json['config'] = {'param': 'invalid'}
    r = as_admin.post('/projects/' + project + '/rules', json=rule_json)
    assert r.status_code == 422
    assert r.json()['reason'] == 'config did not match manifest'
    del rule_json['config']

    # try to add project rule with rule id in input
    r = as_admin.post('/site/rules', json={
        'gear_id': gear,
        'name': 'invalid-regex-rule',
        '_id': 'foo',
        'any': [],
        'not': [],
        'all': [
            {'type': 'file.classification', 'value': 'Functional'},
        ]
    })
    assert r.status_code == 400

    # add project rule w/ proper gear id
    # NOTE this is a legacy rule
    r = as_admin.post('/projects/' + project + '/rules', json=rule_json)
    assert r.ok
    rule = r.json()['_id']

    # get project rules (verify rule was added)
    r = as_admin.get('/projects/' + project + '/rules')
    assert r.ok
    assert r.json()[0]['gear_id'] == gear

    # try to get single project rule using non-existent rule id
    r = as_admin.get('/projects/' + project + '/rules/000000000000000000000000')
    assert r.status_code == 404

    # try to update rule of non-existent project
    r = as_admin.put('/projects/000000000000000000000000/rules/000000000000000000000000', json=bad_payload)
    assert r.status_code == 404

    # try to update non-existent rule
    r = as_admin.put('/projects/' + project + '/rules/000000000000000000000000', json=bad_payload)
    assert r.status_code == 404

    # try to update rule w/ read-only project perms
    r = with_user.session.put('/projects/' + project + '/rules/' + rule, json={'gear_id': gear})
    assert r.status_code == 403

    # try to update rule with invalid gear id
    r = as_admin.put('/projects/' + project + '/rules/' + rule, json={'gear_id': '000000000000000000000000'})
    assert r.status_code == 404

    # try to update rule with invalid gear config
    r = as_admin.put('/projects/' + project + '/rules/' + rule, json={'config': {'param': 'invalid'}})
    assert r.status_code == 422
    assert r.json()['reason'] == 'config did not match manifest'

    # update name of rule
    rule_name = 'improved-csv-trigger-rule'
    r = as_admin.put('/projects/' + project + '/rules/' + rule, json={'name': rule_name})
    assert r.ok

    # verify rule was updated
    r = as_admin.get('/projects/' + project + '/rules/' + rule)
    assert r.ok
    assert r.json()['name'] == rule_name

    # upload file that matches rule
    r = as_admin.post('/projects/' + project + '/files', files=file_form('test2.csv'))
    assert r.ok

    # test that job was created via rule and uses gear default config
    gear_jobs = [job for job in api_db.jobs.find({'gear_id': gear})]
    assert len(gear_jobs) == 1
    assert len(gear_jobs[0]['inputs']) == 1
    assert gear_jobs[0]['inputs'][0]['name'] == 'test2.csv'
    assert gear_jobs[0]['config']['config'] == {'param': 'default'}

    # update rule to have a custom config
    r = as_admin.put('/projects/' + project + '/rules/' + rule, json={'config': {'param': 'custom'}})
    assert r.ok

    # upload another file that matches rule
    r = as_admin.post('/projects/' + project + '/files', files=file_form('test3.csv'))
    assert r.ok

    # test that job was created via rule and custom config
    gear_jobs = [job for job in api_db.jobs.find({'gear_id': gear})]
    assert len(gear_jobs) == 2
    assert gear_jobs[1]['config']['config'] == {'param': 'custom'}

    # try to delete rule of non-existent project
    r = as_admin.delete('/projects/000000000000000000000000/rules/000000000000000000000000')
    assert r.status_code == 404

    # try to delete non-existent rule
    r = as_admin.delete('/projects/' + project + '/rules/000000000000000000000000')
    assert r.status_code == 404

    # try to delete rule w/ read-only project perms
    r = with_user.session.delete('/projects/' + project + '/rules/' + rule)
    assert r.status_code == 403

    # delete rule
    r = as_admin.delete('/projects/' + project + '/rules/' + rule)
    assert r.ok


    # add valid container.has-<something> project rule
    # NOTE this is a legacy rule
    r = as_admin.post('/projects/' + project + '/rules', json={
        'gear_id': gear,
        'name': 'txt-job-trigger-rule-with-classification',
        'any': [
            {'type': 'container.has-classification', 'value': 'functional'},
            {'type': 'container.has-classification', 'value': 'anatomical'}
        ],
        'all': [
            {'type': 'file.type', 'value': 'text'},
        ],
        'not': []
    })
    assert r.ok
    rule2 = r.json()['_id']

    # upload file that matches only part of rule
    r = as_admin.post('/projects/' + project + '/files', files=file_form('test3.txt'))
    assert r.ok

    # test that job was not created via rule
    gear_jobs = [job for job in api_db.jobs.find({'gear_id': gear})]
    assert len(gear_jobs) == 2 # still 2 from before

    # update test2.csv's metadata to include a valid classification to spawn job
    metadata = {
        'project':{
            'label': 'rule project',
            'files': [
                {
                    'name': 'test2.csv',
                    'classification': {'intent': ['functional']}
                }
            ]
        }
    }

    r = as_admin.post('/engine',
        params={'level': 'project', 'id': project},
        files=file_form(meta=metadata)
    )
    assert r.ok

    # Ensure file without type or classification does not cause issues with rule evalution
    # upload file that matches only part of rule
    r = as_admin.post('/projects/' + project + '/files', files=file_form('test3.notreal'))
    assert r.ok

    # test that only one job was created via rule
    gear_jobs = [job for job in api_db.jobs.find({'gear_id': gear})]
    assert len(gear_jobs) == 3
    assert len(gear_jobs[2]['inputs']) == 1
    assert gear_jobs[2]['inputs'][0]['name'] == 'test3.txt'

    # delete rule
    r = as_admin.delete('/projects/' + project + '/rules/' + rule2)
    assert r.ok

    # add regex rule
    # NOTE this is a legacy rule
    r = as_admin.post('/projects/' + project + '/rules', json={
        'gear_id': gear,
        'name': 'file-classification-regex',
        'any': [],
        'not': [],
        'all': [
            {'type': 'file.name', 'value': 'test\d+\.(csv|txt)', 'regex': True},
        ]
    })
    assert r.ok
    rule3 = r.json()['_id']

    # upload file matching regex rule
    r = as_admin.post('/projects/' + project + '/files', files=file_form('test999.txt'))
    assert r.ok

    # test that job was created via regex rule
    gear_jobs = [job for job in api_db.jobs.find({'gear_id': gear})]
    assert len(gear_jobs) == 4

    # delete rule
    r = as_admin.delete('/projects/' + project + '/rules/' + rule3)
    assert r.ok


def test_context_input_rule(randstr, data_builder, default_payload, api_db, as_admin, file_form):
    project = data_builder.create_project()
    session = data_builder.create_session(project=project)
    acquisition = data_builder.create_acquisition(session=session)

    gear_name = randstr()
    gear_doc = default_payload['gear']
    gear_doc['gear']['name'] = gear_name
    gear_doc['gear']['inputs'] = {
        'A': {
            'base': 'context'
        },
        'text-file': {
            'base': 'file',
            'type': {'enum': ['text']}
        }
    }

    r = as_admin.post('/gears/' + gear_name, json=gear_doc)
    assert r.ok
    gear = r.json()['_id']

    r = as_admin.post('/projects/' + project + '/rules', json={
        'gear_id': gear,
        'name': 'context-input-trigger-rule',
        'any': [],
        'not': [],
        'all': [{'type': 'file.type', 'value': 'text'}],
    })
    assert r.ok
    rule = r.json()['_id']

    # Create job with no context
    r = as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('test.txt'))
    assert r.ok

    # Verify that job was created
    gear_jobs = [job for job in api_db.jobs.find({'gear_id': gear})]
    assert len(gear_jobs) == 1

    job1 = gear_jobs[0]
    job1_id = job1['_id']

    assert 'A' in job1['config']['inputs']
    assert job1['config']['inputs']['A']['found'] == False

    # Create context value on session
    r = as_admin.post('/sessions/' + session + '/info', json={
        'set': {
            'context': {
                'A': 'session_context_value'
            }
        }
    })
    assert r.ok

    # Create another job at acquisition level
    r = as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('test2.txt'))
    assert r.ok

    # Create job at project level
    r = as_admin.post('/projects/' + project + '/files', files=file_form('test3.txt'))
    assert r.ok

    session_job = None
    project_job = None

    gear_jobs = [job for job in api_db.jobs.find({'gear_id': gear})]
    assert len(gear_jobs) == 3
    for job in gear_jobs:
        fname = job['config']['inputs']['text-file']['location']['name']
        if fname == 'test2.txt':
            session_job = job
        elif fname == 'test3.txt':
            project_job = job

    assert session_job is not None
    assert 'A' in session_job['config']['inputs']
    assert session_job['config']['inputs']['A']['found'] == True
    assert session_job['config']['inputs']['A']['value'] == 'session_context_value'

    assert project_job is not None
    assert 'A' in project_job['config']['inputs']
    assert project_job['config']['inputs']['A']['found'] == False

    # Cleanup
    r = as_admin.delete('/gears/' + gear)
    assert r.ok

    # must remove jobs manually because gears were added manually
    api_db.jobs.remove({'gear_id': {'$in': [gear]}})


def test_disabled_rules(randstr, data_builder, api_db, as_admin, file_form):
    # Create gear, project and *disabled* rule triggering on any csv (once enabled)
    gear = data_builder.create_gear(gear={'version': '0.0.1'})
    project = data_builder.create_project()
    r = as_admin.post('/projects/' + project + '/rules', json={
        'gear_id': gear,
        'name': 'csv-job-trigger-rule',
        'any': [],
        'not': [],
        'all': [{'type': 'file.type', 'value': 'tabular data'}],
        'disabled': True,
    })
    assert r.ok
    rule = r.json()['_id']

    # Upload 1st file (while rule is disabled)
    r = as_admin.post('/projects/' + project + '/files', files=file_form('test1.csv'))
    assert r.ok

    # Verify that no jobs were created
    gear_jobs = [job for job in api_db.jobs.find({'gear_id': gear})]
    assert len(gear_jobs) == 0

    # Enable rule
    r = as_admin.put('/projects/' + project + '/rules/' + rule, json={'disabled': False})
    assert r.ok

    # Upload 1st file (rule is now enabled)
    r = as_admin.post('/projects/' + project + '/files', files=file_form('test2.csv'))
    assert r.ok

    # Verify that a job was created
    gear_jobs = [job for job in api_db.jobs.find({'gear_id': gear})]
    assert len(gear_jobs) == 1
    assert len(gear_jobs[0]['inputs']) == 1
    assert gear_jobs[0]['inputs'][0]['name'] == 'test2.csv'

def test_auto_update_rules(data_builder, api_db, as_admin):
    # Create gear and project
    gear_config = {'param': {'type': 'boolean', 'default': True}}
    gearv1 = data_builder.create_gear(gear={'name': 'auto-update-gear', 'version': '0.0.1', 'config': gear_config})
    project = data_builder.create_project()

    # Try posting rule with config and that auto-updates
    r = as_admin.post('/projects/' + project + '/rules', json={
        'gear_id': gearv1,
        'name': 'test-auto-update-rule',
        'any': [],
        'not': [],
        'all': [{'type': 'file.type', 'value': 'tabular data'}],
        'disabled': False,
        'config': {'param': True},
        'auto_update': True
    })
    assert r.status_code == 400

    # Post with only auto-update
    r = as_admin.post('/projects/' + project + '/rules', json={
        'gear_id': gearv1,
        'name': 'test_auto_update_rule',
        'any': [],
        'not': [],
        'all': [{'type': 'file.type', 'value': 'tabular data'}],
        'disabled': False,
        'auto_update': True
    })
    assert r.ok
    rule_id = r.json()['_id']

    r = as_admin.get('/projects/' + project + '/rules/' + rule_id)
    assert r.ok
    assert not r.json().get('config')
    assert r.json().get('auto_update')

    # Try to give it a config when it already has auto-update set to True
    r = as_admin.put('/projects/' + project + '/rules/' + rule_id, json={
        'config': {'param': True}
    })
    assert r.status_code == 400

    # Unset auto_update and set config
    r = as_admin.put('/projects/' + project + '/rules/' + rule_id, json={
        'auto_update': False,
        'config': {'param': True}
    })
    assert r.ok

    # Unset config
    r = as_admin.put('/projects/' + project + '/rules/' + rule_id, json={
        'config': {}
    })
    assert r.ok


    r = as_admin.get('/projects/' + project + '/rules/' + rule_id)
    assert r.ok
    assert not r.json().get('config')
    assert not r.json().get('auto_update')

    # Try to set both with put
    r = as_admin.put('/projects/' + project + '/rules/' + rule_id, json={
        'config': {'param': True},
        'auto_update': True
    })
    assert r.status_code == 400

    # Set Config
    r = as_admin.put('/projects/' + project + '/rules/' + rule_id, json={
        'config': {'param': True}
    })
    assert r.ok

    r = as_admin.get('/projects/' + project + '/rules/' + rule_id)
    assert r.ok
    assert r.json().get('config')
    assert not r.json().get('auto_update')

    # Set auto_update and check that config was cleared
    r = as_admin.put('/projects/' + project + '/rules/' + rule_id, json={
        'auto_update': True
    })
    assert r.ok

    r = as_admin.get('/projects/' + project + '/rules/' + rule_id)
    assert r.ok
    assert not r.json().get('config')
    assert r.json().get('auto_update')

    # Unset auto_update, bump gear, try to set auto_update
    r = as_admin.put('/projects/' + project + '/rules/' + rule_id, json={
        'auto_update': False
    })
    assert r.ok

    gearv2 = data_builder.create_gear(gear={'name': 'auto-update-gear', 'version': '0.0.2', 'config': gear_config})


    r = as_admin.get('/projects/' + project + '/rules/' + rule_id)
    assert r.ok
    assert r.json().get('gear_id') == gearv1

    r = as_admin.put('/projects/' + project + '/rules/' + rule_id, json={
        'auto_update': True
    })
    assert r.status_code == 400

    # Update rule gear_id, set auto-date, bump gear
    r = as_admin.put('/projects/' + project + '/rules/' + rule_id, json={
        'gear_id': gearv2,
        'auto_update': True
    })
    assert r.ok

    r = as_admin.get('/projects/' + project + '/rules/' + rule_id)
    assert r.ok
    assert r.json().get('gear_id') == gearv2

    gearv3 = data_builder.create_gear(gear={'name': 'auto-update-gear', 'version': '0.0.3', 'config': gear_config})

    r = as_admin.get('/projects/' + project + '/rules/' + rule_id)
    assert r.ok
    assert r.json().get('gear_id') == gearv3

    # Try to bump down auto_update gear
    r = as_admin.put('/projects/' + project + '/rules/' + rule_id, json={
        'gear_id': gearv1
    })
    assert r.status_code == 400

    # Set gear to invalid
    api_db.gears.update_one({'_id':  bson.ObjectId(gearv3)}, {'$set': {'gear.custom.flywheel.invalid': True}})

    # Bump down auto_update gear to latest valid gear
    r = as_admin.put('/projects/' + project + '/rules/' + rule_id, json={
        'gear_id': gearv2
    })
    assert r.ok


def test_rules_rerun_after_file_replace(randstr, data_builder, file_form, as_root, as_admin, with_user, api_db):
    """
    Always run jobs from rules where at least one of the inputs were "replaced" during the upload.

    When a file is uploaded to a container that already has a file with the same name,
    the original file is replaced with a new one in mongo.
      * Except when the upload type is "reaper", and the hash is the same. In that case the
        file upload is ignored.

    In the rule evaluation step, the rules are evaluated against the container's state before
    the upload (set A) and after (set B). Jobs in set B that are not in set A are queued if
    no files were replaced during the upload.

    If files were replaced, any job in set A that has a replaced file as input is also queued.

    In this test I set up a rule system similar to the default rule configuration on a new FW project,
    replacing the initial dicom after all rules and gears have completed, ensure the entire "suite"
    runs again.
    """

    def simulate_engine_run(job_id, acquisition_id, files):
        """
        Given a job id and a fileform, simulate the running of a job, ending with an engine upload
        """
        job = as_root.get('/jobs/next').json()
        assert job['id'] == job_id # ensure jobs/next gives expected job

        assert as_root.post('/engine',
            params={'level': 'acquisition', 'id': acquisition_id, 'job': job_id},
            files=files
        ).ok
        assert as_root.put('/jobs/' + job_id, json={'state': 'complete'}).ok


    # Create gears
    classifier_gear = data_builder.create_gear(gear={'version': '0.0.1', 'name': 'classifier-gear'})
    converter_gear = data_builder.create_gear(gear={'version': '0.0.1', 'name': 'converter-gear'})
    qa_gear = data_builder.create_gear(gear={'version': '0.0.1', 'name': 'qa-gear'})

    # Create group and project
    group = data_builder.create_group()
    project_label = 'rerun-rule-project'
    project = data_builder.create_project(group=group, label='rerun-rule-project')

    # UID and filename used for repeat reaper uploads
    dicom_file_name = 'some_dicom.dcm.zip'
    nifti_file_name = 'some_dicom.nii.gz'
    qa_file_name = 'qa_report.qa.png'
    session_uid = 'rerun-rule-session-uid'

    # Run classifier gear when new dicom is added
    classifier_rule = {
        'gear_id': classifier_gear,
        'name': 'classifer-rule',
        'any': [],
        'not': [],
        'all': [
            {'type': 'file.type', 'value': 'dicom'}
        ]
    }

    # Run converter gear when classifier has complete
    converter_rule = {
        'gear_id': converter_gear,
        'name': 'converter-rule',
        'any': [],
        'not': [
            {'type': 'file.classification', 'value': 'Non-Image'}
        ],
        'all': [
            {'type': 'file.type', 'value': 'dicom'},
            {'regex': True, 'type': 'file.classification', 'value': '.+'}
        ]
    }

    # Run QA gear when converter has complete
    qa_rule = {
        'gear_id': qa_gear,
        'name': 'qa-rule',
        'any': [
            {'type': 'file.classification', 'value': 'functional'}
        ],
        'not': [],
        'all': [
            {'type': 'file.type', 'value': 'nifti'}
        ]
    }

    # add rules to project
    assert as_admin.post('/projects/' + project + '/rules', json=classifier_rule).ok
    assert as_admin.post('/projects/' + project + '/rules', json=converter_rule).ok
    assert as_admin.post('/projects/' + project + '/rules', json=qa_rule).ok


    # get project rules (verify rules were added)
    r = as_admin.get('/projects/' + project + '/rules')
    assert r.ok
    assert len(r.json()) == 3

    # upload initial dicom via reaper
    r = as_admin.post('/upload/reaper', files=file_form(
        dicom_file_name,
        meta={
            'group': {'_id': group},
            'project': {'label': project_label},
            'session': {'uid': session_uid},
            'acquisition': {
                'uid': session_uid,
                'files': [{'name': dicom_file_name}]
            }
        })
    )
    assert r.ok

    # Ensure session and acquisition created, dicom file uploaded
    r = as_admin.get('/projects/' + project + '/sessions')
    assert r.ok
    assert len(r.json()) == 1
    session = r.json()[0]['_id']

    r = as_admin.get('/sessions/' + session + '/acquisitions')
    assert r.ok
    assert len(r.json()) == 1
    assert len(r.json()[0]['files']) == 1
    acquisition = r.json()[0]['_id']


    # Test that classifier-gear job was created via rule
    jobs = list(api_db.jobs.find({'gear_id': classifier_gear}))
    assert len(jobs) == 1
    job_id = str(jobs[0]['_id'])

    # Simulate engine run
    payload = file_form(meta={
        'acquisition':{
            'files':[
                {
                    'name': dicom_file_name,
                    'classification': {'Intent': ['Functional']}
                }
            ]
        }
    })
    simulate_engine_run(job_id, acquisition, payload)


    # Test that converter-gear job was created via rule
    jobs = list(api_db.jobs.find({'gear_id': converter_gear}))
    assert len(jobs) == 1
    job_id = str(jobs[0]['_id'])

    # Simulate engine runs
    payload = file_form(nifti_file_name, meta={
        'acquisition':{
            'files':[
                {
                    'name': nifti_file_name,
                    'classification': {'Intent': ['Functional']}
                }
            ]
        }
    })
    simulate_engine_run(job_id, acquisition, payload)

    # Test that qa-gear job was created via rule
    jobs = list(api_db.jobs.find({'gear_id': qa_gear}))
    assert len(jobs) == 1
    job_id = str(jobs[0]['_id'])

    # Simulate engine runs
    payload = file_form(qa_file_name, meta={
        'acquisition':{
            'files':[
                {
                    'name': qa_file_name
                }
            ]
        }
    })
    simulate_engine_run(job_id, acquisition, payload)

    # Ensure all 3 files exist on acquisition
    assert len(as_admin.get('/acquisitions/' + acquisition).json()['files']) == 3

    # upload dicom with same hash via reaper
    r = as_admin.post('/upload/reaper', files=file_form(
        dicom_file_name,
        meta={
            'group': {'_id': group},
            'project': {'label': project_label},
            'session': {'uid': session_uid},
            'acquisition': {
                'uid': session_uid,
                'files': [{'name': dicom_file_name}]
            }
        })
    )
    assert r.ok

    # Ensure no jobs were queued
    assert as_root.get('/jobs/next').status_code == 400

    # Ensure file still has classification
    r = as_root.get('/acquisitions/' + acquisition + '/files/' + dicom_file_name + '/info')
    assert 'Functional' in r.json()['classification']['Intent']

    # Upload dicom with different hash via reaper
    r = as_admin.post('/upload/reaper', files=file_form(
        (dicom_file_name, 'new_file_content'),
        meta={
            'group': {'_id': group},
            'project': {'label': project_label},
            'session': {'uid': session_uid},
            'acquisition': {
                'uid': session_uid,
                'files': [{'name': dicom_file_name}]
            }
        })
    )
    assert r.ok

    # Ensure file now does not have classification
    r = as_root.get('/acquisitions/' + acquisition + '/files/' + dicom_file_name + '/info')
    assert not r.json().get('classification')

    # Test that classifier-gear job was created via rule
    jobs = list(api_db.jobs.find({'gear_id': classifier_gear}))
    assert len(jobs) == 2
    job_id = str(jobs[1]['_id'])

    # Simulate engine run
    payload = file_form(meta={
        'acquisition':{
            'files':[
                {
                    'name': dicom_file_name,
                    'classification': {'Intent': ['Functional']}
                }
            ]
        }
    })
    simulate_engine_run(job_id, acquisition, payload)

    # Test that converter-gear job was created via rule
    jobs = list(api_db.jobs.find({'gear_id': converter_gear}))
    assert len(jobs) == 2
    job_id = str(jobs[1]['_id'])

    # Simulate engine run
    payload = file_form((nifti_file_name, 'new_nifti_content'), meta={
        'acquisition':{
            'files':[
                {
                    'name': nifti_file_name,
                    'classification': {'Intent': ['Functional']}
                }
            ]
        }
    })
    simulate_engine_run(job_id, acquisition, payload)

    # Test that qa-gear job was created via rule
    jobs = list(api_db.jobs.find({'gear_id': qa_gear}))
    assert len(jobs) == 2

    data_builder.delete_group(group, recursive=True)


def test_optional_input_gear_rules(default_payload, data_builder, api_db, as_admin, as_root, file_form):
    # Create gear and project
    gear_doc = default_payload['gear']
    # Try creating batch with optional inputs and api-key input
    gear_doc['gear']['inputs'] = {
        'text': {
            'base': 'file',
            'name': {'pattern': '^.*.txt$'},
            'size': {'maximum': 100000}
        },
        'csv': {
            'base': 'file',
            'name': {'pattern': '^.*.csv$'},
            'size': {'maximum': 100000},
            'optional': True
        },
        'api_key': {
            'base': 'api-key',
            'read-only': True
        }
    }

    gear = data_builder.create_gear(gear=gear_doc['gear'])
    project = data_builder.create_project()
    acquisition = data_builder.create_acquisition()

    r = as_admin.get('/gears', params={'filter': ['single_input', 'read_only_key']})
    assert r.ok
    assert r.json()[0]['_id'] == gear

    # Try posting rule with config and that auto-updates
    r = as_admin.post('/projects/' + project + '/rules', json={
        'gear_id': gear,
        'name': 'test-optional-input-rule',
        'any': [],
        'not': [],
        'all': [{'type': 'file.type', 'value': 'text'}],
        'disabled': False,
        'auto_update': True
    })
    assert r.ok
    rule_id = r.json()['_id']

    # create job
    assert as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('test.txt')).ok

    r = as_root.get('/jobs/next')
    assert r.ok
    job_id = r.json()['id']
