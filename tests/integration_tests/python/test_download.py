import cStringIO
import os
import tarfile
import zipfile

from bson.objectid import ObjectId
import pytest

from api import config, util


def test_download_k(data_builder, file_form, as_admin, as_user, api_db, legacy_cas_file):
    project = data_builder.create_project(label='project1')
    session = data_builder.create_session(label='session1', project=project)
    session2 = data_builder.create_session(label='session1', project=project)
    session3 = data_builder.create_session(label='session1', project=project)
    session4 = data_builder.create_session(label='session/1', project=project)
    acquisition = data_builder.create_acquisition(session=session)
    acquisition2 = data_builder.create_acquisition(session=session2)
    acquisition3 = data_builder.create_acquisition(session=session3)
    acquisition4 = data_builder.create_acquisition(session=session4)

    # upload the same file to each container created and use different tags to
    # facilitate download filter tests:
    # acquisition: [], session: ['plus'], project: ['plus', 'minus']
    as_admin.post('/projects/' + project + '/permissions', json={'_id': 'user@user.com', 'access': 'admin'})
    file_name = 'test.csv'
    as_user.post('/acquisitions/' + acquisition + '/files', files=file_form(
        file_name, meta={'name': file_name, 'type': 'csv'}))

    as_user.post('/acquisitions/' + acquisition2 + '/files', files=file_form(
        file_name, meta={'name': file_name, 'type': 'csv'}))

    as_user.post('/acquisitions/' + acquisition3 + '/files', files=file_form(
        'test.txt', meta={'name': file_name, 'type': 'text'}))

    as_user.post('/acquisitions/' + acquisition4 + '/files', files=file_form(
        'test.txt', meta={'name': file_name, 'type': 'text'}))

    as_user.post('/sessions/' + session + '/files', files=file_form(
        file_name, meta={'name': file_name, 'type': 'csv', 'tags': ['plus']}))

    as_user.post('/projects/' + project + '/files', files=file_form(
        file_name, meta={'name': file_name, 'type': 'csv', 'tags': ['plus', 'minus']}))

    # also a deleted file to make sure it doesn't show up
    as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form(
        file_name, meta={'name': 'deleted_'+file_name, 'type': 'csv'}))
    r = as_admin.delete('/acquisitions/' + acquisition + '/files/deleted_' + file_name)
    assert r.ok

    missing_object_id = '000000000000000000000000'

    # Try to download w/ nonexistent ticket
    r = as_user.get('/download', params={'ticket': missing_object_id})
    assert r.status_code == 404

    # Retrieve a ticket for a batch download as superuser
    r = as_admin.post('/download', json={
        'optional': False,
        'filters': [{'tags': {
            '-': ['minus']
        }}],
        'nodes': [
            {'level': 'project', '_id': project},
        ]
    })
    assert r.ok
    ticket = r.json()['ticket']

    # Perform the download
    r = as_admin.get('/download', params={'ticket': ticket})
    assert r.ok

    # Retrieve a ticket for a batch download
    r = as_user.post('/download', json={
        'optional': False,
        'filters': [{'tags': {
            '-': ['minus']
        }}],
        'nodes': [
            {'level': 'project', '_id': project},
        ]
    })
    assert r.ok
    ticket = r.json()['ticket']

    # Perform the download
    r = as_user.get('/download', params={'ticket': ticket})
    assert r.ok

    tar_file = cStringIO.StringIO(r.content)
    tar = tarfile.open(mode="r", fileobj=tar_file)

    # Verify a single file in tar with correct file name
    found_second_session = False
    found_third_session = False
    found_fourth_session = False
    for tarinfo in tar:
        assert os.path.basename(tarinfo.name) == file_name
        if 'session1_0' in str(tarinfo.name):
            found_second_session = True
        if 'session1_1' in str(tarinfo.name):
            found_third_session = True
        if 'session1_2' in str(tarinfo.name):
            found_fourth_session = True
    assert found_second_session
    assert found_third_session
    assert found_fourth_session
    tar.close()

    # Download one session with many acquisitions and make sure they are in the same subject folder

    acquisition3 = data_builder.create_acquisition(session=session)
    r = as_user.post('/acquisitions/' + acquisition3 + '/files', files=file_form(
        file_name, meta={'name': file_name, 'type': 'csv'}))
    assert r.ok

    r = as_user.post('/download', json={
        'optional': False,
        'nodes': [
            {'level': 'acquisition', '_id': acquisition},
            {'level': 'acquisition', '_id': acquisition3},
        ]
    })
    assert r.ok
    ticket = r.json()['ticket']

    # Perform the download
    r = as_user.get('/download', params={'ticket': ticket})
    assert r.ok

    tar_file = cStringIO.StringIO(r.content)
    tar = tarfile.open(mode="r", fileobj=tar_file)

    # Verify a single file in tar with correct file name
    found_second_session = False
    for tarinfo in tar:
        assert os.path.basename(tarinfo.name) == file_name
        if 'session1_0' in str(tarinfo.name):
            found_second_session = True
    assert not found_second_session

    tar.close()

    # Try to perform the download from a different IP
    update_result = api_db.downloads.update_one(
        {'_id': ticket},
        {'$set': {'ip': '255.255.255.255'}})
    assert update_result.modified_count == 1

    r = as_user.get('/download', params={'ticket': ticket})
    assert r.status_code == 400

    # Try to retrieve a ticket referencing nonexistent containers
    r = as_user.post('/download', json={
        'optional': False,
        'nodes': [
            {'level': 'project', '_id': missing_object_id},
            {'level': 'session', '_id': missing_object_id},
            {'level': 'acquisition', '_id': missing_object_id},
        ]
    })
    assert r.status_code == 404

    # Try to retrieve ticket for bulk download w/ invalid container name
    # (not project|session|acquisition)
    r = as_user.post('/download', params={'bulk': 'true'}, json={
        'files': [{'container_name': 'subject', 'container_id': missing_object_id, 'filename': 'nosuch.csv'}]
    })
    assert r.status_code == 400

    # Try to retrieve ticket for bulk download referencing nonexistent file
    r = as_user.post('/download', params={'bulk': 'true'}, json={
        'files': [{'container_name': 'project', 'container_id': project, 'filename': 'nosuch.csv'}]
    })
    assert r.status_code == 404

    # Retrieve ticket for bulk download
    r = as_user.post('/download', params={'bulk': 'true'}, json={
        'files': [{'container_name': 'project', 'container_id': project, 'filename': file_name}]
    })
    assert r.ok
    ticket = r.json()['ticket']

    # Perform the download using symlinks
    r = as_user.get('/download', params={'ticket': ticket, 'symlinks': 'true'})
    assert r.ok

    # test legacy cas file handling
    (project_legacy, file_name_legacy, file_content) = legacy_cas_file

    # Add user to leagcy project permissions
    as_admin.post('/projects/' + project_legacy + '/permissions', json={'_id': 'user@user.com', 'access': 'admin'})
    r = as_user.post('/download', json={
        'optional': False,
        'nodes': [
            {'level': 'project', '_id': project_legacy},
        ]
    })
    assert r.ok
    ticket = r.json()['ticket']

    # Perform the download
    r = as_user.get('/download', params={'ticket': ticket})
    assert r.ok

    tar_file = cStringIO.StringIO(r.content)
    tar = tarfile.open(mode="r", fileobj=tar_file)

    # Verify a single file in tar with correct file name
    for tarinfo in tar:
        assert os.path.basename(tarinfo.name) == file_name_legacy

    tar.close()

    # test missing file hangling

    file_id = api_db.acquisitions.find_one({'_id': ObjectId(acquisition)})['files'][0]['_id']
    config.fs.remove(util.path_from_uuid(file_id))

    r = as_user.post('/download', json={
        'optional': False,
        'nodes': [
            {'level': 'acquisition', '_id': acquisition},
            {'level': 'acquisition', '_id': acquisition3},
        ]
    })
    assert r.ok
    ticket = r.json()['ticket']

    # Perform the download
    r = as_user.get('/download', params={'ticket': ticket})
    assert r.ok

    tar_file = cStringIO.StringIO(r.content)
    tar = tarfile.open(mode="r", fileobj=tar_file)

    # Verify a single file in tar with correct file name
    tarinfo_list = list(tar)
    # it contains two files
    assert len(tarinfo_list) == 2
    assert len([tarinfo for tarinfo in tarinfo_list if tarinfo.name.endswith('.MISSING')]) == 1

    tar.close()


