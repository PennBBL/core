import json

import api.config


def test_apply_env_variables(mocker, tmpdir):
    auth_file, auth_content = 'auth_config.json', {'auth': {'test': 'test'}}
    tmpdir.join(auth_file).write(json.dumps(auth_content))
    mocker.patch('os.environ', {
        'SCITRAN_AUTH_CONFIG_FILE': str(tmpdir.join(auth_file)),
        'SCITRAN_TEST_TRUE': 'true',
        'SCITRAN_TEST_FALSE': 'false',
        'SCITRAN_TEST_NONE': 'none',
        'SCITRAN_SITE_UPLOAD_MAXIMUM_BYTES': '10'})
    config = {
        'auth': {'initial': 'auth'},
        'test': {'true': '', 'false': '', 'none': ''},
        'site': {'upload_maximum_bytes': '10737418240'}}
    api.config.apply_env_variables(config)
    print config
    assert config == {
        'auth': {'test': 'test'},
        'test': {'true': True, 'false': False, 'none': None},
        'site': {'upload_maximum_bytes': '10'}}


    # Test that objects don't persist
    auth_file, auth_content = 'auth_config.json', {'auth': {'test2': 'test2'}}
    tmpdir.join(auth_file).write(json.dumps(auth_content))

    api.config.apply_env_variables(config)
    assert config == {
        'auth': {'test2': 'test2'},
        'test': {'true': True, 'false': False, 'none': None},
        'site': {'upload_maximum_bytes': '10'}}

    # Test Default is used when no auth is provided
    auth_file, auth_content = 'auth_config.json', {}
    tmpdir.join(auth_file).write(json.dumps(auth_content))
    api.config.apply_env_variables(config)
    assert config['auth'].get('google')


def test_create_or_recreate_ttl_index(mocker):
    db = mocker.patch('api.config.db')
    collection, index_id, index_name, ttl = 'collection', 'timestamp_1', 'timestamp', 1

    # create - collection not in collection_names
    db.collection_names.return_value = []
    api.config.create_or_recreate_ttl_index(collection, index_name, ttl)
    db.collection_names.assert_called_with()
    db[collection].create_index.assert_called_with(index_name, expireAfterSeconds=ttl)
    db[collection].create_index.reset_mock()

    # create - index doesn't exist
    db.collection_names.return_value = [collection]
    db[collection].index_information.return_value = {}
    api.config.create_or_recreate_ttl_index(collection, index_name, ttl)
    db[collection].create_index.assert_called_with(index_name, expireAfterSeconds=ttl)
    db[collection].create_index.reset_mock()

    # skip - index exists and matches
    db[collection].index_information.return_value = {index_id: {'key': [[index_name]], 'expireAfterSeconds': ttl}}
    api.config.create_or_recreate_ttl_index(collection, index_name, ttl)
    assert not db[collection].create_index.called

    # recreate - index exists but doesn't match
    db[collection].create_index.reset_mock()
    db[collection].index_information.return_value = {index_id: {'key': [[index_name]], 'expireAfterSeconds': 10}}
    api.config.create_or_recreate_ttl_index(collection, index_name, ttl)
    db[collection].drop_index.assert_called_with(index_id)
    db[collection].create_index.assert_called_with(index_name, expireAfterSeconds=ttl)
