import unittest
from sdk_test_case import SdkTestCase
from test_project import create_test_project

import flywheel

class SessionsTestCases(SdkTestCase):
    def setUp(self):
        self.group_id, self.project_id = create_test_project()

    def tearDown(self):
        self.fw.delete_project(self.project_id)
        self.fw.delete_group(self.group_id)

    def test_sessions(self):
        fw = self.fw
        
        session_name = self.rand_string()
        session = flywheel.Session(
            label=session_name, 
            project=self.project_id, 
            info = { 'some-key': 37 },
            subject = flywheel.Subject(
                code = self.rand_string_lower(),
                firstname = self.rand_string(),
                lastname = self.rand_string(),
                sex = 'other',
                age = 56,
                info = { 'some-subject-key': 37 }
            )
        )

        # Add
        session_id = fw.add_session(session)
        self.assertNotEmpty(session_id)

        # Get
        r_session = fw.get_session(session_id)
        self.assertEqual(r_session.id, session_id)
        self.assertEqual(r_session.label, session_name)
        self.assertIn('some-key', r_session.info)
        self.assertEqual(r_session.info['some-key'], 37)
        self.assertTimestampBeforeNow(r_session.created)
        self.assertGreaterEqual(r_session.modified, r_session.created)
        self.assertIsNotNone(r_session.subject)
        self.assertEqual(r_session.subject.firstname, session.subject.firstname)

        # Get All
        sessions = fw.get_all_sessions()
        self.assertNotEmpty(sessions)

        self.sanitize_for_collection(r_session)
        self.assertIn(r_session, sessions)

        # Get from parent
        sessions = fw.get_project_sessions(self.project_id)
        self.assertIn(r_session, sessions)

        # Modify
        new_name = self.rand_string()
        session_mod = flywheel.Session(label=new_name)
        fw.modify_session(session_id, session_mod)

        changed_session = fw.get_session(session_id)
        self.assertEqual(changed_session.label, new_name)
        self.assertEqual(changed_session.created, r_session.created)
        self.assertGreater(changed_session.modified, r_session.modified)

        # Notes, Tags
        message = 'This is a note'
        fw.add_session_note(session_id, message)
        
        tag = 'example-tag'
        fw.add_session_tag(session_id, tag)

        # Replace Info
        fw.replace_session_info(session_id, { 'foo': 3, 'bar': 'qaz' })

        # Set Info
        fw.set_session_info(session_id, { 'foo': 42, 'hello': 'world' })

        # Check
        r_session = fw.get_session(session_id)

        self.assertEqual(len(r_session.notes), 1)
        self.assertEqual(r_session.notes[0].text, message)
        
        self.assertEqual(len(r_session.tags), 1)
        self.assertEqual(r_session.tags[0], tag)

        self.assertEqual(r_session.info['foo'], 42)
        self.assertEqual(r_session.info['bar'], 'qaz')
        self.assertEqual(r_session.info['hello'], 'world')

        # Delete info fields
        fw.delete_session_info_fields(session_id, ['foo', 'bar'])

        r_session = fw.get_session(session_id)
        self.assertNotIn('foo', r_session.info)
        self.assertNotIn('bar', r_session.info)
        self.assertEqual(r_session.info['hello'], 'world')

        # Delete
        fw.delete_session(session_id)

        sessions = fw.get_all_sessions()
        self.sanitize_for_collection(r_session)
        self.assertNotIn(r_session, sessions)

    def test_session_files(self):
        fw = self.fw
        
        session = flywheel.Session(label=self.rand_string(), project=self.project_id) 
        session_id = fw.add_session(session)

        # Upload a file
        poem = 'The best lack all conviction, while the worst'
        fw.upload_file_to_session(session_id, flywheel.FileSpec('yeats.txt', poem))

        # Check that the file was added to the session
        r_session = fw.get_session(session_id)
        self.assertEqual(len(r_session.files), 1)
        self.assertEqual(r_session.files[0].name, 'yeats.txt')
        self.assertEqual(r_session.files[0].size, 45)
        self.assertEqual(r_session.files[0].mimetype, 'text/plain')

        # Download the file and check content
        self.assertDownloadFileTextEquals(fw.download_file_from_session_as_data, session_id, 'yeats.txt', poem)
        
        # Test unauthorized download with ticket for the file
        self.assertDownloadFileTextEqualsWithTicket(fw.get_session_download_url, session_id, 'yeats.txt', poem)

        # Test file attributes
        self.assertEqual(r_session.files[0].modality, None)
        self.assertEmpty(r_session.files[0].classification)
        self.assertEqual(r_session.files[0].type, 'text')

        resp = fw.modify_session_file(session_id, 'yeats.txt', flywheel.FileEntry(
            modality='modality',
            type='type'
        ))

        # Check that no jobs were triggered, and attrs were modified
        self.assertEqual(resp.jobs_spawned, 0)

        r_session = fw.get_session(session_id)
        self.assertEqual(r_session.files[0].modality, "modality")
        self.assertEmpty(r_session.files[0].classification)
        self.assertEqual(r_session.files[0].type, 'type')

        # Test classifications
        resp = fw.replace_session_file_classification(session_id, 'yeats.txt', {
            'Custom': ['measurement1', 'measurement2'],
        })
        self.assertEqual(resp.modified, 1)
        self.assertEqual(resp.jobs_spawned, 0)

        r_session = fw.get_session(session_id)
        self.assertEqual(r_session.files[0].classification, {
            'Custom': ['measurement1', 'measurement2']
        });

        resp = fw.modify_session_file_classification(session_id, 'yeats.txt', {
            'add': {
                'Custom': ['HelloWorld'],
            },
            'delete': {
                'Custom': ['measurement2']
            }
        })
        self.assertEqual(resp.modified, 1)
        self.assertEqual(resp.jobs_spawned, 0)

        r_session = fw.get_session(session_id)
        self.assertEqual(r_session.files[0].classification, {
            'Custom': ['measurement1', 'HelloWorld'],
        });

        # Test file info
        self.assertEmpty(r_session.files[0].info)
        fw.replace_session_file_info(session_id, 'yeats.txt', {
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4
        })

        fw.set_session_file_info(session_id, 'yeats.txt', {
            'c': 5
        })

        r_session = fw.get_session(session_id)
        self.assertEqual(r_session.files[0].info['a'], 1)
        self.assertEqual(r_session.files[0].info['b'], 2)
        self.assertEqual(r_session.files[0].info['c'], 5)
        self.assertEqual(r_session.files[0].info['d'], 4)
    
        fw.delete_session_file_info_fields(session_id, 'yeats.txt', ['c', 'd'])  
        r_session = fw.get_session(session_id)
        self.assertEqual(r_session.files[0].info['a'], 1)
        self.assertEqual(r_session.files[0].info['b'], 2)
        self.assertNotIn('c', r_session.files[0].info)
        self.assertNotIn('d', r_session.files[0].info)

        fw.replace_session_file_info(session_id, 'yeats.txt', {})
        r_session = fw.get_session(session_id)
        self.assertEmpty(r_session.files[0].info)

        # Delete file
        fw.delete_session_file(session_id, 'yeats.txt')
        r_session = fw.get_session(session_id)
        self.assertEmpty(r_session.files)

        # Delete session
        fw.delete_session(session_id)

    def test_session_errors(self):
        fw = self.fw

        # Try to create session without project id
        try:
            session = flywheel.Session(label=self.rand_string())
            session_id = fw.add_session(session)
            self.fail('Expected ApiException creating invalid session!')
        except flywheel.ApiException as e:
            self.assertEqual(e.status, 400)

        # Try to get a session that doesn't exist
        try:
            fw.get_session('DOES_NOT_EXIST')
            self.fail('Expected ApiException retrieving invalid session!')
        except flywheel.ApiException as e:
            self.assertEqual(e.status, 404)

    def test_session_analysis(self):
        fw = self.fw
        
        session = flywheel.Session(project=self.project_id, label=self.rand_string()) 

        # Add
        session_id = fw.add_session(session)
        self.assertNotEmpty(session_id)

        poem = 'When a vast image out of Spiritus Mundi'
        fw.upload_file_to_session(session_id, flywheel.FileSpec('yeats.txt', poem))

        file_ref = flywheel.FileReference(
            id=session_id,
            type='session',
            name='yeats.txt'
        )

        analysis = flywheel.AnalysisInput(label=self.rand_string(), description=self.rand_string(), inputs=[file_ref])

        # Add
        analysis_id = fw.add_session_analysis(session_id, analysis)
        self.assertNotEmpty(analysis_id)

        # Get the list of analyses in the session
        analyses = fw.get_session_analyses(session_id)
        self.assertEqual(len(analyses), 1)
        
        r_analysis = analyses[0]

        self.assertEqual(r_analysis.id, analysis_id)
        self.assertEmpty(r_analysis.job)

        self.assertTimestampBeforeNow(r_analysis.created)
        self.assertGreaterEqual(r_analysis.modified, r_analysis.created)

        self.assertEqual(len(r_analysis.inputs), 1)
        self.assertEqual(r_analysis.inputs[0].name, 'yeats.txt')

    def sanitize_for_collection(self, session, info_exists=True):
        # workaround: all-container endpoints skip some fields, single-container does not. this sets up the equality check 
        session.info = {}
        session.info_exists = info_exists
        session.analyses = None
        session.subject = flywheel.Subject(
            id = session.subject.id,
            code = session.subject.code,
            info = {},
            info_exists = info_exists
        )


def create_test_session():
    group_id, project_id = create_test_project()
    return group_id, project_id, SdkTestCase.fw.add_session({
        'project': project_id, 
        'label': SdkTestCase.rand_string(),
        'subject': {
            'code': SdkTestCase.rand_string_lower(),
            'firstname': SdkTestCase.rand_string(),
            'lastname': SdkTestCase.rand_string(),
            'sex': 'other',
            'age': 57
        }
    })


