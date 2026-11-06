"""Loopback-only dashboard API and monitor lifecycle."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import re
import threading
import time
from urllib.parse import urlsplit

from tools.ai_usage import monitor, storage

STATIC = storage.ROOT / 'workingfiles/outputs/ai-usage-dashboard'
FILES = {'/': ('index.html', 'text/html; charset=utf-8'),
         '/index.html': ('index.html', 'text/html; charset=utf-8'),
         '/style.css': ('style.css', 'text/css; charset=utf-8'),
         '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
         '/pace.js': ('pace.js', 'text/javascript; charset=utf-8'),
         '/ai-quota-board.js': ('ai-quota-board.js', 'text/javascript; charset=utf-8'),
         '/embed.html': ('embed-demo.html', 'text/html; charset=utf-8'),
         '/embed-demo.css': ('embed-demo.css', 'text/css; charset=utf-8')}
# 允許其他本機網頁服務（任一 loopback 埠）跨來源讀取的 GET 路徑；POST /api/refresh 仍限同來源。
CROSS_ORIGIN_GET = {'/api/status', '/ai-quota-board.js'}
# 只允許這些來源以 iframe 內嵌首頁 `/`；其餘路徑與來源維持禁止內嵌。
FRAME_ANCESTORS = ('http://127.0.0.1:8780',)
LOOPBACK_ORIGIN = re.compile(r'^https?://(127\.0\.0\.1|localhost|\[::1\])(:\d+)?$')


class Application:
    def __init__(self, runtime=storage.RUNTIME):
        self.runtime = runtime
        self.started_at = storage.timestamp()
        self.refresh_lock = threading.Lock()
        self.stopped = threading.Event()
        self.refresh_thread = None

    def request_refresh(self):
        if self.stopped.is_set():
            return {'error': 'stopping'}, 409
        if not self.refresh_lock.acquire(blocking=False):
            return {'error': 'refresh_in_progress'}, 409
        previous = monitor.status(self.runtime)
        attempts = [storage.epoch(item.get('attempted_at')) for item in previous['providers']]
        if len(attempts) == 3 and all(last is not None and time.time() - last < 60
                                      for last in attempts):
            self.refresh_lock.release()
            return {'error': 'cooldown'}, 429
        self.refresh_thread = threading.Thread(target=self.run_refresh)
        self.refresh_thread.start()
        return {'accepted': True}, 202

    def run_refresh(self):
        try:
            storage.heartbeat(self.started_at, True, self.runtime)
            monitor.refresh(self.runtime)
        finally:
            self.refresh_lock.release()
            if not self.stopped.is_set():
                storage.heartbeat(self.started_at, False, self.runtime)

    def run(self):
        next_refresh = 0
        while not self.stopped.is_set():
            if time.monotonic() >= next_refresh:
                self.request_refresh()
                next_refresh = time.monotonic() + 300
            if not self.stopped.is_set():
                storage.heartbeat(self.started_at, self.refresh_lock.locked(), self.runtime)
            self.stopped.wait(15)

    def stop(self, thread):
        self.stopped.set()
        monitor.terminate_collectors()
        thread.join()
        if self.refresh_thread is not None:
            self.refresh_thread.join()
        metadata = storage.read_json('monitor.json', self.runtime)
        metadata.update(running=False, refreshing=False, stopped_at=storage.timestamp())
        storage.save_json('monitor.json', metadata, self.runtime)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def respond(self, code, data, content_type='application/json; charset=utf-8', allow_origin=None, frameable=False):
        payload = (json.dumps(data, ensure_ascii=False, allow_nan=False).encode()
                   if isinstance(data, (dict, list)) else data)
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        if allow_origin:
            self.send_header('Access-Control-Allow-Origin', allow_origin)
            self.send_header('Vary', 'Origin')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        # 僅首頁 `/` 的成功回應可被 FRAME_ANCESTORS 內嵌，其餘一律禁止
        ancestors = ' '.join(FRAME_ANCESTORS) if frameable else "'none'"
        self.send_header('Content-Security-Policy', f"default-src 'self'; frame-ancestors {ancestors}")
        self.end_headers()
        self.wfile.write(payload)

    def is_local_request(self):
        authority = f'127.0.0.1:{self.server.server_port}'
        if self.headers.get('Host') != authority:
            return False
        origin = self.headers.get('Origin')
        fetch_site = self.headers.get('Sec-Fetch-Site')
        return (origin in (None, f'http://{authority}')
                and fetch_site not in ('cross-site', 'same-site'))

    def cross_origin_allowed(self, path):
        """其他 loopback 來源的網頁（如 127.0.0.1:8780 總控台）只能 GET 指定路徑。"""
        if path not in CROSS_ORIGIN_GET or self.headers.get('Host') != f'127.0.0.1:{self.server.server_port}':
            return None
        origin = self.headers.get('Origin')
        if origin is None:
            return '*' if self.headers.get('Sec-Fetch-Site') in (None, 'same-site', 'same-origin') else None
        return origin if LOOPBACK_ORIGIN.match(origin) else None

    def embed_allowed(self, path):
        """首頁 `/` 的 iframe 內嵌導覽：所有條件同時成立才放行。"""
        if path != '/' or self.headers.get('Host') != f'127.0.0.1:{self.server.server_port}':
            return False
        if self.headers.get('Origin') is not None:
            return False
        if (self.headers.get('Sec-Fetch-Site') != 'same-site'
                or self.headers.get('Sec-Fetch-Dest') != 'iframe'
                or self.headers.get('Sec-Fetch-Mode') != 'navigate'):
            return False
        referer = self.headers.get('Referer')
        if referer is not None:
            parts = urlsplit(referer)
            if f'{parts.scheme}://{parts.netloc}' not in FRAME_ANCESTORS:
                return False
        return True

    def do_GET(self):
        path = urlsplit(self.path).path
        allow_origin = None
        embedded = False
        if not self.is_local_request():
            allow_origin = self.cross_origin_allowed(path)
            embedded = not allow_origin and self.embed_allowed(path)
            if not allow_origin and not embedded:
                return self.respond(403, {'error': 'forbidden'})
        if path == '/api/status':
            return self.respond(200, monitor.status(self.application.runtime), allow_origin=allow_origin)
        if path == '/api/history':
            entries = [monitor.compute(item, now=storage.epoch(item.get('generated_at')))
                       for item in storage.read_history(self.application.runtime)
                       if storage.epoch(item.get('generated_at')) is not None]
            return self.respond(200, {'entries': entries})
        if path not in FILES:
            return self.respond(404, {'error': 'not_found'})
        filename, mime = FILES[path]
        try:
            payload = (STATIC / filename).read_bytes()
        except OSError:
            return self.respond(404, {'error': 'not_found'})
        self.respond(200, payload, mime, allow_origin=allow_origin, frameable=(path == '/'))

    def do_POST(self):
        if not self.is_local_request() or self.headers.get('X-Usage-Request') != '1':
            return self.respond(403, {'error': 'forbidden'})
        if self.path != '/api/refresh':
            return self.respond(404, {'error': 'not_found'})
        result, code = self.application.request_refresh()
        self.respond(code, result)



def handler_class(application):
    return type("UsageHandler", (Handler,), {"application": application})

def serve(port=8766):
    if not 1 <= port <= 65535:
        print(json.dumps({'error': 'invalid_port'}))
        return 3
    application = Application()
    try:
        with storage.lock('server.lock', application.runtime):
            server = ThreadingHTTPServer(('127.0.0.1', port), handler_class(application))
            thread = threading.Thread(target=application.run, daemon=True)
            print(f'http://127.0.0.1:{port}', flush=True)
            with monitor.shutdown_signals(application.stopped.set):
                thread.start()
                try:
                    server.serve_forever()
                except KeyboardInterrupt:
                    pass
                finally:
                    application.stop(thread)
                    server.server_close()
            return 0
    except BlockingIOError:
        print(json.dumps({'error': 'server_already_running'}))
        return 3
    except OSError:
        print(json.dumps({'error': 'server_unavailable'}))
        return 3
