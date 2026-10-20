"""Local persistent budgets and sampled process-family memory monitoring."""
from __future__ import annotations
import contextlib
import ctypes
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys
import time


def available_memory():
    if os.name == 'nt':
        class Status(ctypes.Structure):
            _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [
                (x, ctypes.c_ulonglong) for x in
                ['total', 'available', 'page', 'available_page', 'virtual', 'available_virtual', 'extended']]
        status = Status(); status.length = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError('Memory measurement failed')
        return status.available
    info = dict((line.split(':')[0], int(line.split()[1])*1024)
                for line in Path('/proc/meminfo').read_text().splitlines())
    return info['MemAvailable']


def _windows_memory(pid):
    class Counters(ctypes.Structure):
        _fields_ = [('cb', ctypes.c_ulong), ('faults', ctypes.c_ulong)] + [
            (x, ctypes.c_size_t) for x in ['peak', 'working', 'peak_paged', 'paged',
                'peak_nonpaged', 'nonpaged', 'pagefile', 'peak_pagefile']]
    kernel = ctypes.windll.kernel32
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel.OpenProcess(0x410, False, pid)
    if not handle: return None
    try:
        value = Counters(); value.cb = ctypes.sizeof(value)
        ctypes.windll.psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
        if ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(value), value.cb):
            return {'rss': value.working, 'peak': value.peak}
        return None
    finally:
        kernel.CloseHandle(handle)


def peak_rss():
    if os.name != 'nt':
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == 'darwin' else 1024)
    value = _windows_memory(os.getpid())
    if value is None: raise OSError('Process-memory measurement failed')
    return value['peak']


def _process_parents():
    if os.name != 'nt':
        result = {}
        for directory in Path('/proc').iterdir():
            if not directory.name.isdigit(): continue
            try:
                text = (directory/'stat').read_text()
                result[int(directory.name)] = int(text.rsplit(')', 1)[1].split()[1])
            except (FileNotFoundError, PermissionError, ProcessLookupError, ValueError, IndexError):
                continue
        return result
    from ctypes import wintypes
    class Entry(ctypes.Structure):
        _fields_ = [('dwSize', wintypes.DWORD), ('cntUsage', wintypes.DWORD),
            ('th32ProcessID', wintypes.DWORD), ('th32DefaultHeapID', ctypes.c_size_t),
            ('th32ModuleID', wintypes.DWORD), ('cntThreads', wintypes.DWORD),
            ('th32ParentProcessID', wintypes.DWORD), ('pcPriClassBase', wintypes.LONG),
            ('dwFlags', wintypes.DWORD), ('szExeFile', wintypes.WCHAR*260)]
    kernel = ctypes.windll.kernel32
    kernel.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = ctypes.c_void_p
    kernel.Process32FirstW.argtypes = [ctypes.c_void_p, ctypes.POINTER(Entry)]
    kernel.Process32NextW.argtypes = [ctypes.c_void_p, ctypes.POINTER(Entry)]
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    snapshot = kernel.CreateToolhelp32Snapshot(2, 0)
    if snapshot == ctypes.c_void_p(-1).value:
        raise OSError('Cannot enumerate processes for aggregate memory monitoring')
    try:
        entry = Entry(); entry.dwSize = ctypes.sizeof(entry)
        result = {}; ok = kernel.Process32FirstW(snapshot, ctypes.byref(entry))
        while ok:
            result[entry.th32ProcessID] = entry.th32ParentProcessID
            ok = kernel.Process32NextW(snapshot, ctypes.byref(entry))
        return result
    finally:
        kernel.CloseHandle(snapshot)


def _process_memory(pid):
    if os.name == 'nt': return _windows_memory(pid)
    try:
        fields = {}
        for line in Path(f'/proc/{pid}/status').read_text().splitlines():
            if line.startswith(('VmRSS:', 'VmHWM:')):
                fields[line.split(':')[0]] = int(line.split()[1])*1024
        return {'rss': fields.get('VmRSS', 0), 'peak': fields.get('VmHWM', 0)}
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        return None


def process_family_memory(root_pid):
    """Sum concurrent current RSS, never add historical per-process peaks."""
    parents = _process_parents(); selected = {root_pid}
    while True:
        expanded = selected | {pid for pid, parent in parents.items() if parent in selected}
        if expanded == selected: break
        selected = expanded
    measured = {pid: _process_memory(pid) for pid in selected}
    if measured.get(root_pid) is None:
        raise OSError('Cannot measure monitoring process memory')
    values = [value for value in measured.values() if value is not None]
    return {'aggregate_rss_bytes': sum(value['rss'] for value in values),
        'max_native_process_peak_rss_bytes': max((value['peak'] for value in values), default=0),
        'processes_measured': len(values),
        'processes_unreadable_or_exited': len(selected)-len(values)}


def child_rss(pid):
    """Backward-compatible current resident size, not peak working set."""
    value = _process_memory(pid)
    return value['rss'] if value else 0


def _stop_process_tree(process):
    if process.poll() is not None: return
    if os.name == 'nt':
        with contextlib.suppress(OSError, subprocess.SubprocessError):
            subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
    else:
        with contextlib.suppress(ProcessLookupError): os.killpg(process.pid, signal.SIGTERM)
    with contextlib.suppress(OSError): process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        with contextlib.suppress(OSError): process.kill()
        process.wait(timeout=5)


