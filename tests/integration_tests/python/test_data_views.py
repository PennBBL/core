import os
import bson
import csv
import json
import zipfile
import gzip
import collections
import pytest
from StringIO import StringIO

def years_to_secs(age):
    return int(age * 86400 * 365.25)

def secs_to_years(age):
    return age / (86400 * 365.25)

subject1 = {
    'code': '1001',
    'sex': 'male',
    'age': years_to_secs(27),
    'cohort': 'Control',
    'type': 'human'
}

subject2 = {
    'code': '1002',
    'sex': 'female',
    'age': years_to_secs(33),
    'cohort': 'Study',
    'type': 'human'
}

subject3 = {
    'code': '1003'
}

subjects = [subject1, subject2, subject3]

def csv_test_data(name, rows=5, delim=',', compress=False):
    result = [ 'name{0}value{0}value2'.format(delim) ]

    for i in range(rows):
        result.append('{1}{0}{2}{0}{3}'.format(delim, name, i, i*2))

    result = '\r\n'.join(result)

    if compress:
        sio = StringIO()
        gzf = gzip.GzipFile(fileobj=sio, mode='w')
        gzf.write(result)
        gzf.close()
        result = sio.getvalue()

    return result

def json_test_data(name, rows=5):
    output = []
    row_count = rows if rows else 1
    for i in range(row_count):
        output.append(collections.OrderedDict([
            ('name', name),
            ('aValue', i),
            ('value2', i*2)
        ]))

    if not rows:
        output = output[0]

    return json.dumps(output)

def zip_test_data(files=['dir1/file1.csv', 'dir2/file2.csv']):
    sio = StringIO()
    zf = zipfile.ZipFile(sio, 'w')

    for filename in files:
        root, _ext = os.path.splitext(filename)
        file_data = csv_test_data(os.path.basename(root))

        zf.writestr(filename, file_data)

    zf.close()
    return sio.getvalue()

def test_data_view_columns(as_user):
    r = as_user.get('/views/columns')
    assert r.ok
    columns = r.json()
    # This is just a subset of expected aliases
    expected_columns = { 'project', 'project.label', 'subject.label', 'session.age', 'session.age_years', 'file.name', 'analysis.label' }
    expected_missing_columns = { 'subject.age', 'subject.age_years' }
    valid_types = { 'int', 'float', 'bool', 'string', 'object' }

    for col in columns:
        assert 'name' in col
        assert 'description' in col

        if 'group' not in col:
            assert 'src' in col
            assert 'type' in col

            if col['type'] not in valid_types:
                pytest.fail('Unexpected column type: {}'.format(col['type']))

        expected_columns.discard(col['name'])
        assert col['name'] not in expected_missing_columns

    if len(expected_columns):
        pytest.fail('Did not find all expected columns: {}'.format(', '.join(expected_columns)))

def test_adhoc_empty_data_view(data_builder, as_admin, as_user):
    project = data_builder.create_project(label='test-project')
    r = as_user.post('/views/data?containerId={}'.format(project), json={})
    assert r.status_code == 400

def test_adhoc_data_view_permissions(data_builder, as_admin, as_user):
    project = data_builder.create_project(label='test-project')
    r = as_user.post('/views/data?containerId={}'.format(project), json={
        "columns": [
            { "src": "subject.code", "dst": "subject" }
        ]
    })
    assert r.status_code == 403

def test_adhoc_data_view_column_validation(data_builder, file_form, as_admin):
    # JSON
    project = data_builder.create_project(label='test-project')
    session = data_builder.create_session(project=project, label='test-session')
    file_form = file_form(('values.csv', csv_test_data('a1')))
    assert as_admin.post('/sessions/' + session + '/files', files=file_form).ok

    r = as_admin.post('/views/data?containerId={}'.format(project), json={
        "columns": [
            { "src": "session.permissions" }
        ]
    })
    assert r.status_code == 400

    r = as_admin.post('/views/data?containerId={}'.format(project), json={
        "columns": [
            { "src": "session.files" }
        ]
    })
    assert r.status_code == 400

def test_adhoc_data_view_empty_result(data_builder, file_form, as_admin):
    # JSON
    project = data_builder.create_project(label='test-project')
    r = as_admin.post('/views/data?containerId={}'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'project.label', 'dst': 'project' },
            { 'src': 'acquisition.label', 'dst': 'acquisition' }
        ]
    })
    assert r.ok
    assert r.headers['content-disposition'] == 'attachment; filename="view-data.json"'
    rows = r.json()['data']
    assert len(rows) == 0

    # JSON (flat)
    project = data_builder.create_project(label='test-project')
    r = as_admin.post('/views/data?containerId={}&format=json-flat'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'project.label', 'dst': 'project' },
            { 'src': 'acquisition.label', 'dst': 'acquisition' }
        ]
    })
    assert r.ok
    rows = r.json()
    assert len(rows) == 0

    # JSON row-column
    r = as_admin.post('/views/data?containerId={}&format=json-row-column'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'project.label', 'dst': 'project' },
            { 'src': 'acquisition.label', 'dst': 'acquisition' }
        ]
    })
    assert r.ok
    data = r.json()['data']
    assert len(data['columns']) == 0
    assert len(data['rows']) == 0

