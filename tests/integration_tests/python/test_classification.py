def test_modalities(data_builder, as_admin, as_user):

    payload = {
        '_id': 'MR',
        'classification': {
            'Intent': ["Structural", "Functional", "Localizer"],
            'Contrast': ["B0", "B1", "T1", "T2"]
        }
    }

    # test adding new modality
    r = as_admin.post('/modalities', json=payload)
    assert r.ok
    assert r.json()['_id'] == payload['_id']
    modality1 = payload['_id']

    # get specific modality
    r = as_user.get('/modalities/' + modality1)
    assert r.ok
    assert r.json() == payload

    # try replacing existing modality via POST
    r = as_admin.post('/modalities', json=payload)
    assert r.status_code == 409

    # list modalities as non-admin
    r = as_user.get('/modalities')
    assert r.ok
    modalities = r.json()
    assert len(modalities) == 1
    assert modalities[0]['_id'] == modality1

    # replace existing modality
    update = {
        'classification': {
            'Intent': ["new", "stuff"]
        }
    }
    r = as_admin.put('/modalities/' + modality1, json=update)
    assert r.ok
    r = as_admin.get('/modalities/' + modality1)
    assert r.ok
    assert r.json()['classification'] == update['classification']

    # try to replace missing modality
    r = as_admin.put('/modalities/' + 'madeup', json=update)
    assert r.status_code == 404

    # delete modality
    r = as_admin.delete('/modalities/' + modality1)
    assert r.ok

    # try to delete missing modality
    r = as_admin.delete('/modalities/' + modality1)
    assert r.status_code == 404


