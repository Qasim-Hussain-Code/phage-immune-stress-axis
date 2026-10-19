"""Read-only resource and installed-software inventory (no installations)."""
import ctypes
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import sys
from datetime import datetime, timezone


def memory():
    if os.name == 'nt':
        class Status(ctypes.Structure):
            _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [
                (x, ctypes.c_ulonglong) for x in
                ['total', 'available', 'page', 'available_page', 'virtual', 'available_virtual', 'extended']]
        status = Status()
        status.length = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError('Cannot measure system memory')
        return {'total_bytes': status.total, 'available_bytes': status.available}
    values = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, value = line.split(':', 1)
        values[key] = int(value.strip().split()[0]) * 1024
    return {'total_bytes': values['MemTotal'], 'available_bytes': values['MemAvailable']}


def probe(root):
    disk = shutil.disk_usage(root)
    packages = {}
    for name in ['numpy', 'pandas', 'scipy', 'statsmodels', 'matplotlib', 'openpyxl', 'PyYAML', 'scikit-learn', 'pypdf']:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    return {'measured_utc': datetime.now(timezone.utc).isoformat(),
            'platform': platform.platform(), 'python': sys.version, 'executable': sys.executable,
            'memory': memory(), 'disk_free_bytes': disk.free,
            'storage_budget_bytes': max(0, min(10_000_000_000, disk.free - 4_000_000_000)),
            'packages': packages,
            'commands_on_path': {name: shutil.which(name) for name in ['python', 'Rscript', 'conda', 'mamba', 'git', 'gh']}}


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    output = root / 'data/manifests/environment_initial.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    result = probe(root)
    if not output.exists():
        output.write_text(json.dumps(result, indent=2) + '\n')
    (root/'data/manifests/environment_local.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result, indent=2))
