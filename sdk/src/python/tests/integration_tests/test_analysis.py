import unittest
from sdk_test_case import SdkTestCase
from test_session import create_test_session
from test_gear import create_test_gear

import flywheel

class AnalysisTestCases(SdkTestCase):
    def setUp(self):
        self.group_id, self.project_id, self.session_id = create_test_session()
        self.gear_id = create_test_gear()

    def tearDown(self):
        self.fw.delete_project(self.project_id)
        self.fw.delete_group(self.group_id)
        self.fw.delete_gear(self.gear_id)

    def test_ad_hoc_analysis(self):
        fw = self.fw
        
        # Upload to session
        poem = 'A gaze blank and pitiless as the sun,'
        fw.upload_file_to_session(self.session_id, flywheel.FileSpec('yeats.txt', poem))

        file_ref = flywheel.FileReference(
            id=self.session_id,
            type='session',
            name='yeats.txt'
        )

        analysis = flywheel.AnalysisInput(label=self.rand_string(), description=self.rand_string(), inputs=[file_ref])

        # Add
        analysis_id = fw.add_session_analysis(self.session_id, analysis)
        self.assertNotEmpty(analysis_id)

        session = fw.get_session(self.session_id)
        self.assertEqual(len(session.analyses), 1)

        r_analysis = session.analyses[0]
        self.assertEqual(r_analysis.id, analysis_id)
        self.assertIsNone(r_analysis.job)
        self.assertTimestampBeforeNow(r_analysis.created)
        self.assertGreaterEqual(r_analysis.modified, r_analysis.created)
        self.assertEqual(len(r_analysis.inputs), 1)
        self.assertEqual(r_analysis.inputs[0].name, 'yeats.txt')

        # Access analysis directly
        r_analysis2 = fw.get_analysis(analysis_id)
        self.assertEqual(r_analysis, r_analysis2)

        # Analysis Notes
        text = self.rand_string()
        fw.add_session_analysis_note(self.session_id, analysis_id, text)

        # Check
        session = fw.get_session(self.session_id)
        self.assertEqual(len(session.analyses), 1)

        r_analysis = session.analyses[0]
        self.assertEqual(len(r_analysis.notes), 1)
        self.assertNotEmpty(r_analysis.notes[0].user)
        self.assertEqual(r_analysis.notes[0].text, text)
        self.assertTimestampBeforeNow(r_analysis.notes[0].created)
        self.assertTimestampBeforeNow(r_analysis.notes[0].modified)
        self.assertTimestampAfter(r_analysis.notes[0].modified, r_analysis.created)
        self.assertGreaterEqual(r_analysis.notes[0].modified, r_analysis.notes[0].created)

        # Access multiple analyses
        analysis_id2 = fw.add_session_analysis(self.session_id, analysis)
        self.assertNotEmpty(analysis_id2)

        # Try getting analysis incorrectly
        self.assertRaises(flywheel.ApiException, fw.get_analyses, 'session', self.session_id, 'projects')

        # Get all Session level analyses in group
        analyses = fw.get_analyses('groups', self.group_id, 'sessions')
        self.assertEqual(len(analyses), 2)

        self.assertEqual(1, len(list(filter(lambda x: x.id == r_analysis.id, analyses))))
        self.assertEqual(1, len(list(filter(lambda x: x.id == analysis_id2, analyses))))

        # Get project level analyses in group (will be zero)
        analyses = fw.get_analyses('groups', self.group_id, 'projects')
        self.assertEmpty(analyses)

        # Info, tags
        tag = 'example-tag'
        fw.add_analysis_tag(analysis_id, tag)

        # Replace info
        fw.replace_analysis_info(analysis_id, {
            'foo': 3,
            'bar': 'qaz'
        })

        # Set info
        fw.set_analysis_info(analysis_id, {
            'foo': 42,
            'hello': 'world'
        })

        # Check
        r_analysis = fw.get_analysis(analysis_id)
        self.assertEqual(r_analysis.tags, [tag])
        self.assertEqual(r_analysis.info, {
            'foo': 42,
            'bar': 'qaz',
            'hello': 'world'
        })

        # Delete info fields
        fw.delete_analysis_info_fields(analysis_id, ['foo', 'bar'])
        r_analysis = fw.get_analysis(analysis_id)
        self.assertEqual(r_analysis.info, {
            'hello': 'world'
        })

    def test_job_based_analysis(self):
        fw = self.fw
        
        # Upload to session
        poem = 'A gaze blank and pitiless as the sun,'
        fw.upload_file_to_session(self.session_id, flywheel.FileSpec('yeats.txt', poem))

        file_ref = flywheel.FileReference(
            id=self.session_id,
            type='session',
            name='yeats.txt'
        )

        tag = self.rand_string()

        job = flywheel.Job(
            gear_id=self.gear_id,
            inputs={
                'any-file': file_ref
            },
            tags=[tag]
        )
        
        analysis = flywheel.AnalysisInput(label=self.rand_string(), description=self.rand_string(), job=job)

        # Add
        analysis_id = fw.add_session_analysis(self.session_id, analysis)
        self.assertNotEmpty(analysis_id)

        session = fw.get_session(self.session_id)
        self.assertEqual(len(session.analyses), 1)

        r_analysis = session.analyses[0]
        self.assertEqual(r_analysis.id, analysis_id)
        self.assertEqual(r_analysis.job.state, 'pending')
        self.assertTimestampBeforeNow(r_analysis.created)
        self.assertGreaterEqual(r_analysis.modified, r_analysis.created)
        self.assertEqual(len(r_analysis.inputs), 1)
        self.assertEqual(r_analysis.inputs[0].name, 'yeats.txt')

        # Verify job
        r_job = fw.get_job(r_analysis.job.id)
        self.assertEqual(r_analysis.job.state, 'pending')

        # Access analysis directly
        r_analysis2 = fw.get_analysis(analysis_id)
        self.assertEqual(r_analysis, r_analysis2)

    def test_analysis_files(self):
        fw = self.fw
        
        # Upload to session
        poem = 'A gaze blank and pitiless as the sun,'
        fw.upload_file_to_session(self.session_id, flywheel.FileSpec('yeats.txt', poem))

        file_ref = flywheel.FileReference(
            id=self.session_id,
            type='session',
            name='yeats.txt'
        )

        analysis = flywheel.AnalysisInput(label=self.rand_string(), description=self.rand_string(), inputs=[file_ref])

        # Add
        analysis_id = fw.add_session_analysis(self.session_id, analysis)

        # Download the input file and check content
        self.assertDownloadFileTextEquals(fw.download_input_from_analysis_as_data, analysis_id, 'yeats.txt', poem)
        self.assertDownloadFileTextEqualsWithTicket(fw.get_analysis_input_download_url, analysis_id, 'yeats.txt', poem)

        poem_out = 'Surely the Second Coming is at hand.'
        fw.upload_output_to_analysis(analysis_id, flywheel.FileSpec('yeats-out.txt', poem_out))

        r_analysis = fw.get_analysis(analysis_id)
        self.assertEqual(len(r_analysis.files), 1)
        self.assertEqual(r_analysis.files[0].name, 'yeats-out.txt')
        self.assertEqual(r_analysis.files[0].size, 36)
        self.assertEqual(r_analysis.files[0].mimetype, 'text/plain')

        # Download and check content
        self.assertDownloadFileTextEquals(fw.download_output_from_analysis_as_data, analysis_id, 'yeats-out.txt', poem_out)
        self.assertDownloadFileTextEqualsWithTicket(fw.get_analysis_output_download_url, analysis_id, 'yeats-out.txt', poem_out)


