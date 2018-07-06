def path_in_result(path, result):
    return [node.get('_id', node.get('name')) for node in result['path']] == path

def child_in_result(child, result):
    return sum(all((k in c and c[k]==v) for k,v in child.iteritems()) for c in result['children']) == 1

def gear_in_path(name, id, result):
    for g in result['path']:
        if g['gear']['name'] == name and g['_id'] == id:
            return True
    return False

def idz(s):
    return '<id:' + s + '>'

def create_analysis(as_admin, file_form, container, c_id, label, inp_file):
    # Create analysis
    r = as_admin.post('/' + container + '/' + c_id + '/analyses', json={
        'label': label,
        'inputs': [{'type': container[:-1], 'id': c_id, 'name': inp_file}]
    })
    assert r.ok
    analysis = r.json()['_id']

    # Manual upload
    r = as_admin.post('/analyses/' + analysis + '/files', files=file_form('one.csv'))
    assert r.ok

    return analysis

def test_resolver(data_builder, as_admin, as_user, as_public, file_form):
    user_id = as_user.get('/users/self').json()['_id']

    # ROOT
    # try accessing resolver w/o logging in
    r = as_public.post('/resolve', json={'path': []})
    assert r.status_code == 403

    # try resolving invalid (non-list) path
    r = as_admin.post('/resolve', json={'path': 'test'})
    assert r.status_code == 400

    # resolve root (empty)
    r = as_admin.post('/resolve', json={'path': []})
    result = r.json()
    assert r.ok
    assert result['path'] == []
    assert result['children'] == []

    # resolve root (1 group)
    group = data_builder.create_group()

    uid = as_user.get('/users/self').json()['_id']
    r = as_admin.post('/groups/' + group + '/permissions', json={'_id': uid, 'access': 'admin'})
    assert r.ok

    r = as_user.post('/resolve', json={'path': []})
    result = r.json()
    assert r.ok
    assert result['path'] == []
    assert child_in_result({'_id': group, 'container_type': 'group'}, result)

    # try to resolve non-existent root/child
    r = as_admin.post('/resolve', json={'path': ['child']})
    assert r.status_code == 404

    # GROUP
    # try to resolve root/group without permission
    r = as_admin.delete('/groups/' + group + '/permissions/' + uid)
    assert r.ok
    r = as_user.post('/resolve', json={'path': [group]})
    assert r.status_code == 403

    # resolve root/group (empty)
    r = as_admin.post('/resolve', json={'path': [group]})
    result = r.json()
    assert r.ok
    assert path_in_result([group], result)
    assert result['children'] == []

    # resolve root/group (1 project)
    project_label = 'test-resolver-project-label'
    project = data_builder.create_project(label=project_label)
    r = as_admin.post('/resolve', json={'path': [group]})
    result = r.json()
    assert r.ok
    assert path_in_result([group], result)
    assert child_in_result({'_id': project, 'container_type': 'project'}, result)

    # try to resolve non-existent root/group/child
    r = as_admin.post('/resolve', json={'path': [group, 'child']})
    assert r.status_code == 404

    # PROJECT
    # resolve root/group/project (empty)
    r = as_admin.post('/resolve', json={'path': [group, project_label]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project], result)
    assert result['children'] == []

    # resolve root/group/project (1 file)
    project_file = 'project_file'
    r = as_admin.post('/projects/' + project + '/files', files=file_form(project_file))
    assert r.ok
    project_file_id = r.json()[0]['_id']  # save the file id for later usage
    r = as_admin.post('/resolve', json={'path': [group, project_label]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project], result)
    assert child_in_result({'name': project_file, 'container_type': 'file'}, result)
    assert len(result['children']) == 1

    # resolve root/group/project (1 file, 1 session)
    session_label = 'test-resolver-session-label'
    session = data_builder.create_session(label=session_label)
    r = as_admin.post('/resolve', json={'path': [group, project_label]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project], result)
    assert child_in_result({'_id': session, 'container_type': 'session'}, result)
    assert len(result['children']) == 2

    # resolve root/group/project (1 file, 1 session) as user with permission on the project
    assert as_admin.post('/projects/' + project + '/permissions', json={'_id': user_id, 'access': 'ro'}).ok
    r = as_user.post('/resolve', json={'path': [group, project_label]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project], result)
    assert child_in_result({'_id': session, 'container_type': 'session'}, result)
    assert len(result['children']) == 2
    assert as_admin.delete('/projects/' + project + '/permissions/' + user_id).ok

    # resolve root/group/project/files (1 file, 1 session)
    r = as_admin.post('/resolve', json={'path': [group, project_label, 'files']})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project], result)
    assert child_in_result({'name': project_file, 'container_type': 'file'}, result)
    assert len(result['children']) == 1

    # resolve root/group/project/file (old way)
    r = as_admin.post('/resolve', json={'path': [group, project_label, project_file]})
    result = r.json()
    assert r.status_code == 404

    # resolve root/group/project/file
    r = as_admin.post('/resolve', json={'path': [group, project_label, 'files', project_file]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, project_file_id], result)
    assert result['children'] == []

    # resolve non-existent root/group/project/file
    r = as_admin.post('/resolve', json={'path': [group, project_label, 'files', 'NON-EXISTENT-FILE.dat']})
    assert r.status_code == 404

    # try to resolve non-existent root/group/project/child
    r = as_admin.post('/resolve', json={'path': [group, project_label, 'child']})
    assert r.status_code == 404


    # SESSION
    # resolve root/group/project/session (empty)
    r = as_admin.post('/resolve', json={'path': [group, project_label, session_label]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, session], result)
    assert result['children'] == []

    # resolve root/group/project/session (1 file)
    session_file = 'session_file'
    r = as_admin.post('/sessions/' + session + '/files', files=file_form(session_file))
    assert r.ok
    session_file_id = r.json()[0]['_id']
    r = as_admin.post('/resolve', json={'path': [group, project_label, session_label]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, session], result)
    assert child_in_result({'name': session_file, 'container_type': 'file'}, result)
    assert len(result['children']) == 1

    # resolve root/group/project/session (1 file, 1 acquisition)
    acquisition_label = 'test-resolver-acquisition-label'
    acquisition = data_builder.create_acquisition(label=acquisition_label)
    r = as_admin.post('/resolve', json={'path': [group, project_label, session_label]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, session], result)
    assert child_in_result({'_id': acquisition, 'container_type': 'acquisition'}, result)
    assert len(result['children']) == 2

    # resolve root/group/project/session/file
    r = as_admin.post('/resolve', json={'path': [group, project_label, session_label, 'files', session_file]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, session, session_file_id], result)
    assert result['children'] == []

    # try to resolve non-existent root/group/project/session/child
    r = as_admin.post('/resolve', json={'path': [group, project_label, session_label, 'child']})
    assert r.status_code == 404


    # ACQUISITION
    # resolve root/group/project/session/acquisition (empty)
    r = as_admin.post('/resolve', json={'path': [group, project_label, session_label, acquisition_label]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, session, acquisition], result)
    assert result['children'] == []

    # resolve root/group/project/session/acquisition (1 file)
    acquisition_file = 'acquisition_file'
    r = as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form(acquisition_file))
    assert r.ok
    acquisition_file_id = r.json()[0]['_id']
    r = as_admin.post('/resolve', json={'path': [group, project_label, session_label, acquisition_label]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, session, acquisition], result)
    assert child_in_result({'name': acquisition_file, 'container_type': 'file'}, result)
    assert len(result['children']) == 1

    # Verify that each node has a node_type and container_type
    assert all(['node_type' in node for node in result['path']])

    # resolve root/group/project/session/acquisition/file
    r = as_admin.post('/resolve', json={'path': [group, project_label, session_label, acquisition_label, 'files', acquisition_file]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, session, acquisition, acquisition_file_id], result)
    assert result['children'] == []

    # resolve root/group/project/session/acquisition/file with id
    r = as_admin.post('/resolve', json={'path': [idz(group), idz(project), idz(session), idz(acquisition), 'files', acquisition_file]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, session, acquisition, acquisition_file_id], result)
    assert result['children'] == []

    # resolve root/group/project/session/acquisition/file with invalid id
    r = as_admin.post('/resolve', json={'path': [idz(group), idz(project), idz('not-valid'), idz(acquisition), 'files', acquisition_file]})
    assert r.status_code == 400

    # try to resolve non-existent root/group/project/session/acquisition/child
    r = as_admin.post('/resolve', json={'path': [group, project_label, session_label, acquisition_label, 'child']})
    assert r.status_code == 404


    # FILE
    # try to resolve non-existent (also invalid) root/group/project/session/acquisition/file/child
    r = as_admin.post('/resolve', json={'path': [group, project_label, session_label, acquisition_label, acquisition_file, 'child']})
    assert r.status_code == 404

    # try to resolve deleted containers/files
    r = as_admin.delete('/projects/' + project)
    assert r.ok

    # Resolve group
    r = as_admin.post('/resolve', json={'path': [group]})
    assert r.ok
    assert path_in_result([group], r.json())
    assert result['children'] == []

    # Resolve project 404
    r = as_admin.post('/resolve', json={'path': [group, project]})
    assert r.status_code == 404

    # Resolve session 404
    r = as_admin.post('/resolve', json={'path': [group, project, session]})
    assert r.status_code == 404

