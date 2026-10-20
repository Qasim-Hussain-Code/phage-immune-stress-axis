"""Interrupted JSON publication must not truncate the prior record."""
import json
import math
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from pisa.io import write_json


class AtomicJSON(unittest.TestCase):
    def test_native_serialization_is_preserved_and_temporary_is_removed(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'record.json'
            value={'label':'immune outcome','values':[1,None,True]}
            write_json(path,value)
            expected=(json.dumps(value,indent=2,allow_nan=False)+'\n').replace('\n',os.linesep).encode('utf-8')
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