def test_adhoc_data_view_metadata_only(data_builder, file_form, as_admin):
    project = data_builder.create_project(label='test-project')
    session1 = data_builder.create_session(project=project, subject=subject1, label='ses-01')
    session2 = data_builder.create_session(project=project, subject=subject2, label='ses-01')
    acquisition1 = data_builder.create_acquisition(session=session1, label='scout')
    acquisition2 = data_builder.create_acquisition(session=session2, label='scout')

    r = as_admin.post('/views/data?containerId={}'.format(project), json={
        'includeIds': True,
        'includeLabels': False,
        'columns': [
            { 'src': 'project.label', 'dst': 'project_label' },
            { 'src': 'subject.code', 'dst': 'subject_label' },
            { 'src': 'subject.age' },
            { 'src': 'subject.age_years' },
            { 'src': 'subject.sex' },
            { 'src': 'session.label', 'dst': 'session_label' },
            { 'src': 'acquisition.label', 'dst': 'acquisition_label' }
        ]
    })

    assert r.ok
    rows = r.json()['data']
    assert len(rows) == 2

    assert rows[0]['project.id'] == project
    assert rows[0]['project_label'] == 'test-project'
    assert rows[0]['subject_label'] == subject1['code']
    assert rows[0]['subject.age'] == subject1['age']
    assert rows[0]['subject.age_years'] == secs_to_years(subject1['age'])
    assert rows[0]['subject.sex'] == subject1['sex']
    assert rows[0]['session.id'] == session1
    assert rows[0]['session_label'] == 'ses-01'
    assert rows[0]['acquisition.id'] == acquisition1
    assert rows[0]['acquisition_label'] == 'scout'

    assert rows[1]['project.id'] == project
    assert rows[1]['project_label'] == 'test-project'
    assert rows[1]['subject_label'] == subject2['code']
    assert rows[1]['subject.age'] == subject2['age']
    assert rows[1]['subject.age_years'] == secs_to_years(subject2['age'])
    assert rows[1]['subject.sex'] == subject2['sex']
    assert rows[1]['session.id'] == session2
    assert rows[1]['session_label'] == 'ses-01'
    assert rows[1]['acquisition.id'] == acquisition2
    assert rows[1]['acquisition_label'] == 'scout'

def test_adhoc_data_view_flatten_info(data_builder, file_form, as_admin):
    project = data_builder.create_project(label='test-project')
    session1 = data_builder.create_session(project=project, subject=subject1, label='ses-01')
    session2 = data_builder.create_session(project=project, subject=subject2, label='ses-01')

    as_admin.post('/sessions/' + session1 + '/info', json={'replace': {
        'value': 4,
        'nested': {
            'value': 12,
            'value2': 8
        }
    }})
    as_admin.post('/sessions/' + session2 + '/info', json={'replace': {
        'value': 6,
        'value2': 19,
        'nested': {
            'value': 23
        }
    }})

    # Keep src key
    r = as_admin.post('/views/data?containerId={}&format=csv'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'session.id' },
            { 'src': 'session.info' },
        ]
    })

    assert r.ok
    body = StringIO(r.text)
    rows = list(csv.reader(body))
    columns = rows.pop(0)

    assert len(columns) == 4
    assert columns[0] == 'session.id'

    value_idx = columns.index('session.info.value')
    nested_value_idx = columns.index('session.info.nested.value')
    nested_value2_idx = columns.index('session.info.nested.value2')

    assert len(rows) == 2

    assert rows[0][0] == session1
    assert rows[0][value_idx] == '4'
    assert rows[0][nested_value_idx] == '12'
    assert rows[0][nested_value2_idx] == '8'

    assert rows[1][0] == session2
    assert rows[1][value_idx] == '6'
    assert rows[1][nested_value_idx] == '23'
    assert rows[1][nested_value2_idx] == ''

    # Remap to dst key
    r = as_admin.post('/views/data?containerId={}&format=csv'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'session.id' },
            { 'src': 'session.info', 'dst': 'session_info' },
        ]
    })

    assert r.ok
    body = StringIO(r.text)
    rows = list(csv.reader(body))
    columns = rows.pop(0)

    assert len(columns) == 4
    assert columns[0] == 'session.id'

    value_idx = columns.index('session_info.value')
    nested_value_idx = columns.index('session_info.nested.value')
    nested_value2_idx = columns.index('session_info.nested.value2')

    assert len(rows) == 2

    assert rows[0][0] == session1
    assert rows[0][value_idx] == '4'
    assert rows[0][nested_value_idx] == '12'
    assert rows[0][nested_value2_idx] == '8'

    assert rows[1][0] == session2
    assert rows[1][value_idx] == '6'
    assert rows[1][nested_value_idx] == '23'
    assert rows[1][nested_value2_idx] == ''

def test_adhoc_data_view_session_target(data_builder, file_form, as_admin):
    project = data_builder.create_project(label='test-project')
    session1 = data_builder.create_session(project=project, subject=subject1, label='ses-01')
    session2 = data_builder.create_session(project=project, subject=subject2, label='ses-01')
    acquisition1 = data_builder.create_acquisition(session=session1, label='scout')
    acquisition2 = data_builder.create_acquisition(session=session2, label='scout')

    # Test "project" column grouping
    r = as_admin.post('/views/data?containerId={}&format=json-flat'.format(session2), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'project' },
            { 'src': 'subject.code', 'dst': 'subject' },
            { 'src': 'subject.sex' },
            { 'src': 'subject.type' },
            { 'src': 'subject.cohort' },
            { 'src': 'session.label', 'dst': 'session' },
            { 'src': 'session.age_years' },
            { 'src': 'acquisition.label', 'dst': 'acquisition' }
        ]
    })

    assert r.ok
    rows = r.json()
    assert len(rows) == 1

    assert rows[0]['project.id'] == project
    assert rows[0]['project.label'] == 'test-project'
    assert rows[0]['subject'] == subject2['code']
    assert rows[0]['subject.sex'] == subject2['sex']
    assert rows[0]['subject.type'] == subject2['type']
    assert rows[0]['subject.cohort'] == subject2['cohort']
    assert rows[0]['session'] == 'ses-01'
    assert rows[0]['session.age_years'] == 33.0
    assert rows[0]['acquisition'] == 'scout'

