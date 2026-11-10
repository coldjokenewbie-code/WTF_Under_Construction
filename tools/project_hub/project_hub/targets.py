"""Explicit, verifiable provider/session identities. Never infer an agent from a shell."""
import hashlib
import re
import subprocess
from .errors import HubError
from .state import now
from .storage import edit_status

UUID = re.compile(r"^[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$")
IDENTITY = ("project_id", "provider", "session_id", "recipient_id", "surface_id", "workspace_id")


def identity_id(target):
    value = "|".join(str(target.get(key, "")) for key in IDENTITY)
    return hashlib.sha256(value.encode()).hexdigest()[:24]


def normalize(row, registry):
    project = registry.for_cwd(row.get("cwd") or row.get("root"))
    provider = row.get("provider") or row.get("agent") or row.get("agent_type") or ""
    session = row.get("session_id") or row.get("sessionId") or ""
    recipient = row.get("recipient_id") or row.get("agent_id") or ""
    target = dict(project_id=project.project_id if project else "", provider=provider, session_id=session,
                  recipient_id=recipient, surface_id=row.get("surface_id") or "",
                  workspace_id=row.get("workspace_id") or "", name=row.get("name") or provider or "未知工作線")
    target["line_id"] = f"{target['project_id']}:{provider}:{session}"
    target["target_id"] = identity_id(target)
    is_valid = project is not None and provider in ("claude", "codex") and bool(session) and row.get("is_verified") is True
    is_valid = is_valid and all(UUID.fullmatch(target[key]) for key in ("recipient_id", "surface_id", "workspace_id"))
    target.update(can_bind=bool(is_valid), reason=row.get("diagnostic", "") if is_valid else "缺少可核對的專案、provider/session 或 UUID 身分")
    return target


class Targets:
    def __init__(self, registry, adapter):
        self.registry, self.adapter = registry, adapter

    def list(self, project):
        try:
            rows = [normalize(row, self.registry) for row in self.adapter.discover() if isinstance(row, dict)]
            return {"targets": [row for row in rows if row["project_id"] == project.project_id], "diagnostics": []}
        except (OSError, RuntimeError, ValueError, TypeError, subprocess.SubprocessError) as error:
            return {"targets": [], "diagnostics": [str(error)[:240]]}

    def verified(self, project, target_id):
        row = next((row for row in self.list(project)["targets"] if row["target_id"] == target_id and row["can_bind"]), None)
        if row is None:
            raise HubError("target_unverified", "工作線身分無法核對，請重新連結", 409)
        return row

    def bind(self, project, exhibit, target_id):
        row = self.verified(project, target_id)
        target = {key: row[key] for key in (*IDENTITY, "line_id", "target_id", "name")}
        target.update(root=str(project.root), bound_at=now(), binding_version=1)
        edit_status(project, exhibit, lambda value: value.update(target=target))
        return target

    def validate_snapshot(self, project, target):
        if not target or target.get("root") != str(project.root):
            return False
        result = self.list(project)
        if result["diagnostics"]:
            return None
        current = next((row for row in result["targets"] if row["target_id"] == target.get("target_id") and row["can_bind"]), None)
        if current is None:
            return False
        return all(current.get(key) == target.get(key) for key in IDENTITY)
