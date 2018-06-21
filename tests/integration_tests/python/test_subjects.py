import copy

import bson


def test_subject_collection(data_builder, api_db, as_admin):
    # create simple session w/ subject
    session = data_builder.create_session(subject={'code': 'test', 'age': 123})

    # verify subject is created in separate collection
    session_doc = api_db.sessions.find_one({'_id': bson.ObjectId(session)})
    assert type(session_doc['subject']) is bson.ObjectId
    assert session_doc['age'] == 123
    subject_doc = api_db.subjects.find_one({'_id': session_doc['subject']})
    assert subject_doc['code'] == 'test'
    assert subject_doc['project'] == session_doc['project']
    assert subject_doc['permissions'] == session_doc['permissions']
    assert 'created' in subject_doc
    assert 'modified' in subject_doc
    assert 'age' not in subject_doc
    subject_id = str(subject_doc['_id'])

    # verify it's joined by the api
    r = as_admin.get('/sessions/' + session)
    assert r.ok
    assert r.json()['subject']['age'] == 123

    # create new session w/ same subject - implicit subject update
    # NOTE session_2.age will not be populated (even though implicitly known)
    session_2 = data_builder.create_session(subject={'code': 'test', 'sex': 'female'})

    # verify the same subject was used
    session_doc_2 = api_db.sessions.find_one({'_id': bson.ObjectId(session_2)})
    assert session_doc['subject'] == session_doc_2['subject']

    # verify updates were applied
    subject_doc_2 = api_db.subjects.find_one({'_id': session_doc['subject']})
    assert subject_doc_2['sex'] == 'female'

    # modify subject on the session
    r = as_admin.put('/sessions/' + session, json={'project': str(session_doc['project'])})
    assert r.ok
    r = as_admin.get('/sessions/' + session)
    assert r.ok
    assert r.json()['subject']['_id'] == subject_id


