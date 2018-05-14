import unittest
from sdk_test_case import SdkTestCase

import flywheel

class GroupsTestCases(SdkTestCase):

    def test_groups(self):
        fw = self.fw

        group_id = self.rand_string_lower()
        group_name = self.rand_string()

        r_id = self.fw.add_group(flywheel.Group(group_id,label=group_name))
        self.assertEqual(group_id, r_id)

        # Get
        saved_group = fw.get_group(group_id)
        self.assertEqual(group_id, saved_group.id)
        self.assertEqual(group_name, saved_group.label)
        self.assertTimestampBeforeNow(saved_group.created)
        self.assertGreaterEqual(saved_group.modified, saved_group.created)

        self.assertTrue(hasattr(saved_group, 'container_type'))
        self.assertEqual(saved_group.container_type, 'group')

        self.assertTrue(hasattr(saved_group, 'child_types'))
        self.assertEqual(saved_group.child_types, ['projects'])

        # Generic Get is equivalent
        self.assertEqual(fw.get(group_id).to_dict(), saved_group.to_dict())

        # Get All
        groups = fw.get_all_groups()
        self.assertIn(saved_group, groups)

        self.assertEqual(groups[0].container_type, 'group')

        # Modify
        new_name = self.rand_string()
        fw.modify_group(group_id, {'label': new_name})

        changed_group = fw.get_group(group_id)
        self.assertEqual(new_name, changed_group.label)
        self.assertEqual(saved_group.created, changed_group.created)
        self.assertGreater(changed_group.modified, saved_group.modified)

        # Tags
        tag = 'example-tag-group'
        fw.add_group_tag(group_id, tag)

        # Check
        r_group = fw.get_group(group_id)
        self.assertEqual(1, len(r_group.tags))
        self.assertEqual(tag, r_group.tags[0])
        self.assertGreater(r_group.modified, changed_group.modified)

        # Add project
        project = r_group.add_project(label='My Project')
        self.assertIsNotNone(project)
        fw.delete_project(project.id)

        # Delete
        fw.delete_group(group_id)
        groups = fw.get_all_groups()
        self.assertNotIn(r_group, groups)

    def test_group_errors(self):
        fw = self.fw

        # Try to create group without label or id
        try:
            fw.add_group({})
            self.fail('Expected ApiException creating invalid group!')
        except flywheel.ApiException as e:
            self.assertEqual(e.status, 400)

        # Try to get a group that doesn't exist
        try:
            fw.get_group('DOES_NOT_EXIST')
            self.fail('Expected ApiException retrieving invalid group!')
        except flywheel.ApiException as e:
            self.assertEqual(e.status, 404)


def create_test_group():
    group_id = SdkTestCase.rand_string_lower()
    return SdkTestCase.fw.add_group(flywheel.Group(group_id, label=SdkTestCase.rand_string()))
        



