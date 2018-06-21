import re
import unittest
from sdk_test_case import SdkTestCase

import flywheel

class UsersTestCases(SdkTestCase):
    def assertUserIsSane(self, user): 
        """Validate that a user has the expected fields populated"""
        self.assertIsNotNone(user)

        self.assertNotEmpty(user.id)
        self.assertTrue(re.search(r'.+@.+', user.email))
        self.assertNotEmpty(user.firstname)
        self.assertNotEmpty(user.lastname)
        self.assertTimestampBeforeNow(user.created)
        self.assertTimestampBeforeNow(user.modified)

    def test_get_current_user(self):
        user = self.fw.get_current_user()
        self.assertUserIsSane(user)

        self.assertIn('api_key', user)
        self.assertNotEmpty(user.api_key.key)

        self.assertTimestampBeforeNow(user.api_key.created)
        self.assertTimestampBeforeNow(user.api_key.last_used)

    def test_get_all_users(self):
        users = self.fw.get_all_users()

        self.assertTrue(len(users) > 0)
        for user in users:
            self.assertUserIsSane(user)

    def test_get_user(self):
        user = self.fw.get_current_user()
        self.assertIsNotNone(user)

        # Should be a valid user, but not have an api key
        user2 = self.fw.get_user(user.id)
        self.assertUserIsSane(user2)

        self.assertIsNone(user2['api_key'])

    def test_add_modify_delete_user(self):
        fw = self.fw
        email = self.rand_string() + '@' + self.rand_string() + '.io'

        user = flywheel.User(email=email,
            firstname=self.rand_string(), lastname=self.rand_string())

        # Add
        user_id = fw.add_user(user)
        self.assertNotEmpty(user_id)

        # Modify
        new_name = self.rand_string()
        fw.modify_user(user_id, flywheel.User(firstname=new_name))

        # Check
        compare = fw.get_user(user_id)
        self.assertIsNotNone(compare)
        self.assertEqual(compare.id, user_id)
        self.assertEqual(compare.email, email)
        self.assertEqual(compare.firstname, new_name)
        self.assertEqual(compare.lastname, user.lastname)
        self.assertGreater(compare.modified, compare.created)
        self.assertTimestampBeforeNow(compare.created)

        # Check in list
        users = fw.get_all_users()
        self.assertIn(compare, users)

        # Remove
        fw.delete_user(user_id)
        
        # Confirm deletion
        users = fw.get_all_users()
        self.assertNotIn(compare, users)

    def test_client_isolation(self):
        fw = self.fw

        fw2 = flywheel.Flywheel('127.0.0.1:invalid-key')
        
        try:
            user = self.fw.get_current_user()
            self.assertUserIsSane(user)
        except flywheel.ApiException:
            self.fail('Flywheel instance is not isolated!')


