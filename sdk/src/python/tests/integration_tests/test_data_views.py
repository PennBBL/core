import unittest
import json
import csv
import codecs

from sdk_test_case import SdkTestCase
from test_acquisition import create_test_acquisition

import flywheel 
class DataViewTestCases(SdkTestCase):
    @classmethod
    def setUpClass(cls):
        cls.view_id = None
        cls.group_id, cls.project_id, cls.session_id, cls.acquisition_id = create_test_acquisition()
        
        # Get user id
        user = cls.fw.get_current_user()
        cls.user_id = user.id

        cls.session = cls.fw.get_session(cls.session_id)
        cls.subject = cls.session.subject

    @classmethod
    def tearDownClass(cls):
        cls.fw.delete_project(cls.project_id)
        cls.fw.delete_group(cls.group_id)

        if cls.view_id:
            cls.fw.delete_view(cls.view_id)

    def setUp(self):
        self.test_acquisition_id = None

    def tearDown(self):
        if self.test_acquisition_id:
            self.fw.delete_acquisition(self.test_acquisition_id)

    @classmethod
    def ensure_data_view(cls):
        if cls.view_id:
            return

        builder = flywheel.ViewBuilder('test-data-view', include_labels=False)
        builder.column('subject.age')
        builder.column('session.label', dst='session_label')
        builder.column('subject.firstname', dst='firstname')
        builder.column('subject.lastname', dst='lastname')
        builder.public()

        cls.view_id = cls.fw.add_view(cls.user_id, builder.build())

    def test_build_data_view(self):
        fw = self.fw

        # Create the data view
        self.ensure_data_view()

        # Check that we can get the data view back
        self.assertIsNotNone(self.view_id)

        r_view = fw.get_view(self.view_id)
        self.assertIsNotNone(r_view)

        self.assertEqual(r_view.label, 'test-data-view')
        self.assertEqual(len(r_view.columns), 4)

        views = fw.get_views(self.user_id)
        self.assertGreaterEqual(len(views), 1)
        self.assertIn(r_view, views)

    def test_execute_data_view(self):
        fw = self.fw

        self.ensure_data_view()

        with fw.read_view_data(self.view_id, self.project_id) as resp:
            result = json.load(resp)

        self.assertIsNotNone(result)
        self.assertIn('data', result)
        data = result['data']
        self.assertEqual(len(data), 1)

        row = data[0]
        self.assertEqual(row['project.id'], self.project_id)
        self.assertEqual(row['subject.id'], self.subject.id)
        self.assertEqual(row['session.id'], self.session_id)
        self.assertEqual(row['session_label'], self.session.label)
        self.assertEqual(row['subject.age'], self.subject.age)
        self.assertEqual(row['firstname'], self.subject.firstname)
        self.assertEqual(row['lastname'], self.subject.lastname)

    def test_execute_data_view_dataframe(self):
        try: 
            import pandas
        except ImportError:
            print('No pandas, skipping dataframe test!')
            return


        fw = self.fw

        self.ensure_data_view()

        df = fw.read_view_dataframe(self.view_id, self.project_id)
        self.assertIsNotNone(df)
        self.assertEqual(df['project.id'][0], self.project_id)
        self.assertEqual(df['subject.id'][0], self.subject.id)
        self.assertEqual(df['session.id'][0], self.session_id)
        self.assertEqual(df['subject.age'][0], self.subject.age)

        # Example of creating a data-frame with nested session info
        fw.replace_session_info(self.session_id, {
            'current_age': 32,
            'foo': 'bar',
            'tags': ['tag1', 'tag2'],
            'dims': [8.0, 5.9, 6.4]
        })

        view = fw.View(columns=['subject', 'session.info'], include_labels=False)
        df = fw.read_view_dataframe(view, self.project_id)

        info = df['session.info'][0]
        self.assertEqual(info['dims'], [8.0, 5.9, 6.4])

    def test_execute_adhoc_data_view_csv(self):
        fw = self.fw

        view = fw.View(columns=['subject.age', 'subject.sex', 'session'], include_labels=False)
        with fw.read_view_data(view, self.project_id, format='csv') as resp:
            reader = csv.reader(resp)

            row = next(reader)
            self.assertEqual(len(row), 11)
            self.assertEqual(row, ['subject.age', 'subject.sex', 'session.id', 'session.label', 'session.operator', 
                'session.timestamp', 'session.timezone', 'session.age', 'session.weight', 'project.id', 'subject.id'])

            row = next(reader)
            self.assertEqual(len(row), 11)
            self.assertEqual(row, [str(self.subject.age), self.subject.sex, self.session_id, self.session.label, 
                '', '', '', '57', '', self.project_id, self.subject.id])

    def test_data_view_files(self):
        fw = self.fw

        self.test_acquisition_id = fw.add_acquisition({'session': self.session_id, 'label': 'Acquisition2'})

        data = 'col1,col2\n1,10\n2,20'
        fw.upload_file_to_acquisition(self.test_acquisition_id, flywheel.FileSpec('data1.csv', data))
        fw.upload_file_to_acquisition(self.test_acquisition_id, flywheel.FileSpec('data2.csv', data))

        # Get file data
        view = fw.View(container='acquisition', filename='*.csv', match='all', 
            columns=['file.name', ('file_data.col2', 'value2', 'int')])

        with fw.read_view_data(view, self.project_id) as resp:
            result = json.load(resp)

        self.assertIsNotNone(result)
        self.assertIn('data', result)
        rows = result['data']
        self.assertEqual(len(rows), 5)

        self.assertEqual(rows[0]['acquisition.label'], 'Acquisition2')
        self.assertEqual(rows[0]['file.name'], 'data1.csv')
        self.assertEqual(rows[0]['col1'], '1')
        self.assertEqual(rows[0]['value2'], 10)

        self.assertEqual(rows[1]['acquisition.label'], 'Acquisition2')
        self.assertEqual(rows[1]['file.name'], 'data1.csv')
        self.assertEqual(rows[1]['col1'], '2')
        self.assertEqual(rows[1]['value2'], 20)

        self.assertEqual(rows[2]['acquisition.label'], 'Acquisition2')
        self.assertEqual(rows[2]['file.name'], 'data2.csv')
        self.assertEqual(rows[2]['col1'], '1')
        self.assertEqual(rows[2]['value2'], 10)

        self.assertEqual(rows[3]['acquisition.label'], 'Acquisition2')
        self.assertEqual(rows[3]['file.name'], 'data2.csv')
        self.assertEqual(rows[3]['col1'], '2')
        self.assertEqual(rows[3]['value2'], 20)

        self.assertEqual(rows[4]['acquisition.id'], self.acquisition_id)
        self.assertEqual(rows[4]['file.name'], None)
        self.assertEqual(rows[4]['col1'], None)
        self.assertEqual(rows[4]['value2'], None)

        # Test list files
        view = fw.View(columns=['acquisition.file'])
        with fw.read_view_data(view, self.project_id) as resp:
            result = json.load(resp)

        self.assertIsNotNone(result)
        self.assertIn('data', result)
        data = result['data']
        self.assertEqual(len(data), 2)

        row = data[0]
        self.assertEqual(row['project.id'], self.project_id)
        self.assertEqual(row['subject.id'], self.subject.id)
        self.assertEqual(row['session.id'], self.session_id)
        self.assertEqual(row['acquisition.id'], self.test_acquisition_id)
        self.assertEqual(row['acquisition.file.name'], 'data1.csv')
        self.assertEqual(row['acquisition.file.size'], 19)
        self.assertEqual(row['acquisition.file.type'], 'tabular data')
        self.assertIn('acquisition.file.id', row)
        self.assertIn('acquisition.file.classification', row)
        
        row = data[1]
        self.assertEqual(row['project.id'], self.project_id)
        self.assertEqual(row['subject.id'], self.subject.id)
        self.assertEqual(row['session.id'], self.session_id)
        self.assertEqual(row['acquisition.id'], self.test_acquisition_id)
        self.assertEqual(row['acquisition.file.name'], 'data2.csv')
        self.assertEqual(row['acquisition.file.size'], 19)
        self.assertEqual(row['acquisition.file.type'], 'tabular data')

        # List files, only 2 columns
        view = fw.View(columns=['acquisition.file.name', 'acquisition.file.size'])
        
        with fw.read_view_data(view, self.project_id) as resp:
            result = json.load(resp)

        self.assertIsNotNone(result)
        self.assertIn('data', result)
        data = result['data']
        self.assertEqual(len(data), 2)

        row = data[0]
        self.assertEqual(row['project.id'], self.project_id)
        self.assertEqual(row['subject.id'], self.subject.id)
        self.assertEqual(row['session.id'], self.session_id)
        self.assertEqual(row['acquisition.id'], self.test_acquisition_id)
        self.assertEqual(row['acquisition.file.name'], 'data1.csv')
        self.assertEqual(row['acquisition.file.size'], 19)
        self.assertNotIn('acquisition.file.type', row)
        self.assertNotIn('acquisition.file.id', row)
        self.assertNotIn('acquisition.file.classification', row)
        
        row = data[1]
        self.assertEqual(row['project.id'], self.project_id)
        self.assertEqual(row['subject.id'], self.subject.id)
        self.assertEqual(row['session.id'], self.session_id)
        self.assertEqual(row['acquisition.id'], self.test_acquisition_id)
        self.assertEqual(row['acquisition.file.name'], 'data2.csv')
        self.assertEqual(row['acquisition.file.size'], 19)

    def test_data_view_file_column_validation(self):
        fw = self.fw

        try:
            fw.View(columns=['session.file', 'acquisition.file.name'])
            self.fail('Expected ValueError!')
        except:
            pass

        try:
            fw.View(columns=['session.analysis.file', 'session.file'])
            self.fail('Expected ValueError!')
        except:
            pass

        try:
            fw.View(columns=['session.file', 'session.analysis.file'])
            self.fail('Expected ValueError!')
        except:
            pass

