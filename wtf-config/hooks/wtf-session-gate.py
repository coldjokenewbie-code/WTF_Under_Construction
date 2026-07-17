#!/usr/bin/env python3
"""Fail-closed receipt gate for WTF session instructions."""
from __future__ import annotations
import hashlib, json, os, re, secrets, sys
from datetime import datetime, timezone; from pathlib import Path
IDS = re.compile(r"^[A-Za-z0-9._-]+$"); KNOWN_REASONS = {"include", "compact"}
SCRIPT_DIR = Path(__file__).resolve().parent; DEFAULT_POLICY = SCRIPT_DIR.parent / "policies" / "session-policy.json"
class GateError(RuntimeError): pass
def now() -> str: return datetime.now(timezone.utc).isoformat()
def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
def canonical(path: Path) -> str: return os.path.normcase(str(path.resolve()))
def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / f".{path.name}.{secrets.token_hex(8)}.tmp"
    encoded = (json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    try:
        with temporary.open("xb") as output:
            output.write(encoded)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise GateError(f"invalid JSON {path}: {error}") from error
    if not isinstance(value, dict):
        raise GateError(f"JSON object required: {path}")
    return value
def home() -> Path: return Path(os.environ.get("WTF_GATE_HOME", str(Path.home()))).resolve()
def identity(event: dict, require_agent: bool = False) -> tuple[str, str]:
    session = event.get("session_id")
    agent = event.get("agent_key") or event.get("agent_id") or event.get("subagent_id")
    if not session or not IDS.fullmatch(str(session)):
        raise GateError("invalid or missing session_id")
    if require_agent and not agent:
        raise GateError("missing agent key")
    agent = str(agent or "main")
    if not IDS.fullmatch(agent):
        raise GateError("invalid agent key")
    return str(session), agent
def state_dir(event: dict, require_agent: bool = False) -> Path:
    session, agent = identity(event, require_agent)
    path = home() / ".claude" / "wtf-session-state" / session / agent
    if path.exists() and path.is_symlink():
        raise GateError(f"state path cannot be a symlink: {path}")
    return path
def policy() -> dict:
    path = Path(os.environ.get("WTF_GATE_POLICY", str(DEFAULT_POLICY)))
    value = read_json(path)
    if value.get("schema") != 1 or not isinstance(value.get("required_sources"), list):
        raise GateError("unsupported session policy")
    return value
def choose_bundle(event: dict) -> tuple[Path, str, dict]:
    base = home() / ".claude" / "wtf-session-bundles"
    selected = event.get("bundle_sha256") or os.environ.get("WTF_BUNDLE_SHA256")
    candidates = [item for item in base.iterdir() if item.is_dir()] if base.exists() else []
    if selected:
        bundle = base / str(selected)
    elif len(candidates) == 1:
        bundle = candidates[0]
        selected = bundle.name
    else:
        raise GateError("bundle_sha256 is required when bundle selection is ambiguous")
    if not bundle.is_dir() or bundle.is_symlink() or not re.fullmatch(r"[0-9a-f]{64}", str(selected)):
        raise GateError("invalid bundle")
    manifest_path = bundle / "manifest.json"
    if digest(manifest_path) != str(selected):
        raise GateError("manifest hash does not match bundle directory")
    manifest = read_json(manifest_path)
    if manifest.get("schema") != 1 or not isinstance(manifest.get("sources"), dict):
        raise GateError("unsupported bundle manifest")
    required = policy()["required_sources"]
    if any(name not in manifest["sources"] for name in required):
        raise GateError("bundle lacks required sources")
    return bundle.resolve(), str(selected), manifest
def generation(event: dict) -> tuple[Path, dict, dict]:
    directory = state_dir(event)
    current = read_json(directory / "generation.json")
    bundle = Path(current.get("bundle_path", "")); manifest_path = bundle / "manifest.json"
    if bundle.is_symlink() or bundle.name != current.get("bundle_sha256") or digest(manifest_path) != bundle.name: raise GateError("active bundle manifest mismatch")
    manifest = read_json(manifest_path)
    return directory, current, manifest
def source_info(current: dict, manifest: dict, name: str) -> tuple[Path, dict]:
    record = manifest.get("sources", {}).get(name)
    source = Path(current["bundle_path"]) / name
    if not isinstance(record, dict) or source.is_symlink() or not source.is_file():
        raise GateError(f"invalid source: {name}")
    if canonical(source.parent) != canonical(Path(current["bundle_path"])):
        raise GateError(f"source outside bundle: {name}")
    if digest(source) != record.get("sha256") or source.stat().st_size != record.get("bytes"):
        raise GateError(f"source hash or size mismatch: {name}")
    return source, record
def valid_receipt(directory: Path, current: dict, manifest: dict, name: str) -> bool:
    try:
        receipt = read_json(directory / f"{Path(name).stem}.receipt.json")
        source, record = source_info(current, manifest, name)
        return all((receipt.get("schema") == 1,
                    receipt.get("generation") == current.get("generation"),
                    receipt.get("bundle_sha256") == current.get("bundle_sha256"),
                    receipt.get("source_path") == canonical(source),
                    receipt.get("source_sha256") == record.get("sha256"),
                    receipt.get("load_reason") in KNOWN_REASONS | {"recovery"}))
    except GateError:
        return False
def missing_receipts(event: dict) -> tuple[Path, dict, dict, list[str]]:
    directory, current, manifest = generation(event)
    missing = [name for name in policy()["required_sources"]
               if not valid_receipt(directory, current, manifest, name)]
    return directory, current, manifest, missing
def write_receipt(directory: Path, current: dict, name: str, reason: str,
                  event_name: str, parent_check: str) -> None:
    manifest = read_json(Path(current["bundle_path"]) / "manifest.json")
    source, record = source_info(current, manifest, name)
    receipt = {"schema": 1, "generation": current["generation"],
               "bundle_sha256": current["bundle_sha256"], "source_path": canonical(source),
               "source_sha256": record["sha256"], "bytes": record["bytes"],
               "event": event_name, "load_reason": reason,
               "parent_check": parent_check, "created_at": now()}
    atomic_json(directory / f"{Path(name).stem}.receipt.json", receipt)
def cmd_init(event: dict, require_agent: bool) -> None:
    directory = state_dir(event, require_agent)
    bundle, bundle_hash, _ = choose_bundle(event)
    previous = None
    if (directory / "generation.json").exists():
        previous = read_json(directory / "generation.json").get("generation")
    value = {"schema": 1, "generation": secrets.token_hex(16),
             "previous_generation": previous, "bundle_sha256": bundle_hash,
             "bundle_path": str(bundle), "created_at": now()}
    atomic_json(directory / "generation.json", value)
def cmd_instructions(event: dict) -> None:
    directory, current, manifest = generation(event)
    reason = event.get("load_reason")
    if reason not in KNOWN_REASONS:
        raise GateError(f"unknown load_reason: {reason!r}")
    path = Path(str(event.get("file_path", "")))
    matched = [name for name in policy()["required_sources"]
               if canonical(path) == canonical(Path(current["bundle_path"]) / name)]
    if len(matched) != 1:
        raise GateError("InstructionsLoaded path is not a required bundle source")
    source_info(current, manifest, matched[0])
    parent = event.get("parent_file_path")
    parent_check = "unavailable"
    if parent is not None:
        expected = Path(os.environ.get("WTF_GATE_PARENT", str(home() / ".claude" / "CLAUDE.md")))
        if canonical(Path(str(parent))) != canonical(expected):
            raise GateError("parent_file_path does not match expected importing CLAUDE.md")
        parent_check = "matched"
    write_receipt(directory, current, matched[0], str(reason),
                  "InstructionsLoaded", parent_check)
def deny(reason: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}
def full_read(event: dict, source: Path, total_lines: int) -> bool:
    if event.get("tool_name") != "Read":
        return False
    tool_input = event.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("path")
    offset, limit = tool_input.get("offset", 1), tool_input.get("limit")
    return (path is not None and canonical(Path(str(path))) == canonical(source)
            and isinstance(offset, int) and offset <= 1
            and (limit is None or isinstance(limit, int) and limit >= total_lines))
def protected(event: dict) -> bool:
    tool_input = event.get("tool_input") or {}
    values = [str(value) for value in tool_input.values() if isinstance(value, (str, Path))]
    protected_paths = [home() / ".claude" / "wtf-session-state",
                       home() / ".claude" / "wtf-session-bundles",
                       home() / ".claude" / "settings.json",
                       home() / ".claude" / "settings.local.json", SCRIPT_DIR]
    for value in values:
        candidate = canonical(Path(value))
        for guarded in protected_paths:
            guard = canonical(guarded)
            try:
                if os.path.commonpath((candidate, guard)) == guard or guard in os.path.normcase(value): return True
            except ValueError:
                continue
    return False
def recovery_read(directory: Path, current: dict, manifest: dict,
                  missing: list[str], event: dict) -> bool:
    matches = []
    for name in missing:
        source, record = source_info(current, manifest, name)
        if full_read(event, source, record["lines"]):
            matches.append(name)
    if len(matches) != 1:
        return False
    path = directory / "recovery.json"
    recovery = read_json(path) if path.exists() else {"schema": 1, "used": {}}
    generation_id = current["generation"]
    previous = current.get("previous_generation")
    if recovery.get("fused") or (previous and recovery.get("last_recovery_generation") == previous):
        recovery.update({"fused": True, "warning": "consecutive generations require recovery",
                         "warning_at": now()})
        atomic_json(path, recovery)
        return False
    used = recovery.setdefault("used", {}).setdefault(generation_id, [])
    if matches[0] in used:
        recovery.update({"fused": True, "warning": "recovery did not produce a receipt",
                         "warning_at": now()})
        atomic_json(path, recovery)
        return False
    used.append(matches[0])
    recovery["last_recovery_generation"] = generation_id
    atomic_json(path, recovery)
    return True
def cmd_pretool(event: dict) -> dict | None:
    directory, current, manifest, missing = missing_receipts(event)
    if not missing:
        return deny("WTF protected session path") if protected(event) else None
    if recovery_read(directory, current, manifest, missing, event):
        return None
    paths = ", ".join(str(Path(current["bundle_path"]) / name) for name in missing)
    return deny("WTF session receipt missing. To recover, Read the full file(s): " + paths)
def response_succeeded(event: dict) -> bool:
    response = event.get("tool_response")
    if response is None:
        return False
    if isinstance(response, dict):
        return not response.get("is_error") and not response.get("error") and response.get("success", True) is not False
    return bool(str(response))
def cmd_postread(event: dict) -> None:
    if event.get("tool_name") != "Read" or not response_succeeded(event):
        raise GateError("PostToolUse is not a successful Read")
    directory, current, manifest, missing = missing_receipts(event)
    if not missing:
        return  # 收據已齊：一般 Read 不是復原，安靜放行
    recovery = read_json(directory / "recovery.json")
    used = recovery.get("used", {}).get(current["generation"], [])
    matches = []
    for name in missing:
        source, record = source_info(current, manifest, name)
        if name in used and full_read(event, source, record["lines"]):
            matches.append(name)
    if len(matches) != 1:
        raise GateError("Read was not an authorised full-source recovery")
    write_receipt(directory, current, matches[0], "recovery", "PostToolUse", "not_applicable")
def cmd_stop(event: dict) -> dict | None:
    _, current, _, missing = missing_receipts(event)
    if missing:
        paths = ", ".join(str(Path(current["bundle_path"]) / name) for name in missing)
        return {"decision": "block",
                "reason": "全域設定尚未載入，不可結束。立即用 Read 工具完整讀取（不設 offset/limit）：" + paths}
    return None
def audit_bypass(event: dict) -> None:
    root = home() / ".claude" / "wtf-session-state"
    try:
        session, agent = identity(event)
        root = root / session / agent
    except GateError:
        root = root / "_unknown"
    atomic_json(root / f"audit-warning-{secrets.token_hex(8)}.json",
                {"schema": 1, "warning": "WTF_SESSION_GATE_BYPASS=1", "created_at": now()})
def parse_stdin() -> dict:
    try:
        value = json.load(sys.stdin)
    except Exception as error:
        raise GateError(f"malformed hook JSON: {error}") from error
    if not isinstance(value, dict):
        raise GateError("hook input must be a JSON object")
    return value
def emit_failure(command: str, reason: str) -> int:
    print(f"wtf-session-gate: {reason}", file=sys.stderr)
    if command == "pretool":
        print(json.dumps(deny("WTF session gate error: " + reason)))
        return 0
    if command in {"stop", "stop-agent"}:
        print(json.dumps({"decision": "block", "reason": "WTF session gate error: " + reason}))
        return 0
    return 2
def main() -> int:
    command = sys.argv[1] if len(sys.argv) == 2 else ""
    commands = {"init", "init-agent", "instructions", "pretool", "postread", "stop", "stop-agent"}
    if command not in commands: return emit_failure(command, "expected one supported subcommand")
    try:
        event = parse_stdin()
        if os.environ.get("WTF_SESSION_GATE_BYPASS") == "1":
            audit_bypass(event)
            return 0
        if command in {"init", "init-agent"}:
            cmd_init(event, command == "init-agent")
        elif command == "instructions":
            cmd_instructions(event)
        elif command == "pretool":
            output = cmd_pretool(event)
            if output:
                print(json.dumps(output))
        elif command == "postread":
            cmd_postread(event)
        else:
            if command == "stop-agent": identity(event, True)
            output = cmd_stop(event)
            if output:
                print(json.dumps(output))
        return 0
    except Exception as error:
        return emit_failure(command, str(error))
if __name__ == "__main__":
    raise SystemExit(main())
