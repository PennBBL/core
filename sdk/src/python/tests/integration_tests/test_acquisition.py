import unittest
from sdk_test_case import SdkTestCase
from test_session import create_test_session

import flywheel

class AcquisitionsTestCases(SdkTestCase):
    def setUp(self):
        self.group_id, self.project_id, self.session_id = create_test_session()

    def tearDown(self):
        self.fw.delete_project(self.project_id)
        self.fw.delete_group(self.group_id)

    def test_acquisitions(self):
        fw = self.fw
        
        acquisition_name = self.rand_string()
        acquisition = flywheel.Acquisition(label=acquisition_name, session=self.session_id) 

        # Add
        acquisition_id = fw.add_acquisition(acquisition)
        self.assertNotEmpty(acquisition_id)

        # Get
        r_acquisition = fw.get_acquisition(acquisition_id)
        self.assertEqual(r_acquisition.id, acquisition_id)
        self.assertEqual(r_acquisition.label, acquisition_name)
        self.assertTimestampBeforeNow(r_acquisition.created)
        self.assertGreaterEqual(r_acquisition.modified, r_acquisition.created)

        # Get All
        acquisitions = fw.get_all_acquisitions()
        self.sanitize_for_collection(r_acquisition, info_exists=False)
        self.assertIn(r_acquisition, acquisitions)

        # Modify
        new_name = self.rand_string()
        acquisition_mod = flywheel.Project(label=new_name, info={'another-key': 52})
        fw.modify_acquisition(acquisition_id, acquisition_mod)

        changed_acquisition = fw.get_acquisition(acquisition_id)
        self.assertEqual(changed_acquisition.label, new_name)
        self.assertEqual(changed_acquisition.created, r_acquisition.created)
        self.assertGreater(changed_acquisition.modified, r_acquisition.modified)

        # Notes, Tags
        message = 'This is a note'
        fw.add_acquisition_note(acquisition_id, message)
        
        tag = 'example-tag'
        fw.add_acquisition_tag(acquisition_id, tag)

        # Replace Info
        fw.replace_acquisition_info(acquisition_id, { 'foo': 3, 'bar': 'qaz' })

        # Set Info
        fw.set_acquisition_info(acquisition_id, { 'foo': 42, 'hello': 'world' })

        # Check
        r_acquisition = fw.get_acquisition(acquisition_id)

        self.assertEqual(len(r_acquisition.notes), 1)
        self.assertEqual(r_acquisition.notes[0].text, message)
        
        self.assertEqual(len(r_acquisition.tags), 1)
        self.assertEqual(r_acquisition.tags[0], tag)

        self.assertEqual(r_acquisition.info['foo'], 42)
        self.assertEqual(r_acquisition.info['bar'], 'qaz')
        self.assertEqual(r_acquisition.info['hello'], 'world')

        # Delete info fields
        fw.delete_acquisition_info_fields(acquisition_id, ['foo', 'bar'])

        r_acquisition = fw.get_acquisition(acquisition_id)
        self.assertNotIn('foo', r_acquisition.info)
        self.assertNotIn('bar', r_acquisition.info)
        self.assertEqual(r_acquisition.info['hello'], 'world')

        # Delete
        fw.delete_acquisition(acquisition_id)

        acquisitions = fw.get_all_acquisitions()
        self.sanitize_for_collection(r_acquisition)
        self.assertNotIn(r_acquisition, acquisitions)

    def test_acquisition_files(self):
        fw = self.fw
        
        acquisition = flywheel.Acquisition(label=self.rand_string(), session=self.session_id)
        acquisition_id = fw.add_acquisition(acquisition)

        # Upload a file
        poem = 'Turning and turning in the widening gyre'
        fw.upload_file_to_acquisition(acquisition_id, flywheel.FileSpec('yeats.txt', poem))

        # Check that the file was added to the acquisition
        r_acquisition = fw.get_acquisition(acquisition_id)
        self.assertEqual(len(r_acquisition.files), 1)
        self.assertEqual(r_acquisition.files[0].name, 'yeats.txt')
        self.assertEqual(r_acquisition.files[0].size, 40)
        self.assertEqual(r_acquisition.files[0].mimetype, 'text/plain')

        # Download the file and check content
        self.assertDownloadFileTextEquals(fw.download_file_from_acquisition_as_data, acquisition_id, 'yeats.txt', poem)
        
        # Test unauthorized download with ticket for the file
        self.assertDownloadFileTextEqualsWithTicket(fw.get_acquisition_download_url, acquisition_id, 'yeats.txt', poem)

        # Test file attributes
        self.assertEqual(r_acquisition.files[0].modality, None)
        self.assertEmpty(r_acquisition.files[0].classification)
        self.assertEqual(r_acquisition.files[0].type, 'text')

        resp = fw.modify_acquisition_file(acquisition_id, 'yeats.txt', flywheel.FileEntry(
            modality='modality',
            type='type'
        ))

        # Check that no jobs were triggered, and attrs were modified
        self.assertEqual(resp.jobs_spawned, 0)

        r_acquisition = fw.get_acquisition(acquisition_id)
        self.assertEqual(r_acquisition.files[0].modality, "modality")
        self.assertEmpty(r_acquisition.files[0].classification)
        self.assertEqual(r_acquisition.files[0].type, 'type')

        # Test classifications
        resp = fw.modify_acquisition_file_classification(acquisition_id, 'yeats.txt', {
            'modality': 'modality2',
            'replace': {
                'Custom': ['measurement1', 'measurement2'],
            }
        })
        self.assertEqual(resp.modified, 1)
        self.assertEqual(resp.jobs_spawned, 0)

        r_acquisition = fw.get_acquisition(acquisition_id)
        self.assertEqual(r_acquisition.files[0].modality, 'modality2')
        self.assertEqual(r_acquisition.files[0].classification, {
            'Custom': ['measurement1', 'measurement2']
        });

        resp = fw.set_acquisition_file_classification(acquisition_id, 'yeats.txt', {
            'Custom': ['HelloWorld']
        })
        self.assertEqual(resp.modified, 1)
        self.assertEqual(resp.jobs_spawned, 0)

        resp = fw.delete_acquisition_file_classification_fields(acquisition_id, 'yeats.txt', {
            'Custom': ['measurement2']
        })
        self.assertEqual(resp.modified, 1)
        self.assertEqual(resp.jobs_spawned, 0)

        r_acquisition = fw.get_acquisition(acquisition_id)
        self.assertEqual(r_acquisition.files[0].classification, {
            'Custom': ['measurement1', 'HelloWorld'],
        });

        # Test file info
        self.assertEmpty(r_acquisition.files[0].info)
        fw.replace_acquisition_file_info(acquisition_id, 'yeats.txt', {
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4
        })

        fw.set_acquisition_file_info(acquisition_id, 'yeats.txt', {
            'c': 5
        })

        r_acquisition = fw.get_acquisition(acquisition_id)
        self.assertEqual(r_acquisition.files[0].info['a'], 1)
        self.assertEqual(r_acquisition.files[0].info['b'], 2)
        self.assertEqual(r_acquisition.files[0].info['c'], 5)
        self.assertEqual(r_acquisition.files[0].info['d'], 4)
    
        fw.delete_acquisition_file_info_fields(acquisition_id, 'yeats.txt', ['c', 'd'])  
        r_acquisition = fw.get_acquisition(acquisition_id)
        self.assertEqual(r_acquisition.files[0].info['a'], 1)
        self.assertEqual(r_acquisition.files[0].info['b'], 2)
        self.assertNotIn('c', r_acquisition.files[0].info)
        self.assertNotIn('d', r_acquisition.files[0].info)

        fw.replace_acquisition_file_info(acquisition_id, 'yeats.txt', {})
        r_acquisition = fw.get_acquisition(acquisition_id)
        self.assertEmpty(r_acquisition.files[0].info)

        # Delete file
        fw.delete_acquisition_file(acquisition_id, 'yeats.txt')
        r_acquisition = fw.get_acquisition(acquisition_id)
        self.assertEmpty(r_acquisition.files)

        # Delete acquisition
        fw.delete_acquisition(acquisition_id)

    def test_acquisition_errors(self):
        fw = self.fw

        # Try to create acquisition without session id
        try:
            acquisition = flywheel.Acquisition(label=self.rand_string())
            acquisition_id = fw.add_acquisition(acquisition)
            self.fail('Expected ApiException creating invalid acquisition!')
        except flywheel.ApiException as e:
            self.assertEqual(e.status, 400)

        # Try to get an acquisition that doesn't exist
        try:
            fw.get_acquisition('DOES_NOT_EXIST')
            self.fail('Expected ApiException retrieving invalid acquisition!')
        except flywheel.ApiException as e:
            self.assertEqual(e.status, 404)

    def test_acquisition_analysis(self):
        fw = self.fw
        
        acquisition = flywheel.Acquisition(session=self.session_id, label=self.rand_string()) 

        # Add
        acquisition_id = fw.add_acquisition(acquisition)
        self.assertNotEmpty(acquisition_id)

        poem = 'Troubles my sight: a waste of desert sand;'
        fw.upload_file_to_acquisition(acquisition_id, flywheel.FileSpec('yeats.txt', poem))

        file_ref = flywheel.FileReference(
            id=acquisition_id,
            type='acquisition',
            name='yeats.txt'
        )

        analysis = flywheel.AnalysisInput(label=self.rand_string(), description=self.rand_string(), inputs=[file_ref])

        # Add
        analysis_id = fw.add_acquisition_analysis(acquisition_id, analysis)
        self.assertNotEmpty(analysis_id)

        # Get the list of analyses in the acquisition
        analyses = fw.get_acquisition_analyses(acquisition_id)
        self.assertEqual(len(analyses), 1)
        
        r_analysis = analyses[0]

        self.assertEqual(r_analysis.id, analysis_id)
        self.assertEmpty(r_analysis.job)

        self.assertTimestampBeforeNow(r_analysis.created)
        self.assertGreaterEqual(r_analysis.modified, r_analysis.created)

        self.assertEqual(len(r_analysis.inputs), 1)
        self.assertEqual(r_analysis.inputs[0].name, 'yeats.txt')

    def sanitize_for_collection(self, acquisition, info_exists=True):
        # workaround: all-container endpoints skip some fields, single-container does not. this sets up the equality check 
        acquisition.info = {}
        acquisition.info_exists = info_exists
        acquisition.analyses = None

def create_test_acquisition():
    group_id, project_id, session_id = create_test_session()
    return group_id, project_id, session_id, SdkTestCase.fw.add_acquisition({
        'session': session_id, 
        'label': SdkTestCase.rand_string()
    })