def test_subject_endpoints(data_builder, as_admin, as_public, file_form):
    # prep
    def create_user_accessor(email):
        user = data_builder.create_user(email=email, api_key=email)
        as_user = copy.deepcopy(as_public)
        as_user.headers.update({'Authorization': 'scitran-user ' + email})
        return as_user

    project = data_builder.create_project()
    as_rw = create_user_accessor('rw-user@test.com')
    rw_id = as_rw.get('/users/self').json()['_id']
    as_ro = create_user_accessor('ro-user@test.com')
    ro_id = as_ro.get('/users/self').json()['_id']
    assert as_admin.post('/projects/' + project + '/permissions', json={'_id': rw_id, 'access': 'rw'}).ok
    assert as_admin.post('/projects/' + project + '/permissions', json={'_id': ro_id, 'access': 'ro'}).ok

    # GET /subjects no data
    r = as_admin.get('/subjects')
    assert r.ok
    assert type(r.json()) is list

    # POST /subjects
    r = as_admin.post('/subjects', json={'project': project, 'code': 'test', 'firstname': 'foo', 'sex': 'male'})
    assert r.ok
    subject = r.json()['_id']

    # POST /subjects permissions
    assert as_public.post('/subjects', json={'project': project, 'code': 'code'}).status_code == 403
    assert as_ro.post('/subjects', json={'project': project, 'code': 'code'}).status_code == 403
    r = as_rw.post('/subjects', json={'project': project, 'code': 'code'})
    assert r.ok
    subject_2 = r.json()['_id']

    # GET /subjects
    r = as_admin.get('/subjects')
    assert r.ok
    assert subject in [s['_id'] for s in r.json()]
    assert not any('firstname' in s for s in r.json())
    assert not any('sex' in s for s in r.json())

    # GET /subjects permissions
    r = as_public.get('/subjects')
    assert r.ok
    assert r.json() == []
    r = as_ro.get('/subjects')
    assert r.ok
    assert subject in [s['_id'] for s in r.json()]
    r = as_rw.get('/subjects')
    assert r.ok
    assert subject in [s['_id'] for s in r.json()]

    # GET /subjects/x
    r = as_admin.get('/subjects/' + subject)
    assert r.ok
    assert r.json()['firstname'] == 'foo'
    assert r.json()['sex'] == 'male'

    # GET /subjects/x permissions
    assert as_public.get('/subjects/' + subject).status_code == 403
    assert as_ro.get('/subjects/' + subject).ok
    assert as_rw.get('/subjects/' + subject).ok

    # PUT /subjects/x
    r = as_admin.put('/subjects/' + subject, json={'sex': 'female'})
    assert r.ok

    # PUT /subjects/x permissions
    # TODO fix containerauth to 403 on public put (TypeError: f() got an unexpected keyword argument 'r_payload')
    assert as_public.put('/subjects/' + subject, json={'sex': 'female'}).status_code == 500  # should be 403
    assert as_ro.put('/subjects/' + subject, json={'sex': 'female'}).status_code == 403
    assert as_rw.put('/subjects/' + subject, json={'sex': 'female'}).ok

    # verify PUT /subjects/x
    r = as_admin.get('/subjects/' + subject)
    assert r.ok
    assert r.json()['sex'] == 'female'

    # POST /subjects/x/files
    r = as_admin.post('/subjects/' + subject + '/files', files=file_form('test.txt'))
    assert r.ok

    # POST /subjects/x/files permissions
    assert as_public.post('/subjects/' + subject + '/files', files=file_form('test.txt')).status_code == 403
    assert as_ro.post('/subjects/' + subject + '/files', files=file_form('test.txt')).status_code == 403
    assert as_rw.post('/subjects/' + subject + '/files', files=file_form('test.txt')).ok

    # verify POST /subjects/x/files
    r = as_admin.get('/subjects/' + subject)
    assert r.ok
    assert 'test.txt' in [f['name'] for f in r.json()['files']]

    # GET /subjects/x/files/y
    r = as_admin.get('/subjects/' + subject + '/files/test.txt')
    assert r.ok
    assert r.text == 'test\ndata\n'

    # DELETE /subjects/x
    r = as_admin.delete('/subjects/' + subject)
    assert r.ok

    # DELETE /subjects/x permissions
    assert as_public.delete('/subjects/' + subject_2).status_code == 403
    assert as_ro.delete('/subjects/' + subject_2).status_code == 403
    assert as_rw.delete('/subjects/' + subject_2).ok

    # verify DELETE /subjects/x
    r = as_admin.get('/subjects')
    assert subject not in [s['_id'] for s in r.json()]

    r = as_admin.get('/subjects/' + subject)
    assert r.status_code == 404

    # prep
    session_1 = data_builder.create_session(subject={'code': 'test-subj'})
    session_2 = data_builder.create_session(subject={'code': 'test-subj'}, public=False)
    subject = as_admin.get('/sessions/' + session_1).json()['subject']['_id']
    assert subject == as_admin.get('/sessions/' + session_2).json()['subject']['_id']

    # GET /projects/x/subjects
    r = as_admin.get('/projects/' + project + '/subjects')
    assert r.ok
    assert subject in [s['_id'] for s in r.json()]

    # GET /projects/x/subjects permissions
    r = as_public.get('/projects/' + project + '/subjects')
    assert r.ok
    assert r.json() == []
    r = as_ro.get('/projects/' + project + '/subjects')
    assert r.ok
    assert subject in [s['_id'] for s in r.json()]
    r = as_rw.get('/projects/' + project + '/subjects')
    assert r.ok
    assert subject in [s['_id'] for s in r.json()]

    # GET /subjects/x/sessions
    r = as_admin.get('/subjects/' + subject + '/sessions')
    assert r.ok
    assert set([s['_id'] for s in r.json()]) == set([session_1, session_2])

    # GET /subjects/x/sessions permissions
    r = as_public.get('/subjects/' + subject + '/sessions')
    assert r.ok
    assert set([s['_id'] for s in r.json()]) == set([s['_id'] for s in r.json()]) == set([session_1])
    r = as_ro.get('/subjects/' + subject + '/sessions')
    assert r.ok
    assert set([s['_id'] for s in r.json()]) == set([session_1, session_2])
    r = as_rw.get('/subjects/' + subject + '/sessions')
    assert r.ok
    assert set([s['_id'] for s in r.json()]) == set([session_1, session_2])