def test_lookup(data_builder, as_admin, as_user, as_public, file_form):
    # ROOT
    # try accessing lookup w/o logging in
    r = as_public.post('/lookup', json={'path': []})
    assert r.status_code == 403

    # try resolving invalid (non-list) path
    r = as_admin.post('/lookup', json={'path': 'test'})
    assert r.status_code == 400

    # lookup root (empty)
    r = as_admin.post('/lookup', json={'path': []})
    result = r.json()
    assert r.status_code == 404

    # lookup root (1 group)
    group = data_builder.create_group()
    r = as_admin.post('/lookup', json={'path': []})
    assert r.status_code == 404

    # try to lookup non-existent root/child
    r = as_admin.post('/lookup', json={'path': ['child']})
    assert r.status_code == 404


    # GROUP
    # try to lookup root/group as different (and non-root) user
    r = as_user.post('/lookup', json={'path': [group]})
    assert r.status_code == 403

    # lookup root/group (empty)
    r = as_admin.post('/lookup', json={'path': [group]})
    result = r.json()
    assert r.ok
    assert result['container_type'] == 'group'
    assert result['_id'] == group

    # try to lookup non-existent root/group/child
    r = as_admin.post('/lookup', json={'path': [group, 'child']})
    assert r.status_code == 404


    # PROJECT
    # lookup root/group/project (empty)
    project_label = 'test-lookup-project-label'
    project = data_builder.create_project(label=project_label)

    r = as_admin.post('/lookup', json={'path': [group, project_label]})
    result = r.json()
    assert r.ok
    assert result['container_type'] == 'project'
    assert result['_id'] == project

    # lookup root/group/project/file
    project_file = 'project_file'
    r = as_admin.post('/projects/' + project + '/files', files=file_form(project_file))
    assert r.ok

    r = as_admin.post('/lookup', json={'path': [group, project_label, 'files', project_file]})
    result = r.json()
    assert r.ok
    assert result['container_type'] == 'file'
    assert result['name'] == project_file
    assert 'mimetype' in result
    assert 'size' in result

    # try to lookup non-existent root/group/project/child
    r = as_admin.post('/lookup', json={'path': [group, project_label, 'child']})
    assert r.status_code == 404


    # SESSION
    # lookup root/group/project/session (empty)
    session_label = 'test-lookup-session-label'
    session = data_builder.create_session(label=session_label)

    r = as_admin.post('/lookup', json={'path': [group, project_label, session_label]})
    result = r.json()
    assert r.ok
    assert result['container_type'] == 'session'
    assert result['_id'] == session

    # lookup root/group/project/session/file
    session_file = 'session_file'
    r = as_admin.post('/sessions/' + session + '/files', files=file_form(session_file))
    assert r.ok

    r = as_admin.post('/lookup', json={'path': [group, project_label, session_label, 'files', session_file]})
    result = r.json()
    assert r.ok
    assert result['container_type'] == 'file'
    assert result['name'] == session_file
    assert 'mimetype' in result
    assert 'size' in result

    # try to lookup non-existent root/group/project/session/child
    r = as_admin.post('/lookup', json={'path': [group, project_label, session_label, 'child']})
    assert r.status_code == 404

    # ACQUISITION
    # lookup root/group/project/session/acquisition (empty)
    acquisition_label = 'test-lookup-acquisition-label'
    acquisition = data_builder.create_acquisition(label=acquisition_label)
    r = as_admin.post('/lookup', json={'path': [group, project_label, session_label, acquisition_label]})
    result = r.json()
    assert r.ok
    assert result['container_type'] == 'acquisition'
    assert result['_id'] == acquisition

    # lookup root/group/project/session/acquisition/file
    acquisition_file = 'acquisition_file'
    r = as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form(acquisition_file))
    assert r.ok

    r = as_admin.post('/lookup', json={'path': [group, project_label, session_label, acquisition_label, 'files', acquisition_file]})
    result = r.json()
    assert r.ok
    assert result['container_type'] == 'file'
    assert result['name'] == acquisition_file
    assert 'mimetype' in result
    assert 'size' in result

    # lookup root/group/project/session/acquisition with id
    r = as_admin.post('/lookup', json={'path': [idz(group), idz(project), idz(session), idz(acquisition)]})
    result = r.json()
    assert r.ok
    assert result['container_type'] == 'acquisition'
    assert result['_id'] == acquisition

    # lookup root/group/project/session/acquisition/file with id
    r = as_admin.post('/lookup', json={'path': [idz(group), idz(project), idz(session), idz(acquisition), 'files', acquisition_file]})
    result = r.json()
    assert r.ok
    assert result['container_type'] == 'file'
    assert result['name'] == acquisition_file
    assert 'mimetype' in result
    assert 'size' in result

    # try to lookup non-existent root/group/project/session/acquisition/child
    r = as_admin.post('/lookup', json={'path': [group, project_label, session_label, acquisition_label, 'child']})
    assert r.status_code == 404


    # FILE
    # try to lookup non-existent (also invalid) root/group/project/session/acquisition/file/child
    r = as_admin.post('/lookup', json={'path': [group, project_label, session_label, acquisition_label, 'files', acquisition_file, 'child']})
    assert r.status_code == 404

