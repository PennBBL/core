import unittest
from sdk_test_case import SdkTestCase

import flywheel

class ClassificationTestCases(SdkTestCase):
    def setUp(self):
        self.modality_id = None

    def tearDown(self):
        if self.modality_id:
            self.fw.delete_modality(self.modality_id)

    def test_modalities(self):
        fw = self.fw

        modality = flywheel.Modality('CT', {
            'Intent': ["Structural", "Functional", "Localizer"],
            'Contrast': ["B0", "B1", "T1", "T2"]
        })

        # === Add modality ===
        self.modality_id = fw.add_modality(modality)
        self.assertEqual(self.modality_id, 'CT')
        
        # === Get modality ===
        # Non-existent
        try:
            fw.get_modality('NOT_EXIST')
            self.fail('Expected ApiException!')
        except flywheel.ApiException as e:
            self.assertEqual(e.status, 404)

        r_modality = fw.get_modality(self.modality_id)
        self.assertEqual(r_modality, modality)

        # === Get list of modalities ===
        modalities = fw.get_all_modalities()
        self.assertGreaterEqual(len(modalities), 1)

        self.assertIn(modality, modalities)

        # === Try to replace via add ===
        try:
            fw.add_modality(modality)
            self.fail('Expected ApiException!')
        except flywheel.ApiException as e:
            self.assertEqual(e.status, 409)


        # === Replace modality ===
        modality2 = flywheel.Modality(classification={
            'Intent': ['new', 'values']
        })

        # Non-existent
        try:
            fw.replace_modality('NOT_EXIST', modality2) 
            self.fail('Expected ApiException!')
        except flywheel.ApiException as e:
            self.assertEqual(e.status, 404)

        fw.replace_modality(self.modality_id, modality2)
        
        modality2.id = self.modality_id
        r_modality = fw.get_modality(self.modality_id)
        self.assertEqual(r_modality, modality2)

        # === Delete Modality ===
        # Non-existent
        try:
            fw.delete_modality('NOT_EXIST') 
            self.fail('Expected ApiException!')
        except flywheel.ApiException as e:
            self.assertEqual(e.status, 404)

        fw.delete_modality(self.modality_id)
        self.modality_id = None

        modalities = fw.get_all_modalities()
        self.assertNotIn(modality2, modalities)

