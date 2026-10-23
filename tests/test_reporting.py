"""Reports must not convert past runs into claims about the current run."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from pisa.reporting import figure_qa_status, invocation_text, resource_report, summarize, validation_counts_text


class ReportingContracts(unittest.TestCase):
    def test_failed_invocation_text_redacts_local_profile_prefixes(self):
        with tempfile.TemporaryDirectory() as directory:
            text=invocation_text(Path(directory),{'status':'failed','stages':[],
                'error_type':'OSError','error':r'cannot read C:\Users\Researcher\study\file.json'})
            self.assertNotIn(r'C:\Users\Researcher',text)
            self.assertIn('<USER_PROFILE>',text)
            self.assertIn('did not complete',text)

    def test_pilot_and_validation_do_not_claim_full_analysis(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            pilot=invocation_text(root,{'status':'completed_pilot','mode':'pilot','stages':[]})
            self.assertIn('not executed by this pilot',pilot)
            self.assertNotIn('25-test',pilot)
            validation=invocation_text(root,{'status':'completed_validation','mode':'validation',
                'validation':{'success':True,'tests_run':73,'failures':0,'errors':0,'skipped':1}})
            self.assertIn('73 tests collected, 72 executed, 1 skipped',validation)
            self.assertIn('did not download data',validation)

    def test_summary_and_invocation_report_platform_skips_separately(self):
        for skipped,executed in ((6,129),(9,126)):
            with self.subTest(skipped=skipped),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);(root/'docs').mkdir();(root/'results/reports').mkdir(parents=True)
                record={'success':True,'tests_run':135,'failures':0,'errors':0,'skipped':skipped}
                summary={'workbook_animal_rows':0,'principal_run_count':0,
                         'principal_specimen_count':0,'sequencing_category_counts':{}}
                (root/'results/reports/sample_audit_summary.json').write_text(json.dumps(summary))
                (root/'results/reports/validation_summary.json').write_text(json.dumps(record))
                # Empty synthetic scientific tables isolate the generated validation prose.
                with patch('pisa.reporting.read_csv',return_value=[]):
                    summarize(root,{})
                expected=f'135 tests collected, {executed} executed, {skipped} skipped, 0 failures and 0 errors'
                self.assertIn(expected,(root/'docs/results.md').read_text())
                current=invocation_text(root,{'status':'completed_validation','validation':record})
                self.assertIn('Validation (executed in this invocation): '+expected,current)
                cached=invocation_text(root,{'status':'completed_restricted_analysis',
                    'stages':[{'name':'09_robustness_checks','status':'resumed_verified','result':record}]})
                self.assertIn('Validation (verified cached stage result): '+expected,cached)
                self.assertNotIn('135 executed',current)
                self.assertNotIn(f'{executed} passed',current)

    def test_failed_zero_and_all_skipped_validation_counts_do_not_claim_success(self):
        cases=[
            ({'success':False,'tests_run':135,'skipped':6,'failures':2,'errors':1},
             '135 tests collected, 129 executed, 6 skipped, 2 failures and 1 errors'),
            ({'success':False,'tests_run':0,'skipped':0,'failures':0,'errors':0},
             '0 tests collected, 0 executed, 0 skipped, 0 failures and 0 errors'),
            ({'success':True,'tests_run':3,'skipped':3,'failures':0,'errors':0},
             '3 tests collected, 0 executed, 3 skipped, 0 failures and 0 errors'),
            ({'success':True,'tests_run':3,'skipped':0,'failures':1,'errors':0},
             '3 tests collected, 3 executed, 0 skipped, 1 failures and 0 errors'),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            for record,expected in cases:
                with self.subTest(record=record):
                    text=invocation_text(Path(tmp),{'status':'failed','validation':record})
                    self.assertIn(expected,text)
                    self.assertIn('No successful validation result is established',text)
                    self.assertNotIn('passed',text)

    def test_invalid_counts_cannot_generate_negative_executed_tests(self):
        for record in ({'tests_run':2,'skipped':3},{'tests_run':-1},
                       {'tests_run':True},{'tests_run':'135'}):
            with self.subTest(record=record),self.assertRaises(ValueError):
                validation_counts_text(record)

    def test_local_platform_and_scientific_artifact_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'docs').mkdir(); (root/'data/manifests').mkdir(parents=True)
            scientific=root/'docs/results.md'; scientific.write_bytes(b'scientific\r\ncontent')
            (root/'data/manifests/environment_local.json').write_text(json.dumps({'platform':'Linux test host','python':'Python synthetic','packages':{}}))
            resource_report(root,{'max_measured_stage_peak_rss_bytes':123},
                invocation={'invocation_id':'fixture','status':'completed_pilot','mode':'pilot','stages':[]})
            self.assertEqual(scientific.read_bytes(),b'scientific\r\ncontent')
            text=(root/'docs/resource_usage.md').read_text()
            self.assertIn('Linux test host',text)
            self.assertNotIn('Windows 11',text)
            self.assertNotIn('25-test',text)
            self.assertNotIn('scientific\ncontent',(root/'results/reports/final_assessment.md').read_text())

    def test_visual_review_requires_matching_file_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'data/manifests').mkdir(parents=True); (root/'figures').mkdir()
            pdf=root/'figures/artificial.pdf'; pdf.write_bytes(b'not a biological figure; software hash fixture')
            record={'schema_version':1,'reviewed_utc':'fixture','figures':[{'path':'figures/artificial.pdf',
                'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'visual_status':'passed'}]}
            (root/'data/manifests/figure_qa.json').write_text(json.dumps(record))
            self.assertEqual(figure_qa_status(root)['status'],'prior_visual_review_matches_current_files')
            pdf.write_bytes(b'changed')
            self.assertEqual(figure_qa_status(root)['status'],'unverified')


if __name__=='__main__': unittest.main()
