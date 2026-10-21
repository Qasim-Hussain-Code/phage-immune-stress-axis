"""Direct native-worker archive fixtures; do not invoke WSL or install anything."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('native_wsl_guest_fixture',
    Path(__file__).resolve().parents[1]/'scripts/_native_wsl_guest.py')
guest = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guest)


def tar_bytes(entries):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w') as archive:
        for name, payload, kind in entries:
            member = tarfile.TarInfo(name)
            member.type = kind
            member.size = len(payload) if kind == tarfile.REGTYPE else 0
            if kind in (tarfile.SYMTYPE, tarfile.LNKTYPE):
                member.linkname = '../outside'
            archive.addfile(member, io.BytesIO(payload) if member.isfile() else None)
    return stream.getvalue()


class NativeArchiveContracts(unittest.TestCase):
    def test_real_nonseekable_tar_stream_extracts_exact_file_bytes(self):
        payload = b'explicit synthetic stream fixture\n'*3000

        class NonSeekable(io.BytesIO):
            def seek(self, *arguments):
                raise io.UnsupportedOperation('Streaming fixture cannot seek')

            def read(self, count=-1):
                if not 0 <= count <= 1024*1024:
                    raise AssertionError('Unbounded archive read')
                return super().read(count)

        encoded = tar_bytes([('nested/fixture.bin', payload, tarfile.REGTYPE)])
        with tempfile.TemporaryDirectory() as directory, \
             tarfile.open(fileobj=NonSeekable(encoded), mode='r|') as archive:
            destination = Path(directory)
            result = guest.extract(archive, destination, len(payload), 1)
            self.assertEqual((destination/'nested/fixture.bin').read_bytes(), payload)
            self.assertEqual(result, {'members': 1, 'regular_file_bytes': len(payload)})

    def test_traversal_absolute_and_alternate_separator_paths_are_rejected(self):
        for name in ('../outside', '/absolute', 'nested/../../outside', '..\\outside'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                destination = Path(directory)/'destination'
                destination.mkdir()
                encoded = tar_bytes([(name, b'fixture', tarfile.REGTYPE)])
                with tarfile.open(fileobj=io.BytesIO(encoded), mode='r|') as archive, \
                     self.assertRaises(ValueError):
                    guest.extract(archive, destination, 100, 10)
                self.assertFalse((Path(directory)/'outside').exists())
                self.assertEqual(list(destination.iterdir()), [])
        with self.assertRaises(ValueError):
            guest.relative('contains\x00null')

    def test_links_special_files_and_duplicate_members_are_rejected(self):
        for kind in (tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.FIFOTYPE, tarfile.CHRTYPE):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                encoded = tar_bytes([('unsafe', b'', kind)])
                with tarfile.open(fileobj=io.BytesIO(encoded), mode='r|') as archive, \
                     self.assertRaisesRegex(ValueError, 'ordinary non-sparse'):
                    guest.extract(archive, Path(directory), 100, 10)
                self.assertFalse((Path(directory)/'unsafe').exists())
        encoded = tar_bytes([('same', b'first', tarfile.REGTYPE), ('same', b'second', tarfile.REGTYPE)])
        with tempfile.TemporaryDirectory() as directory, \
             tarfile.open(fileobj=io.BytesIO(encoded), mode='r|') as archive, \
             self.assertRaisesRegex(ValueError, 'Duplicate'):
            guest.extract(archive, Path(directory), 100, 10)

    def test_expanded_byte_member_and_truncated_stream_bounds(self):
        encoded = tar_bytes([('first', b'0123456789', tarfile.REGTYPE), ('second', b'x', tarfile.REGTYPE)])
        for byte_cap, member_cap, message in ((9, 10, 'expanded bytes'), (100, 1, 'member count')):
            with self.subTest(message=message), tempfile.TemporaryDirectory() as directory, \
                 tarfile.open(fileobj=io.BytesIO(encoded), mode='r|') as archive, \
                 self.assertRaisesRegex(ValueError, message):
                guest.extract(archive, Path(directory), byte_cap, member_cap)

        class TruncatedMember:
            def __iter__(self):
                member = tarfile.TarInfo('short')
                member.size = 10
                yield member

            def extractfile(self, member):
                return io.BytesIO(b'short')

        with tempfile.TemporaryDirectory() as directory, self.assertRaisesRegex(ValueError, 'Truncated'):
            guest.extract(TruncatedMember(), Path(directory), 100, 10)

    def test_verify_file_requires_exact_size_hash_and_safe_path(self):
        payload = b'synthetic verified bytes'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root/'fixture.whl'
            path.write_bytes(payload)
            record = {'path': path.name, 'bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest()}
            self.assertEqual(guest.verify_file(root, record), path)
            aliases = {'path': path.name, 'wheel_bytes': len(payload), 'wheel_sha256': record['sha256']}
            self.assertEqual(guest.verify_file(root, aliases), path)
            for changed in ({'bytes': True}, {'bytes': len(payload)+1}, {'sha256': 'A'*64}, {'path': '../outside'}):
                with self.subTest(changed=changed), self.assertRaises(ValueError):
                    guest.verify_file(root, record | changed)
            path.write_bytes(b'X'*len(payload))
            with self.assertRaisesRegex(ValueError, 'differs from verified host metadata'):
                guest.verify_file(root, record)


class NativeInputIdentity(unittest.TestCase):
    @staticmethod
    def fixture(root, first=b'x'):
        (root/'data/manifests').mkdir(parents=True)
        records=[]
        for index in range(10):
            payload=first if index==0 else f'input{index}'.encode('ascii')
            name=f'input{index}';(root/name).write_bytes(payload)
            records.append({'path':name,'url':f'https://example.org/source/{index}',
                            'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest(),
                            'max_bytes':100})
        NativeInputIdentity.save_manifest(root,records)
        return records

    @staticmethod
    def save_manifest(root,records):
        (root/'data/manifests/inputs.json').write_text(json.dumps(records),encoding='utf-8')

    def test_ten_inputs_and_zero_byte_file_keep_verified_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);records=self.fixture(root,first=b'')
            expected=[{key:entry[key] for key in ['path','bytes','sha256']} for entry in records]
            self.assertEqual(guest.snapshot_inputs(root),expected)
            self.save_manifest(root,records[:-1])
            with self.assertRaisesRegex(ValueError,'frozen ten-input manifest'):
                guest.snapshot_inputs(root)

    def test_size_is_required_and_rejects_negative_bool_string_and_float(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);records=self.fixture(root)
            variants=[dict(records[0],bytes=size) for size in [-1,True,False,'1',1.0,None]]
            variants.append({key:value for key,value in records[0].items() if key!='bytes'})
            for entry in variants:
                self.save_manifest(root,[entry,*records[1:]])
                with self.subTest(entry=entry),self.assertRaisesRegex(ValueError,'nonnegative integers'):
                    guest.snapshot_inputs(root)

    def test_correct_hash_does_not_override_wrong_size(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);records=self.fixture(root)
            records[0]['bytes']=2;self.save_manifest(root,records)
            with self.assertRaisesRegex(ValueError,'Frozen input size mismatch: input0'):
                guest.snapshot_inputs(root)

    def test_same_size_tampering_still_fails_checksum(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.fixture(root)
            (root/'input0').write_bytes(b'y')
            with self.assertRaisesRegex(ValueError,'Checksum mismatch in frozen input: input0'):
                guest.snapshot_inputs(root)

    def test_prebootstrap_snapshot_imports_no_scientific_packages(self):
        code="""import builtins,importlib.util,pathlib,sys
blocked={'numpy','pandas','scipy','matplotlib','statsmodels','openpyxl','yaml'}
original=builtins.__import__
def guarded(name,*args,**kwargs):
 if name.split('.')[0] in blocked:raise AssertionError('Scientific import before bootstrap: '+name)
 return original(name,*args,**kwargs)
builtins.__import__=guarded
sys.path.insert(0,sys.argv[1])
spec=importlib.util.spec_from_file_location('native_input_fixture',sys.argv[2])
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
assert len(module.snapshot_inputs(pathlib.Path(sys.argv[3])))==10
assert not any(name.split('.')[0] in blocked for name in sys.modules)
print('ten inputs verified without scientific imports')
"""
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.fixture(root)
            project=Path(__file__).resolve().parents[1]
            result=subprocess.run([sys.executable,'-I','-B','-c',code,str(project/'src'),
                                   str(project/'scripts/_native_wsl_guest.py'),str(root)],
                                  capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(result.stdout.strip(),'ten inputs verified without scientific imports')


if __name__ == '__main__':
    unittest.main()
