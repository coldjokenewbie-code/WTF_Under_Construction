#!/usr/bin/env python3
"""Run the session Stop gate and ody lint; combine every block decision."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
GATE = HERE / "wtf-session-gate.py"
ODY = REPO / "tools" / "ody" / "squad" / "stop_hook.py"


def run_hook(path: Path, payload: dict) -> tuple[dict | None, str | None]:
    completed = subprocess.run(
        [sys.executable, str(path)], input=json.dumps(payload), text=True,
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
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("hook input must be an object")
    except Exception as error:
        print(f"stop_dispatcher: {error}", file=sys.stderr)
        print(json.dumps({"decision": "block", "reason": f"stop dispatcher error: {error}"}))
        return 0
    blocks = []
    gate_result, gate_error = run_hook(GATE, payload)
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