def test_subject_notes(data_builder, as_admin, as_public, file_form):
    # prep
    def create_user_accessor(email):
        user = data_builder.create_user(email=email, api_key=email)
        as_user = copy.deepcopy(as_public)
        as_user.headers.update({'Authorization': 'scitran-user ' + email})
        return as_user

    project = data_builder.create_project()
    subject = as_admin.post('/subjects', json={'project': project, 'code': 'test-sublist', 'public': False}).json()['_id']
    as_rw = create_user_accessor('rw-user@test.com')
    as_ro = create_user_accessor('ro-user@test.com')
    rw_id = as_rw.get('/users/self').json()['_id']
    ro_id = as_ro.get('/users/self').json()['_id']
    assert as_admin.post('/projects/' + project + '/permissions', json={'_id': rw_id, 'access': 'rw'}).ok
    assert as_admin.post('/projects/' + project + '/permissions', json={'_id': ro_id, 'access': 'ro'}).ok

    # Add a note
    r = as_admin.post('/subjects/' + subject + '/notes', json={'text': 'note'})
    assert r.ok

    # Add note perms
    assert as_public.post('/subjects/' + subject + '/notes', json={'text': 'note2'}).status_code == 403
    assert as_ro.post('/subjects/' + subject + '/notes', json={'text': 'note2'}).status_code == 403
    assert as_rw.post('/subjects/' + subject + '/notes', json={'text': 'note2'}).ok

    # Verify note is present in subject
    r = as_admin.get('/subjects/' + subject)
    assert r.ok
    note, note2 = [note['_id'] for note in r.json()['notes']]

    # Get note
    r = as_admin.get('/subjects/' + subject + '/notes/' + note)
    assert r.ok
    assert r.json()['text'] == 'note'

    # Get note perms
    assert as_public.get('/subjects/' + subject + '/notes/' + note).status_code == 403
    assert as_ro.get('/subjects/' + subject + '/notes/' + note).ok
    assert as_rw.get('/subjects/' + subject + '/notes/' + note).ok

    # Modify note
    r = as_admin.put('/subjects/' + subject + '/notes/' + note, json={'text': 'modified'})
    assert r.ok

    # Modify note perms
    assert as_public.put('/subjects/' + subject + '/notes/' + note, json={'text': 'modified'}).status_code == 403
    assert as_ro.put('/subjects/' + subject + '/notes/' + note, json={'text': 'modified'}).status_code == 403
    # TODO shouldn't rw PUT succeed instead of 403?
    assert as_rw.put('/subjects/' + subject + '/notes/' + note, json={'text': 'modified'}).status_code == 403

    # Verify modified note
    r = as_admin.get('/subjects/' + subject + '/notes/' + note)
    assert r.ok
    assert r.json()['text'] == 'modified'

    # Delete note
    r = as_admin.delete('/subjects/' + subject + '/notes/' + note)
    assert r.ok

    # Delete note perms
    assert as_public.delete('/subjects/' + subject + '/notes/' + note2).status_code == 403
    assert as_public.delete('/subjects/' + subject + '/notes/' + note2).status_code == 403
    assert as_ro.delete('/subjects/' + subject + '/notes/' + note2).status_code == 403
    assert as_rw.delete('/subjects/' + subject + '/notes/' + note2).ok

    # Verify deleted note
    r = as_admin.get('/subjects/' + subject + '/notes/' + note)
    assert r.status_code == 404