def test_adhoc_data_view_csv_files(data_builder, file_form, as_admin):
    project = data_builder.create_project(label='test-project')
    session1 = data_builder.create_session(project=project, subject=subject1, label='ses-01')
    session2 = data_builder.create_session(project=project, subject=subject2, label='ses-01')
    acquisition1 = data_builder.create_acquisition(session=session1, label='scout')
    acquisition2 = data_builder.create_acquisition(session=session2, label='scout')

    file_form1 = file_form(('values.csv', csv_test_data('a1')))
    assert as_admin.post('/acquisitions/' + acquisition1 + '/files', files=file_form1).ok

    file_form2 = file_form(('values.csv', csv_test_data('a2')))
    assert as_admin.post('/acquisitions/' + acquisition2 + '/files', files=file_form2).ok

    # Test column aliases as well
    r = as_admin.post('/views/data?containerId={}'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'subject.label' },
            { 'src': 'subject.age' },
            { 'src': 'subject.sex' }
        ],
        'fileSpec': {
            'container': 'acquisition',
            'filter': { 'value': '*.csv' },
            'columns': [
                { 'src': 'name' },
                { 'src': 'value', 'type': 'int' },
                { 'src': 'value2', 'type': 'float' }
            ]
        }
    })

    assert r.ok
    rows = r.json()['data']

    assert len(rows) == 10

    for i in range(2):
        name_value = 'a{}'.format(i+1)
        subject = subjects[i]
        for j in range(5):
            row = rows[i*5+j]

            assert row['subject.label'] == subject['code']
            assert row['subject.age'] == subject['age']
            assert row['subject.sex'] == subject['sex']
            assert row['name'] == name_value
            assert row['value'] == j
            assert isinstance(row['value2'], float)
            assert row['value2'] == 2*j

def test_adhoc_data_view_json_row_column_format(data_builder, file_form, as_admin):
    project = data_builder.create_project(label='test-project')
    session1 = data_builder.create_session(project=project, subject=subject1, label='ses-01')
    acquisition1 = data_builder.create_acquisition(session=session1, label='scout')

    file_form1 = file_form(('values.csv', csv_test_data('a1')))
    assert as_admin.post('/acquisitions/' + acquisition1 + '/files', files=file_form1).ok

    r = as_admin.post('/views/data?containerId={}&format=json-row-column'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'subject.code', 'dst': 'subject' },
            { 'src': 'subject.age' },
            { 'src': 'subject.sex' }
        ],
        'fileSpec': {
            'container': 'acquisition',
            'filter': { 'value': '*.csv' }
        }
    })

    assert r.ok
    data = r.json()['data']
    columns = data['columns']
    rows = data['rows']

    assert columns == ['subject', 'subject.age', 'subject.sex', 'name', 'value', 'value2']
    assert len(rows) == 5

    for i in range(5):
        row = rows[i]

        assert row[0] == subject1['code']
        assert row[1] == subject1['age']
        assert row[2] == subject1['sex']
        assert row[3] == 'a1'
        assert row[4] == str(i)
        assert row[5] == str(2*i)

def test_adhoc_data_view_csv_format(data_builder, file_form, as_admin):
    project = data_builder.create_project(label='test-project')
    session1 = data_builder.create_session(project=project, subject=subject1, label='ses-01')
    acquisition1 = data_builder.create_acquisition(session=session1, label='scout')

    file_form1 = file_form(('values.csv', csv_test_data('a1')))
    assert as_admin.post('/acquisitions/' + acquisition1 + '/files', files=file_form1).ok

    # Test without columns
    r = as_admin.post('/views/data?containerId={}&format=csv'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'fileSpec': {
            'container': 'acquisition',
            'filter': { 'value': '*.csv' }
        }
    })

    assert r.ok
    assert r.headers['content-disposition'] == 'attachment; filename="view-data.csv"'
    body = StringIO(r.text)
    rows = list(csv.reader(body))
    columns = rows.pop(0)

    assert columns == ['name', 'value', 'value2']
    assert len(rows) == 5

    for i in range(5):
        row = rows[i]

        assert row[0] == 'a1'
        assert row[1] == str(i)
        assert row[2] == str(2*i)

def test_adhoc_data_view_tsv_format(data_builder, file_form, as_admin):
    project = data_builder.create_project(label='test-project')
    session1 = data_builder.create_session(project=project, subject=subject1, label='ses-01')
    acquisition1 = data_builder.create_acquisition(session=session1, label='scout')

    file_form1 = file_form(('values.csv', csv_test_data('a1')))
    assert as_admin.post('/acquisitions/' + acquisition1 + '/files', files=file_form1).ok

    r = as_admin.post('/views/data?containerId={}&format=tsv'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'subject.code', 'dst': 'subject' },
            { 'src': 'subject.age' },
            { 'src': 'subject.sex' }
        ],
        'fileSpec': {
            'container': 'acquisition',
            'filter': { 'value': '*.csv' }
        }
    })

    assert r.ok
    assert r.headers['content-disposition'] == 'attachment; filename="view-data.tsv"'
    body = StringIO(r.text)
    rows = list(csv.reader(body, dialect='excel-tab'))
    columns = rows.pop(0)

    assert columns == ['subject', 'subject.age', 'subject.sex', 'name', 'value', 'value2']
    assert len(rows) == 5

    for i in range(5):
        row = rows[i]

        assert row[0] == subject1['code']
        assert row[1] == str(subject1['age'])
        assert row[2] == subject1['sex']
        assert row[3] == 'a1'
        assert row[4] == str(i)
        assert row[5] == str(2*i)

def test_adhoc_data_view_tsv_file(data_builder, file_form, as_admin):
    project = data_builder.create_project(label='test-project')
    session1 = data_builder.create_session(project=project, subject=subject1, label='ses-01')
    acquisition1 = data_builder.create_acquisition(session=session1, label='scout')

    file_form1 = file_form(('values.tsv', csv_test_data('a1', delim='\t')))
    assert as_admin.post('/acquisitions/' + acquisition1 + '/files', files=file_form1).ok

    r = as_admin.post('/views/data?containerId={}'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'subject.code', 'dst': 'subject' }
        ],
        'fileSpec': {
            'container': 'acquisition',
            'filter': { 'value': '*.tsv' }
        }
    })

    assert r.ok
    rows = r.json()['data']

    assert len(rows) == 5

    for i in range(5):
        row = rows[i]

        assert row['subject'] == subject1['code']
        assert row['name'] == 'a1'
        assert row['value'] == str(i)
        assert row['value2'] == str(2*i)

