"""Small cross-platform resource guard. No background jobs or optional packages."""
import ctypes
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


def available_memory():
    if os.name == 'nt':
        class Status(ctypes.Structure):
            _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [
                (x, ctypes.c_ulonglong) for x in
                ['total', 'available', 'page', 'available_page', 'virtual', 'available_virtual', 'extended']]
        status = Status()
        status.length = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError('Memory measurement failed')
        return status.available
    info = dict((line.split(':')[0], int(line.split()[1])*1024)
                for line in Path('/proc/meminfo').read_text().splitlines())
    return info['MemAvailable']


def peak_rss():
    if os.name != 'nt':
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if __import__('sys').platform == 'darwin' else 1024)
    class Counters(ctypes.Structure):
        _fields_ = [('cb', ctypes.c_ulong), ('faults', ctypes.c_ulong)] + [
            (x, ctypes.c_size_t) for x in ['peak', 'working', 'peak_paged', 'paged', 'peak_nonpaged', 'nonpaged', 'pagefile', 'peak_pagefile']]
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    ctypes.windll.kernel32.GetCurrentProcess.restype=ctypes.c_void_p
    handle = ctypes.windll.kernel32.GetCurrentProcess()
    ctypes.windll.psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong]
    if not ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
        raise OSError('Process-memory measurement failed')
    return counters.peak


def child_rss(pid):
    if os.name!='nt':
        try:
            return int(next(x.split()[1] for x in Path(f'/proc/{pid}/status').read_text().splitlines() if x.startswith('VmRSS:')))*1024
        except (FileNotFoundError,StopIteration,ProcessLookupError):
            return 0
    class Counters(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('faults',ctypes.c_ulong)]+[(x,ctypes.c_size_t) for x in
             ['peak','working','peak_paged','paged','peak_nonpaged','nonpaged','pagefile','peak_pagefile']]
    kernel=ctypes.windll.kernel32
    kernel.OpenProcess.restype=ctypes.c_void_p
    kernel.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong]
    kernel.CloseHandle.argtypes=[ctypes.c_void_p]
    handle=kernel.OpenProcess(0x410,False,pid)
    if not handle: return 0
    try:
        value=Counters();value.cb=ctypes.sizeof(value)
        ctypes.windll.psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong]
        if ctypes.windll.psapi.GetProcessMemoryInfo(handle,ctypes.byref(value),value.cb): return value.peak
        return 0
    finally: kernel.CloseHandle(handle)


def monitored_run(cmd, root, log_path, guard):
    """Poll storage and native child RSS while writing logs without pipe buffers."""
    with Path(log_path).open('w',encoding='utf-8') as log:
        process=subprocess.Popen(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT,env=os.environ)
        try:
            while process.poll() is None:
                guard.check()
                if child_rss(process.pid)>guard.config['max_process_rss_bytes']:
                    raise RuntimeError('Child process exceeded memory ceiling')
                time.sleep(0.1)
        except BaseException:
            process.terminate()
            process.wait(timeout=15)
            raise
        return process.returncode


def project_size(root,include_git=True):
    total=0
    for p in Path(root).rglob('*'):
        if not include_git and '.git' in p.parts: continue
        try:
            if p.is_file():total+=p.stat().st_size
        except FileNotFoundError:
            continue  # A monitored child may atomically rename a .part file.
    return total


class Guard:
    def __init__(self, root, config):
        self.root = Path(root)
        self.config = config['resources']
        baseline = json.loads((self.root/'data/manifests/environment_initial.json').read_text())
        # The frozen initial probe governs this execution; a new checkout should
        # generate its own local initial probe before acquiring inputs.
        self.budget = min(self.config['max_new_storage_bytes'], baseline['storage_budget_bytes'])
        self.started = time.monotonic()
        self.check()

    def check(self, additional=0):
        if additional < 0:
            raise ValueError('Negative storage estimate')
        size = project_size(self.root)
        free = shutil.disk_usage(self.root).free
        if size + additional > self.budget or free - additional < self.config['disk_reserve_bytes']:
            raise RuntimeError('Storage budget or 4 GB free-space reserve would be exceeded')
        memory = available_memory()
        if memory < self.config['min_available_memory_bytes']:
            raise RuntimeError(f'Insufficient available RAM: {memory} bytes; close applications and resume')
        rss = peak_rss()
        if rss > self.config['max_process_rss_bytes']:
            raise RuntimeError('Process memory ceiling exceeded')
        return {'project_bytes_including_git':size,
                'project_bytes_excluding_git':project_size(self.root,include_git=False), 'disk_free_bytes': free,
                'available_memory_bytes': memory, 'process_peak_rss_bytes': rss,
                'operational_storage_budget_bytes': self.budget,
                'elapsed_seconds': round(time.monotonic()-self.started, 3)}