def test_edit_file_classification(data_builder, as_admin, as_user, file_form):

    ## Setup

    # Add file
    project = data_builder.create_project()
    file_name = 'test_file.txt'

    r = as_admin.post('/projects/' + project + '/files', files=file_form(file_name))
    assert r.ok

    r = as_admin.get('/projects/' + project + '/files/' + file_name + '/info')
    assert r.ok
    assert r.json()['classification'] == {}


    # add modality information
    payload = {
        '_id': 'MR',
        'classification': {
            'Intent': ["Structural", "Functional", "Localizer"],
            'Contrast': ["B0", "B1", "T1", "T2"]
        }
    }

    r = as_admin.post('/modalities', json=payload)
    assert r.ok
    assert r.json()['_id'] == payload['_id']
    modality1 = payload['_id']

    # Add modality to file
    r = as_admin.put('/projects/' + project + '/files/' + file_name, json={
        'modality': 'MR'
    })


    ## Classification editing

    # Send improper payload
    r = as_admin.post('/projects/' + project + '/files/' + file_name + '/classification', json={
        'delete': ['this', 'is'],
        'replace': {'not_going': 'to_happen'}
    })
    assert r.status_code == 400

    # Send improper payload
    r = as_admin.post('/projects/' + project + '/files/' + file_name + '/classification', json={
        'delete': ['should', 'be', 'a', 'map']
    })
    assert r.status_code == 400

    # Send improper payload
    r = as_admin.post('/projects/' + project + '/files/' + file_name + '/classification', json={
        'set': 'cannot do this'
    })
    assert r.status_code == 400

    # Attempt full replace of classification
    file_cls = {
        'Intent':   ['Structural'],
        'Contrast': ['B1', 'T1'],
        'Custom':   ['Custom Value']
    }


    r = as_admin.post('/projects/' + project + '/files/' + file_name + '/classification', json={
        'replace': file_cls
    })
    assert r.ok

    r = as_admin.get('/projects/' + project + '/files/' + file_name + '/info')
    assert r.ok
    assert r.json()['classification'] == file_cls


    # Use 'add' to add new key to list
    r = as_admin.post('/projects/' + project + '/files/' + file_name + '/classification', json={
        'add': {'Intent': ['Functional']}
    })
    assert r.ok

    file_cls['Intent'].append('Functional')
    r = as_admin.get('/projects/' + project + '/files/' + file_name + '/info')
    assert r.ok
    assert r.json()['classification'] == file_cls


    # Remove item from list
    r = as_admin.post('/projects/' + project + '/files/' + file_name + '/classification', json={
        'delete': {'Intent': ['Structural'],
                   'Contrast': ['B1']}
    })
    assert r.ok

    file_cls['Intent'] = ['Functional']
    file_cls['Contrast'] = ['T1']
    r = as_admin.get('/projects/' + project + '/files/' + file_name + '/info')
    assert r.ok
    assert r.json()['classification'] == file_cls

    # Add and delete from same list
    r = as_admin.post('/projects/' + project + '/files/' + file_name + '/classification', json={
        'add': {'Intent': ['Localizer']},
        'delete': {'Intent': ['Functional']}
    })
    assert r.ok

    file_cls['Intent'] = ['Localizer']
    r = as_admin.get('/projects/' + project + '/files/' + file_name + '/info')
    assert r.ok
    assert r.json()['classification'] == file_cls

    # Use 'delete' on keys that do not exist
    r = as_admin.post('/projects/' + project + '/files/' + file_name + '/classification', json={
        'delete': {'Intent': ['Structural', 'Functional']}
    })
    assert r.ok

    r = as_admin.get('/projects/' + project + '/files/' + file_name + '/info')
    assert r.ok
    assert r.json()['classification'] == file_cls

    # Use 'add' on keys that already exist
    r = as_admin.post('/projects/' + project + '/files/' + file_name + '/classification', json={
        'add': {'Intent': ['Localizer']}
    })
    assert r.ok

    r = as_admin.get('/projects/' + project + '/files/' + file_name + '/info')
    assert r.ok
    assert r.json()['classification'] == file_cls

    # Ensure lowercase gets formatted in correct format via modality's classification
    r = as_admin.post('/projects/' + project + '/files/' + file_name + '/classification', json={
        'add': {'contrast': ['t2', 'b0'], 'custom': ['lowercase']}
    })
    assert r.ok

    file_cls['Contrast'].extend(['T2', 'B0'])
    file_cls['Custom'].append('lowercase')
    r = as_admin.get('/projects/' + project + '/files/' + file_name + '/info')
    assert r.ok
    assert r.json()['classification'] == file_cls

    # Ensure lowercase gets formatted in correct format via modality's classification
    r = as_admin.post('/projects/' + project + '/files/' + file_name + '/classification', json={
        'delete': {'contrast': ['t2'], 'custom': ['lowercase']}
    })
    assert r.ok

    file_cls['Contrast'] = ['T1', 'B0']
    file_cls['Custom'] = ['Custom Value']
    r = as_admin.get('/projects/' + project + '/files/' + file_name + '/info')
    assert r.ok
    assert r.json()['classification'] == file_cls

    # Try to replace with bad key names and values
    r = as_admin.post('/projects/' + project + '/files/' + file_name + '/classification', json={
        'replace': {
            'made-up': ['fake'],
            'Intent': ['not real']
        }
    })
    assert r.status_code == 422
    assert r.json()['unaccepted_keys'] == ['made-up:fake', 'Intent:not real']


    # Use 'replace' to set file classification to {}
    r = as_admin.post('/projects/' + project + '/files/' + file_name + '/classification', json={
        'replace': {}
    })
    assert r.ok

    r = as_admin.get('/projects/' + project + '/files/' + file_name + '/info')
    assert r.ok
    assert r.json()['classification'] == {}

    # Add Custom field for unknown modality
    r = as_admin.put('/projects/' + project + '/files/' + file_name, json={
        'modality': 'new unknown'
    })

    file_cls = {
        'Custom':   ['Custom Value']
    }

    # allows custom fields
    r = as_admin.post('/projects/' + project + '/files/' + file_name + '/classification', json={
        'replace': file_cls
    })
    assert r.ok

    r = as_admin.get('/projects/' + project + '/files/' + file_name + '/info')
    assert r.ok
    assert r.json()['classification'] == file_cls

    # does not allow non-custom fields
    file_cls = {
        'Intent':   ['Structural']
    }

    r = as_admin.post('/projects/' + project + '/files/' + file_name + '/classification', json={
        'replace': file_cls
    })
    assert r.status_code == 422

    # Update modality and classification at the same time
    r = as_admin.post('/projects/' + project + '/files/' + file_name + '/classification', json={
        'modality': modality1,
        'replace': file_cls
    })
    assert r.ok

    r = as_admin.get('/projects/' + project + '/files/' + file_name + '/info')
    assert r.ok
    assert r.json()['classification'] == file_cls
    assert r.json()['modality'] == modality1


    # Attempt to add to nonexistent file
    r = as_admin.post('/projects/' + project + '/files/' + 'madeup.txt' + '/classification', json={
        'add': {'Intent': ['Localizer']}
    })
    assert r.status_code == 404

    # Attempt to delete from nonexistent file
    r = as_admin.post('/projects/' + project + '/files/' + 'madeup.txt' + '/classification', json={
        'delete': {'Intent': ['Localizer']}
    })
    assert r.status_code == 404

    # Attempt to replae nonexistent file
    r = as_admin.post('/projects/' + project + '/files/' + 'madeup.txt' + '/classification', json={
        'replace': {'Intent': ['Localizer']}
    })
    assert r.status_code == 404

    # Clean up modality
    r = as_admin.delete('/modalities/' + modality1)
    assert r.ok



