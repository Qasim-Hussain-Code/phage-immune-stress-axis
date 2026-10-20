import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from pisa.acquisition import fetch,normalize_zenodo,verify_cached_inputs,load_manifest
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
            record={'path':'missing','url':'https://example.org/frozen','sha256':'0'*64,'max_bytes':10}
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
            record={'path':'file','url':'https://example.org/frozen','sha256':'0'*64,'max_bytes':10}
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

    def test_validation_does_not_write_or_extract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data/manifests').mkdir(parents=True)
            path=root/'source';path.write_bytes(b'original')
            entry={'path':'source','url':'https://example.org/source','sha256':digest(path),
                   'max_bytes':100,'bytes':path.stat().st_size}
            (root/'data/manifests/inputs.json').write_text(json.dumps([entry]))
            before={p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}
            with patch('pisa.acquisition.extract_metadata',side_effect=AssertionError('must not extract')):
                result=verify_cached_inputs(root,{'resources':{'max_download_bytes':100}},DummyGuard())
            after={p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before,after)
            self.assertEqual(result['scientific_files_written'],0)

    def test_malformed_manifest_fails_before_download(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data/manifests').mkdir(parents=True)
            base={'path':'safe','url':'https://example.org/safe','sha256':'0'*64,'max_bytes':100}
            for change in [{'path':'../outside'},{'max_bytes':0},{'max_bytes':-1},
                           {'sha256':'invalid'},{'url':'https://user:password@example.org/source'},
                           {'transformation':'unrecognized'}]:
                (root/'data/manifests/inputs.json').write_text(json.dumps([{**base,**change}]))
                with self.subTest(change=change),self.assertRaises(ValueError):
                    load_manifest(root,{'resources':{'max_download_bytes':100}})
