import csv
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def _windows_replacement_conflict(error):
    """Only documented Windows permission/sharing/lock replacement conflicts."""
    return (sys.platform == 'win32' and isinstance(error, PermissionError)
            and getattr(error, 'winerror', None) in (5, 32, 33))


def _replace_with_retry(temporary, destination):
    # Six attempts, at most 0.62 seconds total requested sleep. Retry only the
    # replacement; serialization, writing and fsync have already succeeded.
    for delay in (0.02, 0.04, 0.08, 0.16, 0.32, None):
        try:
            os.replace(temporary, destination)
            return
        except PermissionError as error:
            if delay is None or not _windows_replacement_conflict(error):
                raise
            time.sleep(delay)


def write_json(path, value):
    path = Path(path)
    payload=json.dumps(value,indent=2,allow_nan=False)+'\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    # A sibling temporary file keeps replacement on the same filesystem.
    # Serialize first; a failed write/replacement must preserve the prior record.
    descriptor,temporary=tempfile.mkstemp(prefix='.pisa-'+path.name+'-',suffix='.tmp',dir=path.parent)
    try:
        with os.fdopen(descriptor,'w',encoding='utf-8',newline=None) as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        _replace_with_retry(temporary,path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def write_csv(path, rows, fields=None):
    rows = list(rows)
    if not rows and fields is None:
        raise ValueError('Refuse an empty table with no schema')
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path, delimiter=','):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream, delimiter=delimiter))


def code_digest(root):
    """Hash executable source and software fixtures, excluding bytecode caches."""
    root=Path(root)
    checksum=hashlib.sha256()
    for directory in ['src','scripts','tests']:
        for path in sorted((root/directory).rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts or path.suffix in ['.pyc','.pyo']:
                continue
            checksum.update(path.relative_to(root).as_posix().encode('utf-8'))
            checksum.update(b'\0')
            checksum.update(digest(path).encode('ascii'))
    return checksum.hexdigest()