def test_classification_change_triggers_job(randstr, data_builder, as_admin, api_db, file_form):

    ## SETUP gear, rule, file, modality

    gear_name = randstr()
    gear = data_builder.create_gear(gear={'name': gear_name, 'version': '0.0.1'})

    # Add rule
    rule = {
        'alg': gear_name,
        'name': 'classification-job-trigger-rule',
        'any': [],
        'all': [
            {'type': 'file.classification', 'value': 'Localizer'},
        ]
    }

    r = as_admin.post('/site/rules', json=rule)
    assert r.ok
    rule_id = r.json()['_id']

    # Add modality information
    payload = {
        '_id': 'MR',
        'classification': {
            'Intent': ["Structural", "Functional", "Localizer"],
            'Contrast': ["B0", "B1", "T1", "T2"]
        }
    }

    r = as_admin.post('/modalities', json=payload)
    assert r.ok
    assert r.json()['_id'] == payload['_id']
    modality1 = payload['_id']

    # Add container and file
    acquisition = data_builder.create_acquisition()
    file_name = 'test_file.txt'
    r = as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form(file_name))
    assert r.ok

    # Add modality to file
    r = as_admin.put('/acquisitions/' + acquisition + '/files/' + file_name, json={
        'modality': 'MR'
    })

    ## SETUP COMPLETE


    # Test adding classification that doesn't trigger rule
    r = as_admin.post('/acquisitions/' + acquisition + '/files/' + file_name + '/classification', json={
        'add': {'Intent': ['Functional']}
    })
    assert r.ok
    assert r.json()['jobs_spawned'] == 0


    # Test adding classification that does trigger rule
    r = as_admin.post('/acquisitions/' + acquisition + '/files/' + file_name + '/classification', json={
        'add': {'Intent': ['Localizer']}
    })
    assert r.ok
    assert r.json()['jobs_spawned'] == 1

    # Test that job was created via rule
    gear_jobs = [job for job in api_db.jobs.find({'gear_id': gear})]
    assert len(gear_jobs) == 1
    assert len(gear_jobs[0]['inputs']) == 1
    assert gear_jobs[0]['inputs'][0]['name'] == file_name


    ## CLEANUP

    # Clean up modality
    r = as_admin.delete('/modalities/' + modality1)
    assert r.ok

    # Clean up rule
    r = as_admin.delete('/site/rules/' + rule_id)








