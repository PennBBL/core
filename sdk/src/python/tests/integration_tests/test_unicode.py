# coding=utf-8

import six
import unittest
from sdk_test_case import SdkTestCase
from test_session import create_test_session

import flywheel

# A few choice samples from: https://github.com/minimaxir/big-list-of-naughty-strings
TEST_LABELS = [
    six.u('åß∂ƒ©˙∆˚¬…æ'),
    six.u('Ω≈ç√∫˜µ≤≥÷'),
    six.u('ЁЂЃЄЅІЇЈЉЊЋЌЍЎЏАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюя'),
    six.u('(╯°□°）╯︵ ┻━┻'),
    six.u('¯\_(ツ)_/¯')
]

class UnicodeTestCases(SdkTestCase):
    def setUp(self):
        self.group_id, self.project_id, self.session_id = create_test_session()

    def tearDown(self):
        self.fw.delete_project(self.project_id)
        self.fw.delete_group(self.group_id)

    def test_unicode_label(self):
        fw = self.fw

        for label in TEST_LABELS:
            acquisition = flywheel.Acquisition(label=label, session=self.session_id) 

            acquisition_id = fw.add_acquisition(acquisition)
            self.assertIsNotNone(acquisition_id)

            r_acquisition = fw.get_acquisition(acquisition_id)
            self.assertEqual(r_acquisition.label, label)