def test_adhoc_data_view_json_list_file(data_builder, file_form, as_admin):
    project = data_builder.create_project(label='test-project')
    session1 = data_builder.create_session(project=project, subject=subject1, label='ses-01')
    acquisition1 = data_builder.create_acquisition(session=session1, label='scout')

    file_form1 = file_form(('values.json', json_test_data('a1')))
    assert as_admin.post('/acquisitions/' + acquisition1 + '/files', files=file_form1).ok

    r = as_admin.post('/views/data?containerId={}'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'subject.code', 'dst': 'subject' }
        ],
        'fileSpec': {
            'container': 'acquisition',
            'filter': { 'value': '*.json' }
        }
    })

    assert r.ok
    rows = r.json()['data']

    assert len(rows) == 5

    for i in range(5):
        row = rows[i]

        assert row['subject'] == subject1['code']
        assert row['name'] == 'a1'
        assert row['aValue'] == i
        assert row['value2'] == 2*i

def test_adhoc_data_view_json_dict_file(data_builder, file_form, as_admin):
    project = data_builder.create_project(label='test-project')
    session1 = data_builder.create_session(project=project, subject=subject1, label='ses-01')
    acquisition1 = data_builder.create_acquisition(session=session1, label='scout')

    file_form1 = file_form(('values.json', json_test_data('a1', rows=False)))
    assert as_admin.post('/acquisitions/' + acquisition1 + '/files', files=file_form1).ok

    r = as_admin.post('/views/data?containerId={}'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'subject.code', 'dst': 'subject' }
        ],
        'fileSpec': {
            'container': 'acquisition',
            'filter': { 'value': '*.json' }
        }
    })

    assert r.ok
    rows = r.json()['data']

    assert len(rows) == 1
    row = rows[0]
    assert row['subject'] == subject1['code']
    assert row['name'] == 'a1'
    assert row['aValue'] == 0
    assert row['value2'] == 0

def test_adhoc_data_view_missing_data_csv_files(data_builder, file_form, as_admin):
    project = data_builder.create_project(label='test-project')
    session1 = data_builder.create_session(project=project, subject=subject1, label='ses-01')
    session2 = data_builder.create_session(project=project, subject=subject2, label='ses-01')
    session3 = data_builder.create_session(project=project, subject=subject3, label='ses-01')
    acquisition1 = data_builder.create_acquisition(session=session1, label='scout')
    acquisition2 = data_builder.create_acquisition(session=session2, label='scout')
    acquisition3 = data_builder.create_acquisition(session=session3, label='scout')

    file_form1 = file_form(('values.csv.gz', csv_test_data('a1', compress=True)))
    assert as_admin.post('/acquisitions/' + acquisition2 + '/files', files=file_form1).ok

    file_form2 = file_form(('values.csv.gz', csv_test_data('a2', compress=True)))
    assert as_admin.post('/acquisitions/' + acquisition3 + '/files', files=file_form2).ok

    # ============================
    # Default missing data strategy (replace values with null)
    # ============================
    r = as_admin.post('/views/data?containerId={}'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'subject.code', 'dst': 'subject' },
            { 'src': 'subject.age' },
            { 'src': 'subject.sex' }
        ],
        'fileSpec': {
            'container': 'acquisition',
            'filter': { 'value': '*.csv.gz' }
        }
    })

    assert r.ok
    rows = r.json()['data']

    assert len(rows) == 11

    for i in range(2):
        name_value = 'a{}'.format(i+1)
        subject = subjects[i+1]
        for j in range(5):
            row = rows[i*5+j]

            assert row['subject'] == subject['code']
            assert row['subject.age'] == subject.get('age')
            assert row['subject.sex'] == subject.get('sex')
            assert row['name'] == name_value
            assert row['value'] == str(j)
            assert row['value2'] == str(2*j)

    # Subject with no file is last
    row = rows[10]
    assert row['subject'] == subject1['code']
    assert row['subject.age'] == subject1['age']
    assert row['subject.sex'] == subject1['sex']
    assert row['name'] == None
    assert row['value'] == None
    assert row['value2'] == None

    # ============================
    # Drop rows missing data strategy
    # ============================
    r = as_admin.post('/views/data?containerId={}'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'missingDataStrategy': 'drop-row',
        'columns': [
            { 'src': 'subject.code', 'dst': 'subject' },
            { 'src': 'subject.age' },
            { 'src': 'subject.sex' }
        ],
        'fileSpec': {
            'container': 'acquisition',
            'filter': { 'value': '*.csv.gz' }
        }
    })

    assert r.ok
    rows = r.json()['data']

    assert len(rows) == 5
    for i in range(5):
        row = rows[i]

        assert row['subject'] == subject2['code']
        assert row['subject.age'] == subject2.get('age')
        assert row['subject.sex'] == subject2.get('sex')
        assert row['name'] == 'a1'
        assert row['value'] == str(i)
        assert row['value2'] == str(2*i)

def test_adhoc_data_view_zip_members(data_builder, file_form, as_admin):
    project = data_builder.create_project(label='test-project')
    session1 = data_builder.create_session(project=project, subject=subject1, label='ses-01')
    acquisition1 = data_builder.create_acquisition(session=session1, label='scout')

    file_form1 = file_form(('data.zip', zip_test_data()))
    assert as_admin.post('/acquisitions/' + acquisition1 + '/files', files=file_form1).ok

    r = as_admin.post('/views/data?containerId={}'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'subject.code', 'dst': 'subject' },
            { 'src': 'subject.age' },
            { 'src': 'subject.sex' }
        ],
        'fileSpec': {
            'container': 'acquisition',
            'filter': { 'value': '*.zip' },
            'zipMember': { 'value': 'dir2/*.csv' }
        }
    })

    assert r.ok
    rows = r.json()['data']

    assert len(rows) == 5

    for i in range(5):
        row = rows[i]

        assert row['subject'] == subject1['code']
        assert row['subject.age'] == subject1['age']
        assert row['subject.sex'] == subject1['sex']
        assert row['name'] == 'file2'
        assert row['value'] == str(i)
        assert row['value2'] == str(2*i)

