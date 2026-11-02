"""Dispatch gate tests never invoke a model."""
import contextlib
import io
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from tools.ai_usage import dispatch


class DispatchTests(unittest.TestCase):
    def run_dispatch(self, code, allow_warning=False, execute_result=(0, 'finished')):
        result = {'provider': 'claude', 'pool': None, 'state': 'ok', 'exit_code': code,
                  'scope': 'all_provider_pools_conservative', 'buckets': [{'SECRET': 'raw'}]}
        with tempfile.TemporaryDirectory() as directory:
            runtime = Path(directory)
            with patch.object(dispatch, 'refresh_state', side_effect=['updated', 'cooldown']) as refresh, \
                 patch.object(dispatch.monitor, 'status', return_value={}), \
                 patch.object(dispatch.monitor, 'check', return_value=result), \
                 patch.object(dispatch, 'execute', return_value=execute_result) as execute, \
                 contextlib.redirect_stderr(io.StringIO()) as stderr:
                exit_code = dispatch.dispatch('claude', 'test-model', 'PRIVATE PROMPT',
                                              allow_warning=allow_warning, runtime=runtime)
            record = json.loads((runtime / 'dispatch.jsonl').read_text())
            return exit_code, execute.call_count, record, refresh.call_count, stderr.getvalue()

    def test_blocked_quota_never_spawns(self):
        for code in (1, 2, 3):
            with self.subTest(code=code):
                exit_code, calls, record, _, _ = self.run_dispatch(code)
                self.assertEqual(exit_code, code)
                self.assertEqual(calls, 0)
                self.assertEqual(record['status'], 'blocked')

    def test_warning_requires_explicit_exception(self):
        self.assertEqual(self.run_dispatch(1, allow_warning=True)[:2], (0, 1))
        self.assertEqual(self.run_dispatch(2, allow_warning=True)[:2], (2, 0))
        self.assertEqual(self.run_dispatch(3, allow_warning=True)[:2], (3, 0))

    def test_after_refresh_on_failed_or_timed_out_command(self):
        for code, status in ((9, 'finished'), (124, 'timeout'), (127, 'cli_missing')):
            with self.subTest(status=status):
                result = self.run_dispatch(0, execute_result=(code, status))
                self.assertEqual(result[0], code)
                self.assertEqual(result[2]['status'], status)
                self.assertEqual(result[3], 2)
                self.assertEqual(result[2]['after_refresh'], 'cooldown')
                self.assertIn('尚未更新', result[4])

    def test_record_excludes_prompt_and_raw_buckets(self):
        record = json.dumps(self.run_dispatch(0)[2])
        self.assertNotIn('PRIVATE PROMPT', record)
        self.assertNotIn('SECRET', record)
        self.assertNotIn('buckets', record)

    def test_commands_are_argument_arrays_and_keep_prompt_literal(self):
        prompt = '--dangerously-skip-permissions $(touch /tmp/should-not-exist); `echo x`'
        for provider in ('claude', 'codex', 'agy'):
            args = dispatch.command(provider, 'model', prompt)
            self.assertEqual(args.count(prompt), 1)
            self.assertNotIn('--dangerously-skip-permissions', args)
        self.assertIn('--', dispatch.command('codex', 'model', prompt))

    def test_execute_timeout_cleans_process_group_without_shell(self):
        process = Mock(pid=123456789)
        process.wait.side_effect = [subprocess.TimeoutExpired('fake', 600), 0]
        with patch.object(dispatch.subprocess, 'Popen', return_value=process) as popen, \
             patch.object(dispatch.os, 'killpg') as kill:
            self.assertEqual(dispatch.execute(['fake', 'literal']), (124, 'timeout'))
        self.assertNotIn('shell', popen.call_args.kwargs)
        self.assertTrue(popen.call_args.kwargs['start_new_session'])
        self.assertEqual(kill.call_count, 1)

    def test_refresh_conflict_does_not_check_or_spawn(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(dispatch, 'refresh_state', return_value='in_progress'), \
             patch.object(dispatch.monitor, 'check') as check, \
             patch.object(dispatch, 'execute') as execute, \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(dispatch.dispatch('codex', 'model', 'prompt',
                                              runtime=Path(directory)), 3)
        check.assert_not_called()
        execute.assert_not_called()

    def test_journal_is_bounded(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(dispatch, 'MAX_RECORDS', 3):
            runtime = Path(directory)
            for number in range(5):
                dispatch.save_record({'task_id': str(number)}, runtime)
            entries = [json.loads(line) for line in (runtime / 'dispatch.jsonl').read_text().splitlines()]
            self.assertEqual([entry['task_id'] for entry in entries], ['2', '3', '4'])

    def test_concurrent_same_provider_dispatch_is_rejected(self):
        has_entered = threading.Event()
        can_finish = threading.Event()
        def execute(arguments):
            has_entered.set()
            self.assertTrue(can_finish.wait(5))
            return 0, 'finished'
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(dispatch, 'refresh_state', return_value='cooldown'), \
             patch.object(dispatch.monitor, 'status', return_value={}), \
             patch.object(dispatch.monitor, 'check', return_value={'exit_code': 0}), \
             patch.object(dispatch, 'execute', side_effect=execute) as run, \
             contextlib.redirect_stderr(io.StringIO()):
            runtime = Path(directory)
            worker = threading.Thread(target=dispatch.dispatch,
                                      args=('claude', 'model', 'prompt'), kwargs={'runtime': runtime})
            worker.start()
            try:
                self.assertTrue(has_entered.wait(5))
                self.assertEqual(dispatch.dispatch('claude', 'model', 'prompt', runtime=runtime), 3)
            finally:
                can_finish.set()
                worker.join(5)
            self.assertEqual(run.call_count, 1)
            self.assertFalse(worker.is_alive())

    def test_short_task_cooldown_requires_post_execution_observation(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(dispatch, 'refresh_state', return_value='cooldown'), \
             patch.object(dispatch.monitor, 'status', return_value={}), \
             patch.object(dispatch.monitor, 'check', return_value={'exit_code': 0}) as check, \
             patch.object(dispatch, 'execute', return_value=(0, 'finished')) as execute, \
             contextlib.redirect_stderr(io.StringIO()):
            runtime = Path(directory)
            self.assertEqual(dispatch.dispatch('codex', 'model', 'prompt', runtime=runtime), 0)
            self.assertEqual(dispatch.dispatch('codex', 'model', 'prompt', runtime=runtime), 3)
            self.assertEqual(check.call_count, 1)
            self.assertEqual(execute.call_count, 1)
            snapshot = {'providers': [{'id': 'codex', 'status': 'ok',
                                      'attempted_at': dispatch.storage.timestamp(),
                                      'observed_at': dispatch.storage.timestamp()}]}
            self.assertTrue(dispatch.clear_observed_dirty('codex', runtime, snapshot,
                                                        dispatch.storage.timestamp()))
            self.assertFalse((runtime / 'dispatch-codex-dirty.json').exists())

    def test_dirty_marker_requires_sampling_started_after_task_finished(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = Path(directory)
            name = 'dispatch-codex-dirty.json'
            ended = '2026-10-19T12:00:00Z'
            dispatch.storage.save_json(name, {'ended_at': ended}, runtime)
            for attempted, observed in (
                ('2026-10-19T11:59:58Z', '2026-10-19T12:00:01Z'),
                ('2026-10-19T12:00:02Z', '2026-10-19T12:00:01Z'),
                (None, '2026-10-19T12:00:01Z'),
                ('invalid', '2026-10-19T12:00:01Z'),
                ('2026-10-19T12:00:01', '2026-10-19T12:00:02Z'),
                ('2026-10-19T12:00:01Z', None),
            ):
                snapshot = {'providers': [{'id': 'codex', 'status': 'ok',
                                          'attempted_at': attempted, 'observed_at': observed}]}
                with self.subTest(attempted=attempted, observed=observed):
                    self.assertFalse(dispatch.clear_observed_dirty('codex', runtime, snapshot, ended))
                    self.assertTrue((runtime / name).exists())
            snapshot['providers'][0].update(attempted_at=ended, observed_at=ended)
            self.assertTrue(dispatch.clear_observed_dirty('codex', runtime, snapshot, ended))
            self.assertFalse((runtime / name).exists())

    def test_real_monitor_api_does_not_reuse_before_task_snapshot(self):
        entry = {'id': 'codex', 'status': 'ok', 'attempted_at': dispatch.storage.timestamp(),
                 'observed_at': dispatch.storage.timestamp(), 'buckets': [
                     {'id': 'codex:primary', 'used_percent': 10, 'remaining_percent': 90,
                      'resets_at': None}]}
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(dispatch.monitor, 'collect', return_value=entry) as collect, \
             patch.object(dispatch, 'execute', return_value=(0, 'finished')) as execute, \
             contextlib.redirect_stderr(io.StringIO()):
            runtime = Path(directory)
            self.assertEqual(dispatch.dispatch('codex', 'model', 'prompt', runtime=runtime), 0)
            self.assertEqual(dispatch.dispatch('codex', 'model', 'prompt', runtime=runtime), 3)
            self.assertEqual(execute.call_count, 1)
            self.assertEqual(collect.call_count, 1)

    def test_real_sigterm_kills_model_group_and_skips_after_refresh(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = Path(directory)
            child_script = ('import os,time; from pathlib import Path; '
                            f'Path({str(runtime / "child.pid")!r}).write_text(str(os.getpid())); '
                            'time.sleep(60)')
            script = f'''import signal,sys
from pathlib import Path
from tools.ai_usage import dispatch
dispatch.refresh_state = lambda *args: 'cooldown'
dispatch.monitor.status = lambda *args: {{}}
dispatch.monitor.check = lambda *args: {{'exit_code': 0}}
dispatch.command = lambda *args: [sys.executable, '-c', {child_script!r}]
signal.signal(signal.SIGTERM, dispatch._handle_termination)
raise SystemExit(dispatch.dispatch('claude', 'model', 'prompt', runtime=Path({directory!r})))
'''
            process = subprocess.Popen([sys.executable, '-c', script], stderr=subprocess.PIPE)
            try:
                deadline = time.monotonic() + 5
                while not (runtime / 'child.pid').exists() and time.monotonic() < deadline:
                    time.sleep(0.02)
                self.assertTrue((runtime / 'child.pid').exists())
                child_pid = int((runtime / 'child.pid').read_text())
                process.send_signal(signal.SIGTERM)
                _, stderr = process.communicate(timeout=5)
                self.assertEqual(process.returncode, 130, stderr)
                with self.assertRaises(ProcessLookupError):
                    os.kill(child_pid, 0)
                record = json.loads((runtime / 'dispatch.jsonl').read_text())
                self.assertEqual(record['after_refresh'], 'cancelled')
                self.assertTrue((runtime / 'dispatch-claude-dirty.json').exists())
            finally:
                if process.poll() is None:
                    process.kill()
                process.communicate()


if __name__ == '__main__':
    unittest.main()
