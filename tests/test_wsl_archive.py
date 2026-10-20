"""Direct native-worker archive fixtures; do not invoke WSL or install anything."""
import hashlib
import importlib.util
import io
from pathlib import Path
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


if __name__ == '__main__':
    unittest.main()
