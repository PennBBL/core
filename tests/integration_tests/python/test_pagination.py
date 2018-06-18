def test_total(data_builder, as_admin):
    a1 = data_builder.create_acquisition(label='a1')
    a2 = data_builder.create_acquisition(label='a2')

    r_list = as_admin.get('/acquisitions')
    assert r_list.ok
    acqs = r_list.json()

    r_page = as_admin.get('/acquisitions', headers={'X-Accept-Feature': 'pagination'})
    assert r_page.ok
    page = r_page.json()

    assert 'total' in page
    assert 'results' in page
    assert page['total'] == len(acqs)
    assert page['results'] == acqs

    r = as_admin.get('/gears', headers={'X-Accept-Feature': 'pagination'})
    assert r.ok
    assert r.json()['total'] == 0

    g_a0 = data_builder.create_gear(gear={'name': 'a', 'version': '0.0.0'})
    g_a1 = data_builder.create_gear(gear={'name': 'a', 'version': '1.0.0'})
    g_b0 = data_builder.create_gear(gear={'name': 'b', 'version': '0.0.0'})
    g_b1 = data_builder.create_gear(gear={'name': 'b', 'version': '1.0.0'})

    r_list = as_admin.get('/gears')
    assert r_list.ok
    gears = r_list.json()

    r_page = as_admin.get('/gears', headers={'X-Accept-Feature': 'pagination'})
    assert r_page.ok
    page = r_page.json()

    assert 'total' in page
    assert 'results' in page
    assert page['total'] == len(gears)
    assert page['results'] == gears


def test_limit(data_builder, as_admin, file_form):
    assert as_admin.get('/users?limit=foo').status_code == 422
    assert as_admin.get('/users?limit=-1').status_code == 422

    u1 = data_builder.create_user()
    u2 = data_builder.create_user()
    assert len(as_admin.get('/users').json()) > 1
    assert len(as_admin.get('/users?limit=1').json()) == 1

    g1 = data_builder.create_group()
    g2 = data_builder.create_group()
    assert len(as_admin.get('/groups').json()) > 1
    assert len(as_admin.get('/groups?limit=1').json()) == 1

    p1 = data_builder.create_project()
    p2 = data_builder.create_project()
    assert len(as_admin.get('/projects').json()) > 1
    assert len(as_admin.get('/projects?limit=1').json()) == 1
    assert len(as_admin.get('/groups/' + g1 + '/projects').json()) > 1
    assert len(as_admin.get('/groups/' + g1 + '/projects?limit=1').json()) == 1

    s1 = data_builder.create_session()
    s2 = data_builder.create_session()
    assert len(as_admin.get('/sessions').json()) > 1
    assert len(as_admin.get('/sessions?limit=1').json()) == 1
    assert len(as_admin.get('/projects/' + p1 + '/sessions').json()) > 1
    assert len(as_admin.get('/projects/' + p1 + '/sessions?limit=1').json()) == 1

    aq1 = data_builder.create_acquisition()
    aq2 = data_builder.create_acquisition()
    assert len(as_admin.get('/acquisitions').json()) > 1
    assert len(as_admin.get('/acquisitions?limit=1').json()) == 1
    assert len(as_admin.get('/sessions/' + s1 + '/acquisitions').json()) > 1
    assert len(as_admin.get('/sessions/' + s1 + '/acquisitions?limit=1').json()) == 1

    an1 = as_admin.post('/sessions/' + s1 + '/analyses', files=file_form(
        'a.csv', meta={'label': 'no-job', 'inputs': [{'name': 'a.csv'}]})).json()['_id']
    an2 = as_admin.post('/sessions/' + s1 + '/analyses', files=file_form(
        'b.csv', meta={'label': 'no-job', 'inputs': [{'name': 'b.csv'}]})).json()['_id']
    assert len(as_admin.get('/sessions/' + s1 + '/analyses').json()) > 1
    assert len(as_admin.get('/sessions/' + s1 + '/analyses?limit=1').json()) == 1

    c1 = data_builder.create_collection()
    c2 = data_builder.create_collection()
    assert len(as_admin.get('/collections').json()) > 1
    assert len(as_admin.get('/collections?limit=1').json()) == 1

    g_a0 = data_builder.create_gear(gear={'name': 'a', 'version': '0.0.0'})
    g_a1 = data_builder.create_gear(gear={'name': 'a', 'version': '1.0.0'})
    g_b0 = data_builder.create_gear(gear={'name': 'b', 'version': '0.0.0'})
    g_b1 = data_builder.create_gear(gear={'name': 'b', 'version': '1.0.0'})
    assert len(as_admin.get('/gears').json()) > 1
    assert len(as_admin.get('/gears?limit=1').json()) == 1

    rule_doc = {'alg': as_admin.get('/gears/' + g_a1).json()['gear']['name'],
                'name': 'foo', 'any': [], 'all': [], 'not': []}
    r1 = as_admin.post('/site/rules', json=rule_doc).json()['_id']
    r2 = as_admin.post('/site/rules', json=rule_doc).json()['_id']
    assert len(as_admin.get('/site/rules').json()) > 1
    assert len(as_admin.get('/site/rules?limit=1').json()) == 1

    assert as_admin.post('/acquisitions/' + aq1 + '/files', files=file_form('test.txt')).ok
    batch_json = {'gear_id': g_a1, 'targets': [{'type': 'acquisition', 'id': aq1}]}
    b1 = as_admin.post('/batch', json=batch_json).json()['_id']
    b2 = as_admin.post('/batch', json=batch_json).json()['_id']
    assert len(as_admin.get('/batch').json()) > 1
    assert len(as_admin.get('/batch?limit=1').json()) == 1

    job_json = {
        'gear_id': g_a1,
        'inputs': {'text': {'type': 'acquisition', 'id': aq1, 'name': 'test.txt'}},
        'destination': {'type': 'acquisition', 'id': aq2}}
    j1 = as_admin.post('/jobs/add', json=job_json).json()['_id']
    j2 = as_admin.post('/jobs/add', json=job_json).json()['_id']
    assert len(as_admin.get('/jobs').json()) > 1
    assert len(as_admin.get('/jobs?limit=1').json()) == 1

    assert as_admin.delete('/site/rules/' + r1).ok
    assert as_admin.delete('/site/rules/' + r2).ok


