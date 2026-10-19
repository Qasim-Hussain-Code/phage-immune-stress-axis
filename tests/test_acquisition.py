import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from pisa.acquisition import fetch,normalize_zenodo
from pisa.io import digest
from pisa.pipeline import fingerprint


class DummyGuard:
    def check(self,additional=0):
        if additional>100:raise RuntimeError('size cap')
        return {}


class AcquisitionContracts(unittest.TestCase):
    def test_catalog_excludes_usage_stats(self):
        record={'id':1,'metadata':{'title':'Example','license':{'id':'cc-by-4.0'}},
                'files':[{'key':'x.pdf','size':3,'checksum':'md5:test'}],'stats':{'views':1}}
        a=normalize_zenodo(json.dumps(record).encode());record['stats']['views']=400
        self.assertEqual(a,normalize_zenodo(json.dumps(record).encode()))
    def test_offline_missing_and_corrupt_inputs_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data/manifests').mkdir(parents=True)
            record={'path':'missing','url':'https://example.org/frozen','sha256':'invalid','max_bytes':10}
            (root/'data/manifests/inputs.json').write_text(json.dumps([record]))
            config={'resources':{'max_download_bytes':100}}
            with self.assertRaisesRegex(FileNotFoundError,'Offline input missing'):fetch(root,config,DummyGuard(),True)
            (root/'missing').write_text('altered')
            with self.assertRaisesRegex(ValueError,'Checksum mismatch'):fetch(root,config,DummyGuard(),True)
    def test_streaming_cap_is_enforced_and_partial_removed(self):
        class Response(io.BytesIO):
            headers={}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data/manifests').mkdir(parents=True)
            record={'path':'file','url':'https://example.org/frozen','sha256':'invalid','max_bytes':10}
            (root/'data/manifests/inputs.json').write_text(json.dumps([record]))
            with patch('urllib.request.urlopen',return_value=Response(b'x'*11)):
                with self.assertRaisesRegex(ValueError,'size limit'):fetch(root,{'resources':{'max_download_bytes':100}},DummyGuard())
            self.assertFalse((root/'file.part').exists())
            self.assertFalse((root/'file').exists())
    def test_fingerprint_detects_input_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data/manifests').mkdir(parents=True)
            p=root/'input';p.write_text('original')
            config=root/'config.yaml';config.write_text('seed: 1')
            (root/'data/manifests/inputs.json').write_text(json.dumps([{'path':'input'}]))
            a=fingerprint(root,config);p.write_text('changed')
            self.assertNotEqual(a,fingerprint(root,config))