def test_subject_jobs(api_db, data_builder, as_admin, as_drone, file_form):
    # Create gear, project and subject with one input file
    gear = data_builder.create_gear(gear={'inputs': {'csv': {'base': 'file'}}})
    project = data_builder.create_project()
    r = as_admin.post('/subjects', json={'project': project, 'code': 'test'})
    assert r.ok
    subject = r.json()['_id']
    r = as_admin.post('/subjects/' + subject + '/files', files=file_form('input.csv'))
    assert r.ok

    # Create analysis job on subject
    r = as_admin.post('/subjects/' + subject + '/analyses', json={
        'label': 'online',
        'job': {'gear_id': gear,
                'inputs': {'csv': {'type': 'subject', 'id': subject, 'name': 'input.csv'}}}
    })
    assert r.ok
    analysis = r.json()['_id']

    # Verify analysis was created and is accessible on subject
    r = as_admin.get('/subjects/' + subject + '/analyses')
    assert r.ok
    assert analysis in [a['_id'] for a in r.json()]
    r = as_admin.get('/subjects/' + subject + '/analyses/' + analysis)
    assert r.ok
    assert analysis == r.json()['_id']

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

    # Verify output was uploaded and is accessible on subject/x/analysis/y
    r = as_admin.get('/subjects/' + subject + '/analyses/' + analysis)
    assert r.ok
    assert 'output.csv' in [f['name'] for f in r.json()['files']]
    r = as_admin.get('/subjects/' + subject + '/analyses/' + analysis + '/files/output.csv')
    assert r.ok

    # Create job with subject as destination (and input)
    r = as_admin.post('/jobs/add', json={
        'gear_id': gear,
        'inputs': {'csv': {'type': 'subject', 'id': subject, 'name': 'input.csv'}},
        'destination': {'type': 'subject', 'id': subject}
    })
    assert r.ok
    job = r.json()['_id']
    api_db.jobs.update_one({'_id': bson.ObjectId(job)}, {'$set': {'state': 'running'}})

    # Engine upload to subject
    r = as_drone.post('/jobs/' + job + '/prepare-complete', json={'success': True, 'elapsed': 3})
    assert r.ok
    job_ticket = r.json()['ticket']
    r = as_drone.post('/engine',
        params={'level': 'subject', 'id': subject, 'job': job, 'job_ticket': job_ticket},
        files=file_form('result.txt', meta={
            'subject': {'files': [{'name': 'result.txt', 'type': 'text'}]}
        })
    )
    assert r.ok

    r = as_admin.get('/subjects/' + subject)
    assert r.ok
    assert 'result.txt' in [f['name'] for f in r.json()['files']]


