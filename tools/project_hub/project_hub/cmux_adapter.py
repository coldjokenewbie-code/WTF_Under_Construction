"""No terminal typing. Read only discovery; sending is gated by the router."""
import json
import re
import subprocess
from .storage import read_json


def agent_hook(agents):
    return len(agents) == 1 and agents[0].get("has_hook_lifecycle_state") is True


class CmuxAdapter:
    def __init__(self, fixture=None):
        self.fixture = fixture

    def discover(self):
        if self.fixture:
            return read_json(self.fixture, {}).get("targets", [])
        result = subprocess.run(["cmux", "--json", "current", "--limit", "200"], capture_output=True, text=True, timeout=10)
        if result.returncode:
            raise RuntimeError((result.stderr or result.stdout).strip()[:200])
        payload = json.loads(result.stdout)
        return self.projections(payload)

    @staticmethod
    def projections(payload):
        rows = []
        for item in payload.get("items", []):
            agents = [agent for agent in item.get("agents", []) if agent.get("state") != "ended"]
            projections = item.get("projections", [])
            is_verified = len(agents) == 1 and len(projections) == 1
            omitted = item.get("omitted", {}).get("agents", 0)
            is_verified = is_verified and (not omitted or agent_hook(agents))
            is_verified = is_verified and item.get("kind") == "terminal" and item.get("lifecycle") == "running"
            is_verified = is_verified and item.get("freshness", {}).get("state") == "current"
            agent, projection = (agents or [{}])[0], (projections or [{}])[0]
            rows.append(dict(cwd=item.get("cwd"), name=item.get("label"), provider=agent.get("kind"),
                             session_id=agent.get("session_id"), recipient_id=projection.get("panel_id"),
                             surface_id=projection.get("panel_id"), workspace_id=projection.get("workspace_id"),
                             is_verified=is_verified, diagnostic="歷史工作線清單部分省略；綁定目前唯一 hook 工作線" if omitted else ""))
        return rows

    def send(self, target, text):
        if self.fixture:
            return read_json(self.fixture, {}).get("send_result", {"state": "failed", "err": "fixture無send_result", "safe_retry": True})
        try:
            result = subprocess.run(["cmux", "agent", "message", target["recipient_id"],
                                     "--from", "指揮中心", "--", text], capture_output=True, text=True, timeout=15)
        except OSError as error:
            return {"state": "failed", "err": str(error)[:200], "safe_retry": True}
        except subprocess.TimeoutExpired as error:
            return {"state": "uncertain", "err": str(error)[:200]}
        match = re.search(r"\bQueued(?: message)?\s+([0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12})\b", result.stdout)
        if result.returncode == 0 and match:
            return {"state": "queued", "receipt_id": match.group(1), "err": ""}
        # An unrecognised result cannot establish whether the external side accepted it.
        return {"state": "uncertain", "err": (result.stderr or result.stdout or "無法確認外部傳送結果")[:200]}

    def receipt(self, target, identifier):
        if self.fixture:
            rows = read_json(self.fixture, {}).get("messages", [])
        else:
            result = subprocess.run(["cmux", "--json", "agent", "inbox", "--surface", target["recipient_id"], "--limit", "200"],
                                    capture_output=True, text=True, timeout=10)
            if result.returncode:
                return None
            payload = json.loads(result.stdout)
            rows = payload.get("messages", [])
        return next((row for row in rows if row.get("id") == identifier
                     and row.get("recipient_surface_id") == target["recipient_id"]
                     and row.get("recipient_workspace_id") == target["workspace_id"]), None)
