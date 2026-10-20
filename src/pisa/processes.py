"""Bounded cleanup of owned command processes, without a shell or extra packages.

Windows uses a non-inheritable, kill-on-close Job Object. CreateProcessW starts
the primary thread suspended; assignment must succeed before ResumeThread. Only
duplicated stdin/log handles are inherited. Normal parent exit also terminates
remaining job members: this pipeline requires its commands to await their work.

POSIX creates a session/process group and signals that group even if its leader
has exited. Linux additionally retains identities of observed descendants,
including ones that subsequently reparent or start another session. pidfds are
preferred; the fallback checks /proc starttime immediately before signaling.
Polling cannot capture every child that forks and detaches between observations.
This is failure cleanup, not a security boundary; only direct children are reaped.

Native contracts: Microsoft Learn CreateProcessW, AssignProcessToJobObject,
ResumeThread, UpdateProcThreadAttribute, and Job Objects. No breakaway is enabled.
"""
from __future__ import annotations

import ctypes
import errno
import math
import os
from pathlib import Path
import select
import shutil
import signal
import subprocess
import sys
import time


def _linux_stat(pid):
    """Return (parent PID, starttime ticks, state), parsing parenthesized comm."""
    try:
        fields = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
        return int(fields[1]), int(fields[19]), fields[0]
    except (FileNotFoundError, ProcessLookupError, PermissionError, ValueError, IndexError):
        return None


class _LinuxDescendants:
    """Retain observed PID/starttime identities; pidfds prevent signal PID races."""

    def __init__(self, root_pid):
        self.records = {}
        self.closed = False
        self.use_pidfds = hasattr(os, 'pidfd_open') and hasattr(signal, 'pidfd_send_signal')
        initial = _linux_stat(root_pid)
        if initial is None or not self._capture(root_pid, initial[1]):
            raise RuntimeError('Cannot establish Linux child process identity')

    def _capture(self, pid, starttime):
        current = _linux_stat(pid)
        if current is None or current[1] != starttime:
            return False
        descriptor = None
        if self.use_pidfds:
            try:
                descriptor = os.pidfd_open(pid, 0)
            except ProcessLookupError:
                return False
            except OSError as error:
                if error.errno not in (errno.ENOSYS, errno.ENODEV):
                    raise
                self.use_pidfds = False
            # Verify that opening the descriptor did not cross a PID reuse.
            verified = None
            try:
                verified = _linux_stat(pid)
            finally:
                if (verified is None or verified[1] != starttime) and descriptor is not None:
                    os.close(descriptor)
            if verified is None or verified[1] != starttime:
                return False
        self.records[pid] = {'starttime': starttime, 'pidfd': descriptor}
        return True

    def _alive(self, pid, record):
        descriptor = record['pidfd']
        if descriptor is not None:
            poller = select.poll()
            poller.register(descriptor, select.POLLIN)
            events = poller.poll(0)
            if any(event & select.POLLNVAL for _, event in events):
                raise OSError(errno.EBADF, 'Observed child pidfd was unexpectedly closed')
            return not events
        current = _linux_stat(pid)
        return current is not None and current[1] == record['starttime'] and current[2] not in ('Z', 'X')

    def observe(self):
        if self.closed:
            return
        snapshot = {}
        for directory in Path('/proc').iterdir():
            if directory.name.isdigit():
                value = _linux_stat(int(directory.name))
                if value is not None:
                    snapshot[int(directory.name)] = value
        selected = {pid for pid, record in self.records.items()
            if pid in snapshot and snapshot[pid][1] == record['starttime']}
        # A retained descendant is a seed even after its original parent exits.
        while True:
            added = set()
            for pid, (parent, starttime, _) in snapshot.items():
                if parent in selected and pid not in self.records and self._capture(pid, starttime):
                    added.add(pid)
            if not added:
                break
            selected.update(added)
        # Keep the identity record, but release descriptors for exited processes.
        for pid, record in self.records.items():
            if record['pidfd'] is not None and not self._alive(pid, record):
                os.close(record['pidfd'])
                record['pidfd'] = None

    def send_signal(self, signum):
        error = None
        for pid, record in self.records.items():
            try:
                if record['pidfd'] is not None:
                    signal.pidfd_send_signal(record['pidfd'], signum)
                else:
                    current = _linux_stat(pid)
                    if current is not None and current[1] == record['starttime'] and current[2] not in ('Z', 'X'):
                        os.kill(pid, signum)
            except ProcessLookupError:
                pass
            except BaseException as caught:
                if error is None:
                    error = caught
        if error is not None:
            raise error

    def wait(self, timeout=5):
        deadline = time.monotonic() + timeout
        while any(self._alive(pid, record) for pid, record in self.records.items()):
            if time.monotonic() >= deadline:
                raise TimeoutError('Observed Linux descendants did not terminate within cleanup deadline')
            time.sleep(0.01)

    def close(self):
        if self.closed:
            return
        error = None
        for record in self.records.values():
            if record['pidfd'] is not None:
                try:
                    os.close(record['pidfd'])
                except OSError as caught:
                    if error is None:
                        error = caught
                finally:
                    record['pidfd'] = None
        self.closed = True
        if error is not None:
            raise error


