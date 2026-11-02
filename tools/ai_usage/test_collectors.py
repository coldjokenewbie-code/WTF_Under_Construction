"""Quota fixtures and real subprocess transport tests; no model calls."""
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
from unittest.mock import patch

try:
    from . import collectors
    from .normalize import ParseError, parse_agy, parse_claude, parse_codex
except ImportError:
    import collectors
    from normalize import ParseError, parse_agy, parse_claude, parse_codex


def claude_fixture(percent=27):
    return {'type': 'assistant', 'local_command_source': '/usage', 'usage_report': {
        'rate_limits': {'limits': [
            {'kind': 'session', 'group': 'Claude', 'percent': percent,
             'resets_at': '2026-10-19T20:00:00+08:00', 'scope': None, 'is_active': True},
            {'kind': 'weekly_scoped', 'group': 'Claude', 'percent': 0,
             'resets_at': None, 'scope': {'model': {'display_name': 'Fable'}, 'surface': None},
             'is_active': False}]}}}


def agy_fixture(fraction=0.75):
    return {'command': {'data': {'groups': [
        {'name': group, 'buckets': [{'id': 'weekly', 'name': group + ' weekly',
         'window': 'weekly', 'remaining_fraction': fraction,
         'reset_time': '2026-10-20T00:00:00Z'}]}
        for group in ('Gemini', '3p', 'Argon')]}}}


def codex_fixture():
    return {'rateLimitsByLimitId': {
        'codex': {'primary': {'usedPercent': 31, 'windowDurationMins': 90,
                             'resetsAt': 1792411200}, 'secondary': None},
        'review': {'primary': None, 'secondary': {'usedPercent': None,
                   'windowDurationMins': 10080, 'resetsAt': None}}},
        'accountId': 'SECRET', 'creditId': 'SECRET'}


class ParserTests(unittest.TestCase):
    def test_claude_preserves_inactive_scope_and_used_semantics(self):
        raw = json.dumps({'type': 'system', 'usage': {'tokens': 999}}) + '\n'
        buckets = parse_claude(raw + json.dumps(claude_fixture()))
        self.assertEqual(buckets[0]['used_percent'], 27)
        self.assertEqual(buckets[0]['remaining_percent'], 73)
        self.assertEqual(buckets[0]['resets_at'], '2026-10-19T12:00:00Z')
        self.assertFalse(buckets[1]['source_fields']['is_active'])
        self.assertEqual(buckets[1]['scope'], 'Fable')

    def test_claude_ids_survive_reorder_and_scope_is_whitelisted(self):
        fixture = claude_fixture()
        limits = fixture['usage_report']['rate_limits']['limits']
        limits[1]['scope']['credential'] = 'SECRET'
        limits[1]['scope']['model']['accountId'] = 'SECRET'
        original = parse_claude(json.dumps(fixture))
        limits.reverse()
        reordered = parse_claude(json.dumps(fixture))
        self.assertEqual(original[0]['id'], reordered[1]['id'])
        self.assertEqual(original[1]['id'], reordered[0]['id'])
        self.assertNotIn('SECRET', json.dumps(original))

    def test_duplicate_provider_bucket_ids_are_rejected(self):
        fixture = claude_fixture()
        limits = fixture['usage_report']['rate_limits']['limits']
        limits.append(limits[0])
        with self.assertRaises(ParseError):
            parse_claude(json.dumps(fixture))
        fixture = agy_fixture()
        fixture['command']['data']['groups'].append(fixture['command']['data']['groups'][0])
        with self.assertRaises(ParseError):
            parse_agy(json.dumps(fixture))


    def test_agy_keeps_distinct_provider_pools(self):
        buckets = parse_agy(json.dumps(agy_fixture()))
        self.assertEqual({item['group'] for item in buckets}, {'Gemini', '3p', 'Argon'})
        self.assertEqual(len({item['id'] for item in buckets}), 3)
        self.assertEqual(buckets[0]['used_percent'], 25)
        self.assertEqual(buckets[0]['remaining_percent'], 75)

    def test_codex_multi_pool_null_and_actual_window(self):
        buckets, is_blocked = parse_codex(codex_fixture())
        self.assertFalse(is_blocked)
        self.assertEqual(buckets[0]['window_minutes'], 90)
        self.assertIsNone(buckets[1]['used_percent'])
        self.assertIsNone(buckets[1]['remaining_percent'])
        self.assertNotIn('SECRET', json.dumps(buckets))

    def test_codex_block_and_legacy(self):
        payload = {'rateLimits': {'primary': {'usedPercent': 100},
                                 'ordinaryUsageAllowed': False}}
        buckets, is_blocked = parse_codex(payload)
        self.assertTrue(is_blocked)
        self.assertEqual(buckets[0]['remaining_percent'], 0)
        payload = codex_fixture()
        payload['ordinaryUsageAllowed'] = False
        self.assertTrue(parse_codex(payload)[1])

    def test_unknown_values_stay_unknown(self):
        self.assertIsNone(parse_claude(json.dumps(claude_fixture(None)))[0]['used_percent'])
        self.assertIsNone(parse_agy(json.dumps(agy_fixture(None)))[0]['remaining_percent'])

    def test_invalid_percent_rejects_entire_report(self):
        for value in (-1, 101, float('nan'), float('inf'), '30', True):
            with self.subTest(value=value), self.assertRaises(ParseError):
                parse_claude(json.dumps(claude_fixture(value)))
        for value in (-0.1, 1.1, float('nan'), True):
            with self.subTest(value=value), self.assertRaises(ParseError):
                parse_agy(json.dumps(agy_fixture(value)))
        payload = codex_fixture()
        payload['rateLimitsByLimitId']['review']['secondary']['usedPercent'] = 101
        with self.assertRaises(ParseError):
            parse_codex(payload)

    def test_never_interpret_token_usage_as_quota(self):
        with self.assertRaises(ParseError):
            parse_claude(json.dumps({'type': 'result', 'usage': {'input_tokens': 40}}))
        with self.assertRaises(ParseError):
            parse_agy(json.dumps({'usage': {'remaining_fraction': 1}}))
        with self.assertRaises(ParseError):
            parse_codex({'rateLimitsByLimitId': {'codex': {'primary': None}}})

    def test_naive_timestamp_and_invalid_window_rejected(self):
        payload = claude_fixture()
        payload['usage_report']['rate_limits']['limits'][0]['resets_at'] = '2026-10-19T00:00:00'
        with self.assertRaises(ParseError):
            parse_claude(json.dumps(payload))
        payload = codex_fixture()
        payload['rateLimitsByLimitId']['codex']['primary']['windowDurationMins'] = True
        with self.assertRaises(ParseError):
            parse_codex(payload)


