import unittest
from sdk_test_case import SdkTestCase
from test_acquisition import create_test_acquisition
from test_gear import create_test_gear

import flywheel

class MixinTestCases(SdkTestCase):
    def setUp(self):
        self.group_id, self.project_id, self.session_id, self.acquisition_id = create_test_acquisition()
        self.gear_id = None

    def tearDown(self):
        self.fw.delete_project(self.project_id)
        self.fw.delete_group(self.group_id)

        if self.gear_id is not None:
            self.fw.delete_gear(self.gear_id)

    def test_child_mixins(self):
        fw = self.fw

        # Upload file to project
        poem = 'When a vast image out of Spiritus Mundi'
        fw.upload_file_to_project(self.project_id, flywheel.FileSpec('yeats.txt', poem))

        # TODO: Test Analyses

        # GROUP
        r_group = fw.get_group(self.group_id)
        projects = r_group.get_projects()

        self.assertIsNotNone(projects)
        self.assertEqual(len(projects), 1)
        r_project = projects[0]

        self.assertEqual(r_project.id, self.project_id)
        self.assertEqual(r_project.container_type, 'project')

        # Try project.resolve_children()
        # - even though we will only get 1 session here
        children = r_project.resolve_children()
        self.assertIsNotNone(children)

        self.assertEqual(len(children), 2)
        r_session = children[0]
        self.assertEqual(r_session.id, self.session_id)
        self.assertEqual(r_session.project, self.project_id)

        r_file = children[1]
        self.assertEqual(r_file.name, 'yeats.txt')
        self.assertEqual(r_file.size, len(poem))

        acquisitions = r_session.get_acquisitions()
        self.assertIsNotNone(acquisitions)
        self.assertEqual(len(acquisitions), 1)

        r_acquisition = acquisitions[0]
        self.assertEqual(r_acquisition.id, self.acquisition_id)
        self.assertEqual(r_acquisition.session, self.session_id)

    def test_tag_mixins(self):
        fw = self.fw

        for container_type in ['group', 'project', 'session', 'acquisition']:
            cid = getattr(self, '{0}_id'.format(container_type), None)
            self.assertIsNotNone(cid)

            getter = getattr(self.fw, 'get_{0}'.format(container_type), None)
            self.assertIsNotNone(getter)

            container = getter(cid)
            self.assertIsNotNone(container)

            initial_tags = container.tags
            self.assertFalse(bool(initial_tags))

            container.add_tag('tag1')
            container.add_tag('tag2')

            container = getter(cid)
            self.assertEqual(2, len(container.tags))
            self.assertIn('tag1', container.tags)
            self.assertIn('tag2', container.tags)

            # Rename and delete
            container.rename_tag('tag2', 'tag3')
            container.delete_tag('tag1')

            container = getter(cid)
            self.assertEqual(['tag3'], container.tags)



