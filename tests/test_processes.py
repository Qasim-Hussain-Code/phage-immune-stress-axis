"""Small real process fixtures; no scientific data, downloads or large memory."""
from __future__ import annotations

import ctypes
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

from pisa import processes
from pisa.resources import monitored_run


class ReadyFixtureClock:
    """Separate a bounded fixture startup from a real post-handshake timeout.

    Only the integration fixture's clock is patched. Production launch/runtime
    accounting is unchanged. If startup fails, subsequent cleanup calls see a
    progressing real clock, so cleanup deadlines cannot be frozen accidentally.
    """

    def __init__(self, ready, startup_limit=10):
        self.real_monotonic = time.monotonic
        self.start = self.real_monotonic()
        self.ready = ready
        self.ready_started = None
        self.startup_limit = startup_limit
        self.startup_failed = False

    def __call__(self):
        now = self.real_monotonic()
        if self.ready_started is None and not self.startup_failed:
            if self.ready():
                self.ready_started = now
            elif now-self.start >= self.startup_limit:
                self.startup_failed = True
                raise AssertionError(f'Process fixture handshake exceeded {self.startup_limit} s startup bound')
            else:
                return 0.0
        return now-(self.ready_started if self.ready_started is not None else self.start)


class ProcessCleanupContracts(unittest.TestCase):
    def test_posix_group_is_signalled_after_leader_has_already_exited(self):
        child = Mock()
        child.pid = 1234
        child.returncode = 0
        child.poll.return_value = 0
        with patch.object(processes.subprocess, 'Popen', return_value=child), \
             patch.object(processes, '_LinuxDescendants', return_value=Mock()), \
             patch.object(processes.signal, 'SIGKILL', 9, create=True), \
             patch.object(processes.os, 'killpg', create=True) as killpg:
            owned = processes.PosixProcess(['synthetic'], '.', None)
            owned.cleanup()
            owned.cleanup()
        self.assertEqual(killpg.call_args_list,
            [unittest.mock.call(1234, signal.SIGTERM),
             unittest.mock.call(1234, 9)])
        self.assertEqual(owned.returncode, 0)
        self.assertTrue(owned.closed)

    def test_original_guard_error_survives_secondary_cleanup_error(self):
        child = Mock()
        child.poll.return_value = None
        child.cleanup.side_effect = OSError('secondary cleanup failure')
        guard = Mock()
        guard.config = {'stage_timeout_seconds': 5}
        original = RuntimeError('original resource failure')
        guard.check.side_effect = original
        with tempfile.TemporaryDirectory() as directory, \
             patch('pisa.resources.start_process', return_value=child):
            with self.assertRaises(RuntimeError) as caught:
                monitored_run(['synthetic'], directory, Path(directory)/'log', guard)
        self.assertIs(caught.exception, original)
        self.assertIn('secondary cleanup failure', ' '.join(original.__notes__))

    def test_normal_parent_success_does_not_hide_cleanup_failure(self):
        child = Mock()
        child.poll.return_value = 0
        child.returncode = 0
        child.cleanup.side_effect = OSError('cleanup failed after parent exit')
        guard = Mock()
        guard.config = {'stage_timeout_seconds': 5}
        with tempfile.TemporaryDirectory() as directory, \
             patch('pisa.resources.start_process', return_value=child):
            with self.assertRaisesRegex(OSError, 'cleanup failed after parent exit'):
                monitored_run(['synthetic'], directory, Path(directory)/'log', guard)