class PosixProcess:
    """Created process group, plus observed Linux descendants across sessions."""

    def __init__(self, cmd, cwd, stdout):
        self.process = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.DEVNULL,
            stdout=stdout, stderr=subprocess.STDOUT, env=os.environ,
            start_new_session=True)
        self.pid = self.process.pid
        self.closed = False
        self.descendants = None
        try:
            if sys.platform.startswith('linux'):
                self.descendants = _LinuxDescendants(self.pid)
        except BaseException as error:
            try:
                self.cleanup()
            except BaseException as cleanup_error:
                error.add_note(f'POSIX launch cleanup also failed: {cleanup_error!r}')
            raise

    @property
    def returncode(self):
        return self.process.returncode

    def poll(self):
        return self.process.poll()

    def observe(self):
        if self.descendants is not None:
            self.descendants.observe()

    def cleanup(self):
        if self.closed:
            return
        # Do not return just because the group leader exited. Its children may
        # remain in the original group. Escalate even after wait() succeeds.
        try:
            self.observe()
            try:
                os.killpg(self.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            if self.descendants is not None:
                self.descendants.send_signal(signal.SIGTERM)
            try:
                self.process.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                pass
        finally:
            try:
                try:
                    os.killpg(self.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            finally:
                try:
                    if self.descendants is not None:
                        self.descendants.send_signal(signal.SIGKILL)
                    self.process.wait(timeout=5)
                    if self.descendants is not None:
                        self.descendants.wait(timeout=5)
                finally:
                    if self.descendants is not None:
                        self.descendants.close()
                    self.closed = True


def _windows_api():
    """Bind our own ctypes function objects; do not mutate shared windll APIs."""
    from ctypes import wintypes as w

    class BasicLimits(ctypes.Structure):
        _fields_ = [('PerProcessUserTimeLimit', ctypes.c_longlong),
            ('PerJobUserTimeLimit', ctypes.c_longlong), ('LimitFlags', w.DWORD),
            ('MinimumWorkingSetSize', ctypes.c_size_t),
            ('MaximumWorkingSetSize', ctypes.c_size_t), ('ActiveProcessLimit', w.DWORD),
            ('Affinity', ctypes.c_size_t), ('PriorityClass', w.DWORD),
            ('SchedulingClass', w.DWORD)]

    class IoCounters(ctypes.Structure):
        _fields_ = [(name, ctypes.c_ulonglong) for name in
            ('ReadOperationCount', 'WriteOperationCount', 'OtherOperationCount',
             'ReadTransferCount', 'WriteTransferCount', 'OtherTransferCount')]

    class ExtendedLimits(ctypes.Structure):
        _fields_ = [('BasicLimitInformation', BasicLimits), ('IoInfo', IoCounters)] + [
            (name, ctypes.c_size_t) for name in ('ProcessMemoryLimit', 'JobMemoryLimit',
                'PeakProcessMemoryUsed', 'PeakJobMemoryUsed')]

    class Accounting(ctypes.Structure):
        _fields_ = [(name, ctypes.c_longlong) for name in
            ('TotalUserTime', 'TotalKernelTime', 'ThisPeriodTotalUserTime',
             'ThisPeriodTotalKernelTime')] + [(name, w.DWORD) for name in
            ('TotalPageFaultCount', 'TotalProcesses', 'ActiveProcesses',
             'TotalTerminatedProcesses')]

    class StartupInfo(ctypes.Structure):
        _fields_ = [('cb', w.DWORD), ('lpReserved', w.LPWSTR),
            ('lpDesktop', w.LPWSTR), ('lpTitle', w.LPWSTR)] + [
            (name, w.DWORD) for name in ('dwX', 'dwY', 'dwXSize', 'dwYSize',
                'dwXCountChars', 'dwYCountChars', 'dwFillAttribute', 'dwFlags')] + [
            ('wShowWindow', w.WORD), ('cbReserved2', w.WORD),
            ('lpReserved2', ctypes.POINTER(ctypes.c_ubyte)),
            ('hStdInput', w.HANDLE), ('hStdOutput', w.HANDLE), ('hStdError', w.HANDLE)]

    class StartupInfoEx(ctypes.Structure):
        _fields_ = [('StartupInfo', StartupInfo), ('lpAttributeList', ctypes.c_void_p)]

    class ProcessInfo(ctypes.Structure):
        _fields_ = [('hProcess', w.HANDLE), ('hThread', w.HANDLE),
            ('dwProcessId', w.DWORD), ('dwThreadId', w.DWORD)]

    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    signatures = {
        'CreateJobObjectW': ([ctypes.c_void_p, w.LPCWSTR], w.HANDLE),
        'SetInformationJobObject': ([w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD], w.BOOL),
        'QueryInformationJobObject': ([w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD,
            ctypes.POINTER(w.DWORD)], w.BOOL),
        'AssignProcessToJobObject': ([w.HANDLE, w.HANDLE], w.BOOL),
        'TerminateJobObject': ([w.HANDLE, w.UINT], w.BOOL),
        'GetCurrentProcess': ([], w.HANDLE),
        'DuplicateHandle': ([w.HANDLE, w.HANDLE, w.HANDLE, ctypes.POINTER(w.HANDLE),
            w.DWORD, w.BOOL, w.DWORD], w.BOOL),
        'CloseHandle': ([w.HANDLE], w.BOOL),
        'InitializeProcThreadAttributeList': ([ctypes.c_void_p, w.DWORD, w.DWORD,
            ctypes.POINTER(ctypes.c_size_t)], w.BOOL),
        'UpdateProcThreadAttribute': ([ctypes.c_void_p, w.DWORD, ctypes.c_size_t,
            ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p], w.BOOL),
        'DeleteProcThreadAttributeList': ([ctypes.c_void_p], None),
        'CreateProcessW': ([w.LPCWSTR, w.LPWSTR, ctypes.c_void_p, ctypes.c_void_p,
            w.BOOL, w.DWORD, ctypes.c_void_p, w.LPCWSTR,
            ctypes.POINTER(StartupInfoEx), ctypes.POINTER(ProcessInfo)], w.BOOL),
        'ResumeThread': ([w.HANDLE], w.DWORD),
        'WaitForSingleObject': ([w.HANDLE, w.DWORD], w.DWORD),
        'GetExitCodeProcess': ([w.HANDLE, ctypes.POINTER(w.DWORD)], w.BOOL),
        'TerminateProcess': ([w.HANDLE, w.UINT], w.BOOL),
    }
    for name, (arguments, result) in signatures.items():
        function = getattr(kernel, name)
        function.argtypes = arguments
        function.restype = result
    kernel.ExtendedLimits = ExtendedLimits
    kernel.Accounting = Accounting
    kernel.StartupInfoEx = StartupInfoEx
    kernel.ProcessInfo = ProcessInfo
    kernel.DWORD = w.DWORD
    kernel.HANDLE = w.HANDLE
    return kernel


def _checked(value, operation):
    if not value:
        error = ctypes.WinError(ctypes.get_last_error())
        error.add_note(operation)
        raise error
    return value


class WindowsJobProcess:
    """One direct child and all ordinary CreateProcess descendants in its job."""

    def __init__(self, cmd, cwd, stdout):
        if os.name != 'nt':
            raise OSError('Windows Job Object backend is only available on Windows')
        import msvcrt

        arguments = [os.fsdecode(value) for value in cmd]
        if not arguments:
            raise ValueError('An executable is required')
        executable = shutil.which(arguments[0])
        if executable is None:
            raise FileNotFoundError(f'Executable not found: {arguments[0]}')
        self.args = arguments
        self.api = api = _windows_api()
        self.pid = None
        self.returncode = None
        self.job = self.process_handle = self.thread_handle = None
        self.assigned = False
        self.closed = False
        temporary_handles = []
        attributes = None
        attributes_initialized = False
        try:
            self.job = _checked(api.CreateJobObjectW(None, None), 'CreateJobObjectW')
            limits = api.ExtendedLimits()
            limits.BasicLimitInformation.LimitFlags = 0x2000  # KILL_ON_JOB_CLOSE
            _checked(api.SetInformationJobObject(self.job, 9, ctypes.byref(limits),
                ctypes.sizeof(limits)), 'SetInformationJobObject(KILL_ON_JOB_CLOSE)')

            def duplicate(file):
                result = api.HANDLE()
                current = api.GetCurrentProcess()
                _checked(api.DuplicateHandle(current, msvcrt.get_osfhandle(file.fileno()),
                    current, ctypes.byref(result), 0, True, 2), 'DuplicateHandle(stdio)')
                temporary_handles.append(result.value)
                return result.value

            with open(os.devnull, 'rb') as null_input:
                stdin_handle = duplicate(null_input)
            log_handle = duplicate(stdout)
            inherited = (api.HANDLE * 2)(stdin_handle, log_handle)
            size = ctypes.c_size_t()
            api.InitializeProcThreadAttributeList(None, 1, 0, ctypes.byref(size))
            if size.value == 0:
                _checked(False, 'InitializeProcThreadAttributeList(size)')
            attributes = ctypes.create_string_buffer(size.value)
            _checked(api.InitializeProcThreadAttributeList(attributes, 1, 0,
                ctypes.byref(size)), 'InitializeProcThreadAttributeList')
            attributes_initialized = True
            _checked(api.UpdateProcThreadAttribute(attributes, 0, 0x20002, inherited,
                ctypes.sizeof(inherited), None, None), 'UpdateProcThreadAttribute(HANDLE_LIST)')
            startup = api.StartupInfoEx()
            startup.StartupInfo.cb = ctypes.sizeof(startup)
            startup.StartupInfo.dwFlags = 0x100  # STARTF_USESTDHANDLES
            startup.StartupInfo.hStdInput = stdin_handle
            startup.StartupInfo.hStdOutput = startup.StartupInfo.hStdError = log_handle
            startup.lpAttributeList = ctypes.cast(attributes, ctypes.c_void_p)
            info = api.ProcessInfo()
            command_line = ctypes.create_unicode_buffer(subprocess.list2cmdline(arguments))
            # Mutable command line, explicit executable, inherited environment,
            # no shell, no console window. No child code runs before assignment.
            flags = 0x4 | 0x80000 | 0x08000000  # SUSPENDED | EXTENDED_STARTUPINFO | NO_WINDOW
            _checked(api.CreateProcessW(executable, command_line, None, None, True,
                flags, None, os.fsdecode(cwd), ctypes.byref(startup), ctypes.byref(info)),
                'CreateProcessW(CREATE_SUSPENDED)')
            self.process_handle, self.thread_handle = info.hProcess, info.hThread
            self.pid = info.dwProcessId
            _checked(api.AssignProcessToJobObject(self.job, self.process_handle),
                'AssignProcessToJobObject: refusing to run an uncontained child')
            self.assigned = True
            previous = api.ResumeThread(self.thread_handle)
            if previous == 0xFFFFFFFF:
                _checked(False, 'ResumeThread')
            if previous != 1:
                raise RuntimeError(f'Unexpected primary-thread suspend count: {previous}')
            _checked(api.CloseHandle(self.thread_handle), 'CloseHandle(primary thread)')
            self.thread_handle = None
        except BaseException as error:
            try:
                self.cleanup()
            except BaseException as cleanup_error:
                error.add_note(f'Process launch cleanup also failed: {cleanup_error!r}')
            raise
        finally:
            if attributes_initialized:
                api.DeleteProcThreadAttributeList(attributes)
            # These duplicates are not the caller's file handles.
            for handle in temporary_handles:
                api.CloseHandle(handle)

    def poll(self):
        if self.returncode is not None:
            return self.returncode
        if self.closed:
            raise RuntimeError('Process handle closed without an exit status')
        state = self.api.WaitForSingleObject(self.process_handle, 0)
        if state == 258:  # WAIT_TIMEOUT
            return None
        if state != 0:
            _checked(False, 'WaitForSingleObject(process)')
        code = self.api.DWORD()
        _checked(self.api.GetExitCodeProcess(self.process_handle, ctypes.byref(code)),
            'GetExitCodeProcess')
        self.returncode = code.value
        return self.returncode

    def observe(self):
        # Job membership is established before execution and inherited natively.
        pass

    def wait(self, timeout):
        if self.returncode is not None:
            return self.returncode
        milliseconds = min(0xFFFFFFFE, max(0, math.ceil(timeout * 1000)))
        state = self.api.WaitForSingleObject(self.process_handle, milliseconds)
        if state == 258:
            raise subprocess.TimeoutExpired(self.args, timeout)
        if state != 0:
            _checked(False, 'WaitForSingleObject(process)')
        return self.poll()

    def cleanup(self):
        """Terminate the job, await zero active members, then close native handles."""
        if self.closed:
            return
        api = self.api
        try:
            if self.assigned:
                _checked(api.TerminateJobObject(self.job, 1), 'TerminateJobObject')
            elif self.process_handle:
                # Assignment failed: the primary thread is still suspended.
                _checked(api.TerminateProcess(self.process_handle, 1),
                    'TerminateProcess(unassigned suspended child)')
            if self.process_handle:
                self.wait(timeout=5)
            if self.assigned:
                deadline = time.monotonic() + 5
                while True:
                    accounting = api.Accounting()
                    _checked(api.QueryInformationJobObject(self.job, 1,
                        ctypes.byref(accounting), ctypes.sizeof(accounting), None),
                        'QueryInformationJobObject(active processes)')
                    if accounting.ActiveProcesses == 0:
                        break
                    if time.monotonic() >= deadline:
                        raise TimeoutError('Job members did not terminate within cleanup deadline')
                    time.sleep(0.01)
        finally:
            # Closing the last non-inherited job handle is a second termination
            # safeguard, including when a preceding query/wait failed.
            errors = []
            for name in ('thread_handle', 'job', 'process_handle'):
                handle = getattr(self, name)
                if handle:
                    if not api.CloseHandle(handle):
                        errors.append(name)
                    setattr(self, name, None)
            self.closed = True
            if errors:
                raise OSError(f'Could not close native process handles: {errors}')


def start_process(cmd, cwd, stdout):
    """Launch an owned command; Windows containment failure has no fallback."""
    backend = WindowsJobProcess if os.name == 'nt' else PosixProcess
    return backend(cmd, cwd, stdout)
