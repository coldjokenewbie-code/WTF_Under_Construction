"""Bounded, numeric-only transcript usage extraction."""
import json

_CACHE = {}


def tail_lines(path, size=512 * 1024):
    with path.open("rb") as stream:
        start = max(0, path.stat().st_size - size)
        stream.seek(start)
        lines = stream.read().splitlines()
    return lines[1:] if start else lines


def claude_usage(path):
    stat = path.stat()
    key = (str(path), stat.st_size, stat.st_mtime_ns)
    if key in _CACHE:
        return _CACHE[key]
    result = {"model": None, "used": None, "compact": None, "error": None}
    for size in (256 * 1024, 2 * 1024 * 1024, 16 * 1024 * 1024, 32 * 1024 * 1024):
        for line in reversed(tail_lines(path, size)):
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if not isinstance(row, dict):
                continue
            if row.get("isSidechain"):
                continue
            if row.get("subtype") == "compact_boundary" and result["compact"] is None:
                compact = row.get("compactMetadata") or {}
                result["compact"] = {"pre": compact.get("preTokens"), "post": compact.get("postTokens")}
            if row.get("isApiErrorMessage"):
                if result["error"] is None and result["compact"] is None:
                    result["error"] = row.get("error") or "unknown"
                continue
            message = row.get("message") or {}
            if row.get("type") == "assistant" and isinstance(message, dict) and message.get("model") and message["model"] != "<synthetic>":
                usage = message.get("usage") or {}
                result["model"] = message["model"]
                result["used"] = sum(usage.get(field) or 0 for field in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
                _CACHE[key] = result
                return result
        if stat.st_size <= size:
            break
    return result


def codex_usage(path):
    used, limit, model = None, None, "codex"
    for line in reversed(tail_lines(path)):
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if not isinstance(row, dict):
            continue
        payload = row.get("payload") or {}
        if row.get("type") == "event_msg" and payload.get("type") == "token_count" and used is None:
            info = payload.get("info") or {}
            used = (info.get("last_token_usage") or {}).get("input_tokens")
            limit = info.get("model_context_window")
        if row.get("type") == "turn_context" and model == "codex":
            model = payload.get("model") or "codex"
        if used is not None and model != "codex":
            break
    return used, limit, model


def judged(used, limit, is_alive=True):
    pct = round(used * 100 / limit, 1) if used is not None and limit else None
    if not is_alive:
        return "down", "行程已不存在，工作線需重新連結", pct
    if pct is not None and pct >= 90:
        return "down", f"脈絡 {pct:.0f}%，建議壓縮或重開", pct
    if pct is not None and pct >= 70:
        return "tired", f"脈絡 {pct:.0f}%，建議壓縮", pct
    return "normal", f"脈絡 {pct:.0f}%" if pct is not None else "還沒有用量紀錄", pct