def test_subject_move_via_session(data_builder, as_admin, as_user, default_payload, file_form):
    group_1 = data_builder.create_group()
    gear_doc = default_payload['gear']['gear']
    gear_doc['inputs'] = {
        'dicom': {
            'base': 'file'
        }
    }
    gear = data_builder.create_gear(gear=gear_doc)

    group_2 = data_builder.create_group()
    project_1 = data_builder.create_project(group=group_1)
    project_2 = data_builder.create_project(group=group_2)
    session_1 = data_builder.create_session(project=project_1, subject={'code': 'move', 'type': 'human'})
    session_2 = data_builder.create_session(project=project_2, subject={'code': 'ex123', 'type': 'phantom'})
    subject_1 = as_admin.get('/sessions/' + session_1).json()['subject']['_id']
    subject_2 = as_admin.get('/sessions/' + session_2).json()['subject']['_id']

    acquisition = data_builder.create_acquisition(session=session_1)
    assert as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('test.zip')).ok

    # Create a job
    job_data = {
        'gear_id': gear,
        'inputs': {
            'dicom': {
                'type': 'acquisition',
                'id': acquisition,
                'name': 'test.zip'
            }
        },
        'config': { 'two-digit multiple of ten': 40 },
        'destination': {
            'type': 'acquisition',
            'id': acquisition
        },
        'tags': [ 'test-tag' ]
    }
    r = as_admin.post('/jobs/add', json=job_data)
    assert r.ok
    job_id = r.json()['_id']

    # Move session_1 into project_2 - there's no other session on it (move)
    assert as_admin.put('/sessions/' + session_1, json={'project': project_2})
    assert subject_1 == as_admin.get('/sessions/' + session_1).json()['subject']['_id']
    assert (project_2
            == as_admin.get('/sessions/' + session_1).json()['subject']['project']
            == as_admin.get('/subjects/' + subject_1).json()['project'])
    assert as_admin.get('/projects/' + project_1 + '/subjects').json() == []
    assert subject_1 in [s['_id'] for s in as_admin.get('/projects/' + project_2 + '/subjects').json()]

    r_session = as_admin.get('/sessions/' + session_1).json()
    assert r_session['parents']['group'] == group_2
    assert r_session['parents']['project'] == project_2
    assert r_session['parents']['subject'] == subject_1

    # Verify that the job got updated
    job = as_admin.get('/jobs/' + job_id).json()
    assert job['parents']['group'] == group_2
    assert job['parents']['project'] == project_2

    # Create another session on the same subject (now in project_2)
    session_2 = data_builder.create_session(project=project_2, subject={'code': 'move'})
    assert subject_1 == as_admin.get('/sessions/' + session_2).json()['subject']['_id']

    # Move session_1 back into project_1 - there's another session on it (copy)
    assert as_admin.put('/sessions/' + session_1, json={'project': project_1})
    subject_2 = as_admin.get('/sessions/' + session_1).json()['subject']['_id']
    assert subject_2 != subject_1
    assert (project_1
            == as_admin.get('/sessions/' + session_1).json()['subject']['project']
            == as_admin.get('/subjects/' + subject_2).json()['project'])
    assert subject_1 in [s['_id'] for s in as_admin.get('/projects/' + project_2 + '/subjects').json()]
    assert subject_2 in [s['_id'] for s in as_admin.get('/projects/' + project_1 + '/subjects').json()]

    # Change user permissions to read-write on both projects
    user_id = as_user.get('/users/self').json()['_id']
    assert as_admin.post('/projects/' + project_1 + '/permissions', json={'_id': user_id, 'access': 'rw'}).ok
    assert as_admin.post('/projects/' + project_2 + '/permissions', json={'_id': user_id, 'access': 'rw'}).ok

    # Change session subject_1 to subject_2
    assert as_user.put('/sessions/' + session_2, json={'subject': {'_id': subject_1}})
    assert subject_1 == as_user.get('/sessions/' + session_2).json()['subject']['_id']


def test_session_move(data_builder, as_admin, as_user):
    project = data_builder.create_project()
    subject_1 = as_admin.post('/subjects', json={'project': project, 'code': 'move-1'}).json()['_id']
    subject_2 = as_admin.post('/subjects', json={'project': project, 'code': 'move-2'}).json()['_id']
    session = data_builder.create_session(subject={'code': 'move-1', 'type': 'animal'})

    # Move session_1 into subject_2
    assert as_admin.put('/sessions/' + session, json={'subject': {'_id': subject_2}})
    assert subject_2 == as_admin.get('/sessions/' + session).json()['subject']['_id']

    # Change user to read-write
    user_id = as_user.get('/users/self').json()['_id']
    assert as_admin.post('/projects/' + project + '/permissions', json={'_id': user_id, 'access': 'rw'}).ok

    # Move session to subject_1 as a read-write user
    assert as_user.put('/sessions/' + session, json={'subject': {'_id': subject_1}})
    assert subject_1 == as_user.get('/sessions/' + session).json()['subject']['_id']


def test_subject_fields(data_builder, as_admin):
    subject_fields = dict(
        code='test', label='test', cohort='Study',
        type='animal', species='dog', strain='free-string',
        public=True)
    session_fields = dict(age=123, weight=74.8, subject=subject_fields)

    # create new-style session/subject
    session = data_builder.create_session(**session_fields)

    r = as_admin.get('/sessions/' + session)
    assert r.ok
    doc = r.json()

    assert doc.get('age') == 123
    assert doc.get('weight') == 74.8

    assert doc['subject'].get('age') == 123
    assert doc['subject'].get('cohort') == 'Study'
    assert doc['subject'].get('type') == 'animal'
    assert doc['subject'].get('species') == 'dog'
    assert doc['subject'].get('strain') == 'free-string'
    assert doc['subject'].get('public') == True
