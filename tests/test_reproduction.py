"""Archive safety/comparison fixtures; never execute the biological pipeline."""
import hashlib
import io
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import Mock
from pisa.reproduction import contained_path, compare_scientific, scientific_paths, safe_extract, remove_disposable, record_resource_snapshot


class DummyGuard:
    def check(self,additional=0): return {}
    def observe_processes(self): return {}


class ReproductionContracts(unittest.TestCase):
    def test_cleanup_cannot_hide_detected_resource_failure(self):
        report={'status':'passed'}
        guard=Mock(); guard.snapshot.side_effect=[RuntimeError('budget exceeded'),{'project_bytes':1}]
        record_resource_snapshot(report,guard,'before_cleanup','before_error')
        self.assertEqual(report['status'],'failed')
        record_resource_snapshot(report,guard,'after_cleanup','after_error')
        self.assertEqual(report['status'],'failed')
        self.assertIn('budget exceeded',report['before_error'])

    def test_path_containment_rejects_other_shell_and_os_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.assertEqual(contained_path(root,'src/pisa/example.py'),root/'src/pisa/example.py')
            for name in ['../outside','/absolute','C:/outside','a\\..\\outside','a:stream','.', '']:
                with self.subTest(name=name),self.assertRaises(ValueError): contained_path(root,name)

    def test_comparison_excludes_operational_records_and_detects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'results/tables').mkdir(parents=True); (root/'results/reports').mkdir()
            scientific=root/'results/tables/artificial.csv'; scientific.write_bytes(b'id,value\nfixture,1\n')
            (root/'results/tables/input_integrity.csv').write_text('operational cache state')
            (root/'results/reports/run_status.json').write_text('operational timestamp')
            self.assertEqual(scientific_paths(root),['results/tables/artificial.csv'])
            expected={'results/tables/artificial.csv':hashlib.sha256(scientific.read_bytes()).hexdigest()}
            self.assertEqual(compare_scientific(expected,root)[0]['status'],'identical')
            scientific.write_bytes(b'id,value\nfixture,2\n')
            self.assertEqual(compare_scientific(expected,root)[0]['status'],'different_bytes')

    def test_archive_rejects_traversal_and_links(self):
        for kind in ['traversal','link']:
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp); archive=root/'fixture.tar'
                with tarfile.open(archive,'w') as stream:
                    member=tarfile.TarInfo('../outside' if kind=='traversal' else 'symbolic')
                    if kind=='link': member.type=tarfile.SYMTYPE; member.linkname='../outside'
                    stream.addfile(member)
                with self.assertRaises(ValueError): safe_extract(archive,root/'checkout',1000,DummyGuard())
                self.assertFalse((root/'outside').exists())

    def test_archive_expansion_is_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); archive=root/'fixture.tar'
            with tarfile.open(archive,'w') as stream:
                member=tarfile.TarInfo('fixture.txt'); member.size=10
                stream.addfile(member,io.BytesIO(b'0123456789'))
            with self.assertRaisesRegex(ValueError,'expansion size'): safe_extract(archive,root/'checkout',9,DummyGuard())

    def test_regular_archive_extracts_exact_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); archive=root/'fixture.tar'; payload=b'software fixture\r\n'
            with tarfile.open(archive,'w') as stream:
                member=tarfile.TarInfo('nested/fixture.txt'); member.size=len(payload)
                stream.addfile(member,io.BytesIO(payload))
            result=safe_extract(archive,root/'checkout',1000,DummyGuard())
            self.assertEqual((root/'checkout/nested/fixture.txt').read_bytes(),payload)
            self.assertEqual(result['regular_file_bytes'],len(payload))

    def test_recursive_cleanup_cannot_target_workspace_or_cache_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); disposable=root/'.cache/reproduction/run_fixture'
            disposable.mkdir(parents=True); (disposable/'small.txt').write_text('fixture')
            for target in [root,root/'.cache/reproduction',root/'some_other_folder']:
                with self.assertRaises(ValueError): remove_disposable(root,target)
            remove_disposable(root,disposable)
            self.assertFalse(disposable.exists())


if __name__=='__main__': unittest.main()