def test_filelist_download(data_builder, file_form, as_user, as_admin, legacy_cas_file):
    project = data_builder.create_project()
    session = data_builder.create_session(project=project)

    # Add User to permissions
    as_admin.post('/projects/' + project + '/permissions', json={'_id': 'user@user.com', 'access': 'admin'})

    zip_cont = cStringIO.StringIO()
    with zipfile.ZipFile(zip_cont, 'w') as zip_file:
        zip_file.writestr('two.csv', 'sample\ndata\n')
    zip_cont.seek(0)
    session_files = '/sessions/' + session + '/files'
    as_user.post(session_files, files=file_form('one.csv'))
    as_user.post(session_files, files=file_form(('two.zip', zip_cont)))

    # try to get non-existent file (Use admin because the user permissions is checked)
    r = as_user.get(session_files + '/non-existent.csv')
    assert r.status_code == 404

    # try to get file w/ non-matching hash
    r = as_user.get(session_files + '/one.csv', params={'hash': 'match me if you can'})
    assert r.status_code == 409

    # get download ticket for single file
    r = as_user.get(session_files + '/one.csv', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # download single file w/ ticket
    r = as_user.get(session_files + '/one.csv', params={'ticket': ticket})
    assert r.ok

    # try to get zip info for non-zip file
    r = as_user.get(session_files + '/one.csv', params={'ticket': ticket, 'info': 'true'})
    assert r.status_code == 400

    # try to get zip member of non-zip file
    r = as_user.get(session_files + '/one.csv', params={'ticket': ticket, 'member': 'hardly'})
    assert r.status_code == 400

    # try to download a different file w/ ticket
    r = as_user.get(session_files + '/two.zip', params={'ticket': ticket})
    assert r.status_code == 400

    # get download ticket for zip file
    r = as_user.get(session_files + '/two.zip', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # get zip info
    r = as_user.get(session_files + '/two.zip', params={'ticket': ticket, 'info': 'true'})
    assert r.ok

    # try to get non-existent zip member
    r = as_user.get(session_files + '/two.zip', params={'ticket': ticket, 'member': 'hardly'})
    assert r.status_code == 400

    # get zip member
    r = as_user.get(session_files + '/two.zip', params={'ticket': ticket, 'member': 'two.csv'})
    assert r.ok

    # test legacy cas file handling
    (project, file_name, file_content) = legacy_cas_file
    # Add User to permissions
    as_admin.post('/projects/' + project + '/permissions', json={'_id': 'user@user.com', 'access': 'admin'})
    r = as_user.get('/projects/' + project + '/files/' + file_name, params={'ticket': ''})
    assert r.ok

    ticket = r.json()['ticket']

    r = as_user.get('/projects/' + project + '/files/' + file_name, params={'ticket': ticket})
    assert r.ok
    assert r.content == file_content


def test_filelist_range_download(data_builder, as_user, as_admin, file_form):
    project = data_builder.create_project()
    session = data_builder.create_session(project=project)

    # Add user to permissions
    as_admin.post('/projects/' + project + '/permissions', json={'_id': 'user@user.com', 'access': 'admin'})

    session_files = '/sessions/' + session + '/files'
    as_user.post(session_files, files=file_form(('one.csv', '123456789')))

    r = as_user.get(session_files + '/one.csv', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # verify contents
    r = as_user.get(session_files + '/one.csv',
                     params={'ticket': ticket})
    assert r.ok
    assert r.content == '123456789'

    # download single file from byte 0 to end of file
    r = as_user.get(session_files + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'bytes=0-'})
    assert r.ok
    assert r.content == '123456789'

    r = as_user.get(session_files + '/one.csv', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # download single file's first byte by using lower case header
    r = as_user.get(session_files + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'range': 'bytes=0-0'})
    assert r.ok
    assert r.content == '1'

    r = as_user.get(session_files + '/one.csv', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # download single file's first two byte
    r = as_user.get(session_files + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'bytes=0-1'})
    assert r.ok
    assert r.content == '12'

    r = as_user.get(session_files + '/one.csv', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # try to download single file with invalid unit
    r = as_user.get(session_files + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'lol=-5'})
    assert r.status_code == 200
    assert r.content == '123456789'

    r = as_user.get(session_files + '/one.csv', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # try to download single file with invalid range where the last byte is greater then the size of the file
    # in this case the whole file is returned
    r = as_user.get(session_files + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'bytes=0-500'})
    assert r.ok
    assert r.content == '123456789'

    r = as_user.get(session_files + '/one.csv', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # try to download single file with invalid range where the first byte is greater then the size of the file
    r = as_user.get(session_files + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'bytes=500-'})
    assert r.status_code == 416

    r = as_user.get(session_files + '/one.csv', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # try to download single file with invalid range first byte is greater than the last one
    r = as_user.get(session_files + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'bytes=10-5'})
    assert r.ok
    assert r.content == '123456789'

    r = as_user.get(session_files + '/one.csv', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # try to download single file with invalid range header syntax
    r = as_user.get(session_files + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'bytes-1+5'})
    assert r.ok
    assert r.content == '123456789'


@pytest.mark.skipif(not os.getenv('SCITRAN_PERSISTENT_FS_URL', 'osfs').startswith('osfs'),
                    reason="Only OSFS supports all of these special range formats.")
def test_filelist_advanced_range_download(data_builder, as_user, as_admin, file_form):
    # We run this test only with OSFS because other backends don't support fully the RFS standard.
    # Left comments about the found defects with the specific storage backends at the assertions.
    project = data_builder.create_project()
    session = data_builder.create_session(project=project)

    # Add User to permissions
    as_admin.post('/projects/' + project + '/permissions', json={'_id': 'user@user.com', 'access': 'admin'})

    session_files = '/sessions/' + session + '/files'
    as_user.post(session_files, files=file_form(('one.csv', '123456789')))

    r = as_user.get(session_files + '/one.csv', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # download single file's last 5 bytes
    # ASFS returns the whole file, since it doesn't support this range format
    r = as_user.get(session_files + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'bytes=-5'})
    assert r.ok
    assert r.content == '56789'

    r = as_user.get(session_files + '/one.csv', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # try to download single file with invalid range, in this case the whole file is returned
    # ASFS returns with status code 416
    r = as_user.get(session_files + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'bytes=-'})
    assert r.ok
    assert r.content == '123456789'

    r = as_user.get(session_files + '/one.csv', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # try to download single file with invalid range, can't parse first byte
    # ASFS returns with status code 400
    r = as_user.get(session_files + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'bytes=r-0'})
    assert r.ok
    assert r.content == '123456789'

    r = as_user.get(session_files + '/one.csv', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # try to download single file with invalid range, can't parse last byte
    # ASFS returns with status code 400
    r = as_user.get(session_files + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'bytes=0-bb'})
    assert r.ok
    assert r.content == '123456789'

    r = as_user.get(session_files + '/one.csv', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # try to download single file with invalid range syntax
    # ASFS returns with status code 400
    r = as_user.get(session_files + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'bytes=1+5'})
    assert r.ok
    assert r.content == '123456789'

    r = as_user.get(session_files + '/one.csv', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # download multiple ranges
    # GCSFS doesn't support multiple ranges
    r = as_user.get(session_files + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'bytes=1-2, 3-4'})
    assert r.ok
    boundary = r.headers.get('Content-Type').split('boundary=')[1]
    assert r.content == '--{0}\n' \
                        'Content-Type: text/csv\n' \
                        'Content-Range: bytes 1-2/9\n\n' \
                        '23\n' \
                        '--{0}\n' \
                        'Content-Type: text/csv\n' \
                        'Content-Range: bytes 3-4/9\n\n' \
                        '45\n'.format(boundary)

def test_analysis_download(data_builder, file_form, as_user, as_admin, as_drone, default_payload):
    project = data_builder.create_project()
    session = data_builder.create_session(project=project)
    # Add User to permissions
    as_admin.post('/projects/' + project + '/permissions', json={'_id': 'user@user.com', 'access': 'admin'})
    zip_cont = cStringIO.StringIO()
    with zipfile.ZipFile(zip_cont, 'w') as zip_file:
        zip_file.writestr('two.csv', 'sample\ndata\n')
    zip_cont.seek(0)

    # create (legacy) analysis for testing the download functionality
    r = as_user.post('/sessions/' + session + '/analyses', files=file_form('one.csv', ('two.zip', zip_cont), meta={
        'label': 'test',
        'inputs': [{'name': 'one.csv'}],
        'outputs': [{'name': 'two.zip'}],
    }))
    assert r.ok
    analysis = r.json()['_id']

    analysis_inputs = '/sessions/' + session + '/analyses/' + analysis + '/inputs'
    analysis_outputs = '/sessions/' + session + '/analyses/' + analysis + '/files'
    new_analysis_inputs = '/analyses/' + analysis + '/inputs'
    new_analysis_outputs = '/analyses/' + analysis + '/files'

    # Check that analysis inputs are placed under the inputs key
    r = as_user.get('/sessions/' + session + '/analyses/' + analysis)
    assert r.ok
    assert [f['name'] for f in r.json().get('inputs', [])] == ['one.csv']

    # try to download analysis inputs w/ non-existent ticket
    r = as_user.get(analysis_inputs, params={'ticket': '000000000000000000000000'})
    assert r.status_code == 404

    # get analysis batch download ticket for all inputs
    r = as_user.get(analysis_inputs, params={'ticket': ''}, json={"optional":True,"nodes":[{"level":"analysis","_id":analysis}]})
    assert r.ok
    ticket = r.json()['ticket']

    # filename is analysis_<label> not analysis_<_id>
    assert r.json()['filename'] == 'analysis_test.tar'

    # batch download analysis inputs w/ ticket from wrong endpoint
    r = as_user.get(analysis_inputs, params={'ticket': ticket})
    assert r.status_code == 400

    # batch download analysis inputs w/ ticket from correct endpoint
    r = as_user.get('/download', params={'ticket': ticket})
    assert r.ok

    # Check to make sure outputs are in tar
    with tarfile.open(mode='r', fileobj=cStringIO.StringIO(r.content)) as tar:
        assert [m.name for m in tar.getmembers()] == ['test/input/one.csv']

    ### Using '/download' endpoint only - for analysis outputs only! ###
    # try to download analysis outputs w/ non-existent ticket
    r = as_user.get('/download', params={'ticket': '000000000000000000000000'})
    assert r.status_code == 404

    # get analysis batch download ticket for all outputs
    r = as_user.get('/download', params={'ticket': ''}, json={"optional":True,"nodes":[{"level":"analysis","_id":analysis}]})
    assert r.ok
    ticket = r.json()['ticket']

    # filename is analysis_<label> not analysis_<_id>
    assert r.json()['filename'] == 'analysis_test.tar'

    # batch download analysis outputs w/ ticket
    r = as_user.get('/download', params={'ticket': ticket})
    assert r.ok

    # Check to make sure inputs and outputs are in tar
    with tarfile.open(mode='r', fileobj=cStringIO.StringIO(r.content)) as tar:
        assert set([m.name for m in tar.getmembers()]) == set(['test/input/one.csv', 'test/output/two.zip'])

    # try to get download ticket for non-existent analysis file
    r = as_user.get(analysis_inputs + '/non-existent.csv')
    assert r.status_code == 404

    # get analysis download ticket for single file
    r = as_user.get(analysis_inputs + '/one.csv', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # download single analysis file w/ ticket
    r = as_user.get(analysis_inputs + '/one.csv', params={'ticket': ticket})
    assert r.ok

    # try to get zip info for non-zip file
    r = as_user.get(analysis_inputs + '/one.csv', params={'ticket': ticket, 'info': 'true'})
    assert r.status_code == 400

    # try to get zip member of non-zip file
    r = as_user.get(analysis_inputs + '/one.csv', params={'ticket': ticket, 'member': 'nosuch'})
    assert r.status_code == 400

    # try to download a different file w/ ticket
    r = as_user.get(analysis_outputs + '/two.zip', params={'ticket': ticket})
    assert r.status_code == 400

    # get analysis download ticket for zip file
    r = as_user.get(analysis_outputs + '/two.zip', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # get zip info
    r = as_user.get(analysis_outputs + '/two.zip', params={'ticket': ticket, 'info': 'true'})
    assert r.ok

    # try to get non-existent zip member
    r = as_user.get(analysis_outputs + '/two.zip', params={'ticket': ticket, 'member': 'nosuch'})
    assert r.status_code == 400

    # get zip member
    r = as_user.get(analysis_outputs + '/two.zip', params={'ticket': ticket, 'member': 'two.csv'})
    assert r.ok

    ### single file analysis download using FileListHandler ###
    # try to get download ticket for non-existent analysis file
    r = as_user.get(new_analysis_inputs + '/non-existent.csv')
    assert r.status_code == 404

    # get analysis download ticket for single file
    r = as_user.get(new_analysis_inputs + '/one.csv', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # download single analysis file w/ ticket
    r = as_user.get(new_analysis_inputs + '/one.csv', params={'ticket': ticket})
    assert r.ok

    # try to get zip info for non-zip file
    r = as_user.get(new_analysis_inputs + '/one.csv', params={'ticket': ticket, 'info': 'true'})
    assert r.status_code == 400

    # try to get zip member of non-zip file
    r = as_user.get(new_analysis_inputs + '/one.csv', params={'ticket': ticket, 'member': 'nosuch'})
    assert r.status_code == 400

    # try to download a different file w/ ticket
    r = as_user.get(new_analysis_outputs + '/two.zip', params={'ticket': ticket})
    assert r.status_code == 400

    # get analysis download ticket for zip file
    r = as_user.get(new_analysis_outputs + '/two.zip', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # get zip info
    r = as_user.get(new_analysis_outputs + '/two.zip', params={'ticket': ticket, 'info': 'true'})
    assert r.ok

    # try to get non-existent zip member
    r = as_user.get(new_analysis_outputs + '/two.zip', params={'ticket': ticket, 'member': 'nosuch'})
    assert r.status_code == 400

    # get zip member
    r = as_user.get(new_analysis_outputs + '/two.zip', params={'ticket': ticket, 'member': 'two.csv'})
    assert r.ok

    # delete session analysis (job)
    r = as_user.delete('/sessions/' + session + '/analyses/' + analysis)
    assert r.ok


def test_analyses_range_download(data_builder, as_user, as_admin, file_form):
    project = data_builder.create_project()
    session = data_builder.create_session(project=project)
    # Add User to permissions
    as_admin.post('/projects/' + project + '/permissions', json={'_id': 'user@user.com', 'access': 'admin'})
    zip_cont = cStringIO.StringIO()
    with zipfile.ZipFile(zip_cont, 'w') as zip_file:
        zip_file.writestr('two.csv', 'sample\ndata\n')
    zip_cont.seek(0)

    # create (legacy) analysis for testing the download functionality
    r = as_user.post('/sessions/' + session + '/analyses', files=file_form(('one.csv', '123456789'),
                                                                            ('two.zip', zip_cont),
                                                                            meta={
                                                                                'label': 'test',
                                                                                'inputs': [{'name': 'one.csv'}],
                                                                                'outputs': [{'name': 'two.zip'}],
                                                                            }))
    assert r.ok
    analysis = r.json()['_id']

    analysis_inputs = '/analyses/' + analysis + '/inputs'

    r = as_user.get(analysis_inputs + '/one.csv', params={'ticket': ''})
    assert r.ok
    ticket = r.json()['ticket']

    # verify contents
    r = as_user.get(analysis_inputs + '/one.csv',
                     params={'ticket': ticket})
    assert r.ok
    assert r.content == '123456789'

    # download single file from byte 0 to end of file
    r = as_user.get(analysis_inputs + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'bytes=0-'})
    assert r.ok
    assert r.content == '123456789'

    # download single file's first byte by using lower case header
    r = as_user.get(analysis_inputs + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'range': 'bytes=0-0'})
    assert r.ok
    assert r.content == '1'

    # download single file's first two byte
    r = as_user.get(analysis_inputs + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'bytes=0-1'})
    assert r.ok
    assert r.content == '12'

    # try to download single file with invalid unit
    r = as_user.get(analysis_inputs + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'lol=-5'})
    assert r.status_code == 200
    assert r.content == '123456789'

    # try to download single file with invalid range where the last byte is greater then the size of the file
    # in this case the whole file is returned
    r = as_user.get(analysis_inputs + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'bytes=0-500'})
    assert r.ok
    assert r.content == '123456789'

    # try to download single file with invalid range where the first byte is greater then the size of the file
    r = as_user.get(analysis_inputs + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'bytes=500-'})
    assert r.status_code == 416

    # try to download single file with invalid range first byte is greater than the last one
    r = as_user.get(analysis_inputs + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'bytes=10-5'})
    assert r.ok
    assert r.content == '123456789'

    # try to download single file with invalid range header syntax
    r = as_user.get(analysis_inputs + '/one.csv',
                     params={'ticket': ticket, 'view': 'true'},
                     headers={'Range': 'bytes-1+5'})
    assert r.ok
    assert r.content == '123456789'