def test_adhoc_data_view_analyses_files(data_builder, file_form, as_admin, as_drone, api_db):
    project = data_builder.create_project(label='test-project')
    session = data_builder.create_session(project=project, subject=subject1, label='ses-01')
    acquisition = data_builder.create_acquisition(session=session, label='scout')
    assert as_admin.post('/acquisitions/' + acquisition + '/files', files=file_form('input.csv')).ok

    gear1 = data_builder.create_gear(gear={'name': 'data-view-gear1', 'version': '0.0.12', 'inputs': {'csv': {'base': 'file'}}})
    gear2 = data_builder.create_gear(gear={'name': 'data-view-gear2', 'version': '0.0.13', 'inputs': {'csv': {'base': 'file'}}})

    # Create job-based analysis 1
    r = as_admin.post('/sessions/' + session + '/analyses', json={
        'label': 'analysis-1',
        'job': {'gear_id': gear1,
                'inputs': {'csv': {'type': 'acquisition', 'id': acquisition, 'name': 'input.csv'}}}
    })
    assert r.ok
    analysis1 = r.json()['_id']

    # Get job id
    r = as_admin.get('/analyses/' + analysis1)
    assert r.ok
    job1 = r.json().get('job')

    # Upload output file
    file_form1 = file_form(('values.csv', csv_test_data('a1')))
    r = as_drone.post('/engine',
        params={'level': 'analysis', 'id': analysis1, 'job': job1},
        files=file_form1)
    assert r.ok

    # Create job-based analysis 2
    r = as_admin.post('/sessions/' + session + '/analyses', json={
        'label': 'second-analysis',
        'job': {'gear_id': gear2,
                'inputs': {'csv': {'type': 'acquisition', 'id': acquisition, 'name': 'input.csv'}}}
    })
    assert r.ok
    analysis2 = r.json()['_id']

    # Get job id
    r = as_admin.get('/analyses/' + analysis2)
    assert r.ok
    job2 = r.json().get('job')

    # Upload output file
    file_form2 = file_form(('values2.csv', csv_test_data('a2')))
    file_form3 = file_form(('values3.csv', csv_test_data('a3')))
    r = as_drone.post('/engine',
        params={'level': 'analysis', 'id': analysis2, 'job': job2},
        files=[
            ('file', file_form2['file']),
            ('file', file_form3['file'])
        ])
    assert r.ok

    # Execute data view, match on label
    r = as_admin.post('/views/data?containerId={}'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'subject.code', 'dst': 'subject' },
            { 'src': 'subject.age' },
            { 'src': 'subject.sex' }
        ],
        'fileSpec': {
            'container': 'session',
            'filter': { 'value': '*.csv' },
            'analysisFilter': {
                'label': { 'value': 'analysis*' }
            }
        }
    })

    assert r.ok
    rows = r.json()['data']

    assert len(rows) == 5

    for i in range(5):
        row = rows[i]

        assert row['subject'] == subject1['code']
        assert row['subject.age'] == subject1['age']
        assert row['subject.sex'] == subject1['sex']
        assert row['name'] == 'a1'
        assert row['value'] == str(i)
        assert row['value2'] == str(2*i)
        assert '_index' not in row

    # Execute data view, match on second label, multiple files
    r = as_admin.post('/views/data?containerId={}'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'subject.code', 'dst': 'subject' },
            { 'src': 'subject.age' },
            { 'src': 'subject.sex' },
            { 'src': 'analysis.label', 'dst': 'analysis' },
            { 'src': 'file.name', 'dst': 'filename' },
            { 'src': 'file.row_number', 'dst': 'row' }
        ],
        'fileSpec': {
            'container': 'session',
            'filter': { 'value': '*.csv' },
            'match': 'all',
            'analysisFilter': {
                'label': { 'value': 'second-analysis' }
            }
        }
    })

    assert r.ok
    rows = r.json()['data']

    assert len(rows) == 10

    for i in range(2):
        name_value = 'a{}'.format(i+2)
        filename = 'values{}.csv'.format(i+2)
        for j in range(5):
            row = rows[i*5+j]

            assert row['subject'] == subject1['code']
            assert row['subject.age'] == subject1['age']
            assert row['subject.sex'] == subject1['sex']
            assert row['filename'] == filename
            assert row['row'] == j
            assert row['analysis'] == 'second-analysis'
            assert row['name'] == name_value
            assert row['value'] == str(j)
            assert row['value2'] == str(2*j)
            assert '_index' not in row

    # Execute data view, match on second label, multiple files, no processing
    r = as_admin.post('/views/data?containerId={}'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'subject.code', 'dst': 'subject' },
            { 'src': 'subject.age' },
            { 'src': 'subject.sex' },
            { 'src': 'analysis.label', 'dst': 'analysis' },
            { 'src': 'file.name', 'dst': 'filename' }
        ],
        'fileSpec': {
            'container': 'session',
            'filter': { 'value': '*.csv' },
            'match': 'all',
            'analysisFilter': {
                'label': { 'value': 'second-analysis' }
            },
            'processFiles': False
        }
    })

    assert r.ok
    rows = r.json()['data']

    assert len(rows) == 2

    for i in range(2):
        row = rows[i]

        assert row['subject'] == subject1['code']
        assert row['subject.age'] == subject1['age']
        assert row['subject.sex'] == subject1['sex']
        assert row['filename'] == 'values{}.csv'.format(i+2)
        assert row['analysis'] == 'second-analysis'

    # Execute data view, match on gear.name
    r = as_admin.post('/views/data?containerId={}'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'file.name', 'dst': 'filename' }
        ],
        'fileSpec': {
            'container': 'session',
            'filter': { 'value': '*.csv' },
            'match': 'all',
            'analysisFilter': {
                'gear.name': {'value': 'data-view-gear1'}
            },
            'processFiles': False
        }
    })

    assert r.ok
    rows = r.json()['data']
    assert len(rows) == 1
    assert {'filename':'values.csv'} in rows

    # Execute data view, match on gear.name + gear.version
    r = as_admin.post('/views/data?containerId={}'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'file.name', 'dst': 'filename' }
        ],
        'fileSpec': {
            'container': 'session',
            'filter': { 'value': '*.csv' },
            'match': 'all',
            'analysisFilter': {
                'gear.name': {'value': 'data-view-gear?'},
                'gear.version': {'value': '0.0.13'}
            },
            'processFiles': False
        }
    })

    assert r.ok
    rows = r.json()['data']
    assert len(rows) == 2
    assert {'filename':'values2.csv'} in rows
    assert {'filename':'values3.csv'} in rows

    api_db.analyses.delete_one({'_id': bson.ObjectId(analysis1)})
    api_db.analyses.delete_one({'_id': bson.ObjectId(analysis2)})

