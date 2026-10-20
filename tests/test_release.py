"""A staged release must contain the observations and code actually verified."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('release_checker',ROOT/'scripts/check_release.py')
release=importlib.util.module_from_spec(spec);spec.loader.exec_module(release)


class ReleasePayload(unittest.TestCase):
    def test_stale_staged_code_and_missing_new_code_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            def git(*args):
                return subprocess.run(['git','-c',f'safe.directory={root.as_posix()}',*args],
                    cwd=root,capture_output=True,check=True)
            git('init','--quiet')
            (root/'src').mkdir();path=root/'src/model.py'
            path.write_bytes(b'value=1\n');git('add','src/model.py')
            self.assertEqual(release.verify_payload_consistency(root,'index'),1)
            path.write_bytes(b'value=1\r\n')
            self.assertEqual(release.verify_payload_consistency(root,'index'),1)
            path.write_bytes(b'value=2\n')
            with self.assertRaisesRegex(ValueError,'differs from tested'):
                release.verify_payload_consistency(root,'index')
            path.write_bytes(b'value=1\n');(root/'src/new.py').write_text('new=True\n')
            with self.assertRaisesRegex(ValueError,'inventory differs'):
                release.verify_payload_consistency(root,'index')

    def test_upstream_bytes_are_never_text_normalized(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            prefix=['git','-c',f'safe.directory={root.as_posix()}']
            subprocess.run(prefix+['init','--quiet'],cwd=root,check=True,capture_output=True)
            (root/'data/raw').mkdir(parents=True)
            path=root/'data/raw/upstream.txt';path.write_bytes(b'original\n')
            subprocess.run(prefix+['add','data/raw/upstream.txt'],cwd=root,check=True,capture_output=True)
            path.write_bytes(b'original\r\n')
            with self.assertRaisesRegex(ValueError,'differs from tested'):
                release.verify_payload_consistency(root,'index')


class LatestInvocationProof(unittest.TestCase):
    @staticmethod
    def record(identifier='current',started='2026-10-20T06:00:00+00:00',status='completed_restricted_analysis'):
        return {'invocation_id':identifier,'started_utc':started,'status':status,
                'mode':'full','stages':[],'synthetic_fixture':True}

    @staticmethod
    def save(root,record,latest=False,name=None):
        directory=root/'results/reports/invocations'
        directory.mkdir(parents=True,exist_ok=True)
        (directory/(name or record['invocation_id']+'.json')).write_text(json.dumps(record),encoding='utf-8')
        if latest:
            (root/'results/reports/run_status.json').write_text(json.dumps(record),encoding='utf-8')

    def test_old_completed_record_rejected_after_newer_failed_or_successful_attempt(self):
        for outcome in ('failed','interrupted','running','completed_restricted_analysis'):
            with self.subTest(outcome=outcome),tempfile.TemporaryDirectory() as directory:
                root=Path(directory)
                self.save(root,self.record('old'),latest=True)
                self.save(root,self.record('new','2026-10-20T06:00:01+00:00',outcome))
                with self.assertRaisesRegex(ValueError,'proof stale'):
                    release.verify_latest_invocation(root)

    def test_latest_success_matches_counterpart_and_follows_older_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            self.save(root,self.record('old','2026-10-20T05:00:00+00:00','failed'))
            current=self.record('current','2026-10-20T14:00:01+08:00')
            self.save(root,current,latest=True)
            self.assertEqual(release.verify_latest_invocation(root),current)

    def test_matching_id_but_different_record_body_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            current=self.record()
            self.save(root,current,latest=True)
            changed=dict(current,stages=[{'synthetic':'different body'}])
            self.save(root,changed)
            with self.assertRaisesRegex(ValueError,'differs from its'):
                release.verify_latest_invocation(root)

    def test_missing_counterpart_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            self.save(root,self.record(),latest=True)
            (root/'results/reports/invocations/current.json').unlink()
            with self.assertRaisesRegex(ValueError,'no per-invocation counterpart'):
                release.verify_latest_invocation(root)

    def test_unsafe_ids_and_naive_or_invalid_start_times_are_rejected(self):
        invalid=[dict(self.record(),invocation_id=value) for value in
                 ['../outside','a/b','a\\b','C:drive','with space','',None]]
        invalid += [dict(self.record(),started_utc=value) for value in
                    ['2026-10-20T06:00:00','not a timestamp','2026-13-01T00:00:00+00:00',None]]
        for record in invalid:
            with self.subTest(record=record),tempfile.TemporaryDirectory() as directory:
                root=Path(directory)
                self.save(root,self.record(),latest=True)
                (root/'results/reports/run_status.json').write_text(json.dumps(record),encoding='utf-8')
                with self.assertRaises(ValueError):
                    release.verify_latest_invocation(root)

    def test_malformed_older_record_is_not_silently_ignored(self):
        for payload in ('{','[]','null','{"invocation_id":"old"}'):
            with self.subTest(payload=payload),tempfile.TemporaryDirectory() as directory:
                root=Path(directory)
                self.save(root,self.record(),latest=True)
                (root/'results/reports/invocations/old.json').write_text(payload,encoding='utf-8')
                with self.assertRaises(ValueError):
                    release.verify_latest_invocation(root)

    def test_filename_identity_and_simultaneous_attempts_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            self.save(root,self.record(),latest=True)
            self.save(root,self.record('other','2026-10-20T05:00:00+00:00'),name='wrong_name.json')
            with self.assertRaisesRegex(ValueError,'filename and record ID'):
                release.verify_latest_invocation(root)
            (root/'results/reports/invocations/wrong_name.json').unlink()
            self.save(root,self.record('simultaneous'))
            with self.assertRaisesRegex(ValueError,'proof stale'):
                release.verify_latest_invocation(root)
