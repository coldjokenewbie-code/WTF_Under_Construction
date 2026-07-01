#!/usr/bin/env python3
"""ody Stop hook — Tyrion 守門：Claude 每次收尾前，lint 最後一則回覆。

命中「禁詞」→ block 並要求重寫（強制，非自律）。過長只警示不 block（避免迴圈）。
防迴圈：stop_hook_active=true 時直接放行。fail-open：任何例外一律放行(exit 0)。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
try:
    from reply_lint import lint
except Exception:
    sys.exit(0)


def last_assistant_text(transcript_path: str) -> str:
    text = ""
    for line in Path(transcript_path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        role = obj.get("role") or obj.get("type")
        if role != "assistant":
            continue
        msg = obj.get("message", obj)
        content = msg.get("content", "")
        if isinstance(content, list):
            parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
            text = "".join(parts) or text
        elif isinstance(content, str):
            text = content or text
    return text


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("stop_hook_active"):
        return 0  # 防無限迴圈
    tp = data.get("transcript_path")
    if not tp or not Path(tp).exists():
        return 0
    try:
        text = last_assistant_text(tp)
        violations = [v for v in lint(text) if v.startswith("禁詞")]  # 只對禁詞硬擋
    except Exception:
        return 0
    if violations:
        reason = "ody-lint 攔截（Tyrion）：" + "；".join(violations) + "。請移除後以極簡、結論先行重寫本則回覆。"
        print(json.dumps({"decision": "block", "reason": reason}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
