"""Interrupted JSON publication must not truncate the prior record."""
import json
import math
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import call,patch
from pisa.io import write_json,_windows_replacement_conflict


def replacement_error(code=None):
    error=PermissionError(13,'synthetic replacement conflict')
    if code is not None:error.winerror=code
    return error


class AtomicJSON(unittest.TestCase):
    def test_lf_serialization_is_preserved_and_temporary_is_removed(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'record.json'
            value={'label':'immune outcome','values':[1,None,True]}
            write_json(path,value)
            expected=(json.dumps(value,indent=2,allow_nan=False)+'\n').encode('utf-8')
            self.assertEqual(path.read_bytes(),expected)
            self.assertEqual(json.loads(path.read_text()),value)
            self.assertEqual(list(Path(directory).glob('.pisa-*.tmp')),[])

    def test_failed_replace_preserves_existing_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'record.json';path.write_bytes(b'previous exact bytes')
            with patch('pisa.io.os.replace',side_effect=OSError('injected replace failure')):
                with self.assertRaisesRegex(OSError,'replace failure'):write_json(path,{'new':True})
            self.assertEqual(path.read_bytes(),b'previous exact bytes')
            self.assertEqual(list(Path(directory).glob('.pisa-*.tmp')),[])

    def test_serialization_failure_never_opens_or_truncates_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'record.json';path.write_bytes(b'original')
            with self.assertRaises(ValueError):write_json(path,{'invalid':math.nan})
            self.assertEqual(path.read_bytes(),b'original')
            self.assertEqual(list(Path(directory).glob('.pisa-*.tmp')),[])

    def test_transient_windows_conflicts_retry_then_publish_with_real_replace(self):
        real_replace=os.replace
        for code in (5,32,33):
            with self.subTest(winerror=code),tempfile.TemporaryDirectory() as directory:
                path=Path(directory)/'record.json';path.write_bytes(b'previous exact bytes')
                attempts=[]
                def transient(source,destination):
                    attempts.append(source)
                    self.assertEqual(json.loads(Path(source).read_text()),{'new':True})
                    if len(attempts)<=2:
                        self.assertEqual(path.read_bytes(),b'previous exact bytes')
                        raise replacement_error(code)
                    return real_replace(source,destination)
                with patch('pisa.io.sys.platform','win32'), \
                     patch('pisa.io.os.replace',side_effect=transient) as replace, \
                     patch('pisa.io.time.sleep') as sleep:
                    write_json(path,{'new':True})
                self.assertEqual(replace.call_count,3)
                self.assertEqual(sleep.call_args_list,[call(0.02),call(0.04)])
                self.assertEqual(len(set(attempts)),1,'Retries must use the same fully written temporary')
                self.assertEqual(json.loads(path.read_text()),{'new':True})
                self.assertEqual(list(Path(directory).glob('.pisa-*.tmp')),[])

    def test_persistent_known_windows_conflict_is_bounded_and_preserves_old_bytes(self):
        for code in (5,32,33):
            with self.subTest(winerror=code),tempfile.TemporaryDirectory() as directory:
                path=Path(directory)/'record.json';path.write_bytes(b'previous exact bytes')
                error=replacement_error(code)
                with patch('pisa.io.sys.platform','win32'), \
                     patch('pisa.io.os.replace',side_effect=error) as replace, \
                     patch('pisa.io.time.sleep') as sleep:
                    with self.assertRaises(PermissionError) as caught:write_json(path,{'new':True})
                self.assertIs(caught.exception,error)
                self.assertEqual(replace.call_count,6)
                self.assertEqual(sleep.call_args_list,[call(value) for value in (0.02,0.04,0.08,0.16,0.32)])
                self.assertAlmostEqual(sum(item.args[0] for item in sleep.call_args_list),0.62)
                self.assertEqual(path.read_bytes(),b'previous exact bytes')
                self.assertEqual(list(Path(directory).glob('.pisa-*.tmp')),[])

    def test_ordinary_permission_nonwindows_and_other_oserrors_are_not_retried(self):
        for platform,error in [('win32',replacement_error()),('win32',replacement_error(13)),
                ('linux',replacement_error(32)),('win32',OSError('unrelated IO failure'))]:
            with self.subTest(platform=platform,error=repr(error)),tempfile.TemporaryDirectory() as directory:
                path=Path(directory)/'record.json';path.write_bytes(b'original')
                with patch('pisa.io.sys.platform',platform), \
                     patch('pisa.io.os.replace',side_effect=error) as replace, \
                     patch('pisa.io.time.sleep') as sleep:
                    with self.assertRaises(OSError) as caught:write_json(path,{'new':True})
                self.assertIs(caught.exception,error)
                replace.assert_called_once();sleep.assert_not_called()
                self.assertEqual(path.read_bytes(),b'original')
                self.assertEqual(list(Path(directory).glob('.pisa-*.tmp')),[])

    def test_conflict_classifier_requires_windows_permissionerror_and_known_code(self):
        with patch('pisa.io.sys.platform','win32'):
            for code in (5,32,33):self.assertTrue(_windows_replacement_conflict(replacement_error(code)))
            self.assertFalse(_windows_replacement_conflict(replacement_error(13)))
            other=OSError('not a permission error');other.winerror=5
            self.assertFalse(_windows_replacement_conflict(other))
        with patch('pisa.io.sys.platform','linux'):
            self.assertFalse(_windows_replacement_conflict(replacement_error(5)))