def test_resolve_gears(data_builder, as_admin, as_user, as_public, file_form):
    # ROOT
    # try accessing resolver w/o logging in
    r = as_public.post('/resolve', json={'path': ['gears']})
    assert r.status_code == 403

    # Generate a gear name
    gear_name = data_builder.randstr()

    # resolve root (1 gear)
    gear_id = data_builder.create_gear(gear={'name':gear_name, 'version': '0.0.1'})
    gear = as_admin.get('/gears/' + gear_id).json()

    r = as_admin.post('/resolve', json={'path': ['gears']})
    result = r.json()
    assert r.ok
    assert result['path'] == []
    assert child_in_result({'_id': gear_id, 'container_type': 'gear'}, result)

    # resolve gear (empty)
    r = as_admin.post('/resolve', json={'path': ['gears', gear_name]})
    result = r.json()
    assert r.ok
    assert gear_in_path(gear_name, gear_id, result)
    assert result['children'] == []

    # resolve gear by id
    r = as_admin.post('/resolve', json={'path': ['gears', idz(gear_id)]})
    result = r.json()
    assert r.ok
    assert gear_in_path(gear_name, gear_id, result)
    assert result['children'] == []

    # Lookup (empty)
    r = as_admin.post('/lookup', json={'path': ['gears']})
    result = r.json()
    assert r.status_code == 404

    # Lookup by name
    r = as_admin.post('/lookup', json={'path': ['gears', gear_name]})
    result = r.json()
    assert r.ok
    assert result['container_type'] == 'gear'
    assert result['_id'] == gear_id
    assert result['gear']['name'] == gear_name

    # Lookup by id
    r = as_admin.post('/lookup', json={'path': ['gears', idz(gear_id)]})
    result = r.json()
    assert r.ok
    assert result['container_type'] == 'gear'
    assert result['_id'] == gear_id
    assert result['gear']['name'] == gear_name

    # Lookup (not-found)
    r = as_admin.post('/lookup', json={'path': ['gears', 'NON-EXISTENT-GEAR']})
    assert r.status_code == 404

    # Lookup by id (not-found)
    r = as_admin.post('/lookup', json={'path': ['gears', idz('ffffffffffffffffffffffff')]})
    assert r.status_code == 404

    # Child gears
    new_gear_id = data_builder.create_gear(gear={'name':gear_name, 'version': '0.0.2'})
    new_gear = as_admin.get('/gears/' + new_gear_id).json()

    # Resolve gear children
    r = as_admin.post('/resolve', json={'path': ['gears', gear_name]})
    result = r.json()
    assert r.ok

    # The latest gear should be the parent
    assert gear_in_path(gear_name, new_gear_id, result)
    # The older gear should be in children
    assert len(result['children']) == 1
    assert child_in_result({'_id': gear_id, 'container_type': 'gear'}, result)

    # Resolve gear version
    r = as_admin.post('/resolve', json={'path': ['gears', gear_name, '0.0.2']})
    result = r.json()
    assert r.ok
    assert gear_in_path(gear_name, new_gear_id, result)
    assert result['children'] == []

    # Resolve gear (older) version
    r = as_admin.post('/resolve', json={'path': ['gears', gear_name, '0.0.1']})
    result = r.json()
    assert r.ok
    assert gear_in_path(gear_name, gear_id, result)
    assert result['children'] == []

    # Lookup gear version
    r = as_admin.post('/lookup', json={'path': ['gears', gear_name, '0.0.1']})
    result = r.json()
    assert r.ok
    assert result['container_type'] == 'gear'
    assert result['_id'] == gear_id
    assert result['gear']['name'] == gear_name

    # Lookup gear version (not found)
    r = as_admin.post('/lookup', json={'path': ['gears', gear_name, '0.0.3']})
    assert r.status_code == 404

