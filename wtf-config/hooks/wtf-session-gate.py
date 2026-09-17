#!/usr/bin/env python3
"""Fail-closed receipt gate for WTF session instructions."""
from __future__ import annotations
import hashlib, json, os, re, secrets, sys, time
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
def canonical(path: Path) -> str:
    """正規化路徑。兩個不得依賴 cwd 的理由（2026-09-16 文件主控 session 實例）：
    1) 相對字串（Bash 指令文字等）resolve() 會呼叫 getcwd()，session 的 cwd 在 Drive 上被
       FileProvider 重建 inode 後 getcwd 直接 EPERM，每次工具呼叫都被 fail-closed 成全域 deny；
    2) 不可讀／未掛載的外部絕對路徑 resolve() 也可能拋 OSError。
    因此：相對路徑一律不 resolve、只做字串正規化（受保護路徑全是絕對路徑，commonpath 對相對
    字串本來就不可能命中，子字串檢查另在 protected() 內保留）；絕對路徑 resolve 失敗退回原字串，
    絕不在 except 內再呼叫任何會碰 cwd 的函式（abspath 也會）。"""
    raw = str(path)
    if not path.is_absolute():
        return os.path.normcase(os.path.normpath(raw))
    try:
        return os.path.normcase(str(path.resolve()))
    except OSError as error:
        print(f"wtf-session-gate: canonical fallback for {raw} ({error})", file=sys.stderr)
        return os.path.normcase(os.path.normpath(raw))
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
def quarantine_state_file(path: Path, why: str) -> None:
    """只對 wtf-session-state 下的狀態檔：損壞即改名 .corrupt-<ts> 並留 stderr，下一次呼叫視為不存在
    → init／補讀可重建（ch06 第 2 輪：狀態 JSON 損壞否則＝全 deny＋Stop block 無復原路徑）。
    bundle／manifest 等共用檔絕不隔離。"""
    try:
        state_root = canonical(home() / ".claude" / "wtf-session-state")
        if os.path.commonpath((canonical(path), state_root)) != state_root:
            return
        target = path.with_name(f"{path.name}.corrupt-{time.strftime('%Y%m%dT%H%M%S')}-{secrets.token_hex(3)}")
        path.rename(target)
        print(f"wtf-session-gate: quarantined corrupt state file {path.name} -> {target.name} ({why})", file=sys.stderr)
    except Exception as error:
        print(f"wtf-session-gate: quarantine failed for {path} ({error})", file=sys.stderr)
QUARANTINE_ENABLED = True   # doctor 進入時關閉：唯讀承諾（Codex 第 3 輪）
def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        if QUARANTINE_ENABLED: quarantine_state_file(path, str(error))
        raise GateError(f"invalid JSON {path}: {error}") from error
    except OSError as error:
        raise GateError(f"invalid JSON {path}: {error}") from error
    if not isinstance(value, dict):
        if QUARANTINE_ENABLED: quarantine_state_file(path, "not a JSON object")
        raise GateError(f"JSON object required: {path}")
    return value
