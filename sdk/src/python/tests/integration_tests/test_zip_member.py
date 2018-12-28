import datetime
import os
import tempfile
import unittest
import zipfile

from sdk_test_case import SdkTestCase
from test_acquisition import create_test_acquisition

import flywheel

ENTRY_TEXT = 'Hello World!'
ENTRY_SIZE = len(ENTRY_TEXT)
ENTRY_TIMESTAMP = (2018, 10, 30, 2, 5, 10)

class ZipMemberTestCases(SdkTestCase):
    def setUp(self):
        self.group_id, self.project_id, self.session_id, self.acquisition_id = create_test_acquisition()

    def tearDown(self):
        self.fw.delete_project(self.project_id)
        self.fw.delete_group(self.group_id)

        if self.zip_path:
            os.remove(self.zip_path)

    def test_zip_members(self):
        fw = self.fw

        # Create a zip file with comments
        fd, self.zip_path = tempfile.mkstemp(suffix='.zip')
        with os.fdopen(fd, 'wb') as f:
            with zipfile.ZipFile(f, 'w') as zf:
                zf.comment = b'This is a zipfile comment'

                entry_info = zipfile.ZipInfo(filename='test-entry.txt', date_time=ENTRY_TIMESTAMP)
                entry_info.comment = b'This is a zipinfo comment'
                zf.writestr(entry_info, ENTRY_TEXT)

        # Upload the file
        filename = os.path.basename(self.zip_path)
        fw.upload_file_to_acquisition(self.acquisition_id, self.zip_path)

        # Get zip info
        zip_info = fw.get_acquisition_file_zip_info(self.acquisition_id, filename)
        self.assertEqual(zip_info.comment, 'This is a zipfile comment')
        self.assertEqual(len(zip_info.members), 1)
        zip_entry_info = zip_info.members[0]
        self.assertEqual(zip_entry_info.path, 'test-entry.txt')
        timestamp = zip_entry_info.timestamp.replace(tzinfo=None)
        self.assertEqual(timestamp, datetime.datetime(*ENTRY_TIMESTAMP))
        self.assertEqual(zip_entry_info.size, ENTRY_SIZE)
        self.assertEqual(zip_entry_info.comment, 'This is a zipinfo comment')

        # Download the zip member
        data = fw.download_file_from_acquisition_as_data(self.acquisition_id, filename, member='test-entry.txt')
        self.assertEqual(data, ENTRY_TEXT.encode('ascii'))

        # Use helper mixin
        acq = fw.get(self.acquisition_id)
        zip_info2 = acq.get_file_zip_info(filename)
        self.assertEqual(zip_info, zip_info2)