def test_page(data_builder, as_admin):
    assert as_admin.get('/users?page=foo').status_code == 422
    assert as_admin.get('/users?page=-1').status_code == 422

    a = data_builder.create_acquisition(label='a')
    b = data_builder.create_acquisition(label='b')

    r = as_admin.get('/acquisitions?limit=1&page=1')
    assert {aq['_id'] for aq in r.json()} == {a}

    r = as_admin.get('/acquisitions?limit=1&page=2')
    assert {aq['_id'] for aq in r.json()} == {b}

    r = as_admin.get('/acquisitions?limit=1&page=3')
    assert {aq['_id'] for aq in r.json()} == set()


def test_skip(data_builder, as_admin):
    assert as_admin.get('/users?skip=foo').status_code == 422
    assert as_admin.get('/users?skip=-1').status_code == 422

    a = data_builder.create_acquisition(label='a')
    b = data_builder.create_acquisition(label='b')

    r = as_admin.get('/acquisitions')
    assert {aq['_id'] for aq in r.json()} == {a, b}

    r = as_admin.get('/acquisitions?skip=1')
    assert {aq['_id'] for aq in r.json()} == {b}


def test_sort(data_builder, as_admin):
    assert as_admin.get('/acquisitions?sort=label:foo').status_code == 422

    a1 = data_builder.create_acquisition(label='a')
    b1 = data_builder.create_acquisition(label='b')
    c1 = data_builder.create_acquisition(label='c')

    r = as_admin.get('/acquisitions?sort=label:1')
    assert [a['_id'] for a in r.json()] == [a1, b1, c1]
    assert as_admin.get('/acquisitions?sort=label:asc').json() == r.json()

    r = as_admin.get('/acquisitions?sort=label:-1')
    assert [a['_id'] for a in r.json()] == [c1, b1, a1]
    assert as_admin.get('/acquisitions?sort=label:desc').json() == r.json()

    a2 = data_builder.create_acquisition(label='a')
    b2 = data_builder.create_acquisition(label='b')
    c2 = data_builder.create_acquisition(label='c')

    r = as_admin.get('/acquisitions?sort=label:1,created:-1')
    assert [a['_id'] for a in r.json()] == [a2, a1, b2, b1, c2, c1]

    g_a0 = data_builder.create_gear(gear={'name': 'a', 'version': '0.0.0'})
    g_a1 = data_builder.create_gear(gear={'name': 'a', 'version': '1.0.0'})
    g_b0 = data_builder.create_gear(gear={'name': 'b', 'version': '0.0.0'})
    g_b1 = data_builder.create_gear(gear={'name': 'b', 'version': '1.0.0'})
    r = as_admin.get('/gears?sort=gear.name:-1')
    assert [g['_id'] for g in r.json()] == [g_b1, g_a1]


def test_filter(data_builder, as_admin):
    assert as_admin.get('/acquisitions?filter=foo').status_code == 422
    assert as_admin.get('/acquisitions?filter=label=a&filter=label=b').status_code == 422

    a = data_builder.create_acquisition(label='a')
    b = data_builder.create_acquisition(label='b')
    c = data_builder.create_acquisition(label='c')

    r = as_admin.get('/acquisitions?filter=label<b')
    assert {aq['_id'] for aq in r.json()} == {a}

    r = as_admin.get('/acquisitions?filter=label<=b')
    assert {aq['_id'] for aq in r.json()} == {a, b}

    r = as_admin.get('/acquisitions?filter=label=b')
    assert {aq['_id'] for aq in r.json()} == {b}

    r = as_admin.get('/acquisitions?filter=label!=b')
    assert {aq['_id'] for aq in r.json()} == {a, c}

    r = as_admin.get('/acquisitions?filter=label>=b')
    assert {aq['_id'] for aq in r.json()} == {b, c}

    r = as_admin.get('/acquisitions?filter=label>b')
    assert {aq['_id'] for aq in r.json()} == {c}

    r = as_admin.get('/acquisitions?filter=label>a,label<c')
    assert {aq['_id'] for aq in r.json()} == {b}

    r = as_admin.get('/acquisitions?filter=_id=' + b)
    assert {aq['_id'] for aq in r.json()} == {b}

    b_created = as_admin.get('/acquisitions/' + b).json()['created'][:-6]
    r = as_admin.get('/acquisitions?filter=created=' + b_created)
    assert {aq['_id'] for aq in r.json()} == {b}

    r = as_admin.get('/gears?filter=single_input')
    assert r.ok

    g_a0 = data_builder.create_gear(gear={'name': 'a', 'version': '0.0.0'})
    g_a1 = data_builder.create_gear(gear={'name': 'a', 'version': '1.0.0'})
    g_b0 = data_builder.create_gear(gear={'name': 'b', 'version': '0.0.0'})
    g_b1 = data_builder.create_gear(gear={'name': 'b', 'version': '1.0.0'})
    r = as_admin.get('/gears?filter=gear.name=a')
    assert r.ok
    assert {g['_id'] for g in r.json()} == {g_a1}
