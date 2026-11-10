"""Read provider sessions in enabled project roots; never expose conversation text."""
import datetime as dt
import json
import os
from pathlib import Path
import time
from .sessions_usage import claude_usage, codex_usage, judged
from .state import now


def alive(pid):
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def line_row(project, provider, session, name, updated, status, usage, limit, model, is_alive=True):
    state, reason, pct = judged(usage, limit, is_alive)
    return dict(line_id=f"{project.project_id}:{provider}:{session}", project_id=project.project_id,
                provider=provider, session_id=session, name=name, project=project.name, status=status,
                model=model, used_tokens=usage, limit_tokens=limit, pct=pct, state=state, reason=reason,
                updated=dt.datetime.fromtimestamp(updated).isoformat(timespec="seconds"))


def claude_lines(registry, home, timestamp):
    rows = []
    for path in (home / ".claude/sessions").glob("*.json"):
        try:
            data = json.loads(path.read_text())
            project = registry.for_cwd(data.get("cwd"))
            updated = (data.get("updatedAt") or data.get("statusUpdatedAt") or 0) / 1000
            session = data.get("sessionId")
            is_alive = alive(data.get("pid"))
            if not project or not session or (not is_alive and timestamp - updated > 86400):
                continue
            transcript = next((home / ".claude/projects").glob(f"*/{session}.jsonl"), None)
            usage = claude_usage(transcript) if transcript else {}
            model = usage.get("model")
            post = (usage.get("compact") or {}).get("post")
            used = post if post is not None else usage.get("used")
            limit = 200000 if "haiku" in (model or "") else 1000000
            rows.append(line_row(project, "claude", session, data.get("name") or f"Claude-{session[:4]}",
                                 updated, data.get("status") or "idle", used, limit, model, is_alive))
        except (OSError, ValueError, TypeError, KeyError):
            continue
    return rows


def codex_lines(registry, home, timestamp):
    rows = []
    for day in {dt.date.fromtimestamp(timestamp - shift * 86400) for shift in (0, 1)}:
        directory = home / ".codex/sessions" / f"{day:%Y/%m/%d}"
        for path in directory.glob("rollout-*.jsonl"):
            try:
                updated = path.stat().st_mtime
                with path.open() as stream:
                    metadata = json.loads(stream.readline()).get("payload") or {}
                project = registry.for_cwd(metadata.get("cwd"))
                if not project or timestamp - updated > 86400 or metadata.get("source") != "cli" or metadata.get("originator") != "codex-tui":
                    continue
                used, limit, model = codex_usage(path)
                session = metadata["id"]
                rows.append(line_row(project, "codex", session, f"Codex-{session[-4:]}", updated,
                                     "busy" if timestamp - updated < 90 else "idle", used, limit, model))
            except (OSError, ValueError, TypeError, KeyError):
                continue
    return rows


def lines(registry):
    timestamp, home = time.time(), Path.home()
    rows = claude_lines(registry, home, timestamp) + codex_lines(registry, home, timestamp)
    unique = {row["line_id"]: row for row in sorted(rows, key=lambda row: row["updated"])}
    return dict(ok=True, now=now(), lines=list(unique.values()),
                thresholds=dict(tired_pct=70, down_pct=90, limit_default=1000000, auto_compact_tokens=967000))
