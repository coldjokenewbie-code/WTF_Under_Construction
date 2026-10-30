#!/usr/bin/env python3
"""Run the session Stop gate and ody lint; combine every block decision."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
GATE = HERE / "wtf-session-gate.py"
ODY = REPO / "tools" / "ody" / "squad" / "stop_hook.py"


def run_hook(path: Path, payload: dict, args: list[str] = []) -> tuple[dict | None, str | None]:
    completed = subprocess.run(
        [sys.executable, str(path), *args], input=json.dumps(payload), text=True,
        capture_output=True, timeout=30, check=False)
    if completed.returncode != 0:
        return None, f"{path.name} exited {completed.returncode}: {completed.stderr.strip()}"
    if not completed.stdout.strip():
        return None, None
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        return None, f"{path.name} emitted malformed JSON: {error}"
    return result, None


def main() -> int:
    try:
        raw = sys.stdin.read()
        if raw.strip() == "":
            try:
                log_path = os.path.expanduser("~/.claude/wtf-session-state/empty-stdin.log")
                os.makedirs(os.path.dirname(log_path), exist_ok=True)
                try:
                    cwd = os.getcwd()
                except Exception:
                    cwd = "cwd-unavailable"
                timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
                subcommand = sys.argv[1] if len(sys.argv) > 1 else ""
                program = f"stop_dispatcher {subcommand}".strip()
                argv_text = " ".join(sys.argv[1:])
                with open(log_path, "a", encoding="utf-8") as log_file:
                    log_file.write(f"{timestamp}\t{program}\t{cwd}\t{argv_text}\n")
            except Exception:
                pass
            sys.exit(0)
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("hook input must be an object")
    except Exception as error:
        print(f"stop_dispatcher: {error}", file=sys.stderr)
        print(json.dumps({"decision": "block", "reason": f"stop dispatcher error: {error}"}))
        return 0
    blocks = []
    gate_result, gate_error = run_hook(GATE, payload, ["stop"])
    if gate_error:
        blocks.append(gate_error)
    elif gate_result and gate_result.get("decision") == "block":
        blocks.append(str(gate_result.get("reason", "session gate blocked")))
    ody_payload = dict(payload)
    ody_payload["stop_hook_active"] = False
    ody_result, ody_error = run_hook(ODY, ody_payload)
    if ody_error:
        blocks.append(ody_error)
    elif ody_result and ody_result.get("decision") == "block":
        blocks.append(str(ody_result.get("reason", "ody lint blocked")))
    if blocks:
        print(json.dumps({"decision": "block", "reason": " | ".join(blocks)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