def test_user_data_view(as_user, as_public, as_admin):
    user_id = as_user.get('/users/self').json()['_id']
    admin_id = as_admin.get('/users/self').json()['_id']
    # Try to create with no body
    r = as_user.post('/containers/' + user_id + '/views')
    assert r.status_code == 400

    # Try to create invalid view
    view = { 'columns': [{'src': 'acquisition.label'}] }
    r = as_user.post('/containers/' + user_id + '/views', json=view)
    assert r.status_code == 400

    # Try to create a view on a different user
    view['label'] = 'test-view'
    r = as_user.post('/containers/' + admin_id + '/views', json=view)
    assert r.status_code == 403

    # Create a user-owned view
    r = as_user.post('/containers/' + user_id + '/views', json=view)
    assert r.ok
    view = r.json()['_id']

    # Attempt to get view as public
    r = as_public.get('/views/' + view)
    assert r.status_code == 403

    # Get view
    r = as_user.get('/views/' + view)
    assert r.ok
    r_view = r.json()

    assert r_view['_id'] == view
    assert r_view['label'] == 'test-view'
    assert len(r_view['columns']) == 1

    # Attempt to list another user's views
    r = as_user.get('/containers/' + admin_id + '/views')
    assert r.ok
    views = r.json()
    assert len(views) == 0

    # List views
    r = as_user.get('/containers/' + user_id + '/views')
    assert r.ok
    views = r.json()

    assert len(views) == 1
    assert views[0] == r_view

    # Update view with no payload
    r = as_user.put('/views/' + view)
    assert r.status_code == 400

    # Update view with invalid payload
    r = as_user.put('/views/' + view, json={'_id': 'otherid'})
    assert r.status_code == 400

    # Update view
    r = as_user.put('/views/' + view, json={'public':True})
    assert r.ok

    # Attempt to get view as public after making it public
    r = as_public.get('/views/' + view)

    assert r.ok
    r_view = r.json()

    assert r_view['_id'] == view
    assert r_view['label'] == 'test-view'
    assert r_view['public'] == True
    assert len(r_view['columns']) == 1

    r = as_user.delete('/views/' + view)
    assert r.ok

def test_site_data_view(as_admin, as_user):
    view = {
        'label': 'test-site-view',
        'columns': [{'src': 'acquisition.label'}]
    }

    # Try to create a view as non admin
    r = as_user.post('/containers/site/views', json=view)
    assert r.status_code == 403

    # Create a site-owned view
    r = as_admin.post('/containers/site/views', json=view)
    assert r.ok
    view = r.json()['_id']

    # Attempt to get view as user
    r = as_user.get('/views/' + view)
    assert r.status_code == 403

    # Get view
    r = as_admin.get('/views/' + view)
    assert r.ok
    r_view = r.json()

    assert r_view['_id'] == view
    assert r_view['label'] == 'test-site-view'
    assert len(r_view['columns']) == 1

    # Attempt to list site views
    r = as_user.get('/containers/site/views')
    assert r.ok
    views = r.json()
    assert len(views) == 0

    # List views
    r = as_admin.get('/containers/site/views')
    assert r.ok
    views = r.json()

    assert len(views) == 1
    assert views[0] == r_view

    # Update view
    r = as_admin.put('/views/' + view, json={'public':True})
    assert r.ok

    # Attempt to get view as public after making it public
    r = as_user.get('/views/' + view)

    assert r.ok
    r_view = r.json()

    assert r_view['_id'] == view
    assert r_view['label'] == 'test-site-view'
    assert r_view['public'] == True
    assert len(r_view['columns']) == 1

    # Attempt to list site views
    r = as_user.get('/containers/site/views')
    assert r.ok
    views = r.json()
    assert len(views) == 1
    assert views[0] == r_view

    r = as_admin.delete('/views/' + view)
    assert r.ok

def test_group_data_view(as_admin, as_user, data_builder):
    user_id = as_user.get('/users/self').json()['_id']
    group = data_builder.create_group(_id='data_view_group')
    assert group == 'data_view_group'

    r = as_admin.post('/groups/data_view_group/permissions', json={'_id': user_id, 'access': 'rw'})
    assert r.ok

    view = {
        'label': 'test-group-view',
        'columns': [{'src': 'acquisition.label'}]
    }

    # Try to create a view as non admin
    r = as_user.post('/containers/data_view_group/views', json=view)
    assert r.status_code == 403

    # Create a group-owned view
    r = as_admin.post('/containers/data_view_group/views', json=view)
    assert r.ok
    view = r.json()['_id']

    # Attempt to get view as user
    r = as_user.get('/views/' + view)
    assert r.ok
    r_view = r.json()

    assert r_view['_id'] == view
    assert r_view['label'] == 'test-group-view'
    assert len(r_view['columns']) == 1

    # Get view
    r = as_admin.get('/views/' + view)
    assert r.ok
    assert r_view == r.json()

    # Attempt to list site views
    r = as_user.get('/containers/data_view_group/views')
    assert r.ok
    views = r.json()
    assert len(views) == 1
    assert views[0] == r_view

    # List views
    r = as_admin.get('/containers/data_view_group/views')
    assert r.ok
    views = r.json()
    assert len(views) == 1
    assert views[0] == r_view

    r = as_admin.delete('/views/' + view)
    assert r.ok

