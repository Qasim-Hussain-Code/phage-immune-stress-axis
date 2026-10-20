import copy
from pathlib import Path
import tempfile
import unittest
import yaml
from pisa.pipeline import load_config


class ResourcePolicyConfiguration(unittest.TestCase):
    def test_hardware_policy_cannot_be_silently_weakened(self):
        root=Path(__file__).resolve().parents[1]
        base=yaml.safe_load((root/'config/analysis.yaml').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'configuration.yaml'
            for key,value in [('max_workers',5),('max_workers',True),
                              ('max_new_storage_bytes',10_000_000_001),
                              ('disk_reserve_bytes',3_999_999_999),('max_download_bytes',0),
                              ('max_aggregate_rss_bytes',False),('stage_timeout_seconds',0),
                              ('max_process_rss_bytes',8_000_000_001),
                              ('max_aggregate_rss_bytes',8_000_000_001)]:
                config=copy.deepcopy(base);config['resources'][key]=value
                path.write_text(yaml.safe_dump(config))
                with self.subTest(key=key,value=value),self.assertRaises(ValueError):load_config(path)
            path.write_text(yaml.safe_dump(base))
            self.assertEqual(load_config(path)['resources']['max_workers'],4)