class TransportTests(unittest.TestCase):
    def test_stopped_collectors_cannot_spawn_new_cli(self):
        with patch.object(collectors, '_IS_STOPPING', threading.Event()), \
             patch.object(collectors.subprocess, 'Popen') as popen:
            collectors.terminate_active_collectors()
            self.assertEqual(collectors.collect_provider('claude')['error_code'], 'command_failed')
            popen.assert_not_called()

    def test_real_sigterm_cleanup_registry_reaps_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            pid_file = Path(directory) / 'child.pid'
            child = ('import os,time; from pathlib import Path; '
                     f'Path({str(pid_file)!r}).write_text(str(os.getpid())); time.sleep(60)')
            script = f'''import signal,sys,threading,time
from tools.ai_usage import collectors
collectors.COMMANDS['claude'] = [sys.executable, '-c', {child!r}]
def stop(*args):
    collectors.terminate_active_collectors()
    raise SystemExit(0)
signal.signal(signal.SIGTERM, stop)
threading.Thread(target=collectors.collect_provider, args=('claude',)).start()
while True:
    time.sleep(1)
'''
            process = subprocess.Popen([sys.executable, '-c', script], stderr=subprocess.PIPE)
            try:
                deadline = time.monotonic() + 5
                while not pid_file.exists() and time.monotonic() < deadline:
                    time.sleep(0.02)
                self.assertTrue(pid_file.exists())
                child_pid = int(pid_file.read_text())
                process.send_signal(signal.SIGTERM)
                _, stderr = process.communicate(timeout=5)
                self.assertEqual(process.returncode, 0, stderr)
                with self.assertRaises(ProcessLookupError):
                    os.kill(child_pid, 0)
            finally:
                if process.poll() is None:
                    process.kill()
                process.communicate()

    def test_claude_probe_disables_settings_hooks_and_mcp(self):
        command = collectors.COMMANDS['claude']
        self.assertEqual(command[command.index('--setting-sources') + 1], '')
        self.assertIn('--strict-mcp-config', command)
        self.assertEqual(command[command.index('--tools') + 1], '')

    def run_fake(self, provider, script):
        with patch.dict(collectors.COMMANDS, {provider: [sys.executable, '-c', script]}):
            return collectors.collect_provider(provider)

    def test_pretty_printed_agy_and_safe_error(self):
        script = 'print(' + repr(json.dumps(agy_fixture(), indent=2)) + ')'
        self.assertEqual(self.run_fake('agy', script)['status'], 'ok')
        result = self.run_fake('agy', "print('SECRET'); raise SystemExit(5)")
        self.assertEqual(result['error_code'], 'command_failed')
        self.assertNotIn('SECRET', json.dumps(result))
        self.assertIsNone(result['observed_at'])

    def test_rpc_handshake_order_and_cleanup(self):
        script = '''import json, sys
request = json.loads(input())
assert request['method'] == 'initialize'
assert request['params']['capabilities']['experimentalApi']
print(json.dumps({'id': 1, 'result': {}}), flush=True)
assert json.loads(input())['method'] == 'initialized'
assert json.loads(input())['method'] == 'account/rateLimits/read'
print(json.dumps({'id': 2, 'result': PAYLOAD}), flush=True)
sys.stdin.read()
'''.replace('PAYLOAD', repr(codex_fixture()))
        result = self.run_fake('codex', script)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(len(result['buckets']), 2)

    def test_rpc_error_and_missing_binary(self):
        result = self.run_fake('codex', "input(); print('{\"id\":1,\"error\":{}}', flush=True)")
        self.assertEqual(result['error_code'], 'rpc_error')
        with patch.object(collectors.subprocess, 'Popen', side_effect=FileNotFoundError):
            self.assertEqual(collectors.collect_provider('claude')['error_code'], 'cli_missing')

    def test_timeout_terminates_process_group(self):
        process = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.DEVNULL, start_new_session=True)
        with patch.object(collectors.subprocess, 'Popen', return_value=process), \
             patch.object(collectors, '_command', side_effect=collectors.CollectError('timeout')):
            self.assertEqual(collectors.collect_provider('claude')['error_code'], 'timeout')
        self.assertIsNotNone(process.returncode)
        with self.assertRaises(ProcessLookupError):
            os.kill(process.pid, 0)

    def test_malformed_numeric_error_has_no_partial_buckets(self):
        script = 'print(' + repr(json.dumps(claude_fixture(float('nan')))) + ')'
        result = self.run_fake('claude', script)
        self.assertEqual(result['error_code'], 'parse_error')
        self.assertEqual(result['buckets'], [])


if __name__ == '__main__':
    unittest.main()
