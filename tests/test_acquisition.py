import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from pisa.acquisition import fetch,normalize_zenodo,verify_cached_inputs,load_manifest,verify_input_file
from pisa.io import digest
from pisa.pipeline import fingerprint


class DummyGuard:
    def __init__(self,max_additional=100):
        self.max_additional=max_additional
    def check(self,additional=0):
        if additional>self.max_additional:raise RuntimeError('size cap')
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
            record={'path':'missing','url':'https://example.org/frozen','sha256':'0'*64,'max_bytes':10,'bytes':7}
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
            record={'path':'file','url':'https://example.org/frozen','sha256':'0'*64,'max_bytes':10,'bytes':10}
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
            base={'path':'safe','url':'https://example.org/safe','sha256':'0'*64,'max_bytes':100,'bytes':0}
            for change in [{'path':'../outside'},{'max_bytes':0},{'max_bytes':-1},
                           {'sha256':'invalid'},{'url':'https://user:password@example.org/source'},
                           {'transformation':'unrecognized'}]:
                (root/'data/manifests/inputs.json').write_text(json.dumps([{**base,**change}]))
                with self.subTest(change=change),self.assertRaises(ValueError):
                    load_manifest(root,{'resources':{'max_download_bytes':100}})

    def test_input_byte_size_schema_rejects_invalid_and_missing_sizes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data/manifests').mkdir(parents=True)
            base={'path':'source','url':'https://example.org/source','sha256':'0'*64,
                  'max_bytes':100,'bytes':1}
            variants=[{**base,'bytes':value} for value in (-1,True,False,'1',1.0,None)]
            variants.append({key:value for key,value in base.items() if key!='bytes'})
            with patch('urllib.request.urlopen',side_effect=AssertionError('must not download')) as download:
                for entry in variants:
                    (root/'data/manifests/inputs.json').write_text(json.dumps([entry]))
                    with self.subTest(entry=entry),self.assertRaises(ValueError):
                        load_manifest(root)
                    with self.subTest(verifier_entry=entry),self.assertRaises(ValueError):
                        verify_input_file(root/'source',entry)
                download.assert_not_called()
            self.assertFalse((root/'source').exists())

    def test_zero_byte_input_is_valid_for_cache_and_offline_fetch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data/manifests').mkdir(parents=True)
            source=root/'empty';source.write_bytes(b'')
            entry={'path':'empty','url':'https://example.org/empty','sha256':digest(source),
                   'max_bytes':100,'bytes':0}
            (root/'data/manifests/inputs.json').write_text(json.dumps([entry]))
            config={'resources':{'max_download_bytes':100}}
            self.assertEqual(load_manifest(root)[0]['bytes'],0)
            verify_input_file(source,entry)
            self.assertEqual(verify_cached_inputs(root,config,DummyGuard())['verified_inputs'],1)
            with patch('urllib.request.urlopen',side_effect=AssertionError('must not download')) as download, \
                    patch('pisa.acquisition.extract_metadata',return_value=0):
                self.assertEqual(fetch(root,config,DummyGuard(),offline=True)['verified_inputs'],1)
                download.assert_not_called()
            self.assertEqual(source.read_bytes(),b'')

    def test_correct_hash_does_not_override_wrong_cached_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data/manifests').mkdir(parents=True)
            source=root/'source';source.write_bytes(b'original')
            entry={'path':'source','url':'https://example.org/source','sha256':digest(source),
                   'max_bytes':100,'bytes':source.stat().st_size+1}
            (root/'data/manifests/inputs.json').write_text(json.dumps([entry]))
            config={'resources':{'max_download_bytes':100}}
            before={p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}
            with patch('urllib.request.urlopen',side_effect=AssertionError('must not download')) as download, \
                    patch('pisa.acquisition.extract_metadata',side_effect=AssertionError('must not extract')):
                calls=[('file',lambda:verify_input_file(source,entry)),
                       ('cache',lambda:verify_cached_inputs(root,config,DummyGuard())),
                       ('fetch',lambda:fetch(root,config,DummyGuard(),offline=True))]
                for name,call in calls:
                    with self.subTest(path=name),self.assertRaisesRegex(ValueError,'^Frozen input size mismatch: source$'):
                        call()
                download.assert_not_called()
            after={p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before,after)

    def test_download_with_correct_hash_and_wrong_size_is_not_promoted(self):
        class Response(io.BytesIO):
            headers={}
        payload=b'original'
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data/manifests').mkdir(parents=True)
            entry={'path':'source','url':'https://example.org/source',
                   'sha256':hashlib.sha256(payload).hexdigest(),'max_bytes':100,'bytes':len(payload)+1}
            (root/'data/manifests/inputs.json').write_text(json.dumps([entry]))
            with patch('urllib.request.urlopen',return_value=Response(payload)), \
                    patch('pisa.acquisition.extract_metadata',side_effect=AssertionError('must not extract')):
                with self.assertRaisesRegex(ValueError,'^Frozen input size mismatch: source$'):
                    fetch(root,{'resources':{'max_download_bytes':100}},DummyGuard())
            self.assertFalse((root/'source').exists())
            self.assertFalse((root/'source.part').exists())
            self.assertFalse((root/'results/tables/input_integrity.csv').exists())

    def test_zenodo_download_verifies_canonical_stored_size(self):
        class Response(io.BytesIO):
            headers={}
        record={'id':1,'metadata':{'title':'Example','license':{'id':'cc-by-4.0'}},
                'files':[{'key':'x.pdf','size':3,'checksum':'md5:test'}],
                'stats':{'views':1},'description':'ignored metadata '*30}
        payload=json.dumps(record).encode('utf-8')
        canonical=normalize_zenodo(payload)
        self.assertNotEqual(len(payload),len(canonical))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data/manifests').mkdir(parents=True)
            entry={'path':'catalog.json','url':'https://example.org/record','transformation':'zenodo_catalog',
                   'sha256':hashlib.sha256(canonical).hexdigest(),'max_bytes':4096,'bytes':len(canonical)}
            (root/'data/manifests/inputs.json').write_text(json.dumps([entry]))
            with patch('urllib.request.urlopen',return_value=Response(payload)), \
                    patch('pisa.acquisition.extract_metadata',return_value=0):
                result=fetch(root,{'resources':{'max_download_bytes':4096}},DummyGuard(4096))
            self.assertEqual(result['verified_inputs'],1)
            self.assertEqual((root/'catalog.json').read_bytes(),canonical)
            self.assertFalse((root/'catalog.json.part').exists())

    def test_zenodo_download_rejects_wrong_canonical_size(self):
        class Response(io.BytesIO):
            headers={}
        record={'id':1,'metadata':{'title':'Example','license':{'id':'cc-by-4.0'}},
                'files':[{'key':'x.pdf','size':3,'checksum':'md5:test'}],
                'stats':{'views':1},'description':'ignored metadata '*30}
        payload=json.dumps(record).encode('utf-8')
        canonical=normalize_zenodo(payload)
        self.assertNotEqual(len(payload),len(canonical))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data/manifests').mkdir(parents=True)
            entry={'path':'catalog.json','url':'https://example.org/record','transformation':'zenodo_catalog',
                   'sha256':hashlib.sha256(canonical).hexdigest(),'max_bytes':4096,'bytes':len(payload)}
            (root/'data/manifests/inputs.json').write_text(json.dumps([entry]))
            with patch('urllib.request.urlopen',return_value=Response(payload)), \
                    patch('pisa.acquisition.extract_metadata',side_effect=AssertionError('must not extract')):
                with self.assertRaisesRegex(ValueError,'^Frozen input size mismatch: catalog\\.json$'):
                    fetch(root,{'resources':{'max_download_bytes':4096}},DummyGuard(4096))
            self.assertFalse((root/'catalog.json').exists())
            self.assertFalse((root/'catalog.json.part').exists())
            self.assertFalse((root/'results/tables/input_integrity.csv').exists())
