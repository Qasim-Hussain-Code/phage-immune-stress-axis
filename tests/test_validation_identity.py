"""A changing test/source tree cannot receive a successful validation attestation."""
import contextlib
import io
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch


class ValidationIdentity(unittest.TestCase):
    def test_source_edit_during_suite_fails_and_retains_both_identities(self):
        script=Path(__file__).resolve().parents[1]/'scripts/validate.py'
        original_directory=Path.cwd();original_path=list(sys.path)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);copy=root/'scripts/validate.py';copy.parent.mkdir()
            copy.write_bytes(script.read_bytes())
            source=root/'src/fixture.py';source.parent.mkdir();source.write_text('before')
            suite=unittest.TestSuite([unittest.FunctionTestCase(lambda:source.write_text('after'))])
            try:
                with patch.dict(os.environ),patch.object(tempfile,'tempdir',tempfile.tempdir), \
                     patch.object(unittest.defaultTestLoader,'discover',return_value=suite), \
                     contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as stopped:
                        runpy.run_path(str(copy),run_name='__main__')
                self.assertEqual(stopped.exception.code,1)
                record=json.loads((root/'results/reports/validation_summary.json').read_text())
                self.assertFalse(record['success'])
                self.assertFalse(record['source_unchanged_during_validation'])
                self.assertNotEqual(record['code_sha256'],record['code_sha256_after'])
                self.assertEqual(record['tests_run'],1)
                self.assertEqual(record['failures'],0)
            finally:
                os.chdir(original_directory);sys.path[:]=original_path
