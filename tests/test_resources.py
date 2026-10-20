"""Resource invariants use mocked small values; no large allocation or child."""
from collections import namedtuple
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from pisa.resources import Guard, monitored_run, process_family_memory

Disk=namedtuple('Disk','total used free')
CONFIG={'resources':{'max_new_storage_bytes':10_000_000_000,'disk_reserve_bytes':4_000_000_000,
    'max_process_rss_bytes':1000,'max_aggregate_rss_bytes':1200,'min_available_memory_bytes':100}}


class ResourceContracts(unittest.TestCase):
    def test_local_baseline_ignores_historical_machine_and_does_not_reset(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'data/manifests').mkdir(parents=True)
            (root/'data/manifests/environment_initial.json').write_text(json.dumps({'storage_budget_bytes':1}))
            with patch('pisa.resources.shutil.disk_usage',return_value=Disk(50_000_000_000,0,8_000_000_000)), \
                 patch('pisa.resources.available_memory',return_value=10_000), patch('pisa.resources.peak_rss',return_value=50):
                guard=Guard(root,CONFIG)
                self.assertEqual(guard.budget,4_000_000_000)
            with patch('pisa.resources.shutil.disk_usage',return_value=Disk(50_000_000_000,0,20_000_000_000)), \
                 patch('pisa.resources.available_memory',return_value=10_000), patch('pisa.resources.peak_rss',return_value=50):
                self.assertEqual(Guard(root,CONFIG).budget,4_000_000_000)
                with self.assertRaises(ValueError): guard.check(-1)

    def test_family_sums_current_rss_not_historical_peaks(self):
        values={1:{'rss':10,'peak':100},2:{'rss':20,'peak':500},3:{'rss':30,'peak':400}}
        with patch('pisa.resources._process_parents',return_value={1:0,2:1,3:2,4:0}), \
             patch('pisa.resources._process_memory',side_effect=lambda pid:values.get(pid)):
            result=process_family_memory(1)
        self.assertEqual(result['aggregate_rss_bytes'],60)
        self.assertEqual(result['max_native_process_peak_rss_bytes'],500)
        self.assertEqual(result['processes_measured'],3)

    def test_aggregate_limit_separate_from_per_process_limit(self):
        with tempfile.TemporaryDirectory() as tmp, \
             patch('pisa.resources.shutil.disk_usage',return_value=Disk(50_000_000_000,0,8_000_000_000)), \
             patch('pisa.resources.available_memory',return_value=10_000), \
             patch('pisa.resources.peak_rss',return_value=50):
            guard=Guard(Path(tmp),CONFIG)
            with patch('pisa.resources.process_family_memory',return_value={'aggregate_rss_bytes':1300,
                 'max_native_process_peak_rss_bytes':700,'processes_unreadable_or_exited':0}):
                with self.assertRaisesRegex(RuntimeError,'Aggregate'): guard.observe_processes()

    def test_timeout_terminates_spawned_process_tree(self):
        process=Mock(); process.poll.return_value=None
        guard=Mock(); guard.config={'stage_timeout_seconds':1}
        with tempfile.TemporaryDirectory() as tmp, \
             patch('pisa.resources.start_process',return_value=process), \
             patch('pisa.resources.time.monotonic',side_effect=[0,2]), \
             patch('pisa.resources._stop_process_tree') as stop:
            with self.assertRaises(TimeoutError):
                monitored_run(['synthetic'],Path(tmp),Path(tmp)/'test.log',guard)
            stop.assert_called_once_with(process)


if __name__=='__main__': unittest.main()
