#!/usr/bin/env python3
"""Loopback-only shared hub. Defaults to disabled delivery, including recover/resend."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import sys
import threading
import urllib.parse
if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "project_hub"
from .errors import HubError
from .http_api import Service
from .paths import within
from .review_assets import REVIEW_CSP, inject_one_item

WEB = Path(__file__).resolve().parents[1] / "web"


class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, content_type="application/json; charset=utf-8", csp=None):
        encoded = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        for name, value in (("Content-Type", content_type), ("Content-Length", str(len(encoded))),
                            ("Cache-Control", "no-store"), ("X-Content-Type-Options", "nosniff")):
            self.send_header(name, value)
        if csp:
            self.send_header("Content-Security-Policy", csp)
        self.end_headers()
        self.wfile.write(encoded)

    def guarded(self, callback):
        try:
            allowed = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
            if self.headers.get("Host") not in allowed:
                raise HubError("invalid_host", "拒絕非本機 Host", 403)
            callback()
        except HubError as error:
            self.send(error.status, error.payload())
        except (ValueError, TypeError, KeyError, UnicodeError) as error:
            self.send(400, {"error": "請求或資料格式無效", "code": "invalid_request"})
        except Exception as error:
            self.send(500, {"error": f"服務暫時無法處理：{type(error).__name__}", "code": "internal_error"})

    def do_GET(self):
        self.guarded(self.get)

    def get(self):
        url = urllib.parse.urlsplit(self.path)
        path = urllib.parse.unquote(url.path)
        if path.startswith("/api/"):
            return self.send(200, self.server.service.get(path, urllib.parse.parse_qs(url.query)))
        if path in ("/", "/index.html"):
            file_path = within(WEB, "index.html", public=True)
        elif path.startswith("/static/"):
            file_path = within(WEB, path[len("/static/"):], public=True)
        elif path.startswith("/f/"):
            identifier, _, relative = path[len("/f/"):].partition("/")
            project = self.server.service.registry.get(identifier)
            file_path = within(project.root, relative, public=True)
            return self.file(file_path, is_review=True)
        else:
            raise HubError("not_found", "找不到頁面", 404)
        return self.file(file_path)

    def file(self, path, is_review=False):
        if not path.is_file():
            raise HubError("not_found", "找不到檔案", 404)
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        body, csp = path.read_bytes(), None
        if is_review and path.suffix.lower() in (".html", ".htm", ".svg", ".xhtml"):
            csp = REVIEW_CSP
            if path.suffix.lower() in (".html", ".htm"):
                body = inject_one_item(body)
        self.send(200, body, content_type, csp)

    def do_POST(self):
        self.guarded(self.post)

    def post(self):
        origin = self.headers.get("Origin")
        if origin not in {f"http://127.0.0.1:{self.server.server_port}", f"http://localhost:{self.server.server_port}"}:
            raise HubError("invalid_origin", "拒絕不同來源的寫入", 403)
        if self.headers.get_content_type() != "application/json":
            raise HubError("invalid_content_type", "只接受 application/json", 415)
        length = int(self.headers.get("Content-Length", "0"))
        if not 0 < length <= 65536:
            raise HubError("invalid_length", "請求大小必須介於1與65536 bytes", 413)
        payload = json.loads(self.rfile.read(length))
        if not isinstance(payload, dict):
            raise HubError("invalid_request", "JSON 必須是物件")
        self.send(200, self.server.service.post(self.path, payload))

    def log_message(self, *_args):
        return


def make_server(service, port):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.service = service
    service.port = server.server_port
    return server


def retry_loop(service, stop):
    while not stop.wait(30):
        service.router.retry_tick()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--settings", required=True)
    parser.add_argument("--port", type=int, default=8780)
    parser.add_argument("--delivery-mode", choices=("disabled", "enabled"), default="disabled")
    parser.add_argument("--transport-fixture")
    args = parser.parse_args(argv)
    service = Service(args.settings, args.delivery_mode, args.transport_fixture)
    server = make_server(service, args.port)
    service.router.recover()
    stop = threading.Event()
    threading.Thread(target=retry_loop, args=(service, stop), daemon=True).start()
    try:
        server.serve_forever()
    finally:
        stop.set()
        server.server_close()


if __name__ == "__main__":
    main()