def test_resolve_analyses(data_builder, as_admin, as_user, as_public, file_form):
    analysis_file = 'one.csv'

    # Create group
    group = data_builder.create_group()

    # Create project
    project_label = 'test-resolve-analyses-project-label'
    project = data_builder.create_project(label=project_label)

    project_file = 'project_file'
    r = as_admin.post('/projects/' + project + '/files', files=file_form(project_file))
    assert r.ok

    project_analysis_name = 'test-project-analysis'
    project_analysis = create_analysis(as_admin, file_form, 'projects', project, project_analysis_name, project_file)

    # Create session
    session_label = 'test-resolve-analyses-session-label'
    session = data_builder.create_session(label=session_label)

    session_file = 'session_file'
    r = as_admin.post('/sessions/' + session + '/files', files=file_form(session_file))
    assert r.ok

    session_analysis_name = 'test-session-analysis'
    session_analysis = create_analysis(as_admin, file_form, 'sessions', session, session_analysis_name, session_file)

    # Create acquisition
    acquisition_label = 'test-resolve-analyses-acquisition-label'
    acquisition = data_builder.create_acquisition(label=acquisition_label)

    acquisition_file = 'acquisition_file'
    r = as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form(acquisition_file))
    assert r.ok

    acq_analysis_name = 'test-acquisition-analysis'
    acq_analysis = create_analysis(as_admin, file_form, 'acquisitions', acquisition, acq_analysis_name, acquisition_file)

    # GROUP
    r = as_admin.post('/resolve', json={'path': [group, 'analyses']})
    assert r.status_code == 404

    # PROJECT
    # resolve root/group/project (1 file, 1 session)
    r = as_admin.post('/resolve', json={'path': [group, project_label]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project], result)
    assert child_in_result({'name': project_file, 'container_type': 'file'}, result)
    assert child_in_result({'_id': session, 'container_type': 'session'}, result)
    assert child_in_result({'_id': project_analysis, 'container_type': 'analysis'}, result)
    assert len(result['children']) == 3

    # resolve root/group/project/analysis
    r = as_admin.post('/resolve', json={'path': [group, project_label, 'analyses']})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project], result)
    assert child_in_result({'_id': project_analysis, 'container_type': 'analysis'}, result)
    assert len(result['children']) == 1

    # resolve root/group/project/analysis/name
    r = as_admin.post('/resolve', json={'path': [group, project_label, 'analyses', project_analysis_name]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, project_analysis], result)
    assert child_in_result({'name': analysis_file, 'container_type': 'file'}, result)
    assert len(result['children']) == 1

    # lookup root/group/project/analysis/name
    r = as_admin.post('/lookup', json={'path': [group, project_label, 'analyses', project_analysis_name]})
    result = r.json()
    assert r.ok
    assert result['container_type'] == 'analysis'
    assert result['_id'] == project_analysis
    assert len(result['files']) == 1
    project_analysis_file_id = result['files'][0]['_id']  # save the file id for later usage

    # resolve root/group/project/analysis/files
    r = as_admin.post('/resolve', json={'path': [group, project_label, 'analyses', project_analysis_name, 'files', analysis_file]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, project_analysis, project_analysis_file_id], result)
    assert result['children'] == []

    # SESSION
    # resolve root/group/project/session
    r = as_admin.post('/resolve', json={'path': [group, project_label, session_label]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, session], result)
    assert child_in_result({'name': session_file, 'container_type': 'file'}, result)
    assert child_in_result({'_id': acquisition, 'container_type': 'acquisition'}, result)
    assert child_in_result({'_id': session_analysis, 'container_type': 'analysis'}, result)
    assert len(result['children']) == 3

    # resolve root/group/project/analysis/name
    r = as_admin.post('/resolve', json={'path': [group, project_label, session_label, 'analyses', session_analysis_name]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, session, session_analysis], result)
    assert child_in_result({'name': analysis_file, 'container_type': 'file'}, result)
    assert len(result['children']) == 1

    # lookup root/group/project/analysis/name
    r = as_admin.post('/lookup', json={'path': [group, project_label, session_label, 'analyses', session_analysis_name]})
    result = r.json()
    assert r.ok
    assert result['container_type'] == 'analysis'
    assert result['_id'] == session_analysis
    assert len(result['files']) == 1
    session_analysis_file_id = result['files'][0]['_id']  # save the file id for later usage

    # resolve root/group/project/analysis/files
    r = as_admin.post('/resolve', json={'path': [group, project_label, session_label, 'analyses', session_analysis_name, 'files', analysis_file]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, session, session_analysis, session_analysis_file_id], result)
    assert result['children'] == []

    # ACQUISITION
    # resolve root/group/project/session/acquisition
    r = as_admin.post('/resolve', json={'path': [group, project_label, session_label, acquisition_label]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, session, acquisition], result)
    assert child_in_result({'name': acquisition_file, 'container_type': 'file'}, result)
    assert child_in_result({'_id': acq_analysis, 'container_type': 'analysis'}, result)
    assert len(result['children']) == 2

    # resolve root/group/project/analysis/name
    r = as_admin.post('/resolve', json={'path': [group, project_label, session_label, acquisition_label, 'analyses', acq_analysis_name]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, session, acquisition, acq_analysis], result)
    assert child_in_result({'name': analysis_file, 'container_type': 'file'}, result)
    assert len(result['children']) == 1

    # lookup root/group/project/analysis/name
    r = as_admin.post('/lookup', json={'path': [group, project_label, session_label, acquisition_label, 'analyses', acq_analysis_name]})
    result = r.json()
    assert r.ok
    assert result['container_type'] == 'analysis'
    assert result['_id'] == acq_analysis
    assert len(result['files']) == 1
    acq_analysis_file_id = result['files'][0]['_id']  # save the file id for later usage

    # resolve root/group/project/analysis/id
    r = as_admin.post('/resolve', json={'path': [group, project_label, idz(session), acquisition_label, 'analyses', idz(acq_analysis)]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, session, acquisition, acq_analysis], result)
    assert child_in_result({'name': analysis_file, 'container_type': 'file'}, result)
    assert len(result['children']) == 1

    # lookup root/group/project/analysis/name
    r = as_admin.post('/lookup', json={'path': [group, project_label, idz(session), acquisition_label, 'analyses', idz(acq_analysis)]})
    result = r.json()
    assert r.ok
    assert result['container_type'] == 'analysis'
    assert result['_id'] == acq_analysis
    assert len(result['files']) == 1

    # resolve root/group/project/analysis/files
    r = as_admin.post('/resolve', json={'path': [group, project_label, session_label, acquisition_label, 'analyses', acq_analysis_name, 'files', analysis_file]})
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, session, acquisition, acq_analysis, acq_analysis_file_id], result)
    assert result['children'] == []


