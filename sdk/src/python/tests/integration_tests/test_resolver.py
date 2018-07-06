import unittest
from sdk_test_case import SdkTestCase
from test_acquisition import create_test_acquisition
from test_gear import create_test_gear

import flywheel

def idz(s):
    return '<id:{0}>'.format(s)

class ResolverTestCases(SdkTestCase):
    def setUp(self):
        self.group_id, self.project_id, self.subject_id, self.session_id, self.acquisition_id = create_test_acquisition(return_subject=True)
        self.gear_id = None

    def tearDown(self):
        self.fw.delete_project(self.project_id)
        self.fw.delete_group(self.group_id)

        if self.gear_id is not None:
            self.fw.delete_gear(self.gear_id)

    def test_resolver(self):
        fw = self.fw
        group_id = self.group_id

        # Create test gear
        self.gear_id = create_test_gear()
        gear = self.fw.get_gear(self.gear_id)
        self.assertIsNotNone(gear)

        # Upload file acquisition
        poem = 'The Second Coming! Hardly are those words out'
        fw.upload_file_to_acquisition(self.acquisition_id, flywheel.FileSpec('yeats.txt', poem))

        # Resolve group children
        result = fw.resolve([group_id])

        self.assertEqual(len(result.path), 1)
        r_group = result.path[0]
        self.assertEqual(r_group.id, group_id)

        self.assertEqual(len(result.children), 1)
        r_project = result.children[0]
        self.assertEqual(r_project.id, self.project_id)

        # Resolve project children
        result = fw.resolve('{0}/{1}'.format(group_id, r_project.label))
        self.assertEqual(len(result.path), 2)
        self.assertEqual(result.path[0], r_group)
        self.assertEqual(result.path[1], r_project)

        self.assertEqual(len(result.children), 1)
        r_subject = result.children[0]
        self.assertEqual(r_subject.project, self.project_id)
        self.assertEqual(r_subject.id, self.subject_id)

        # Resolve subject children (using id string)
        result = fw.resolve('{0}/{1}/<id:{2}>'.format(group_id, r_project.label, self.subject_id))
        self.assertEqual(len(result.path), 3)
        self.assertEqual(result.path[0], r_group)
        self.assertEqual(result.path[1], r_project)
        self.assertEqual(result.path[2], r_subject)

        self.assertEqual(len(result.children), 1)
        r_session = result.children[0]
        self.assertEqual(r_session.project, self.project_id)
        self.assertEqual(r_session.subject.id, self.subject_id)
        self.assertEqual(r_session.id, self.session_id)

        # Resolve session children (using id string)
        result = fw.resolve('{0}/{1}/<id:{2}>/<id:{3}>'.format(group_id, r_project.label, 
            self.subject_id, self.session_id))
        self.assertEqual(len(result.path), 4)
        self.assertEqual(result.path[0], r_group)
        self.assertEqual(result.path[1], r_project)
        self.assertEqual(result.path[2], r_subject)
        self.assertEqual(result.path[3], r_session)

        self.assertEqual(len(result.children), 1)
        r_acquisition = result.children[0]
        self.assertEqual(r_acquisition.session, self.session_id)
        self.assertEqual(r_acquisition.id, self.acquisition_id)

        # Finally, resolve acquisition files
        result = fw.resolve([group_id, r_project.label, r_subject.label, r_session.label, r_acquisition.label])
        self.assertEqual(len(result.path), 5)
        self.assertEqual(result.path[0], r_group)
        self.assertEqual(result.path[1], r_project)
        self.assertEqual(result.path[2], r_subject)
        self.assertEqual(result.path[3], r_session)
        self.assertEqual(result.path[4], r_acquisition)

        self.assertEqual(len(result.children), 1)
        r_file = result.children[0]
        self.assertEqual(r_file.name, 'yeats.txt')
        self.assertEqual(r_file.size, len(poem))

        # TODO: Test Analyses

        # Test resolve gears
        result = fw.resolve('gears')
        self.assertEmpty(result.path)
        self.assertGreaterEqual(len(result.children), 1)
        found = False
        for child in result.children:
            if child.id == self.gear_id:
                found = True
                break
        self.assertTrue(found)

    def test_lookup(self):
        fw = self.fw
        group_id = self.group_id

        # Get labels for everything
        result = fw.resolve([group_id, idz(self.project_id), idz(self.subject_id), idz(self.session_id)])
        self.assertEqual(4, len(result.path))
        self.assertEqual(1, len(result.children))

        group = result.path[0]
        project = result.path[1]
        subject = result.path[2]
        session = result.path[3]
        acquisition = result.children[0]

        # Create test gear
        self.gear_id = create_test_gear()
        gear = self.fw.get_gear(self.gear_id)
        self.assertIsNotNone(gear)

        # Upload file acquisition
        poem = 'The Second Coming! Hardly are those words out'
        fw.upload_file_to_acquisition(self.acquisition_id, flywheel.FileSpec('yeats.txt', poem))

        # Resolve group 
        r_group = fw.lookup([group_id])
        self.assertEqual(r_group.id, group_id)
        self.assertIsNotNone(r_group.label)
        self.assertNotEmpty(r_group.permissions)

        # Resolve project 
        r_project = fw.lookup('{0}/{1}'.format(group_id, project.label))
        self.assertEqual(r_project.id, self.project_id)

        # Resolve subject 
        r_subject = fw.lookup('{0}/{1}/<id:{2}>'.format(group_id, project.label, 
            self.subject_id))
        self.assertEqual(r_subject.id, self.subject_id)

        # Resolve session
        r_session = fw.lookup('{0}/{1}/<id:{2}>/<id:{3}>'.format(group_id, project.label, 
            self.subject_id, self.session_id))
        self.assertEqual(r_session.id, self.session_id)

        # Resolve acquisition 
        r_acquisition = fw.lookup([group_id, project.label, subject.label, session.label, acquisition.label])
        self.assertEqual(r_acquisition.id, self.acquisition_id)

        # Resolve acquisition file
        r_file = fw.lookup([group_id, project.label, subject.label, session.label, 
            acquisition.label, 'files', 'yeats.txt'])
        self.assertEqual(r_file.name, 'yeats.txt')
        self.assertEqual(r_file.size, len(poem))

        # Test not found
        try:
            fw.lookup('NOT-A-GROUP/NOT-A-PROJECT')
            self.fail('Expected ApiException!')
        except flywheel.ApiException as e:
            self.assertEqual(e.status, 404)

        # TODO: Test Analyses

        # Test resolve gears
        r_gear = fw.lookup(['gears', gear.gear.name])
        self.assertEqual(r_gear.gear, gear.gear)


    def test_resolver_permissions(self):
        fw = self.fw
        group_id = self.group_id

        # Change project permission
        r_project = fw.get_project(self.project_id)
        self.assertEqual(len(r_project.permissions), 1)
        user_id = r_project.permissions[0].id

        fw.delete_project_user_permission(self.project_id, user_id)

        # Resolve group
        result = fw.resolve([group_id])

        self.assertEqual(len(result.path), 1)
        r_group = result.path[0]
        self.assertEmpty(result.children)

        # Resolve project, but no children
        result = fw.resolve([group_id, r_project.label])
        self.assertEqual(len(result.path), 2)
        self.assertEqual(len(result.children), 0)

        # Try to resolve project with exhaustive flag
        result = fw.resolve([group_id], exhaustive=True)

        self.assertEqual(len(result.path), 1)
        self.assertEqual(len(result.children), 1)
        r_project = result.children[0]
        self.assertEqual(r_project.id, self.project_id)

        # Resolve project children
        result = fw.resolve('{0}/{1}'.format(group_id, r_project.label), exhaustive=True)
        self.assertEqual(len(result.path), 2)

        self.assertEqual(result.path[0].to_dict(), r_group.to_dict())
        self.assertEqual(result.path[1].to_dict(), r_project.to_dict())

        self.assertEqual(len(result.children), 1)
        r_subject = result.children[0]
        self.assertEqual(r_subject.project, self.project_id)
        self.assertEqual(r_subject.id, self.subject_id)


