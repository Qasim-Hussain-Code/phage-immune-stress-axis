"""Lightweight cache/dependency contracts using artificial files only."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from pisa.io import digest
from pisa.pipeline import STAGES, DECLARED, cache_valid, fingerprint, upstream_hashes, validate_only, source_contract, require_unchanged_source


class PipelineContracts(unittest.TestCase):
    def test_execution_contract_rejects_source_config_spec_and_runtime_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            paths=[root/'src/example.py',root/'config.yaml',root/'requirements.txt',root/'data/manifests/inputs.json']
            for path in paths:path.parent.mkdir(parents=True,exist_ok=True);path.write_text('original')
            expected=source_contract(root,paths[1])
            for path in paths:
                with self.subTest(path=path.relative_to(root)):
                    path.write_text('changed')
                    with self.assertRaisesRegex(RuntimeError,'changed during execution'):
                        require_unchanged_source(root,paths[1],expected)
                    path.write_text('original')
            with patch('pisa.pipeline.runtime_identity',return_value={'different':'runtime'}):
                with self.assertRaises(RuntimeError):require_unchanged_source(root,paths[1],expected)

    def test_expected_input_materialization_does_not_change_source_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);config=root/'config.yaml';config.write_text('fixture')
            expected=source_contract(root,config)
            target=root/'data/raw/expected.txt';target.parent.mkdir(parents=True);target.write_text('frozen input')
            require_unchanged_source(root,config,expected)

    def test_output_tamper_and_exact_output_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); stage=STAGES[0]; name=DECLARED[stage][0]
            target=root/name; target.parent.mkdir(parents=True); target.write_text('original')
            record={'schema_version':2,'stage':stage,'fingerprint':'key','upstream_outputs':{},
                    'outputs':{name:digest(target)},'result':{},'resources':{'process_peak_rss_bytes':1}}
            self.assertTrue(cache_valid(root,stage,record,'key',{}))
            target.write_text('tampered')
            self.assertFalse(cache_valid(root,stage,record,'key',{}))
            target.write_text('original')
            record['outputs']['../outside']='bad'
            self.assertFalse(cache_valid(root,stage,record,'key',{}))
            record['outputs']={}
            self.assertFalse(cache_valid(root,stage,record,'key',{}))

    def test_malformed_valid_json_cache_is_invalidated_without_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); stage=STAGES[0]; name=DECLARED[stage][0]
            target=root/name; target.parent.mkdir(parents=True); target.write_text('fixture')
            valid={'schema_version':2,'stage':stage,'fingerprint':'key','upstream_outputs':{},
                   'outputs':{name:digest(target)},'result':{},'resources':{'process_peak_rss_bytes':1}}
            cases=[None,[],42,'json scalar',{},dict(valid,outputs=None),dict(valid,result=[]),
                   dict(valid,resources={}),dict(valid,resources={'process_peak_rss_bytes':True}),
                   dict(valid,upstream_outputs=[]),dict(valid,outputs={name:123})]
            for value in cases:
                with self.subTest(value=value):
                    parsed=json.loads(json.dumps(value))
                    self.assertFalse(cache_valid(root,stage,parsed,'key',{}))

    def test_upstream_changes_invalidate_downstream_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            target=root/DECLARED[STAGES[0]][0]
            target.parent.mkdir(parents=True); target.write_text('before')
            before=upstream_hashes(root,STAGES[1]); target.write_text('after')
            self.assertNotEqual(before,upstream_hashes(root,STAGES[1]))
            with self.assertRaisesRegex(FileNotFoundError,'prerequisite missing'):
                upstream_hashes(root,STAGES[2])

    def test_runtime_change_invalidates_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'data/manifests').mkdir(parents=True)
            (root/'data/manifests/inputs.json').write_text('[]')
            config=root/'config.yaml'; config.write_text('seed: 1')
            with patch('pisa.pipeline.runtime_identity',return_value={'packages':{'scipy':'old'}}):
                before=fingerprint(root,config)
            with patch('pisa.pipeline.runtime_identity',return_value={'packages':{'scipy':'new'}}):
                self.assertNotEqual(before,fingerprint(root,config))

    def test_validation_only_does_not_fetch_or_extract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); sentinel=root/'scientific.csv'; sentinel.write_bytes(b'exact\r\nbytes\r\n')
            with patch('pisa.acquisition.verify_cached_inputs',return_value={'verified_inputs':1}) as verify, \
                 patch('pisa.acquisition.fetch',side_effect=AssertionError('must not fetch')), \
                 patch('pisa.acquisition.extract_metadata',side_effect=AssertionError('must not extract')), \
                 patch('pisa.pipeline.validate',return_value={'success':True,'tests_run':7}):
                result=validate_only(root,{},object())
            verify.assert_called_once()
            self.assertEqual(sentinel.read_bytes(),b'exact\r\nbytes\r\n')
            self.assertEqual(result['validation']['tests_run'],7)


if __name__=='__main__': unittest.main()
