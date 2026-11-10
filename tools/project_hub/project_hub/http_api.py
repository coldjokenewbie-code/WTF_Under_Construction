"""Validated service operations independent from HTTP framing."""
import os
import hashlib
import subprocess
from .cmux_adapter import CmuxAdapter
from .delivery import Router
from .errors import HubError
from .paths import within
from .registry import Registry
from .sessions import lines
from .state import now, snapshot
from .storage import edit_status, read_json, status_path
from .targets import Targets


def text_field(payload, key, required=False, limit=10000):
    value = payload.get(key)
    if key not in payload and not required:
        return
    if not isinstance(value, str) or len(value) > limit or (required and not value.strip()):
        raise HubError("invalid_field", f"欄位 {key} 格式無效")


class Service:
    def __init__(self, settings, mode="disabled", fixture=None):
        self.registry = Registry(settings)
        self.adapter = CmuxAdapter(fixture)
        self.targets = Targets(self.registry, self.adapter)
        self.router = Router(self.registry, self.targets, self.adapter, mode)
        self.mode, self.port = mode, None

    def project(self, payload):
        value = payload.get("project_id", payload.get("project"))
        text_field({"project_id": value}, "project_id", True, 200)
        project = self.registry.get(value)
        within(project.root, "")
        if not project.root.is_dir():
            raise HubError("project_offline", "專案工作目錄暫時離線", 409)
        return project

    def get(self, path, query):
        if path == "/api/health":
            return dict(ok=True, service="project_hub", pid=os.getpid(), delivery_mode=self.mode, port=self.port,
                        settings=str(self.registry.path.resolve()), settings_sha256=hashlib.sha256(self.registry.path.read_bytes()).hexdigest(),
                        project_ids=[project.project_id for project in self.registry.projects])
        if path == "/api/state":
            return snapshot(self.registry, self.mode)
        if path in ("/api/projects/catalog", "/api/catalog"):
            return {"candidates": self.registry.catalog()}
        if path == "/api/targets":
            return self.targets.list(self.project({key: value[0] for key, value in query.items()}))
        if path == "/api/lines":
            return lines(self.registry)
        raise HubError("not_found", "找不到 API", 404)

    def post(self, path, payload):
        if path in ("/api/projects/register", "/api/projects"):
            if set(payload) - {"candidate_id", "project_id"}:
                raise HubError("invalid_field", "註冊只接受 catalog 專案 ID")
            identifier = payload.get("candidate_id") or payload.get("project_id")
            text_field({"id": identifier}, "id", True, 100)
            return {"ok": True, "project": self.registry.register(identifier).public()}
        project = self.project(payload)
        if path == "/api/open":
            text_field(payload, "path", True, 2000)
            file_path = within(project.root, payload["path"], public=True)
            if not file_path.is_file():
                raise HubError("file_not_found", "檔案不存在", 404)
            subprocess.run(["/usr/bin/open", "-g", str(file_path)], check=True, timeout=10)
            return {"ok": True}
        text_field(payload, "exhibit", True, 160)
        if not status_path(project.data, payload["exhibit"]).is_file():
            raise HubError("exhibit_not_found", "找不到工作項目", 404)
        return self.exhibit_post(path, project, payload)

    def exhibit_post(self, path, project, payload):
        if path == "/api/bind":
            text_field(payload, "target_id", True, 100)
            return {"ok": True, "target": self.targets.bind(project, payload["exhibit"], payload["target_id"])}
        if path == "/api/answer":
            for key in ("id", "kind", "choice", "text"):
                text_field(payload, key, key == "id", 10000)
            return self.router.answer(project, payload)
        if path == "/api/resend":
            text_field(payload, "uid", True, 100)
            if "rebind" in payload and not isinstance(payload["rebind"], bool):
                raise HubError("invalid_field", "rebind 必須是布林值")
            return self.router.resend(project, payload["exhibit"], payload["uid"], payload.get("rebind", False))
        if path == "/api/todo":
            text_field(payload, "id", True, 200)
            if payload.get("state") not in ("todo", "doing", "wait", "submitted", "done"):
                raise HubError("invalid_state", "待辦狀態無效")
            def update(data):
                row = next((row for row in data.get("todos", []) if row["id"] == payload["id"]), None)
                if row is None:
                    raise HubError("todo_not_found", "找不到待辦", 404)
                row.update(state=payload["state"], by="po", at=now())
                todos = data["todos"]
                data.setdefault("progress", {}).update(done=sum(row.get("state") == "done" for row in todos), total=len(todos))
            edit_status(project, payload["exhibit"], update)
            return {"ok": True}
        raise HubError("not_found", "找不到 API", 404)
