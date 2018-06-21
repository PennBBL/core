
def test_saving_search_queries(as_admin, as_user, data_builder):

    user_id = as_user.get('/users/self').json()["_id"]

    # Try posting a malformed search
    r = as_admin.post('/dataexplorer/queries', json={"not-label":"random-string"})
    assert r.status_code == 400

    # Try getting a non-existent saved search
    r = as_admin.get('/dataexplorer/queries/000000000000000000000000')
    assert r.status_code == 404

    # Save a search
    r = as_admin.post('/dataexplorer/queries', json={'label': 'search1', 'search': {'return_type': 'session'}})
    assert r.ok
    search = r.json()['_id']

    # Get all searched user has access to
    r = as_admin.get('/dataexplorer/queries')
    assert r.ok

    # Get the saved search by id
    r = as_admin.get('/dataexplorer/queries/' + search)
    assert r.ok
    assert r.json()['label'] == 'search1'

    # Malformed search replace
    payload = {'label': 'good-label', 'search' : { 'not-return-type' : 'not-container'}}
    r = as_admin.put('/dataexplorer/queries/' + search, json=payload)
    assert r.status_code == 400

    # Replace search
    r = as_admin.get('/dataexplorer/queries/' + search)
    assert r.ok
    assert r.json()['label'] == 'search1'
    payload = {'label': 'newSearch'}
    payload['label'] = 'newSearch'
    r = as_admin.put('/dataexplorer/queries/' + search, json=payload)
    assert r.ok
    assert r.json()['modified'] == 1
    r = as_admin.get('/dataexplorer/queries/' + search)
    assert r.ok
    assert r.json()['label'] == 'newSearch'

    # Add permission to search
    r = as_admin.post('/dataexplorer/queries/' + search + '/permissions', json={'access': 'admin', '_id': user_id})
    assert r.ok
    r = as_admin.get('/dataexplorer/queries/' + search)
    assert r.ok
    assert r.json()['permissions'][1]['_id'] == user_id

    # Modify permission
    r = as_admin.put('/dataexplorer/queries/' + search + '/permissions/' + user_id, json={'access': 'ro'})
    assert r.ok
    r = as_admin.get('/dataexplorer/queries/' + search)
    assert r.ok
    assert r.json()['permissions'][1]['access'] == 'ro'

    # Remove permission
    r = as_admin.delete('/dataexplorer/queries/' + search + '/permissions/' + user_id)
    assert r.ok
    r = as_admin.get('/dataexplorer/queries/' + search)
    assert r.ok
    assert len(r.json()['permissions']) == 1

    # Delete saved search
    r = as_admin.delete('/dataexplorer/queries/' + search)
    assert r.ok
    r = as_admin.get('/dataexplorer/queries')
    assert r.ok
    assert len(r.json()) == 0