def test_filters(data_builder, file_form, as_user, as_admin):

    project = data_builder.create_project()
    session = data_builder.create_session()
    acquisition = data_builder.create_acquisition()
    acquisition2 = data_builder.create_acquisition()

    # Add User to permissions
    as_admin.post('/projects/' + project + '/permissions', json={'_id': 'user@user.com', 'access': 'admin'})

    as_user.post('/acquisitions/' + acquisition + '/files', files=file_form(
        "test.csv", meta={'name': "test.csv", 'type': 'csv', 'tags': ['red', 'blue']}))
    as_user.post('/acquisitions/' + acquisition + '/files', files=file_form(
        'test.dicom', meta={'name': 'test.dicom', 'type': 'dicom', 'tags': ['red']}))
    as_user.post('/acquisitions/' + acquisition2 + '/files', files=file_form(
        'test.nifti', meta={'name': 'test.nifti', 'type': 'nifti'}))
    r = as_user.get('/acquisitions/' + acquisition)
    assert r.ok

    # Malformed filters
    r = as_user.post('/download', json={
        'optional': False,
        'filters': [
            {'tags': 'red'}
        ],
        'nodes': [
            {'level': 'session', '_id': session},
        ]
    })
    assert r.status_code == 400

    # No filters
    r = as_user.post('/download', json={
        'optional': False,
        'nodes': [
            {'level': 'session', '_id': session},
        ]
    })
    assert r.ok
    assert r.json()['file_cnt'] == 3

    # Filter by tags
    r = as_user.post('/download', json={
        'optional': False,
        'filters': [
            {'tags': {'+':['red']}}
        ],
        'nodes': [
            {'level': 'session', '_id': session},
        ]
    })
    assert r.ok
    assert r.json()['file_cnt'] == 2

    # Use filter aliases
    r = as_user.post('/download', json={
        'optional': False,
        'filters': [
            {'tags': {'plus':['red']}}
        ],
        'nodes': [
            {'level': 'session', '_id': session},
        ]
    })
    assert r.ok
    # 'plus' is same as using '+'
    assert r.json()['file_cnt'] == 2

    # Filter by type
    as_user.post('/acquisitions/' + acquisition + '/files', files=file_form(
        "test", meta={'name': "test", 'tags': ['red', 'blue']}))
    r = as_user.post('/download', json={
        'optional': False,
        'filters': [
            {'types': {'+':['nifti']}}
        ],
        'nodes': [
            {'level': 'session', '_id': session},
        ]
    })
    assert r.ok
    assert r.json()['file_cnt'] == 1
    r = as_user.post('/download', json={
        'optional': False,
        'filters': [
            {'types': {'+':['null']}}
        ],
        'nodes': [
            {'level': 'session', '_id': session},
        ]
    })
    assert r.ok
    assert r.json()['file_cnt'] == 1

