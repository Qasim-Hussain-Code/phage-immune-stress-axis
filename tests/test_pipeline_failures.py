"""Bounded main-runner failure injections, without scientific subprocesses."""
from __future__ import annotations

from contextlib import ExitStack
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from pisa import pipeline
from pisa.io import write_json as real_write_json


class RunnerFinalizationFailures(unittest.TestCase):
    def invoke(self, root, guard_checks, analysis_error=None, report_error=None, write_hook=None):
        guard=Mock()
        guard.check.side_effect=guard_checks
        guard.max_observed_native_process_peak_rss_bytes=2
        config={'seed':1,'resources':{'max_workers':4}}
        with ExitStack() as stack:
            stack.enter_context(patch.object(pipeline,'__file__',str(root/'src/pisa/pipeline.py')))
            stack.enter_context(patch('sys.argv',['run_all.py','--validate-only','--offline']))
            stack.enter_context(patch.object(pipeline,'runtime_identity',return_value={'synthetic':'runtime'}))
            stack.enter_context(patch.object(pipeline,'peak_rss',return_value=1))
            stack.enter_context(patch.object(pipeline,'configure_environment'))
            stack.enter_context(patch.object(pipeline,'load_config',return_value=config))
            stack.enter_context(patch.object(pipeline,'Guard',return_value=guard))
            stack.enter_context(patch.object(pipeline.runpy,'run_path',return_value={'probe':lambda path:{}}))
            stack.enter_context(patch.object(pipeline,'validate_only',
                side_effect=analysis_error,return_value={'validation':{'success':True,'tests_run':1}}))
            stack.enter_context(patch('pisa.reporting.resource_report',side_effect=report_error))
            if write_hook is not None:
                stack.enter_context(patch.object(pipeline,'write_json',side_effect=write_hook))
            pipeline.main()

    @staticmethod
    def saved_status(root):
        return json.loads((root/'results/reports/run_status.json').read_text(encoding='utf-8'))

    def test_final_resource_failure_cannot_preserve_completed_status(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with self.assertRaisesRegex(RuntimeError,'late resource breach'):
                self.invoke(root,[{'process_peak_rss_bytes':2},RuntimeError('late resource breach')])
            status=self.saved_status(root)
            self.assertEqual(status['status'],'failed')
            self.assertEqual(status['failed_stage'],'finalization')
            self.assertEqual(status['error'],'late resource breach')
            self.assertEqual(status['finalization_errors'][0]['phase'],'final_resource_snapshot')
            resource=json.loads((root/'results/reports/resource_usage.json').read_text())
            self.assertEqual(resource['snapshot_error'],'late resource breach')

    def test_original_failure_survives_secondary_resource_and_reporting_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with self.assertRaisesRegex(ValueError,'original analysis failure'):
                self.invoke(root,[RuntimeError('secondary resource error')],
                    analysis_error=ValueError('original analysis failure'),
                    report_error=OSError('secondary report error'))
            status=self.saved_status(root)
            self.assertEqual(status['status'],'failed')
            self.assertEqual(status['error_type'],'ValueError')
            self.assertEqual(status['error'],'original analysis failure')
            self.assertEqual({row['phase'] for row in status['finalization_errors']},
                             {'final_resource_snapshot','resource_report'})

    def test_interruption_survives_secondary_finalization_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with self.assertRaises(KeyboardInterrupt):
                self.invoke(root,[RuntimeError('secondary resource error')],
                    analysis_error=KeyboardInterrupt(),report_error=OSError('report error'))
            status=self.saved_status(root)
            self.assertEqual(status['status'],'interrupted')
            self.assertEqual(status['error_type'],'KeyboardInterrupt')

    def test_new_reporting_failure_fails_previously_completed_analysis(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with self.assertRaisesRegex(OSError,'final reporting failure'):
                self.invoke(root,[{},{}],report_error=OSError('final reporting failure'))
            status=self.saved_status(root)
            self.assertEqual(status['status'],'failed')
            self.assertEqual(status['error'],'final reporting failure')
            self.assertEqual(status['report_error'],'final reporting failure')

    def test_resource_record_write_failure_is_terminal_and_recorded(self):
        def writes(path,value):
            if Path(path).name=='resource_usage.json':
                raise OSError('resource record unavailable')
            return real_write_json(path,value)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with self.assertRaisesRegex(OSError,'resource record unavailable'):
                self.invoke(root,[{},{}],write_hook=writes)
            status=self.saved_status(root)
            self.assertEqual(status['status'],'failed')
            self.assertIn('resource_usage_write',{row['phase'] for row in status['finalization_errors']})

    def test_status_path_failure_still_records_failed_invocation(self):
        def writes(path,value):
            if Path(path).name=='run_status.json':
                raise OSError('latest status path unavailable')
            return real_write_json(path,value)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with self.assertRaisesRegex(OSError,'latest status path unavailable'):
                self.invoke(root,[],write_hook=writes)
            records=list((root/'results/reports/invocations').glob('*.json'))
            self.assertEqual(len(records),1)
            status=json.loads(records[0].read_text())
            self.assertEqual(status['status'],'failed')
            self.assertEqual(status['error_type'],'OSError')
            self.assertEqual(status['error'],'latest status path unavailable')


if __name__=='__main__':
    unittest.main()