def test_project_data_view(as_admin, as_user, as_public, data_builder, file_form):
    project = data_builder.create_project(label='test-project', public=False)
    session1 = data_builder.create_session(project=project, subject=subject1, label='ses-01')
    acquisition1 = data_builder.create_acquisition(session=session1, label='scout')
    user_id = as_user.get('/users/self').json()['_id']

    file_form1 = file_form(('values.csv', csv_test_data('a1')))
    assert as_admin.post('/acquisitions/' + acquisition1 + '/files', files=file_form1).ok

    r = as_admin.post('/projects/' + project + '/permissions', json={'_id': user_id, 'access': 'ro'})
    assert r.ok

    view = {
        'label': 'test-project-view',
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'subject.label' },
            { 'src': 'subject.age' },
            { 'src': 'subject.sex' }
        ],
        'fileSpec': {
            'container': 'acquisition',
            'filter': { 'value': '*.csv' }
        }
    }

    # Try to create a view as read-only
    r = as_user.post('/containers/'+ project + '/views', json=view)
    assert r.status_code == 403

    # Create a project-owned view
    r = as_admin.post('/containers/' + project + '/views', json=view)
    assert r.ok
    view = r.json()['_id']

    # Attempt to get view as user
    r = as_user.get('/views/' + view)
    assert r.ok
    r_view = r.json()

    assert r_view['_id'] == view
    assert r_view['label'] == 'test-project-view'
    assert len(r_view['columns']) == 3

    # Get view
    r = as_admin.get('/views/' + view)
    assert r.ok
    assert r_view == r.json()

    # Attempt to list project views as public
    r = as_public.get('/containers/' + project + '/views')
    assert r.ok
    views = r.json()
    assert len(views) == 0

    # List project views
    r = as_user.get('/containers/' + project + '/views')
    assert r.ok
    views = r.json()
    assert len(views) == 1
    assert views[0] == r_view

    # Modify project to public
    r = as_admin.put('/projects/' + project, json={'public':True})
    assert r.ok

    # Get view
    r = as_public.get('/views/' + view)
    assert r.ok
    assert r_view == r.json()

    # Attempt to list project views as public
    r = as_public.get('/containers/' + project + '/views')
    assert r.ok
    views = r.json()
    assert len(views) == 1
    assert views[0] == r_view

    # Execute the view
    r = as_admin.get('/views/' + view + '/data?containerId={}'.format(project))

    assert r.ok
    rows = r.json()['data']

    assert len(rows) == 5

    for i in range(5):
        row = rows[i]

        assert row['subject.label'] == subject1['code']
        assert row['subject.age'] == subject1['age']
        assert row['subject.sex'] == subject1['sex']
        assert row['name'] == 'a1'
        assert row['value'] == str(i)
        assert row['value2'] == str(2*i)

    r = as_admin.delete('/views/' + view)
    assert r.ok

def test_data_view_filtering(data_builder, file_form, as_admin):
    project = data_builder.create_project(label='test-project')
    session1 = data_builder.create_session(project=project, subject=subject1, label='ses-01')
    session2 = data_builder.create_session(project=project, subject=subject2, label='ses-01')

    # Add tags for testing tag filtering
    r = as_admin.post('/sessions/{}/tags'.format(session1), json={'value': 'tag1'})
    assert(r.ok)
    r = as_admin.post('/sessions/{}/tags'.format(session1), json={'value': 'tag2'})
    assert(r.ok)

    # Validate that we can't sort
    r = as_admin.post('/views/data?containerId={}&sort=subject.label:asc'.format(project), json={
        'columns': [
            { 'src': 'session.label' },
        ]
    })
    assert r.status_code == 422

    # Validate that we can't filter on unselected containers
    r = as_admin.post('/views/data?containerId={}&filter=acquisition.label=foobar'.format(project), json={
        'columns': [
            { 'src': 'session.label' },
        ]
    })
    assert r.status_code == 400

    r = as_admin.post('/views/data?containerId={}&filter=subject.code=1001'.format(project), json={
        'includeIds': True,
        'includeLabels': True,
        'columns': [
            { 'src': 'session.label' },
        ]
    })

    assert r.ok
    rows = r.json()['data']
    assert len(rows) == 1

    r = as_admin.post('/views/data?containerId={}&filter=subject.cohort=Control'.format(project), json={
        'includeIds': True,
        'includeLabels': True,
        'columns': [
            { 'src': 'session.label' },
        ]
    })

    assert r.ok
    rows = r.json()['data']
    assert len(rows) == 1

    # Regex filter=subject.code~=\d+
    r = as_admin.post('/views/data?containerId={}&filter=subject.code=~%5Cd%2B'.format(project), json={
        'includeIds': True,
        'includeLabels': True,
        'columns': [
            { 'src': 'session.label' },
        ]
    })

    assert r.ok
    rows = r.json()['data']
    assert len(rows) == 2

    assert rows[0]['project.id'] == project
    assert rows[0]['project.label'] == 'test-project'
    assert rows[0]['subject.label'] == subject1['code']
    assert rows[0]['session.id'] == session1
    assert rows[0]['session.label'] == 'ses-01'

    r = as_admin.post('/views/data?containerId={}&filter=session.tags=tag1'.format(project), json={
        'includeIds': True,
        'includeLabels': True,
        'columns': [
            { 'src': 'session.label' },
        ]
    })

    assert r.ok
    rows = r.json()['data']
    assert len(rows) == 1

    assert rows[0]['project.id'] == project
    assert rows[0]['project.label'] == 'test-project'
    assert rows[0]['subject.label'] == subject1['code']
    assert rows[0]['session.id'] == session1
    assert rows[0]['session.label'] == 'ses-01'

    r = as_admin.post('/views/data?containerId={}&filter=session.tags!=tag1'.format(project), json={
        'includeIds': True,
        'includeLabels': True,
        'columns': [
            { 'src': 'session.label' },
        ]
    })

    assert r.ok
    rows = r.json()['data']
    assert len(rows) == 1

    assert rows[0]['project.id'] == project
    assert rows[0]['project.label'] == 'test-project'
    assert rows[0]['subject.label'] == subject2['code']
    assert rows[0]['session.id'] == session2
    assert rows[0]['session.label'] == 'ses-01'

