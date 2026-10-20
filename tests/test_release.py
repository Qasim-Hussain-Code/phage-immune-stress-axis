"""A staged release must contain the observations and code actually verified."""
import importlib.util
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
