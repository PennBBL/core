import bson

from api import config
from api.dao import containerutil

def test_container_search(data_builder):
    assert config.db is not None

    group = data_builder.create_group()
    project = data_builder.create_project(label="project1")
    session = data_builder.create_session(project=project, label="label")
    acquisition = data_builder.create_acquisition(session=session, label="label")

    session_id = bson.ObjectId(session)
    acquisition_id = bson.ObjectId(acquisition)
    
    # Should get a single match on session, with early return
    results = containerutil.container_search({'_id': session_id}, {'_id':1})
    assert results == [('sessions', [{'_id': session_id}])]

    # Search for non-existent value
    assert [] == containerutil.container_search({'_id': 'DOES_NOT_EXIST'})

    # Search for multiple return
    results = containerutil.container_search({'label': 'label'}, {'_id':1}, early_return=False)
    assert len(results) == 2
    assert ('sessions', [{'_id': session_id}]) in results
    assert ('acquisitions', [{'_id': acquisition_id}]) in results

    # Get first result from a defined set of containers
    results = containerutil.container_search({'label': 'label'}, {'_id':1}, collections=['sessions', 'acquisitions'])
    assert results == [('sessions', [{'_id': session_id}])]