def test_data_view_skip_and_limit(data_builder, file_form, as_admin):
    project = data_builder.create_project(label='test-project')
    session1 = data_builder.create_session(project=project, subject=subject1, label='ses-01')
    session2 = data_builder.create_session(project=project, subject=subject2, label='ses-01')
    acquisition1 = data_builder.create_acquisition(session=session1, label='scout')

    file_form1 = file_form(('values.csv', csv_test_data('a1')))
    assert as_admin.post('/acquisitions/' + acquisition1 + '/files', files=file_form1).ok

    # Test column aliases as well
    r = as_admin.post('/views/data?containerId={}&skip=2&limit=2'.format(project), json={
        'includeIds': False,
        'includeLabels': False,
        'columns': [
            { 'src': 'subject.label' },
            { 'src': 'subject.age' },
            { 'src': 'subject.sex' }
        ],
        'fileSpec': {
            'container': 'acquisition',
            'filter': { 'value': '*.csv' },
            'columns': [
                { 'src': 'name' },
                { 'src': 'value', 'type': 'int' },
                { 'src': 'value2', 'type': 'float' }
            ]
        }
    })

    assert r.ok
    rows = r.json()['data']

    assert len(rows) == 2

    name_value = 'a1'
    subject = subjects[0]
    for i in range(2):
        j = i+2
        row = rows[i]

        assert row['subject.label'] == subject['code']
        assert row['subject.age'] == subject['age']
        assert row['subject.sex'] == subject['sex']
        assert row['name'] == name_value
        assert row['value'] == j
        assert isinstance(row['value2'], float)
        assert row['value2'] == 2*j

def test_save_data_view_to_container(data_builder, file_form, as_admin, as_user, as_public):
    project = data_builder.create_project(label='test-project')
    session = data_builder.create_session(project=project, subject=subject1, label='ses-01')
    acquisition = data_builder.create_acquisition(session=session, label='scout')

    view = {
        'includeIds': True,
        'includeLabels': False,
        'columns': [
            { 'src': 'project.label' },
            { 'src': 'subject.label' },
            { 'src': 'subject.age' },
            { 'src': 'subject.sex' },
            { 'src': 'session.label' },
            { 'src': 'acquisition.label' }
        ]
    }

    # No public access
    r = as_public.post('/views/save?containerId={}'.format(project), json={
        'view': view,
        'containerType': 'project',
        'containerId': project,
        'filename': 'data_view.json'
    })
    assert r.status_code == 403

    # No user access (Can't save to container)
    user_id = as_user.get('/users/self').json()['_id']
    r = as_admin.post('/projects/' + project + '/permissions', json={'_id': user_id, 'access': 'ro'})
    assert r.ok

    r = as_user.post('/views/save?containerId={}'.format(project), json={
        'view': view,
        'containerType': 'project',
        'containerId': project,
        'filename': 'data_view.json'
    })
    assert r.status_code == 403

    # Execute adhoc view and save it to project
    r = as_admin.post('/views/save?containerId={}'.format(project), json={
        'view': view,
        'containerType': 'project',
        'containerId': project,
        'filename': 'data_view.json'
    })

    assert r.ok

    # Verify the contents of the file saved to the project
    r = as_admin.get('/projects/{}/files/data_view.json'.format(project))
    assert r.ok

    rows = r.json()['data']
    assert len(rows) == 1

    assert rows[0]['project.id'] == project
    assert rows[0]['project.label'] == 'test-project'
    assert rows[0]['subject.label'] == subject1['code']
    assert rows[0]['subject.age'] == subject1['age']
    assert rows[0]['subject.sex'] == subject1['sex']
    assert rows[0]['session.id'] == session
    assert rows[0]['session.label'] == 'ses-01'
    assert rows[0]['acquisition.id'] == acquisition
    assert rows[0]['acquisition.label'] == 'scout'

    # Create a project-owned view, execute and save to session
    view['label'] = 'test-data-view'
    r = as_admin.post('/containers/' + project + '/views', json=view)
    assert r.ok
    view_id = r.json()['_id']

    r = as_admin.post('/views/save?containerId={}'.format(project), json={
        'viewId': view_id,
        'containerType': 'session',
        'containerId': session,
        'filename': 'saved_data_view.json'
    })
    assert r.ok

    # Verify the contents of the file saved to the project
    r = as_admin.get('/sessions/{}/files/saved_data_view.json'.format(session))
    assert r.ok

    rows = r.json()['data']
    assert len(rows) == 1

    assert rows[0]['project.id'] == project
    assert rows[0]['project.label'] == 'test-project'
    assert rows[0]['subject.label'] == subject1['code']
    assert rows[0]['subject.age'] == subject1['age']
    assert rows[0]['subject.sex'] == subject1['sex']
    assert rows[0]['session.id'] == session
    assert rows[0]['session.label'] == 'ses-01'
    assert rows[0]['acquisition.id'] == acquisition
    assert rows[0]['acquisition.label'] == 'scout'

