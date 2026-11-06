"""Service tests use synthetic quotas and never invoke provider CLIs."""
import datetime as dt
import http.client
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import tempfile
import subprocess
import sys
import threading
import time
import unittest
from unittest.mock import patch

from tools.ai_usage import monitor, server, storage


def fixture(used=20):
    now = dt.datetime.now(dt.timezone.utc)
    provider = {'id': 'codex', 'label': 'Codex', 'status': 'ok',
                'observed_at': now.isoformat(), 'attempted_at': now.isoformat(),
                'buckets': [{'id': 'primary', 'used_percent': used,
                             'remaining_percent': 100 - used,
                             'resets_at': (now + dt.timedelta(hours=1)).isoformat()}]}
    value = monitor.empty_snapshot()
    value.update(generated_at=now.isoformat(), providers=[provider])
    return value


class StateTests(unittest.TestCase):
    def state(self, value):
        return monitor.compute(value)['providers'][0]['state']

    def test_thresholds(self):
        for used, expected in [(0, 'ok'), (80, 'warning'), (95, 'reserve'),
                               (100, 'exhausted')]:
            with self.subTest(used=used):
                self.assertEqual(self.state(fixture(used)), expected)

    def test_time_constraints(self):
        for offset, expected in [(-601, 'stale'), (61, 'unknown')]:
            value = fixture()
            value['providers'][0]['observed_at'] = dt.datetime.fromtimestamp(
                time.time() + offset, dt.timezone.utc).isoformat()
            self.assertEqual(self.state(value), expected)
        value = fixture()
        value['providers'][0]['buckets'][0]['resets_at'] = storage.timestamp()
        self.assertEqual(self.state(value), 'stale')

    def test_invalid_and_missing(self):
        for invalid in [None, True, -1, 101, float('nan'), '20']:
            value = fixture()
            value['providers'][0]['buckets'][0]['used_percent'] = invalid
            self.assertEqual(self.state(value), 'unknown')
        value = fixture()
        value['providers'][0]['buckets'] = []
        self.assertEqual(self.state(value), 'unknown')

    def test_failure_and_block(self):
        value = fixture()
        value['providers'][0]['status'] = 'error'
        self.assertEqual(self.state(value), 'unknown')
        value['providers'][0].update(status='ok', usage_blocked=True)
        self.assertEqual(self.state(value), 'exhausted')
        self.assertEqual(monitor.check(monitor.compute(value), 'codex')['exit_code'], 2)

    def test_scoped_and_unscoped(self):
        value = fixture()
        value['providers'][0]['buckets'].append({'id': 'unknown'})
        result = monitor.compute(value)
        self.assertEqual(monitor.check(result, 'codex')['exit_code'], 3)
        self.assertEqual(monitor.check(result, 'codex', 'primary')['exit_code'], 3)
        self.assertEqual(monitor.check(result, 'codex', 'missing')['exit_code'], 3)
        self.assertEqual(monitor.check(result, 'other')['exit_code'], 3)

    def test_selected_pool_keeps_shared_guards(self):
        value = fixture(10)
        value['providers'][0]['buckets'].append(dict(
            value['providers'][0]['buckets'][0], id='shared',
            used_percent=100, remaining_percent=0))
        self.assertEqual(monitor.check(monitor.compute(value), 'codex', 'primary')['exit_code'], 2)


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.runtime = Path(self.directory.name)

    def test_atomic_snapshot_and_history(self):
        value = fixture()
        storage.persist(value, self.runtime)
        self.assertEqual(storage.read_json('snapshot.json', self.runtime), value)
        self.assertEqual(storage.read_history(self.runtime), [value])
        self.assertFalse(list(self.runtime.glob('.usage-*')))

    def test_corrupted_snapshot_shapes_fail_closed(self):
        for invalid in [{'providers': 'bad'}, {'schema_version': 1, 'providers': [None]},
                        {'schema_version': 1, 'providers': [{'id': 'codex', 'buckets': 4}]}]:
            storage.save_json('snapshot.json', invalid, self.runtime)
            self.assertEqual(monitor.check(monitor.status(self.runtime), 'codex')['exit_code'], 3)

    def test_history_retention(self):
        value = fixture()
        value['generated_at'] = (dt.datetime.now(dt.timezone.utc)
                                 - dt.timedelta(days=8)).isoformat()
        storage.atomic_write(self.runtime / 'history.jsonl', json.dumps(value) + '\n')
        self.assertEqual(storage.read_history(self.runtime), [])

    def test_failed_replace_preserves_snapshot(self):
        storage.save_json('snapshot.json', {'old': True}, self.runtime)
        with patch.object(storage.os, 'replace', side_effect=OSError('test')):
            with self.assertRaises(OSError):
                storage.save_json('snapshot.json', {'new': True}, self.runtime)
        self.assertEqual(storage.read_json('snapshot.json', self.runtime), {'old': True})
        self.assertFalse(list(self.runtime.glob('.usage-*')))

    def test_refresh_lock_and_cooldown(self):
        with storage.lock('refresh.lock', self.runtime):
            self.assertEqual(monitor.refresh(self.runtime)[1], 409)
        with patch.object(monitor, 'collect', side_effect=lambda key: fixture()['providers'][0]):
            self.assertEqual(monitor.refresh(self.runtime)[1], 200)
            self.assertEqual(monitor.refresh(self.runtime)[1], 429)

    def test_failed_refresh_replaces_previous(self):
        value = fixture()
        value['generated_at'] = '2020-01-01T00:00:00+00:00'
        value['providers'][0]['attempted_at'] = value['generated_at']
        storage.persist(value, self.runtime)
        failed = dict(value['providers'][0], status='error', error_code='failed')
        with patch.object(monitor, 'collect', return_value=failed):
            monitor.refresh(self.runtime)
        self.assertEqual(monitor.check(monitor.status(self.runtime), 'codex')['exit_code'], 3)

    def test_selective_refresh_keeps_other_provider_times(self):
        value = fixture()
        storage.persist(value, self.runtime)
        original = value['providers'][0]
        with patch.object(monitor, 'collect', return_value=dict(original, id='agy')) as probe:
            self.assertEqual(monitor.refresh_provider('agy', self.runtime)[1], 200)
            self.assertEqual(monitor.refresh_provider('agy', self.runtime)[1], 429)
            probe.assert_called_once_with('agy')
        saved = monitor.status(self.runtime)
        codex = next(item for item in saved['providers'] if item['id'] == 'codex')
        self.assertEqual(codex['observed_at'], original['observed_at'])
        self.assertEqual(codex['attempted_at'], original['attempted_at'])

    def test_parallel_collection(self):
        barrier = threading.Barrier(3)
        def collect(key):
            barrier.wait(timeout=2)
            return dict(fixture()['providers'][0], id=key)
        with patch.object(monitor, 'collect', side_effect=collect):
            self.assertEqual(monitor.refresh(self.runtime)[1], 200)