def test_resolve_subjects(data_builder, as_admin, as_user, as_public, file_form):
    group = data_builder.create_group()

    project = data_builder.create_project(label='project_label')
    assert as_admin.post('/projects/' + project + '/files', files=file_form('project_file'))
    project_analysis = create_analysis(as_admin, file_form, 'projects', project, 'project_analysis', 'project_file')

    session = data_builder.create_session(label='session_label', subject={'code': 'subject_code'})
    assert as_admin.post('/sessions/' + session + '/files', files=file_form('session_file'))
    session_analysis = create_analysis(as_admin, file_form, 'sessions', session, 'session_analysis', 'session_file')

    subject = as_admin.get('/sessions/' + session).json()['subject']['_id']
    assert as_admin.post('/subjects/' + subject + '/files', files=file_form('subject_file'))
    subject_file = as_admin.get('/subjects/' + subject).json()['files'][0]['_id']
    subject_analysis = create_analysis(as_admin, file_form, 'subjects', subject, 'subject_analysis', 'subject_file')

    acquisition = data_builder.create_acquisition(label='acquisition_label')

    enable_subjects = {'X-Accept-Feature': 'Subject-Container'}

    # PROJECT
    # resolve root/group/project
    r = as_admin.post('/resolve', json={'path': [group, 'project_label']}, headers=enable_subjects)
    result = r.json()
    assert r.ok
    assert path_in_result([group, project], result)
    assert child_in_result({'name': 'project_file', 'container_type': 'file'}, result)
    assert child_in_result({'_id': subject, 'container_type': 'subject'}, result)
    assert child_in_result({'_id': project_analysis, 'container_type': 'analysis'}, result)
    assert len(result['children']) == 3

    # SUBJECT
    # resolve root/group/project/subject
    r = as_admin.post('/resolve', json={'path': [group, 'project_label', 'subject_code']}, headers=enable_subjects)
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, subject], result)
    assert child_in_result({'name': 'subject_file', 'container_type': 'file'}, result)
    assert child_in_result({'_id': session, 'container_type': 'session'}, result)
    assert child_in_result({'_id': subject_analysis, 'container_type': 'analysis'}, result)
    assert len(result['children']) == 3

    # resolve root/group/project/subject/analysis
    r = as_admin.post('/resolve', json={'path': [group, 'project_label', 'subject_code', 'analyses']}, headers=enable_subjects)
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, subject], result)
    assert child_in_result({'_id': subject_analysis, 'container_type': 'analysis'}, result)
    assert len(result['children']) == 1

    # resolve root/group/project/subject/analysis/name
    r = as_admin.post('/resolve', json={'path': [group, 'project_label', 'subject_code', 'analyses', 'subject_analysis']}, headers=enable_subjects)
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, subject, subject_analysis], result)
    assert child_in_result({'name': 'one.csv', 'container_type': 'file'}, result)
    assert len(result['children']) == 1

    # resolve root/group/project/subject/files
    r = as_admin.post('/resolve', json={'path': [group, 'project_label', 'subject_code', 'files']}, headers=enable_subjects)
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, subject], result)
    assert child_in_result({'name': 'subject_file', 'container_type': 'file'}, result)
    assert len(result['children']) == 1

    # resolve root/group/project/subject/files/name
    r = as_admin.post('/resolve', json={'path': [group, 'project_label', 'subject_code', 'files', 'subject_file']}, headers=enable_subjects)
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, subject, subject_file], result)
    assert result['children'] == []

    # SESSION
    # resolve root/group/project/subject/session
    r = as_admin.post('/resolve', json={'path': [group, 'project_label', 'subject_code', 'session_label']}, headers=enable_subjects)
    result = r.json()
    assert r.ok
    assert path_in_result([group, project, subject, session], result)
    assert child_in_result({'name': 'session_file', 'container_type': 'file'}, result)
    assert child_in_result({'_id': acquisition, 'container_type': 'acquisition'}, result)
    assert child_in_result({'_id': session_analysis, 'container_type': 'analysis'}, result)
    assert len(result['children']) == 3
