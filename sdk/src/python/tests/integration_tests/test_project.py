import unittest
from sdk_test_case import SdkTestCase
from test_group import create_test_group

import flywheel

class ProjectsTestCases(SdkTestCase):
    def setUp(self):
        self.group_id = create_test_group()
        self.project_id = None

    def tearDown(self):
        if self.project_id:
            self.fw.delete_project(self.project_id)

        self.fw.delete_group(self.group_id)

    def test_projects(self):
        fw = self.fw
        
        project_name = self.rand_string()
        project = flywheel.Project(label=project_name, group=self.group_id, 
            description="This is a description", info = { 'some-key': 37 })

        # Add
        self.project_id = project_id = fw.add_project(project)
        self.assertNotEmpty(project_id)

        # Get
        r_project = fw.get_project(project_id)
        self.assertEqual(r_project.id, project_id)
        self.assertEqual(r_project.label, project_name)
        self.assertEqual(r_project.description, project.description)
        self.assertIn('some-key', r_project.info)
        self.assertEqual(r_project.info['some-key'], 37)
        self.assertTimestampBeforeNow(r_project.created)
        self.assertGreaterEqual(r_project.modified, r_project.created)

        # Get All
        projects = fw.get_all_projects()
        r_project.info = {}
        # TODO: Should we be setting this, shouldn't it be coming from api?
        r_project.info_exists = True
        r_project.analyses = None
        self.assertIn(r_project, projects)

        # Modify
        new_name = self.rand_string()
        project_mod = flywheel.Project(label=new_name, info={'another-key': 52})
        fw.modify_project(project_id, project_mod)

        changed_project = fw.get_project(project_id)
        self.assertEqual(changed_project.label, new_name)
        self.assertIn('some-key', changed_project.info)
        self.assertIn('another-key', changed_project.info)
        self.assertEqual(changed_project.info['another-key'], 52)
        self.assertEqual(changed_project.created, r_project.created)
        self.assertGreater(changed_project.modified, r_project.modified)

        # Notes, Tags
        message = 'This is a note'
        fw.add_project_note(project_id, message)
        
        tag = 'example-tag'
        fw.add_project_tag(project_id, tag)

        # Replace Info
        fw.replace_project_info(project_id, { 'foo': 3, 'bar': 'qaz' })

        # Set Info
        fw.set_project_info(project_id, { 'foo': 42, 'hello': 'world' })

        # Check
        r_project = fw.get_project(project_id)

        self.assertEqual(len(r_project.notes), 1)
        self.assertEqual(r_project.notes[0].text, message)
        
        self.assertEqual(len(r_project.tags), 1)
        self.assertEqual(r_project.tags[0], tag)

        self.assertEqual(r_project.info['foo'], 42)
        self.assertEqual(r_project.info['bar'], 'qaz')
        self.assertEqual(r_project.info['hello'], 'world')

        # Delete info fields
        fw.delete_project_info_fields(project_id, ['foo', 'bar'])

        r_project = fw.get_project(project_id)
        self.assertNotIn('foo', r_project.info)
        self.assertNotIn('bar', r_project.info)
        self.assertEqual(r_project.info['hello'], 'world')

        # Delete
        fw.delete_project(project_id)
        self.project_id = None

        projects = fw.get_all_projects()
        self.assertNotIn(r_project, projects)

    def test_project_files(self):
        fw = self.fw
        
        project = flywheel.Project(label=self.rand_string(), group=self.group_id)
        self.project_id = project_id = fw.add_project(project)

        # Upload a file
        poem = 'The ceremony of innocence is drowned;'
        fw.upload_file_to_project(project_id, flywheel.FileSpec('yeats.txt', poem))

        # Check that the file was added to the project
        r_project = fw.get_project(project_id)
        self.assertEqual(len(r_project.files), 1)
        self.assertEqual(r_project.files[0].name, 'yeats.txt')
        self.assertEqual(r_project.files[0].size, 37)
        self.assertEqual(r_project.files[0].mimetype, 'text/plain')

        # Download the file and check content
        self.assertDownloadFileTextEquals(fw.download_file_from_project_as_data, project_id, 'yeats.txt', poem)
        
        # Test unauthorized download with ticket for the file
        self.assertDownloadFileTextEqualsWithTicket(fw.get_project_download_url, project_id, 'yeats.txt', poem)

        # Test file attributes
        self.assertEqual(r_project.files[0].modality, None)
        self.assertEmpty(r_project.files[0].classification)
        self.assertEqual(r_project.files[0].type, 'text')

        resp = fw.modify_project_file(project_id, 'yeats.txt', flywheel.FileEntry(
            modality='modality',
            type='type'
        ))

        # Check that no jobs were triggered, and attrs were modified
        self.assertEqual(resp.jobs_spawned, 0)

        r_project = fw.get_project(project_id)
        self.assertEqual(r_project.files[0].modality, "modality")
        self.assertEmpty(r_project.files[0].classification)
        self.assertEqual(r_project.files[0].type, 'type')

        # Test classifications
        resp = fw.modify_project_file_classification(project_id, 'yeats.txt', {
            'replace': {
                'Custom': ['measurement1', 'measurement2'],
            }
        })
        self.assertEqual(resp.modified, 1)
        self.assertEqual(resp.jobs_spawned, 0)

        r_project = fw.get_project(project_id)
        self.assertEqual(r_project.files[0].classification, {
            'Custom': ['measurement1', 'measurement2']
        });

        resp = fw.modify_project_file_classification(project_id, 'yeats.txt', {
            'add': {
                'Custom': ['HelloWorld'],
            },
            'delete': {
                'Custom': ['measurement2']
            }
        })
        self.assertEqual(resp.modified, 1)
        self.assertEqual(resp.jobs_spawned, 0)

        r_project = fw.get_project(project_id)
        self.assertEqual(r_project.files[0].classification, {
            'Custom': ['measurement1', 'HelloWorld'],
        });

        # Test file info
        self.assertEmpty(r_project.files[0].info)
        fw.replace_project_file_info(project_id, 'yeats.txt', {
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4
        })

        fw.set_project_file_info(project_id, 'yeats.txt', {
            'c': 5
        })

        r_project = fw.get_project(project_id)
        self.assertEqual(r_project.files[0].info['a'], 1)
        self.assertEqual(r_project.files[0].info['b'], 2)
        self.assertEqual(r_project.files[0].info['c'], 5)
        self.assertEqual(r_project.files[0].info['d'], 4)
    
        fw.delete_project_file_info_fields(project_id, 'yeats.txt', ['c', 'd'])  
        r_project = fw.get_project(project_id)
        self.assertEqual(r_project.files[0].info['a'], 1)
        self.assertEqual(r_project.files[0].info['b'], 2)
        self.assertNotIn('c', r_project.files[0].info)
        self.assertNotIn('d', r_project.files[0].info)

        fw.replace_project_file_info(project_id, 'yeats.txt', {})
        r_project = fw.get_project(project_id)
        self.assertEmpty(r_project.files[0].info)

        # Delete file
        fw.delete_project_file(project_id, 'yeats.txt')
        r_project = fw.get_project(project_id)
        self.assertEmpty(r_project.files)

    def test_create_project_in_root_mode(self):
        fw = self.fw

        group = fw.get_group(self.group_id)
        
        # Remove permissions from group
        user_id = group.permissions[0].id
        fw.delete_group_user_permission(self.group_id, user_id)

        # Check that permission was removed successfully
        group = fw.get_group(self.group_id)
        self.assertEmpty(group.permissions)

        # Assert that we get a 403 error attempting to create a project without permission
        project_name = self.rand_string()
        project = flywheel.Project(label=self.rand_string(), group=self.group_id)

        try:
            fw.add_project(project)
            self.fail('Expected ApiException creating project!')
        except flywheel.ApiException as e:
            self.assertEqual(e.status, 403)

        # We shouldn't get an error in root mode
        project_id = self.fw_root.add_project(project)
        self.assertNotEmpty(project_id)
      
        try:
            # Delete implicit permission from the project
            fw.delete_project_user_permission(project_id, user_id)

            # Should get a 403 error trying to retrieve the project
            try:
                fw.get_project(project_id)
                self.fail('Expected ApiException retrieving project!')
            except flywheel.ApiException as e:
                self.assertEqual(e.status, 403)

            # Should be able to retrieve as root
            r_project = self.fw_root.get_project(project_id)
            self.assertEqual(r_project.label, project.label)

            # Should be in list retrieved as root
            r_project.info = {}
            r_project.info_exists = False 
            r_project.analyses = None
            projects = self.fw_root.get_all_projects()
            self.assertIn(r_project, projects)

            # Should not show up in normal list
            projects = fw.get_all_projects()
            self.assertNotIn(r_project, projects)

        finally:
            # Always cleanup project
            self.fw_root.delete_project(project_id)

    def test_project_errors(self):
        fw = self.fw

        # Try to create project without group id
        try:
            project = flywheel.Project(label=self.rand_string())
            fw.add_project(project)
            self.fail('Expected ApiException creating invalid project!')
        except flywheel.ApiException as e:
            self.assertEqual(e.status, 400)

        # Try to get a project that doesn't exist
        try:
            fw.get_project('DOES_NOT_EXIST')
            self.fail('Expected ApiException retrieving invalid project!')
        except flywheel.ApiException as e:
            self.assertEqual(e.status, 404)

    def test_project_analysis(self):
        fw = self.fw
        
        project = flywheel.Project(group=self.group_id, label=self.rand_string()) 

        # Add
        self.project_id = project_id = fw.add_project(project)
        self.assertNotEmpty(project_id)

        poem = 'The Second Coming! Hardly are those words out'
        fw.upload_file_to_project(project_id, flywheel.FileSpec('yeats.txt', poem))

        file_ref = flywheel.FileReference(
            id=project_id,
            type='project',
            name='yeats.txt'
        )

        analysis = flywheel.AnalysisInput(label=self.rand_string(), description=self.rand_string(), inputs=[file_ref])

        # Add
        analysis_id = fw.add_project_analysis(project_id, analysis)
        self.assertNotEmpty(analysis_id)

        # Get the list of analyses in the project
        analyses = fw.get_project_analyses(project_id)
        self.assertEqual(len(analyses), 1)
        
        r_analysis = analyses[0]

        self.assertEqual(r_analysis.id, analysis_id)
        self.assertEmpty(r_analysis.job)

        self.assertTimestampBeforeNow(r_analysis.created)
        self.assertGreaterEqual(r_analysis.modified, r_analysis.created)

        self.assertEqual(len(r_analysis.inputs), 1)
        self.assertEqual(r_analysis.inputs[0].name, 'yeats.txt')

def create_test_project():
    group_id = create_test_group()
    return group_id, SdkTestCase.fw.add_project({
        'group': group_id, 
        'label': SdkTestCase.rand_string()
    })
        