def load_recovery(path: Path) -> dict:
    """recovery.json 讀取＋形狀驗證：used 必須是 dict[str, list[str]]、fused 必須是 bool；
    形狀錯視同損壞（隔離並拋錯），否則 used=null 這類會在 recovery_state／recovery_read 拋
    AttributeError 落到放行捕捉之外（Codex 第 3 輪 L402）。"""
    if not path.exists():
        return {"schema": 1, "used": {}}
    value = read_json(path)
    used = value.get("used", {})
    shape_ok = isinstance(used, dict) and all(isinstance(k, str) and isinstance(v, list) and all(isinstance(x, str) for x in v)
                                             for k, v in used.items()) and isinstance(value.get("fused", False), bool)
    if not shape_ok:
        if QUARANTINE_ENABLED: quarantine_state_file(path, "recovery.json shape invalid")
        raise GateError(f"recovery.json shape invalid: {path}")
    value["used"] = used
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
def bundle_sha_from_claude_md() -> str | None:
    """CLAUDE.md 的 managed import block 由 sync_config.py 每次 sync 自動改寫，是當代 bundle SHA
    的權威來源；env var／event 欄位是手動覆寫用，不會隨 sync 換代，容易變成陳舊設定（見
    2026-07-21 session-gate 診斷）。"""
    claude_md = home() / ".claude" / "CLAUDE.md"
    if not claude_md.exists():
        return None
    m = re.search(r"@wtf-session-bundles/([0-9a-f]{64})/GLOBAL\.md",
                  claude_md.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else None
def choose_bundle(event: dict) -> tuple[Path, str, dict]:
    base = home() / ".claude" / "wtf-session-bundles"
    selected = (event.get("bundle_sha256") or os.environ.get("WTF_BUNDLE_SHA256")
                or bundle_sha_from_claude_md())
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
ROTATE_SOURCES = {"resume", "compact", "compaction", "clear"}
RECOVERY_ATTEMPTS = 3
def create_generation(directory: Path, bundle: Path, bundle_hash: str, created_by: str) -> None:
    """以 O_EXCL 原子創建 generation.json——並行的 init／多個 InstructionsLoaded 只有一個建成，
    其餘讀既有共用同 generation，避免互相覆蓋造成部分收據 generation 對不上而失效。"""
    directory.mkdir(parents=True, exist_ok=True)
    value = {"schema": 1, "generation": secrets.token_hex(16), "previous_generation": None,
             "bundle_sha256": bundle_hash, "bundle_path": str(bundle),
             "created_by": created_by, "created_at": now()}
    encoded = (json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    try:
        fd = os.open(directory / "generation.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return
    with os.fdopen(fd, "wb") as output:
        output.write(encoded)
        output.flush()
        os.fsync(output.fileno())
def cmd_init(event: dict, require_agent: bool) -> None:
    directory = state_dir(event, require_agent)
    bundle, bundle_hash, _ = choose_bundle(event)
    gen_path = directory / "generation.json"
    if event.get("source") in ROTATE_SOURCES:
        # 明確旋轉（resume/compact/clear）：SessionStart 單一、無並行，覆蓋語意安全。
        previous = read_json(gen_path).get("generation") if gen_path.exists() else None
        atomic_json(gen_path, {"schema": 1, "generation": secrets.token_hex(16),
                               "previous_generation": previous, "bundle_sha256": bundle_hash,
                               "bundle_path": str(bundle), "created_by": "init", "created_at": now()})
    else:
        # startup：O_EXCL 建；若 InstructionsLoaded 已先建則尊重既有，不覆蓋（否則作廢其收據）。
        create_generation(directory, bundle, bundle_hash, "init")
def cmd_instructions(event: dict) -> None:
    directory = state_dir(event)
    if not (directory / "generation.json").exists():
        # 事件先於 init 到達：自建 generation（O_EXCL 並行安全）。bundle 由事件 file_path 推導，
        # 不靠 choose_bundle（多 bundle 過渡期會 ambiguous）。事件本身即 loader 已處理檔案的證據。
        try:
            fp = Path(str(event.get("file_path", ""))).resolve()
        except OSError as error:
            raise GateError(f"cannot resolve InstructionsLoaded file_path {event.get('file_path')!r}: {error}") from error
        bdir = fp.parent
        bhash = bdir.name
        if re.fullmatch(r"[0-9a-f]{64}", bhash) and (bdir / "manifest.json").is_file() \
           and digest(bdir / "manifest.json") == bhash:
            create_generation(directory, bdir, bhash, "instructions")
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
PATH_FIELDS = {"file_path", "path", "notebook_path", "old_path", "new_path", "directory", "cwd"}
def protected(event: dict) -> bool:
    """受保護路徑檢查，兩道各自獨立（2026-09-16 Codex 審查：原本寫在同一個 or 裡，commonpath 遇
    相對／絕對混用拋 ValueError 會連子字串檢查一起跳過，含受保護路徑的 Bash 指令文字漏攔）：
    1) 子字串：任一字串值含受保護絕對路徑 → True（涵蓋 Bash 指令文字）。
    2) 路徑欄位：相對路徑用**事件自帶的 cwd**（不呼叫行程 getcwd，cwd 失效時也能判）接成絕對路徑，
       再做 commonpath；接不出絕對路徑者視為無法判定，保守回 True。"""
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return True   # 畸形事件無法判定 → 保守擋（Codex 第 2 輪）
    protected_paths = [home() / ".claude" / "wtf-session-state",
                       home() / ".claude" / "wtf-session-bundles",
                       home() / ".claude" / "settings.json",
                       home() / ".claude" / "settings.local.json", SCRIPT_DIR]
    guards = [canonical(g) for g in protected_paths]
    # 子字串比對同時用「已 resolve」與「未 resolve 的 home」兩種寫法（macOS /var ↔ /private/var）。
    raw_home = Path(os.environ.get("WTF_GATE_HOME", str(Path.home())))
    raw_paths = [raw_home / ".claude" / "wtf-session-state", raw_home / ".claude" / "wtf-session-bundles",
                 raw_home / ".claude" / "settings.json", raw_home / ".claude" / "settings.local.json", SCRIPT_DIR]
    guard_texts = set(guards) | {os.path.normcase(str(g)) for g in protected_paths + raw_paths}
    event_cwd = str(event.get("cwd") or "")
    for key, value in tool_input.items():
        if not isinstance(value, (str, Path)):
            continue
        text = os.path.normcase(str(value))
        if any(g in text for g in guard_texts):
            return True
        if key not in PATH_FIELDS or str(event.get("tool_name", "")).startswith("mcp__"):
            continue     # MCP 工具的 path 多是邏輯鍵（如 Artifact read_file path="index.html"），不當檔案系統路徑解析
        raw = os.path.expanduser(str(value))
        if not os.path.isabs(raw):
            if not os.path.isabs(event_cwd):
                return True          # 相對路徑且無可信 cwd：無法判定，保守擋下
            raw = os.path.join(event_cwd, raw)
        candidate = canonical(Path(raw))
        for guard in guards:
            try:
                if os.path.commonpath((candidate, guard)) == guard:
                    return True
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
    recovery = load_recovery(path)
    generation_id = current["generation"]
    # 2026-09-16 移除「連續兩代都靠補讀→熔斷」規則：resume／compact 會換代，但 harness 是否重發
    # InstructionsLoaded 不可靠（HsinchuSEC 第六章 session 105 次 deny 永久死鎖；互動機具 session 則
    # 2 分鐘後才收到事件）。補讀本身已受「每代每檔一次」限制，連續代熔斷只把 harness 的不可靠
    # 升級成無法自救的死鎖。舊版寫下的該類熔斷視為過期，自動解除。
    if recovery.get("fused") and recovery.get("warning") == "consecutive generations require recovery":
        recovery.pop("fused", None); recovery["warning"] = "legacy consecutive-generation fuse cleared"
        recovery["warning_at"] = now()
    if recovery.get("fused"):
        return False
    used = recovery.setdefault("used", {}).setdefault(generation_id, [])
    # 補讀額度：每代每檔 3 次（原本 1 次）。PreToolUse 在 Read 真正完成前就扣額度，Read 若被其他
    # hook／權限擋下或中斷，1 次額度會被白白燒掉直接熔斷（Codex 審查）。收據只由 postread 在成功
    # 回應後寫，重複放行不會憑空產生收據，3 次只是給失敗留餘裕。
    if used.count(matches[0]) >= RECOVERY_ATTEMPTS:
        recovery.update({"fused": True, "warning": "recovery did not produce a receipt",
                         "warning_at": now()})
        atomic_json(path, recovery)
        return False
    used.append(matches[0])
    recovery["last_recovery_generation"] = generation_id
    atomic_json(path, recovery)
    return True
def cmd_pretool(event: dict) -> dict | None:
    if event.get("agent_id"):
        # subagent 工具呼叫略過收據檢查：初始化 subagent 收據要靠 SubagentStart 事件，
        # 官方確認不可靠、常不觸發（github.com/anthropics/claude-code/issues/27755，已
        # close 標 not planned）——硬查收據會永久 deny 所有 subagent 的每次工具呼叫。
        # 仍保留受保護路徑檢查。
        return deny("WTF protected session path") if protected(event) else None
    directory, current, manifest, missing = missing_receipts(event)
    if not missing:
        return deny("WTF protected session path") if protected(event) else None
    if recovery_read(directory, current, manifest, missing, event):
        return None
    return deny(recovery_notice(directory, current, missing))
def recovery_state(directory: Path, current: dict) -> dict:
    """唯讀：熔斷與各檔剩餘補讀次數。"""
    recovery = load_recovery(directory / "recovery.json")
    used = recovery["used"].get(current.get("generation"), [])
    remaining = {name: max(0, RECOVERY_ATTEMPTS - used.count(name)) for name in policy()["required_sources"]}
    legacy = recovery.get("warning") == "consecutive generations require recovery"
    return {"fused": bool(recovery.get("fused")) and not legacy, "legacy_fuse": bool(recovery.get("fused")) and legacy,
            "warning": recovery.get("warning"), "remaining": remaining}
def recovery_notice(directory: Path, current: dict, missing: list[str]) -> str:
    """deny／block 訊息：原因碼＋餘額＋一句可執行復原（ch06 2026-09-16：原訊息在熔斷時仍叫人補讀、
    不說已熔斷、不給餘額，模型白燒 99 次）。"""
    state = recovery_state(directory, current)
    paths = [str(Path(current["bundle_path"]) / name) for name in missing]
    if state["fused"]:
        return ("WTF session gate: reason=FUSE_TRIPPED (" + str(state["warning"]) + "). In-session recovery is "
                "exhausted; do NOT retry Read. Tell the user to run:\n"
                f"  python3 {SCRIPT_DIR / 'wtf-session-gate.py'} doctor {directory.parent.name}\n"
                "(doctor only diagnoses, it does not repair) or start a new session.")
    listing = "\n".join(f"{i}. {p}  (remaining attempts: {state['remaining'].get(missing[i-1], 0)})"
                        for i, p in enumerate(paths, 1))
    return ("WTF session gate: reason=RECEIPT_MISSING. Call Read separately for EACH file below "
            "(one file_path per Read call, no offset/limit). Each attempt consumes one of the remaining "
            "attempts for that file; a successful Read writes the receipt automatically:\n" + listing)
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
    path = directory / "recovery.json"
    recovery = read_json(path) if path.exists() else {"schema": 1, "used": {}}
    used = recovery.get("used", {}).get(current["generation"], [])
    matches = []
    for name in missing:
        source, record = source_info(current, manifest, name)
        if name in used and full_read(event, source, record["lines"]):
            matches.append(name)
    if len(matches) != 1:
        raise GateError("Read was not an authorised full-source recovery")
    write_receipt(directory, current, matches[0], "recovery", "PostToolUse", "not_applicable")
def allow_stop(reason: str, directory: Path | None, state: dict | None) -> None:
    """放行結束（不可再 block）：稽核寫入盡力而為，失敗只記 stderr（Codex 第 2 輪 P1）。"""
    print(f"wtf-session-gate: stop allowed — {reason}", file=sys.stderr)
    if directory is not None:
        try:
            atomic_json(directory / f"audit-stop-unrecoverable-{secrets.token_hex(8)}.json",
                        {"schema": 1, "warning": reason, "state": state, "created_at": now()})
        except Exception as error:
            print(f"wtf-session-gate: audit write failed ({error})", file=sys.stderr)
def cmd_stop(event: dict) -> dict | None:
    directory = state_dir(event)            # identity 錯誤照舊往外拋 → block（畸形事件不放行）
    try:
        directory, current, _, missing = missing_receipts(event)
    except Exception as error:
        # 狀態損壞／bundle 消失：session 內無法復原，block 只會永久卡住使用者。
        allow_stop(f"gate state unusable ({type(error).__name__}: {error}); session cannot self-recover", directory, None)
        return None
    if not missing:
        return None
    try:
        state = recovery_state(directory, current)
        notice = recovery_notice(directory, current, missing)
    except Exception as error:
        allow_stop(f"recovery state unusable ({type(error).__name__}: {error}); session cannot self-recover", directory, None)
        return None
    if state["fused"]:
        # session 內已無復原路徑：再 block 只會無限空轉（ch06 實例：使用者喊停仍被擋）。
        # 工具層 PreToolUse 仍 fail-closed，這裡放行「結束」並留稽核，讓使用者另開 session。
        allow_stop("recovery fused, session cannot self-recover", directory, state)
        return None
    return {"decision": "block", "reason": "全域設定尚未載入，不可結束。" + notice}
def cmd_doctor(event: dict) -> int:
    """唯讀診斷：不改任何狀態、不依賴 cwd、逐項容錯。用法：
    echo '{"session_id":"…"}' | gate.py doctor   或   gate.py doctor <session_id>"""
    global QUARANTINE_ENABLED
    QUARANTINE_ENABLED = False   # 唯讀：診斷不改名任何檔
    report: dict = {"session_id": event.get("session_id"), "ok": True, "problems": []}
    def problem(msg: str) -> None:
        report["ok"] = False; report["problems"].append(msg)
    try:
        directory = state_dir(event)
    except GateError as error:
        problem(f"state_dir: {error}"); print(json.dumps(report, ensure_ascii=False, indent=2)); return 1
    report["state_dir"] = str(directory)
    gen_path = directory / "generation.json"
    if not gen_path.exists():
        problem("generation.json missing (init／InstructionsLoaded never ran for this session)")
        print(json.dumps(report, ensure_ascii=False, indent=2)); return 1
    try:
        current = read_json(gen_path)
    except Exception as error:
        problem(f"generation.json unreadable: {error}"); print(json.dumps(report, ensure_ascii=False, indent=2)); return 1
    report["generation"] = {k: current.get(k) for k in ("generation", "previous_generation", "bundle_sha256", "bundle_path", "created_by", "created_at")}
    bundle = Path(str(current.get("bundle_path", "")))
    report["bundle_exists"] = bundle.is_dir()
    if not bundle.is_dir():
        problem(f"bundle directory missing: {bundle}")
    manifest = None
    try:
        _, _, manifest = generation(event)
    except Exception as error:
        problem(f"bundle／manifest: {type(error).__name__}: {error}")
    report["receipts"] = {}
    for name in policy()["required_sources"]:
        rp = directory / f"{Path(name).stem}.receipt.json"
        entry: dict = {"file": str(bundle / name), "receipt_exists": rp.exists()}
        if rp.exists():
            try:
                r = read_json(rp)
                entry.update({"generation_match": r.get("generation") == current.get("generation"),
                              "bundle_match": r.get("bundle_sha256") == current.get("bundle_sha256"),
                              "load_reason": r.get("load_reason"), "event": r.get("event"), "created_at": r.get("created_at")})
            except Exception as error:
                entry["error"] = f"{type(error).__name__}: {error}"
        try:
            entry["valid"] = bool(manifest) and valid_receipt(directory, current, manifest, name)
        except Exception as error:
            entry["valid"] = False; entry["error"] = f"{type(error).__name__}: {error}"
        if not entry["valid"]:
            problem(f"receipt invalid or missing: {name}")
        report["receipts"][name] = entry
    try:
        report["recovery"] = recovery_state(directory, current)
    except Exception as error:
        report["recovery"] = {"fused": False, "legacy_fuse": False, "warning": None, "remaining": {}}
        problem(f"recovery.json unreadable: {type(error).__name__}: {error}")
    if report["recovery"].get("legacy_fuse"):
        problem("legacy consecutive-generation fuse: auto-clears on the next full Read of a listed file")
    if report["recovery"]["fused"]:
        problem("recovery fused: session cannot self-recover; start a new session")
    report["next_step"] = ("OK — tools should be allowed" if report["ok"] else
                           ("start a new session" if report["recovery"]["fused"] else
                            "in the session: Read each listed file fully (one per call); receipts are written on success"))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1
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
def describe_failure(error: Exception, event: dict | None) -> str:
    """失敗訊息帶上工具名與 tool_input 內的路徑候選，讓收到 deny 的 session 能直接定位是哪個路徑出事。"""
    reason = f"{type(error).__name__}: {error}"
    try:  # 錯誤描述本身絕不能再拋錯——拋了就沒有 deny 輸出，hook 以 exit 1 結束＝fail-open（Codex 審查）
        if isinstance(event, dict):
            tool_input = event.get("tool_input")
            tool_input = tool_input if isinstance(tool_input, dict) else {}
            paths = [str(v) for k, v in tool_input.items()
                     if isinstance(v, str) and ("/" in v or "\\" in v) and k in PATH_FIELDS | {"command"}]
            context = f" [tool={event.get('tool_name')}"
            if paths:
                context += " inputs=" + "; ".join(p[:200] for p in paths[:3])
            reason += context + "]"
    except Exception:
        pass
    return reason
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
    event = None
    if len(sys.argv) == 3 and sys.argv[1] == "doctor":
        try:
            return cmd_doctor({"session_id": sys.argv[2]})
        except Exception as error:
            print(json.dumps({"ok": False, "problems": [f"doctor crashed: {type(error).__name__}: {error}"]})); return 1
    command = sys.argv[1] if len(sys.argv) == 2 else ""
    commands = {"init", "init-agent", "instructions", "pretool", "postread", "stop", "stop-agent", "doctor"}
    if command not in commands: return emit_failure(command, "expected one supported subcommand")
    try:
        event = parse_stdin()
        if command == "doctor":          # 唯讀診斷：在 bypass 稽核之前，絕不寫任何狀態
            try:
                return cmd_doctor(event)
            except Exception as error:
                print(json.dumps({"ok": False, "problems": [f"doctor crashed: {type(error).__name__}: {error}"]})); return 1
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
        return emit_failure(command, describe_failure(error, event))
if __name__ == "__main__":
    raise SystemExit(main())