def monitored_run(cmd, root, log_path, guard, timeout=None):
    """Bound runtime, storage and process-family memory; terminate on failure."""
    timeout = guard.config.get('stage_timeout_seconds', 600) if timeout is None else timeout
    if timeout <= 0: raise ValueError('Child timeout must be positive')
    log_path = Path(log_path); log_path.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    with log_path.open('w', encoding='utf-8') as log:
        process = subprocess.Popen(cmd, cwd=root, stdout=log, stderr=subprocess.STDOUT,
            env=os.environ, start_new_session=os.name != 'nt')
        try:
            while process.poll() is None:
                guard.check(); guard.observe_processes()
                if time.monotonic()-started > timeout:
                    raise TimeoutError(f'Child process exceeded {timeout} second timeout')
                time.sleep(0.1)
        except BaseException:
            _stop_process_tree(process)
            raise
        return process.returncode


def project_size(root, include_git=True):
    total = 0
    for path in Path(root).rglob('*'):
        if not include_git and '.git' in path.parts: continue
        try:
            if path.is_file(): total += path.stat().st_size
        except FileNotFoundError: continue
    return total


def baseline_identity(root):
    value = f'{Path(root).resolve()}|{Path(root).stat().st_dev}|{platform.node()}|{sys.platform}'
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


class Guard:
    def __init__(self, root, config):
        self.root = Path(root); self.config = config['resources']
        for key in ('max_new_storage_bytes', 'disk_reserve_bytes', 'max_process_rss_bytes', 'min_available_memory_bytes'):
            if self.config[key] <= 0: raise ValueError(f'Resource limit must be positive: {key}')
        path = self.root/'data/manifests/resource_baseline_local.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        identity = baseline_identity(self.root)
        baseline = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        if baseline.get('identity') != identity:
            baseline = {'identity': identity, 'disk_free_bytes': shutil.disk_usage(self.root).free,
                'project_bytes': project_size(self.root), 'platform': platform.platform(),
                'measured_unix_seconds': time.time()}
            path.write_text(json.dumps(baseline, indent=2)+'\n', encoding='utf-8')
        self.baseline = baseline
        # Complete project bytes are counted, conservatively including existing
        # inputs/environments, Git, downloads and caches within the checkout.
        self.budget = max(0, min(self.config['max_new_storage_bytes'],
            baseline['disk_free_bytes']-self.config['disk_reserve_bytes']))
        self.started = time.monotonic()
        self.max_sampled_aggregate_rss_bytes = 0
        self.max_observed_native_process_peak_rss_bytes = peak_rss()
        self.aggregate_samples = 0; self.max_unreadable_processes = 0
        self.check()

    def observe_processes(self):
        value = process_family_memory(os.getpid()); self.aggregate_samples += 1
        self.max_sampled_aggregate_rss_bytes = max(self.max_sampled_aggregate_rss_bytes, value['aggregate_rss_bytes'])
        self.max_observed_native_process_peak_rss_bytes = max(
            self.max_observed_native_process_peak_rss_bytes, value['max_native_process_peak_rss_bytes'])
        self.max_unreadable_processes = max(self.max_unreadable_processes, value['processes_unreadable_or_exited'])
        if value['max_native_process_peak_rss_bytes'] > self.config['max_process_rss_bytes']:
            raise RuntimeError('Process family member exceeded per-process memory ceiling')
        if value['aggregate_rss_bytes'] > self.config.get('max_aggregate_rss_bytes', self.config['max_process_rss_bytes']):
            raise RuntimeError('Aggregate process-family memory ceiling exceeded')
        return value

    def check(self, additional=0):
        if additional < 0: raise ValueError('Negative storage estimate')
        size = project_size(self.root); free = shutil.disk_usage(self.root).free
        if size+additional > self.budget or free-additional < self.config['disk_reserve_bytes']:
            raise RuntimeError('Storage budget or configured free-space reserve would be exceeded')
        memory = available_memory()
        if memory < self.config['min_available_memory_bytes']:
            raise RuntimeError(f'Insufficient available RAM: {memory} bytes; close applications and resume')
        rss = peak_rss()
        if rss > self.config['max_process_rss_bytes']: raise RuntimeError('Process memory ceiling exceeded')
        return {'project_bytes_including_git': size,
            'project_bytes_excluding_git': project_size(self.root, include_git=False),
            'disk_free_bytes': free, 'available_memory_bytes': memory,
            'process_peak_rss_bytes': rss, 'operational_storage_budget_bytes': self.budget,
            'baseline_scope': 'local_persistent_checkout_baseline_conservative_total_project_cap',
            'baseline_disk_free_bytes': self.baseline['disk_free_bytes'],
            'baseline_project_bytes': self.baseline['project_bytes'],
            'max_sampled_aggregate_rss_bytes': self.max_sampled_aggregate_rss_bytes,
            'max_observed_native_process_peak_rss_bytes': self.max_observed_native_process_peak_rss_bytes,
            'aggregate_memory_samples': self.aggregate_samples,
            'max_unreadable_or_exited_processes_per_sample': self.max_unreadable_processes,
            'elapsed_seconds': round(time.monotonic()-self.started, 3)}
