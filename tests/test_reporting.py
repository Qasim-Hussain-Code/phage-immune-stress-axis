"""Reports must not convert past runs into claims about the current run."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from pisa.reporting import figure_qa_status, invocation_text, resource_report


class ReportingContracts(unittest.TestCase):
    def test_pilot_and_validation_do_not_claim_full_analysis(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            pilot=invocation_text(root,{'status':'completed_pilot','mode':'pilot','stages':[]})
            self.assertIn('not executed by this pilot',pilot)
            self.assertNotIn('25-test',pilot)
            validation=invocation_text(root,{'status':'completed_validation','mode':'validation',
                'validation':{'success':True,'tests_run':73,'failures':0,'errors':0,'skipped':1}})
            self.assertIn('73 tests',validation)
            self.assertIn('did not download data',validation)

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