def test_summary(data_builder, as_user, as_admin, file_form):
    project = data_builder.create_project(label='project1')
    session = data_builder.create_session(label='session1')
    session2 = data_builder.create_session(label='session1')
    acquisition = data_builder.create_acquisition(session=session)
    acquisition2 = data_builder.create_acquisition(session=session2)

    # Add User to permissions
    as_admin.post('/projects/' + project + '/permissions', json={'_id': 'user@user.com', 'access': 'admin'})

    # upload the same file to each container created and use different tags to
    # facilitate download filter tests:
    # acquisition: [], session: ['plus'], project: ['plus', 'minus']
    file_name = 'test.csv'
    as_user.post('/acquisitions/' + acquisition + '/files', files=file_form(
        file_name, meta={'name': file_name, 'type': 'csv'}))

    as_user.post('/acquisitions/' + acquisition2 + '/files', files=file_form(
        file_name, meta={'name': file_name, 'type': 'csv'}))

    as_user.post('/sessions/' + session + '/files', files=file_form(
        file_name, meta={'name': file_name, 'type': 'csv', 'tags': ['plus']}))

    as_user.post('/projects/' + project + '/files', files=file_form(
        file_name, meta={'name': file_name, 'type': 'csv', 'tags': ['plus', 'minus']}))


    # also a deleted file to make sure it doesn't show up
    as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form(
        file_name, meta={'name': 'deleted_'+file_name, 'type': 'csv'}))
    r = as_admin.delete('/acquisitions/' + acquisition + '/files/deleted_' + file_name)
    assert r.ok

    missing_object_id = '000000000000000000000000'

    r = as_user.post('/download/summary', json=[{"level":"project", "_id":project}])
    assert r.ok
    assert len(r.json()) == 1
    assert r.json().get("csv", {}).get("count",0) == 4

    r = as_user.post('/download/summary', json=[{"level":"session", "_id":session}])
    assert r.ok
    assert len(r.json()) == 1
    assert r.json().get("csv", {}).get("count",0) == 2

    r = as_user.post('/download/summary', json=[{"level":"acquisition", "_id":acquisition},{"level":"acquisition", "_id":acquisition2}])
    assert r.ok
    assert len(r.json()) == 1
    assert r.json().get("csv", {}).get("count",0) == 2

    r = as_user.post('/download/summary', json=[{"level":"group", "_id":missing_object_id}])
    assert r.status_code == 400

    r = as_user.post('/sessions/' + session + '/analyses',  files=file_form(
        file_name, meta={'label': 'test', 'outputs':[{'name':file_name}]}))
    assert r.ok
    analysis = r.json()['_id']

    r = as_user.post('/download/summary', json=[{"level":"analysis", "_id":analysis}])
    assert r.ok
    assert len(r.json()) == 1
    assert r.json().get("tabular data", {}).get("count",0) == 1


def test_subject_download(data_builder, as_admin, file_form):
    project = data_builder.create_project()
    session = data_builder.create_session(subject={'code': 'subject-download'})
    subject = as_admin.get('/sessions/' + session).json()['subject']['_id']

    as_admin.post('/projects/' + project + '/files', files=file_form('test1.txt'))
    as_admin.post('/subjects/' + subject + '/files', files=file_form('test2.txt'))
    as_admin.post('/sessions/' + session + '/files', files=file_form('test3.txt'))

    r = as_admin.post('/download/summary', json=[{'level': 'project', '_id': project}])
    assert r.ok
    assert len(r.json()) == 1
    assert r.json()['text']['count'] == 3

    r = as_admin.post('/download', json={'nodes': [{'level': 'project', '_id': project}], 'optional': False})
    assert r.ok
    assert r.json()['file_cnt'] == 3

    r = as_admin.post('/download/summary', json=[{'level': 'subject', '_id': subject}])
    assert r.ok
    assert len(r.json()) == 1
    assert r.json()['text']['count'] == 2

    r = as_admin.post('/download', json={'nodes': [{'level': 'subject', '_id': subject}], 'optional': False})
    assert r.ok
    assert r.json()['file_cnt'] == 2
