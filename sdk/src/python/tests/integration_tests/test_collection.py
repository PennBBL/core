import unittest
from sdk_test_case import SdkTestCase
from test_acquisition import create_test_acquisition

import flywheel

class CollectionsTestCases(SdkTestCase):
    def setUp(self):
        self.project_ids = []
        self.group_ids = []
        self.collection_id = None

    def tearDown(self):
        for project_id in self.project_ids:
            self.fw.delete_project(project_id)

        for group_id in self.group_ids:
            self.fw.delete_group(group_id)

        if self.collection_id:
            self.fw.delete_collection(self.collection_id)

    def test_collections(self):
        fw = self.fw
        
        collection_name = self.rand_string()
        collection = flywheel.Collection(label=collection_name, description=self.rand_string()) 

        # Add
        self.collection_id = collection_id = fw.add_collection(collection)
        self.assertNotEmpty(collection_id)

        # Get
        saved_collection = fw.get_collection(collection_id)
        self.assertEqual(saved_collection.id, collection_id)
        self.assertEqual(saved_collection.label, collection_name)
        self.assertEqual(saved_collection.description, collection.description)
        self.assertTimestampBeforeNow(saved_collection.created)
        self.assertGreaterEqual(saved_collection.modified, saved_collection.created)

        # Add acquisition to the collection
        group_id, project_id, session_id, acquisition_id = create_test_acquisition()
        self.group_ids.append(group_id)
        self.project_ids.append(project_id)
        fw.add_acquisitions_to_collection(collection_id, [acquisition_id])

        # Get sessions
        saved_sessions = fw.get_collection_sessions(collection_id)
        self.assertEqual(len(saved_sessions), 1)
        self.assertEqual(saved_sessions[0].id, session_id)

        # Get acquisitions
        saved_acquisitions = fw.get_collection_acquisitions(collection_id)
        self.assertEqual(len(saved_acquisitions), 1)
        self.assertEqual(saved_acquisitions[0].id, acquisition_id)

        # Get session acquisitions
        saved_session_acquisitions = fw.get_collection_acquisitions(collection_id, session=session_id)
        self.assertEqual(len(saved_session_acquisitions), 1)
        self.assertEqual(saved_session_acquisitions[0].id, acquisition_id)

        # Add session to the collection
        group_id, project_id, session_id2, acquisition_id2 = create_test_acquisition()
        self.group_ids.append(group_id)
        self.project_ids.append(project_id)
        fw.add_sessions_to_collection(collection_id, [session_id2])
        saved_collection = fw.get_collection(collection_id)
        
        # Get sessions
        saved_sessions = fw.get_collection_sessions(collection_id)
        self.assertEqual(len(saved_sessions), 2)
        self.assertEqual(len(list(filter(lambda x: x.id == session_id, saved_sessions))), 1)
        self.assertEqual(len(list(filter(lambda x: x.id == session_id2, saved_sessions))), 1)

        # Get acquisitions
        saved_acquisitions = fw.get_collection_acquisitions(collection_id)
        self.assertEqual(len(saved_acquisitions), 2)
        self.assertEqual(len(list(filter(lambda x: x.id == acquisition_id, saved_acquisitions))), 1)
        self.assertEqual(len(list(filter(lambda x: x.id == acquisition_id2, saved_acquisitions))), 1)

        # Get session acquisitions
        saved_session_acquisitions = fw.get_collection_acquisitions(collection_id, session=session_id)
        self.assertEqual(len(saved_session_acquisitions), 1)
        self.assertEqual(saved_session_acquisitions[0].id, acquisition_id)

        # Get All
        collections = fw.get_all_collections()
        self.sanitize_for_collection(saved_collection, info_exists=False)
        self.assertIn(saved_collection, collections)

        # Modify
        new_name = self.rand_string()
        collection_mod = flywheel.Collection(label=new_name)
        fw.modify_collection(collection_id, collection_mod)

        changed_collection = fw.get_collection(collection_id)
        self.assertEqual(changed_collection.label, new_name)
        self.assertEqual(changed_collection.created, saved_collection.created)
        self.assertGreater(changed_collection.modified, saved_collection.modified)

        # Add note 
        message = 'This is a note'
        fw.add_collection_note(collection_id, message)
        
        tag = 'example-tag'
        fw.add_collection_tag(collection_id, tag)

        # Replace Info
        fw.replace_collection_info(collection_id, { 'foo': 3, 'bar': 'qaz' })

        # Set Info
        fw.set_collection_info(collection_id, { 'foo': 42, 'hello': 'world' })

        # Check
        changed_collection = fw.get_collection(collection_id)

        self.assertEqual(len(changed_collection.notes), 1)
        self.assertEqual(changed_collection.notes[0].text, message)
        
        self.assertEqual(len(changed_collection.tags), 1)
        self.assertEqual(changed_collection.tags[0], tag)

        self.assertEqual(changed_collection.info['foo'], 42)
        self.assertEqual(changed_collection.info['bar'], 'qaz')
        self.assertEqual(changed_collection.info['hello'], 'world')

        # Delete info fields
        fw.delete_collection_info_fields(collection_id, ['foo', 'bar'])

        changed_collection = fw.get_collection(collection_id)
        self.assertNotIn('foo', changed_collection.info)
        self.assertNotIn('bar', changed_collection.info)
        self.assertEqual(changed_collection.info['hello'], 'world')

        # Delete
        fw.delete_collection(collection_id)
        self.collection_id = None

        collections = fw.get_all_collections()
        self.sanitize_for_collection(changed_collection)
        self.assertNotIn(changed_collection, collections)

    def test_collection_files(self):
        fw = self.fw
        
        collection = flywheel.Collection(label=self.rand_string())
        self.collection_id = collection_id = fw.add_collection(collection)

        # Upload a file
        poem = 'Things fall apart; the centre cannot hold;'
        fw.upload_file_to_collection(collection_id, flywheel.FileSpec('yeats.txt', poem))

        # Check that the file was added to the collection
        r_collection = fw.get_collection(collection_id)
        self.assertEqual(len(r_collection.files), 1)
        self.assertEqual(r_collection.files[0].name, 'yeats.txt')
        self.assertEqual(r_collection.files[0].size, 42)
        self.assertEqual(r_collection.files[0].mimetype, 'text/plain')

        # Download the file and check content
        self.assertDownloadFileTextEquals(fw.download_file_from_collection_as_data, collection_id, 'yeats.txt', poem)
        
        # Test unauthorized download with ticket for the file
        self.assertDownloadFileTextEqualsWithTicket(fw.get_collection_download_url, collection_id, 'yeats.txt', poem)

        # Test file attributes
        self.assertEqual(r_collection.files[0].modality, None)
        self.assertEmpty(r_collection.files[0].classification)
        self.assertEqual(r_collection.files[0].type, 'text')

        resp = fw.modify_collection_file(collection_id, 'yeats.txt', flywheel.FileEntry(
            modality='modality',
            type='type'
        ))

        # Check that no jobs were triggered, and attrs were modified
        self.assertEqual(resp.jobs_spawned, 0)

        r_collection = fw.get_collection(collection_id)
        self.assertEqual(r_collection.files[0].modality, "modality")
        self.assertEmpty(r_collection.files[0].classification)
        self.assertEqual(r_collection.files[0].type, 'type')

        # Test classifications
        resp = fw.modify_collection_file_classification(collection_id, 'yeats.txt', {
            'replace': {
                'Custom': ['measurement1', 'measurement2'],
            }
        })
        self.assertEqual(resp.modified, 1)
        self.assertEqual(resp.jobs_spawned, 0)

        r_collection = fw.get_collection(collection_id)
        self.assertEqual(r_collection.files[0].classification, {
            'Custom': ['measurement1', 'measurement2']
        });

        resp = fw.modify_collection_file_classification(collection_id, 'yeats.txt', {
            'add': {
                'Custom': ['HelloWorld'],
            },
            'delete': {
                'Custom': ['measurement2']
            }
        })
        self.assertEqual(resp.modified, 1)
        self.assertEqual(resp.jobs_spawned, 0)

        r_collection = fw.get_collection(collection_id)
        self.assertEqual(r_collection.files[0].classification, {
            'Custom': ['measurement1', 'HelloWorld'],
        });

        # Test file info
        self.assertEmpty(r_collection.files[0].info)
        fw.replace_collection_file_info(collection_id, 'yeats.txt', {
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4
        })

        fw.set_collection_file_info(collection_id, 'yeats.txt', {
            'c': 5
        })

        r_collection = fw.get_collection(collection_id)
        self.assertEqual(r_collection.files[0].info['a'], 1)
        self.assertEqual(r_collection.files[0].info['b'], 2)
        self.assertEqual(r_collection.files[0].info['c'], 5)
        self.assertEqual(r_collection.files[0].info['d'], 4)
    
        fw.delete_collection_file_info_fields(collection_id, 'yeats.txt', ['c', 'd'])  
        r_collection = fw.get_collection(collection_id)
        self.assertEqual(r_collection.files[0].info['a'], 1)
        self.assertEqual(r_collection.files[0].info['b'], 2)
        self.assertNotIn('c', r_collection.files[0].info)
        self.assertNotIn('d', r_collection.files[0].info)

        fw.replace_collection_file_info(collection_id, 'yeats.txt', {})
        r_collection = fw.get_collection(collection_id)
        self.assertEmpty(r_collection.files[0].info)

        # Delete file
        fw.delete_collection_file(collection_id, 'yeats.txt')
        r_collection = fw.get_collection(collection_id)
        self.assertEmpty(r_collection.files)

    def test_collection_analysis(self):
        fw = self.fw
        
        collection = flywheel.Collection(label=self.rand_string()) 

        # Add
        self.collection_id = collection_id = fw.add_collection(collection)
        self.assertNotEmpty(collection_id)

        poem = 'A shape with lion body and the head of a man,'
        fw.upload_file_to_collection(collection_id, flywheel.FileSpec('yeats.txt', poem))

        file_ref = flywheel.FileReference(
            id=collection_id,
            type='collection',
            name='yeats.txt'
        )

        analysis = flywheel.AnalysisInput(label=self.rand_string(), description=self.rand_string(), inputs=[file_ref])

        # Add
        analysis_id = fw.add_collection_analysis(collection_id, analysis)
        self.assertNotEmpty(analysis_id)

        # Get the list of analyses in the collection
        r_collection = fw.get_collection(collection_id)
        self.assertEqual(len(r_collection.analyses), 1)
        
        r_analysis = r_collection.analyses[0]

        self.assertEqual(r_analysis.id, analysis_id)
        self.assertEmpty(r_analysis.job)

        self.assertTimestampBeforeNow(r_analysis.created)
        self.assertGreaterEqual(r_analysis.modified, r_analysis.created)

        self.assertEqual(len(r_analysis.inputs), 1)
        self.assertEqual(r_analysis.inputs[0].name, 'yeats.txt')

    def sanitize_for_collection(self, collection, info_exists=True):
        # workaround: all-container endpoints skip some fields, single-container does not. this sets up the equality check 
        collection.files = []
        collection.info_exists = info_exists
        collection.analyses = None