class ShutdownTests(unittest.TestCase):
    def runner(self, directory, command):
        probe = ('import os,sys,time;from pathlib import Path;'
                 'Path(sys.argv[1]).write_text(str(os.getpid()));time.sleep(60)')
        script = '\n'.join([
            'from pathlib import Path', 'import sys',
            'from tools.ai_usage import collectors,monitor,server',
            f'root=Path({str(directory)!r})',
            f'collectors.COMMANDS={{key:[sys.executable,"-c",{probe!r},str(root/(key+".pid"))] for key in monitor.PROVIDERS}}',
            'original_refresh=monitor.refresh',
            'monitor.refresh=lambda runtime=root:original_refresh(runtime)',
            'original_app=server.Application',
            'server.Application=lambda:original_app(root)',
            'original_http=server.ThreadingHTTPServer',
            'server.ThreadingHTTPServer=lambda address,handler:original_http(("127.0.0.1",0),handler)',
            f'raise SystemExit(monitor.main([{command!r}]))'])
        return subprocess.Popen([sys.executable, '-c', script], stdout=subprocess.DEVNULL,
                                stderr=subprocess.PIPE, text=True)

    def test_sigterm_reaps_refresh_and_server_collectors(self):
        for command in ('refresh', 'serve'):
            with self.subTest(command=command), tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                process = self.runner(directory, command)
                try:
                    deadline = time.monotonic() + 5
                    while len(list(directory.glob('*.pid'))) < 3 and time.monotonic() < deadline:
                        time.sleep(0.02)
                    self.assertEqual(len(list(directory.glob('*.pid'))), 3)
                    pids = [int(path.read_text()) for path in directory.glob('*.pid')]
                    process.terminate()
                    _, errors = process.communicate(timeout=5)
                    self.assertNotIn('Traceback', errors)
                    for pid in pids:
                        with self.assertRaises(ProcessLookupError):
                            os.kill(pid, 0)
                    if command == 'serve':
                        self.assertFalse(storage.read_json('monitor.json', directory)['running'])
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.communicate()


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.application = server.Application(Path(self.directory.name))
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), server.handler_class(self.application))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    def request(self, method, path, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port)
        self.addCleanup(connection.close)
        connection.request(method, path, headers=headers or {})
        response = connection.getresponse()
        return response.status, response.read(), response.getheader('Cache-Control')

    def csp(self, method, path, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port)
        self.addCleanup(connection.close)
        connection.request(method, path, headers=headers or {})
        response = connection.getresponse()
        response.read()
        return response.status, response.getheader('Content-Security-Policy')

    EMBED = {'Sec-Fetch-Site': 'same-site', 'Sec-Fetch-Dest': 'iframe',
             'Sec-Fetch-Mode': 'navigate'}

    DOC = dict(EMBED, **{'Sec-Fetch-Dest': 'document'})

    def test_embed_home_allowed(self):
        code, csp = self.csp('GET', '/', self.EMBED)
        self.assertEqual(code, 200)
        self.assertIn('frame-ancestors http://127.0.0.1:8780', csp)
        self.assertNotIn("'none'", csp)
        headers = dict(self.EMBED, Referer='http://127.0.0.1:8780/index.html')
        self.assertEqual(self.request('GET', '/', headers)[0], 200)

    def test_embed_rejections(self):
        cases = [dict(self.EMBED, Referer='http://127.0.0.1:9999/'),
                 dict(self.EMBED, **{'Sec-Fetch-Site': 'cross-site'}),
                 dict(self.EMBED, **{'Sec-Fetch-Dest': 'script'}),
                 dict(self.EMBED, **{'Sec-Fetch-Dest': 'empty'}),
                 dict(self.DOC, Referer='http://127.0.0.1:9999/'),
                 dict(self.DOC, **{'Sec-Fetch-Site': 'cross-site'})]
        for headers in cases:
            self.assertEqual(self.request('GET', '/', headers)[0], 403)
        for path in ('/api/history', '/style.css'):
            self.assertEqual(self.request('GET', path, self.EMBED)[0], 403)
            self.assertEqual(self.request('GET', path, self.DOC)[0], 403)

    def test_window_navigation_allowed(self):
        self.assertEqual(self.request('GET', '/', self.DOC)[0], 200)
        headers = dict(self.DOC, Referer='http://127.0.0.1:8780/')
        self.assertEqual(self.request('GET', '/', headers)[0], 200)

    def test_embed_does_not_loosen_others(self):
        code, csp = self.csp('GET', '/api/status')
        self.assertEqual(code, 200)
        self.assertIn("frame-ancestors 'none'", csp)
        headers = {'X-Usage-Request': '1', 'Sec-Fetch-Site': 'same-site'}
        self.assertEqual(self.request('POST', '/api/refresh', headers)[0], 403)
        self.assertEqual(self.request('GET', '/')[0], 200)

    def test_read_and_path_limits(self):
        code, body, cache = self.request('GET', '/api/status')
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body)['providers'][0]['state'], 'unknown')
        self.assertEqual(cache, 'no-store')
        self.assertEqual(self.request('GET', '/../../etc/passwd')[0], 404)
        self.assertEqual(self.request('GET', '/%2e%2e/monitor.py')[0], 404)
        self.assertEqual(self.request('GET', '/api/history')[0], 200)

    def test_external_requests_rejected(self):
        self.assertEqual(self.request('GET', '/api/status', {'Host': 'evil.test'})[0], 403)
        self.assertEqual(self.request('GET', '/api/status', {'Origin': 'https://evil.test'})[0], 403)
        self.assertEqual(self.request('POST', '/api/refresh')[0], 403)
        headers = {'X-Usage-Request': '1', 'Origin': 'https://evil.test'}
        self.assertEqual(self.request('POST', '/api/refresh', headers)[0], 403)

    def test_history_uses_sampling_time(self):
        value = fixture()
        sampled = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)
        value['generated_at'] = sampled.isoformat()
        value['providers'][0]['observed_at'] = sampled.isoformat()
        value['providers'][0]['buckets'][0]['resets_at'] = (
            sampled + dt.timedelta(minutes=30)).isoformat()
        storage.persist(value, self.application.runtime)
        code, body, _ = self.request('GET', '/api/history')
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body)['entries'][0]['providers'][0]['state'], 'ok')
        self.assertEqual(monitor.status(self.application.runtime)['providers'][0]['state'], 'stale')

    def test_refresh_background_response(self):
        with patch.object(self.application, 'request_refresh', return_value=({'accepted': True}, 202)):
            self.assertEqual(self.request('POST', '/api/refresh', {'X-Usage-Request': '1'})[0], 202)


if __name__ == '__main__':
    unittest.main()