class LinuxIdentityContracts(unittest.TestCase):
    def test_reused_pid_is_not_signalled_by_starttime_fallback(self):
        tracker = processes._LinuxDescendants.__new__(processes._LinuxDescendants)
        tracker.records = {1234: {'starttime': 100, 'pidfd': None}}
        tracker.closed = False
        with patch.object(processes, '_linux_stat', return_value=(1, 101, 'S')), \
             patch.object(processes.os, 'kill') as kill:
            tracker.send_signal(signal.SIGTERM)
            kill.assert_not_called()
        tracker.close()

    def test_pidfd_capture_rechecks_identity_and_closes_raced_descriptor(self):
        with patch.object(processes, '_linux_stat', side_effect=[(1, 100, 'S'),
                (1, 100, 'S'), (1, 101, 'S')]), \
             patch.object(processes.os, 'pidfd_open', return_value=42, create=True), \
             patch.object(processes.signal, 'pidfd_send_signal', create=True), \
             patch.object(processes.os, 'close') as close:
            with self.assertRaisesRegex(RuntimeError, 'establish Linux child process identity'):
                processes._LinuxDescendants(1234)
            close.assert_called_once_with(42)


@unittest.skipUnless(sys.platform.startswith('linux'), 'Real Linux /proc and pidfd fixtures require Linux')
class LinuxProcessIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary_root = Path(__file__).resolve().parents[1]/'.cache/tmp'
        cls.temporary_root.mkdir(parents=True, exist_ok=True)

    def cleanup_fixture_handles(self, handles):
        for descriptor in handles:
            try:
                try:
                    signal.pidfd_send_signal(descriptor, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            finally:
                os.close(descriptor)

    def fixture(self, *, separate_session=False, exit_code=None, failure=None, reparent=False):
        if not hasattr(os, 'pidfd_open') or not hasattr(signal, 'pidfd_send_signal'):
            self.skipTest('Integration fixture requires exact pidfd cleanup handles')
        with tempfile.TemporaryDirectory(dir=self.temporary_root) as directory:
            root = Path(directory)
            (root/'leaf.py').write_text("import os,time\nfrom pathlib import Path\n"
                "Path('leaf.pid').write_text(str(os.getpid()))\ntime.sleep(30)\n")
            worker_source = ("import os,subprocess,sys,time\nfrom pathlib import Path\n"
                f"subprocess.Popen([sys.executable,'leaf.py'],start_new_session={separate_session!r})\n"
                "Path('worker.pid').write_text(str(os.getpid()))\n")
            worker_source += ("while not Path('release').exists(): time.sleep(.005)\n"
                if reparent else "time.sleep(30)\n")
            (root/'worker.py').write_text(worker_source)
            parent_source = ("import subprocess,sys,time\nfrom pathlib import Path\n"
                f"worker=subprocess.Popen([sys.executable,'worker.py'],start_new_session={separate_session!r})\n"
                "while not Path('release').exists(): time.sleep(.005)\n")
            if reparent:
                parent_source += "worker.wait()\nPath('worker_reaped').write_text('reparented leaf')\ntime.sleep(30)\n"
            elif exit_code is None:
                parent_source += "time.sleep(30)\n"
            else:
                parent_source += f"raise SystemExit({exit_code})\n"
            parent = root/'parent.py'
            parent.write_text(parent_source)
            handles, owned, observed_fds = [], [], []
            self.addCleanup(self.cleanup_fixture_handles, handles)
            real_start = processes.start_process
            owner = self

            def capture_owned(*arguments, **keywords):
                child = real_start(*arguments, **keywords)
                owned.append(child)
                return child

            class FixtureGuard:
                config = {'stage_timeout_seconds': 5}

                def check(self):
                    if handles and failure is not None and (not reparent or (root/'worker_reaped').exists()):
                        if reparent:
                            leaf_pid = int((root/'leaf.pid').read_text())
                            worker_pid = int((root/'worker.pid').read_text())
                            owner.assertNotEqual(processes._linux_stat(leaf_pid)[0], worker_pid)
                            owner.assertIn(leaf_pid, owned[0].descendants.records)
                        raise failure

                def observe_processes(self):
                    if not handles and all((root/name).exists() for name in ('worker.pid', 'leaf.pid')):
                        pids = [int((root/name).read_text()) for name in ('worker.pid', 'leaf.pid')]
                        tracker = owned[0].descendants
                        # Give the tracker an actual observation before granting
                        # parent exit. This does not test unobserved detach races.
                        if not all(pid in tracker.records for pid in pids):
                            return
                        for pid in pids:
                            handles.append(os.pidfd_open(pid, 0))
                            if separate_session:
                                owner.assertNotEqual(os.getpgid(pid), owned[0].pid)
                        observed_fds.extend(record['pidfd'] for record in tracker.records.values()
                            if record['pidfd'] is not None)
                        (root/'release').write_text('controller observed both descendants')

            clock = ReadyFixtureClock(lambda: len(handles) == 2)
            with patch('pisa.resources.start_process', side_effect=capture_owned), \
                 patch('pisa.resources.time.monotonic', side_effect=clock):
                if failure is not None:
                    with self.assertRaises(type(failure)) as caught:
                        monitored_run([sys.executable, str(parent)], root, root/'parent.log', FixtureGuard())
                    self.assertIs(caught.exception, failure)
                elif exit_code is None:
                    with self.assertRaises(TimeoutError):
                        monitored_run([sys.executable, str(parent)], root, root/'parent.log', FixtureGuard(), timeout=0.5)
                else:
                    self.assertEqual(monitored_run([sys.executable, str(parent)], root,
                        root/'parent.log', FixtureGuard()), exit_code)
            self.assertEqual(len(handles), 2, 'Fixture must observe both live descendants')
            if failure is None and exit_code is None:
                self.assertIsNotNone(clock.ready_started)
                self.assertGreaterEqual(clock.real_monotonic()-clock.ready_started, 0.5)
            self.assertTrue(owned[0].closed)
            self.assertTrue(owned[0].descendants.closed)
            poller = processes.select.poll()
            for descriptor in handles:
                poller.register(descriptor, processes.select.POLLIN)
            ready = dict(poller.poll(1000))
            self.assertEqual(set(ready), set(handles), 'An exact known Linux descendant survived cleanup')
            for descriptor in observed_fds:
                with self.assertRaises(OSError):
                    os.fstat(descriptor)
            self.cleanup_fixture_handles(handles)
            handles.clear()

    def test_parent_success_cleans_ordinary_process_group(self):
        self.fixture(exit_code=0)

    def test_parent_nonzero_cleans_ordinary_process_group(self):
        self.fixture(exit_code=7)

    def test_timeout_cleans_observed_separate_sessions(self):
        self.fixture(separate_session=True)

    def test_resource_failure_cleans_observed_separate_sessions(self):
        self.fixture(separate_session=True, failure=RuntimeError('synthetic Linux resource ceiling'))

    def test_keyboard_interrupt_cleans_observed_separate_sessions(self):
        self.fixture(separate_session=True, failure=KeyboardInterrupt('synthetic Linux interruption'))

    def test_observed_reparented_leaf_is_cleaned_on_controller_failure(self):
        self.fixture(separate_session=True, reparent=True,
            failure=RuntimeError('synthetic Linux failure after worker exit'))


@unittest.skipUnless(os.name == 'nt', 'Native Job Object integration requires Windows')
class WindowsJobIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from ctypes import wintypes as w
        cls.api = processes._windows_api()
        cls.api.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
        cls.api.OpenProcess.restype = w.HANDLE
        cls.api.GetProcessHandleCount.argtypes = [w.HANDLE, ctypes.POINTER(w.DWORD)]
        cls.api.GetProcessHandleCount.restype = w.BOOL

    def exact_process_handle(self, pid):
        # Holding this native handle prevents a reused PID from becoming a
        # cleanup target. No enumeration-based killing of arbitrary processes.
        handle = self.api.OpenProcess(0x100000 | 0x1000 | 0x1, False, pid)
        if not handle:
            raise ctypes.WinError(ctypes.get_last_error())
        return handle

    def finish_exact_handles(self, handles):
        for handle in handles:
            try:
                if self.api.WaitForSingleObject(handle, 0) == 258:
                    self.api.TerminateProcess(handle, 19)
                    self.api.WaitForSingleObject(handle, 2000)
            finally:
                self.api.CloseHandle(handle)

    def descendant_fixture(self, exit_code=None, failure=None, startup_delay=0):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # Both worker and leaf are alive before the controller permits
            # the parent to exit. This tests real inheritance across two levels.
            leaf = root/'leaf.py'
            leaf.write_text("import os,time\nfrom pathlib import Path\n"
                "Path('leaf.pid').write_text(str(os.getpid()))\ntime.sleep(30)\n")
            worker = root/'worker.py'
            worker.write_text("import os,subprocess,sys,time\nfrom pathlib import Path\n"
                "subprocess.Popen([sys.executable,'leaf.py'])\n"
                "Path('worker.pid').write_text(str(os.getpid()))\ntime.sleep(30)\n")
            parent = root/'parent.py'
            parent.write_text("import subprocess,sys,time\nfrom pathlib import Path\n"
                f"time.sleep({startup_delay!r})\n"
                "subprocess.Popen([sys.executable,'worker.py'])\n"
                "while not Path('release').exists(): time.sleep(.005)\n" +
                (f"raise SystemExit({exit_code})\n" if exit_code is not None else "time.sleep(30)\n"))
            handles = []
            self.addCleanup(self.finish_exact_handles, handles)
            api = self.api
            owner = self

            class FixtureGuard:
                config = {'stage_timeout_seconds': 5}

                def check(self):
                    if handles and failure is not None:
                        raise failure

                def observe_processes(self):
                    if not handles and all((root/name).exists() for name in ('worker.pid', 'leaf.pid')):
                        for name in ('worker.pid', 'leaf.pid'):
                            handles.append(owner.exact_process_handle(int((root/name).read_text())))
                        (root/'release').write_text('controller observed exact fixture handles')

            guard = FixtureGuard()
            clock = ReadyFixtureClock(lambda: len(handles) == 2)
            with patch('pisa.resources.time.monotonic', side_effect=clock):
                if failure is not None:
                    with self.assertRaises(type(failure)) as caught:
                        monitored_run([sys.executable, str(parent)], root, root/'parent.log', guard)
                    self.assertIs(caught.exception, failure)
                elif exit_code is None:
                    with self.assertRaises(TimeoutError):
                        monitored_run([sys.executable, str(parent)], root, root/'parent.log', guard, timeout=0.5)
                else:
                    self.assertEqual(monitored_run([sys.executable, str(parent)], root,
                        root/'parent.log', guard), exit_code)
            self.assertEqual(len(handles), 2, 'Fixture must reach both live descendants')
            if failure is None and exit_code is None:
                self.assertIsNotNone(clock.ready_started)
                self.assertGreaterEqual(clock.real_monotonic()-clock.ready_started, 0.5)
            for handle in handles:
                self.assertEqual(api.WaitForSingleObject(handle, 1000), 0,
                    'An exact known descendant survived monitored_run')
            self.finish_exact_handles(handles)
            handles.clear()

    def test_parent_success_cleans_worker_and_grandchild(self):
        self.descendant_fixture(exit_code=0)

    def test_parent_nonzero_cleans_worker_and_grandchild(self):
        self.descendant_fixture(exit_code=7)

    def test_timeout_cleans_worker_and_grandchild(self):
        # Deliberately exceed the old launch-based 1.5 s fixture deadline.
        self.descendant_fixture(startup_delay=2)

    def test_resource_error_cleans_worker_and_grandchild(self):
        self.descendant_fixture(failure=RuntimeError('synthetic resource ceiling'))

    def test_keyboard_interrupt_cleans_worker_and_grandchild(self):
        self.descendant_fixture(failure=KeyboardInterrupt('synthetic interruption'))

    def test_argv_cwd_environment_stdin_and_combined_log(self):
        arguments = ['has spaces', 'a"quote', 'trailing\\', 'Unicode_\u03b1', '']
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root/'argument check.py'
            script.write_text("import json,os,sys\n"
                "print(json.dumps([sys.argv[1:],os.getcwd(),os.environ['PISA_PROCESS_TEST'],sys.stdin.read()]))\n"
                "print('stderr is captured',file=sys.stderr)\n", encoding='utf-8')
            with (root/'log').open('w', encoding='utf-8') as log, \
                 patch.dict(os.environ, {'PISA_PROCESS_TEST': 'synthetic environment fixture'}):
                child = processes.start_process([sys.executable, str(script), *arguments], root, log)
                try:
                    self.assertEqual(child.wait(3), 0)
                finally:
                    child.cleanup()
                self.assertTrue(child.closed)
                self.assertIsNone(child.job)
                self.assertIsNone(child.process_handle)
                self.assertIsNone(child.thread_handle)
            lines = (root/'log').read_text().splitlines()
            actual = json.loads(next(line for line in lines if line.startswith('[')))
            self.assertEqual(actual, [arguments, str(root), 'synthetic environment fixture', ''])
            self.assertIn('stderr is captured', lines)

    def assert_launch_failure_is_contained(self, operation):
        api = processes._windows_api()
        handles = []
        self.addCleanup(self.finish_exact_handles, handles)
        real_create = api.CreateProcessW
        real_operation = getattr(api, operation)
        before = api.DWORD()
        after = api.DWORD()
        self.assertTrue(self.api.GetProcessHandleCount(self.api.GetCurrentProcess(), ctypes.byref(before)))

        def capture_child(*arguments):
            result = real_create(*arguments)
            if result:
                info = ctypes.cast(arguments[-1], ctypes.POINTER(api.ProcessInfo)).contents
                handles.append(self.exact_process_handle(info.dwProcessId))
            return result

        def injected_failure(*arguments):
            ctypes.set_last_error(5)
            return 0xFFFFFFFF if operation == 'ResumeThread' else 0

        api.CreateProcessW = capture_child
        setattr(api, operation, injected_failure)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = root/'must_not_execute'
            script = root/'never.py'
            script.write_text("from pathlib import Path\nPath('must_not_execute').write_text('executed')\n")
            with (root/'log').open('w') as log, patch.object(processes, '_windows_api', return_value=api):
                with self.assertRaises(OSError):
                    processes.start_process([sys.executable, str(script)], root, log)
            self.assertEqual(len(handles), 1)
            self.assertEqual(self.api.WaitForSingleObject(handles[0], 1000), 0)
            self.assertFalse(marker.exists(), 'Uncontained or unresumed child executed user code')
        setattr(api, operation, real_operation)
        self.finish_exact_handles(handles)
        handles.clear()
        self.assertTrue(self.api.GetProcessHandleCount(self.api.GetCurrentProcess(), ctypes.byref(after)))
        self.assertEqual(after.value, before.value, 'Native handles leaked on failed launch')

    def test_assignment_failure_never_executes_child_and_closes_handles(self):
        self.assert_launch_failure_is_contained('AssignProcessToJobObject')

    def test_resume_failure_never_executes_child_and_closes_handles(self):
        self.assert_launch_failure_is_contained('ResumeThread')

    def test_create_failure_does_not_leak_job_or_stdio_handles(self):
        api = processes._windows_api()
        before = api.DWORD()
        after = api.DWORD()
        self.assertTrue(self.api.GetProcessHandleCount(self.api.GetCurrentProcess(), ctypes.byref(before)))

        def injected_failure(*arguments):
            ctypes.set_last_error(5)
            return 0

        api.CreateProcessW = injected_failure
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with (root/'log').open('w') as log, patch.object(processes, '_windows_api', return_value=api):
                with self.assertRaises(OSError):
                    processes.start_process([sys.executable, '-c', 'pass'], root, log)
        self.assertTrue(self.api.GetProcessHandleCount(self.api.GetCurrentProcess(), ctypes.byref(after)))
        self.assertEqual(after.value, before.value)


if __name__ == '__main__':
    unittest.main()
