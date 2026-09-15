#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_config.py — WTF 設定真相源同步腳本
真相源(SSOT): wtf-config/AGENTS.md、CLAUDE_CODE.md、skills/
用途: 把 SSOT 實體複製到各專案 AGENTS.md 與本機 ~/.claude/（取代跨平台失效的 symlink）

子命令:
  python sync_config.py check     掃描所有專案 AGENTS.md 與 ~/.claude/，回報 OK / 失效，不改檔
  python sync_config.py sync      把 SSOT 實體複製到每個專案 AGENTS.md 與 ~/.claude/
  python sync_config.py register  偵測本機並寫入 machines.md（每台電腦首次執行）
  python sync_config.py status    彙整本機所有註冊專案的現況＋git＋最新 TaskLog（治理/可視，唯讀）
  python sync_config.py dashboard 產 outputs/dashboard.html：現況＋git＋待辦的網頁儀表板（RWD，手機友善）
  python sync_config.py inbox-info 輸出 JSON：本機 inbox vault 路徑＋待分流「工作」開頭檔＋專案路由表（供 /inbox skill）
  python sync_config.py chat-instruction 組 Claude Chat 的 Project Instruction → outputs/chat-project-instruction.md（改正本後重產、貼回 claude.ai）

設計備註:
  - Drive 不支援跨平台 symlink，故改用實體複製。
  - 產生的副本頂部含 HTML 註記標頭，用於辨識「自動產生」並比對是否過期。
  - 失效偵測為內容式判斷，與機器無關，Cowork 沙盒內亦可執行。
  - ~/.claude/ 部署：CLAUDE_CODE.md → ~/.claude/CLAUDE.md，skills/ → ~/.claude/skills/
"""
import sys
import shutil
import socket
import platform
import datetime
import subprocess
import html
import re
from pathlib import Path

from skill_catalog import check_skill_set, deploy_skill_set, read_skills

SCRIPT_DIR = Path(__file__).resolve().parent          # .../wtf-config
SSOT = SCRIPT_DIR / "AGENTS.md"                        # 真相源
SSOT_CLAUDE = SCRIPT_DIR / "CLAUDE_CODE.md"            # ~/.claude/CLAUDE.md 真相源
SSOT_CODEX = SCRIPT_DIR / "CODEX.md"                   # ~/.codex/AGENTS.md 真相源（Codex 原生讀 AGENTS.md）
SSOT_GEMINI = SCRIPT_DIR / "GEMINI.md"                 # ~/.gemini/GEMINI.md 真相源（Antigravity 原生讀 GEMINI.md）
SSOT_SKILLS = SCRIPT_DIR / "skills"                    # ~/.claude/skills/ 真相源
SSOT_AGENTS = SCRIPT_DIR / "agents"                    # ~/.claude/agents/ 真相源（subagent 定義，如 ody-verifier）
REPO_ROOT = SCRIPT_DIR.parent                         # WTF repo 根（已移出 Drive，供 register 記錄）
MACHINES = SCRIPT_DIR / "machines.md"
CLAUDE_DIR = Path.home() / ".claude"
REGISTRY = SCRIPT_DIR / "projects-registry.md"         # 專案註冊表（取代 extra-scan-dirs.txt 與 PROJECTS_DIR 推導）
INBOX_CONFIG = SCRIPT_DIR / "inbox-config.md"          # 語音速記 inbox 的 per-machine vault 路徑

MARK_BEGIN = "<!-- WTF-AUTOGEN:AGENTS"
MARK_END = "WTF-AUTOGEN:END -->"

SSOT_GLOBAL = SCRIPT_DIR / "GLOBAL.md"                 # session bundle 來源（GLOBAL 全域設定；AGENTS 用 SSOT）
BUNDLE_BEGIN = "# >>> WTF-SESSION-BUNDLE (managed by sync_config.py, do not edit) >>>"
BUNDLE_END = "# <<< WTF-SESSION-BUNDLE <<<"


def _load_bundle_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("wtf_bundle", SCRIPT_DIR / "hooks" / "wtf_bundle.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def strip_bundle_block(text):
    """移除 CLAUDE.md 尾端 managed import block，回傳純本體（用於與 SSOT 比對）。"""
    pattern = re.compile(r"\n*" + re.escape(BUNDLE_BEGIN) + r".*?" + re.escape(BUNDLE_END) + r"\n*",
                         re.DOTALL)
    return pattern.sub("\n", text)


def build_bundle_block(sha):
    return (BUNDLE_BEGIN + "\n"
            + f"@wtf-session-bundles/{sha}/GLOBAL.md\n"
            + f"@wtf-session-bundles/{sha}/AGENTS.md\n"
            + BUNDLE_END + "\n")


def bundle_sha_in_claude_md():
    """讀 ~/.claude/CLAUDE.md 的 managed block，回傳 import 的 bundle SHA（無則 None）。"""
    claude_md = CLAUDE_DIR / "CLAUDE.md"
    if not claude_md.exists():
        return None
    m = re.search(r"@wtf-session-bundles/([0-9a-f]{64})/GLOBAL\.md",
                  claude_md.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else None


def deploy_session_bundle():
    """copy2 部署 CLAUDE.md 後呼叫：產生/確認 bundle，並在 CLAUDE.md 尾端寫入當代 SHA 的 import block。
    根因修正——import 由此自動維護，不再手改部署副本（手改必被下次 sync 洗掉）。"""
    if not (SSOT_GLOBAL.exists() and SSOT.exists()):
        return None, ["  - 略過 session bundle（GLOBAL.md/AGENTS.md 真相源不存在）"]
    try:
        mod = _load_bundle_module()
        bundle = mod.create_bundle(SSOT_GLOBAL, SSOT, home=Path.home(),
                                   max_source_bytes=100000, max_source_lines=3000)
        sha = bundle.name
    except Exception as e:
        return None, [f"  ! session bundle 產生失敗（{e}）"]
    claude_md = CLAUDE_DIR / "CLAUDE.md"
    if not claude_md.exists():
        return sha, ["  ! 略過 bundle import（~/.claude/CLAUDE.md 不存在）"]
    body = strip_bundle_block(claude_md.read_text(encoding="utf-8")).rstrip() + "\n\n"
    claude_md.write_text(body + build_bundle_block(sha), encoding="utf-8")
    return sha, [f"  v 寫入 ~/.claude/CLAUDE.md session bundle import（SHA {sha[:12]}…）"]


def check_bundle_integrity():
    """機檢：CLAUDE.md import SHA ＝ bundle 目錄名 ＝ manifest digest，且 bundle 內容與當前 SSOT 一致。
    回傳 (ok: bool|None, notes: list)。ok=None＝未部署 import，由 check_claude_dir 判失敗。"""
    import hashlib
    notes = []
    sha = bundle_sha_in_claude_md()
    if sha is None:
        return None, ["  ! [MISSING] session bundle import 未部署"]
    bundle_dir = CLAUDE_DIR / "wtf-session-bundles" / sha
    manifest = bundle_dir / "manifest.json"
    if not manifest.exists():
        return False, [f"  x [BROKEN ] bundle {sha[:12]}… 目錄或 manifest 不存在"]
    digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
    if digest != sha:
        return False, [f"  x [BROKEN ] manifest digest 與目錄名不符（{digest[:12]}…≠{sha[:12]}…）"]
    for name, ssot in (("GLOBAL.md", SSOT_GLOBAL), ("AGENTS.md", SSOT)):
        bfile = bundle_dir / name
        if not bfile.exists() or not ssot.exists():
            return False, [f"  x [BROKEN ] bundle 或 SSOT 缺 {name}"]
        if hashlib.sha256(bfile.read_bytes()).hexdigest() != hashlib.sha256(ssot.read_bytes()).hexdigest():
            return False, [f"  x [STALE  ] bundle 的 {name} 與當前 SSOT 不一致（需重跑 sync）"]
    notes.append(f"  v [OK     ] session bundle import SHA/manifest/SSOT 三者一致（{sha[:12]}…）")
    return True, notes


def ts():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def read_ssot():
    if not SSOT.exists():
        sys.exit(f"[錯誤] 找不到真相源: {SSOT}")
    return SSOT.read_text(encoding="utf-8")


def build_copy(ssot_body, hostname):
    header = (
        f"{MARK_BEGIN} | 真相源: wtf-config/AGENTS.md | "
        f"由 sync_config.py 產生 | 最後同步: {ts()} | 機器: {hostname} | "
        f"請勿手動編輯，改源頭後重跑 sync。 {MARK_END}\n\n"
    )
    return header, header + ssot_body


def extract_body(text):
    if MARK_BEGIN in text and MARK_END in text:
        idx = text.find(MARK_END)
        return text[idx + len(MARK_END):].lstrip("\n")
    return None


def looks_like_symlink_remnant(text):
    lines = [l for l in text.splitlines() if l.strip()]
    if len(lines) == 1 and "wtf-config/AGENTS.md" in lines[0]:
        return True
    return False


def registry_rows():
    """讀 projects-registry.md（專案為主格式），回傳本機相關的 row dict 清單。

    registry 表頭：| project | github | <hostname-A> | <hostname-B> | ...
    依本機 hostname 找對應「機器欄」，回傳 [{project, github, path}]。
    只含 path 非佔位（非全形「（」開頭）且非空的列；不檢查目錄是否存在。
    """
    if not REGISTRY.exists():
        sys.exit(f"[錯誤] 找不到專案註冊表: {REGISTRY}")
    hostname = socket.gethostname()
    rows = []
    header = None
    host_idx = None
    gh_idx = None
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if header is None:                            # 第一個表格列＝表頭
            header = cols
            if hostname in header:
                host_idx = header.index(hostname)
            if "github" in header:
                gh_idx = header.index("github")
            continue
        if cols and set("".join(cols)) <= {"-", " "}:  # 分隔列 |---|
            continue
        if host_idx is None:                          # 本機無對應欄
            continue
        if len(cols) <= host_idx:
            continue
        project = cols[0]
        path = cols[host_idx]
        github = cols[gh_idx] if (gh_idx is not None and len(cols) > gh_idx) else ""
        if not path or path.startswith("（"):          # 佔位/未部署
            continue
        rows.append({"project": project, "github": github, "path": path})
    if host_idx is None:
        print(f"  ! [WARN] registry 表頭無本機 hostname 欄: {hostname}", file=sys.stderr)
    return rows


def registry_dirs():
    """回傳本機 hostname 對應、實際存在的專案目錄清單。"""
    dirs = []
    for row in registry_rows():
        p = Path(row["path"])
        if p.is_dir():
            dirs.append(p)
        else:
            print(f"  ! [WARN] registry 路徑不存在，略過: {row['project']} → {row['path']}", file=sys.stderr)
    return dirs


def inbox_vault():
    """讀 inbox-config.md，回傳本機 hostname 對應的 (vault_path, clippings_dir) 或 (None, None)。

    表格：| machine (hostname) | vault_path | inbox 子夾 |
    佔位（全形「（」開頭）視為未設定。
    """
    if not INBOX_CONFIG.exists():
        return None, None
    hostname = socket.gethostname()
    for line in INBOX_CONFIG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 3:
            continue
        machine, vault, subdir = cols[0], cols[1], cols[2]
        if machine != hostname:
            continue
        if not vault or vault.startswith("（"):
            return None, None
        return vault, str(Path(vault) / subdir)
    return None, None


def cmd_inbox_info():
    """輸出本機 inbox 分流所需資訊（JSON）：vault clippings 路徑、待分流檔、專案路由表。

    供 /inbox skill 跨平台取資料（自行處理 Windows 反斜線）。
    """
    import json
    vault, clippings = inbox_vault()
    pending = []
    if clippings and Path(clippings).is_dir():
        for f in sorted(Path(clippings).iterdir()):
            if f.is_file() and f.name.startswith("工作"):
                pending.append(f.name)
    projects = [{"project": r["project"], "path": r["path"],
                 "github": r["github"], "has_github": not r["github"].startswith("（")}
                for r in registry_rows()]
    out = {
        "hostname": socket.gethostname(),
        "vault": vault,
        "clippings": clippings,
        "ingested": str(Path(vault) / "Ingested") if vault else None,
        "pending": pending,
        "projects": projects,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def classify(target, ssot_body):
    if not target.exists():
        return ("MISSING", "檔案不存在")
    text = target.read_text(encoding="utf-8", errors="replace")
    body = extract_body(text)
    if body is not None:
        if body.rstrip() == ssot_body.rstrip():
            return ("OK", "與真相源一致")
        return ("STALE", "自動產生但內容與真相源不符（源頭已更新）")
    if not text.strip():
        return ("BROKEN", "空檔")
    if looks_like_symlink_remnant(text):
        return ("BROKEN", "Drive 失效 symlink 殘跡（單行路徑）")
    if text.rstrip() == ssot_body.rstrip():
        return ("ADOPT", "無標頭但內容與真相源一致，sync 將補標頭接管")
    return ("FOREIGN", "非自動產生的內容（疑似手改或他用），sync 不會覆蓋")


def check_claude_dir():
    """回傳 (claude_md_ok, skills_ok, 說明list)"""
    notes = []
    claude_md = CLAUDE_DIR / "CLAUDE.md"
    skills_ok = None  # 內容與索引統一由 _check_skills 驗證

    if not SSOT_CLAUDE.exists():
        notes.append(f"  ! [SKIP  ] ~/.claude/CLAUDE.md — 真相源 {SSOT_CLAUDE} 不存在")
        claude_md_ok = None
    elif not claude_md.exists():
        notes.append(f"  x [MISSING] ~/.claude/CLAUDE.md")
        claude_md_ok = False
    elif claude_md.is_symlink():
        notes.append(f"  x [SYMLINK] ~/.claude/CLAUDE.md — 仍為 symlink，需改為實體檔")
        claude_md_ok = False
    elif strip_bundle_block(claude_md.read_text(encoding="utf-8", errors="replace")).rstrip() == SSOT_CLAUDE.read_text(encoding="utf-8").rstrip():
        # 去掉 managed bundle block 後比對本體；block 由 deploy_session_bundle 維護，另有機檢
        notes.append(f"  v [OK     ] ~/.claude/CLAUDE.md")
        claude_md_ok = True
    else:
        notes.append(f"  x [STALE  ] ~/.claude/CLAUDE.md — 內容與真相源不符")
        claude_md_ok = False

    bundle_ok, bundle_notes = check_bundle_integrity()
    notes.extend(bundle_notes)
    if bundle_ok is not True:
        claude_md_ok = False
        if bundle_ok is None:
            notes.append("  x [MISSING] Claude session bundle import 必須存在")

    # subagent 定義（~/.claude/agents/，per-machine 部署洞要主動驗）
    if SSOT_AGENTS.exists():
        agents_dst = CLAUDE_DIR / "agents"
        missing = []
        for src in sorted(SSOT_AGENTS.glob("*.md")):
            dst = agents_dst / src.name
            if not dst.exists() or dst.read_text(encoding="utf-8", errors="replace").rstrip() \
                    != src.read_text(encoding="utf-8").rstrip():
                missing.append(src.name)
        if missing:
            notes.append(f"  x [STALE  ] ~/.claude/agents/ — 缺/不符：{missing}")
        else:
            n = len(list(SSOT_AGENTS.glob('*.md')))
            notes.append(f"  v [OK     ] ~/.claude/agents/ （{n} 個 agent）")

    return claude_md_ok, skills_ok, notes


def deploy_claude_dir():
    """部署 Claude bootstrap、session bundle 與 subagent 定義。"""
    results = []
    CLAUDE_DIR.mkdir(exist_ok=True)

    # 絕對路徑錨點：供 session-start／CLAUDE.md 從任何 cwd（含非 WTF 專案）定位 WTF repo 讀 SSOT
    try:
        (CLAUDE_DIR / "wtf-root.txt").write_text(str(REPO_ROOT), encoding="utf-8")
        results.append(f"  v 寫入 ~/.claude/wtf-root.txt（{REPO_ROOT}）")
    except Exception as e:
        results.append(f"  ! 略過 ~/.claude/wtf-root.txt（{e}）")

    if SSOT_CLAUDE.exists():
        dst = CLAUDE_DIR / "CLAUDE.md"
        if dst.is_symlink():
            dst.unlink()
        shutil.copy2(SSOT_CLAUDE, dst)
        results.append(f"  v 寫入 ~/.claude/CLAUDE.md")
        # copy2 用 SSOT 覆蓋 CLAUDE.md（洗掉 import block），故在此後自動重寫 bundle import——根因修正點
        _, bundle_notes = deploy_session_bundle()
        results.extend(bundle_notes)
    else:
        results.append(f"  - 略過 ~/.claude/CLAUDE.md（真相源不存在）")

    # subagent 定義 → ~/.claude/agents/（只加不 prune：agents 夾可能有使用者自建 agent）
    if SSOT_AGENTS.exists():
        agents_dst = CLAUDE_DIR / "agents"
        agents_dst.mkdir(parents=True, exist_ok=True)
        ok = 0
        for src in sorted(SSOT_AGENTS.glob("*.md")):
            try:
                dst = agents_dst / src.name
                if dst.is_symlink():
                    dst.unlink()
                shutil.copy2(src, dst)
                ok += 1
            except Exception as e:
                results.append(f"  ! 略過 agents/{src.name}（{e}）")
        results.append(f"  v 寫入 ~/.claude/agents/（{ok} 個 agent）")

    return results


# 其他工具（Codex／Gemini）部署設定：僅對「已安裝」(home 存在) 工具部署。
#   home        ：工具 home 目錄
#   instr_src   ：全域指令檔真相源（bootstrap 檔）
#   instr_dst   ：部署到 home 下的檔名 —— **此工具原生開場會讀的檔名**
#                 Codex 原生讀 AGENTS.md（非 CODEX.md，codex debug prompt-input 實證）；
#                 Antigravity 原生讀 GEMINI.md。
#   stale       ：要清掉的舊／斷鏈檔名（多為移出 Drive 後 dangling 的 symlink）
OTHER_TOOLS = [
    {"home": Path.home() / ".codex",  "instr_src": SSOT_CODEX,  "instr_dst": "AGENTS.md", "stale": ["CODEX.md"]},
    {"home": Path.home() / ".gemini", "instr_src": SSOT_GEMINI, "instr_dst": "GEMINI.md", "stale": ["AGENTS.md"]},
]


PROJECT_SKILL_NATIVE_DIRS = [".claude/skills", ".agents/skills"]
# .claude/skills ＝ Claude Code 專案層級原生掃描路徑（2026-07-25 經 claude-code-guide 查證，
#   官方文件 code.claude.com/docs/en/skills.md）；.agents/skills ＝ Codex 官方原生路徑。
# 工具中立 SSOT 仍是專案內 ._agents/skills/，本函式只負責複製到雙方原生路徑，SSOT 目錄不動。


def _skill_targets():
    """全域為本機絕對路徑；專案索引指向相對專案根的 SSOT。"""
    targets = []
    for base in [CLAUDE_DIR] + [tool["home"] for tool in OTHER_TOOLS]:
        if base.is_dir():
            targets.append(dict(source=SSOT_SKILLS, destination=base / "skills",
                                index_path=base / "wtf-skills-index.md"))
    for project in registry_dirs():
        source = project / "._agents" / "skills"
        if source.is_dir():
            for relative in PROJECT_SKILL_NATIVE_DIRS:
                targets.append(dict(source=source, destination=project / relative,
                                    index_path=project / "._agents" / "skills-index.md",
                                    index_root=source, relative_to=project))
    return targets


def _check_skills():
    has_error, notes = False, []
    for target in _skill_targets():
        has_failed, details = check_skill_set(**target)
        has_error = has_error or has_failed
        notes.extend(details)
    for tool in OTHER_TOOLS:
        if not tool["home"].is_dir():
            notes.append(f"  - [SKIP   ] {tool['home']}（工具未安裝）")
    return has_error, notes


def deploy_other_tools():
    """部署已安裝工具的 bootstrap；skill 複製由 deploy_skill_set 統一處理。"""
    results = []
    for tool in OTHER_TOOLS:
        base = tool["home"]
        if not base.is_dir():
            continue
        (base / "wtf-root.txt").write_text(str(REPO_ROOT), encoding="utf-8")
        source = tool["instr_src"]
        if not source.exists():
            raise FileNotFoundError(source)
        destination = base / tool["instr_dst"]
        if destination.is_symlink():
            destination.unlink()
        shutil.copy2(source, destination)
        results.append(f"  v 寫入 {destination}（全域指令）")
        for name in tool["stale"]:
            stale = base / name
            if stale.is_symlink():
                stale.unlink()
                results.append(f"  - 移除 {stale}（舊指令 symlink）")
    return results


def _check_projects(ssot_body):
    counts, broken, orphans = {}, [], []
    for directory in registry_dirs():
        status, note = classify(directory / "AGENTS.md", ssot_body)
        counts[status] = counts.get(status, 0) + 1
        print(f"  {'v' if status == 'OK' else 'x'} [{status:7}] {directory.name}/AGENTS.md — {note}")
        if status in ("MISSING", "BROKEN", "STALE"):
            broken.append(str(directory / "AGENTS.md"))
        orphans.extend(str(path) for path in directory.glob("AGENTS (*).md"))
    return counts, broken, orphans


def _check_tool_instructions():
    broken, notes = [], []
    for tool in OTHER_TOOLS:
        base = tool["home"]
        if not base.is_dir():
            continue
        source, target = tool["instr_src"], base / tool["instr_dst"]
        if target.is_symlink() or not target.is_file() or not source.is_file():
            broken.append(str(target))
            notes.append(f"  x [MISSING] {target}（需實體入口與來源）")
        elif target.read_bytes() != source.read_bytes():
            broken.append(str(target))
            notes.append(f"  x [STALE  ] {target}（內容與真相源不符）")
        else:
            notes.append(f"  v [OK     ] {target}（全域指令內容）")
        for name in tool["stale"]:
            if (base / name).is_symlink():
                broken.append(str(base / name))
                notes.append(f"  x [STALE  ] {base / name}（舊 symlink）")
    return broken, notes


def cmd_check():
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"真相源: {SSOT}")
    print(f"掃描來源: {REGISTRY.name}（本機 {socket.gethostname()}）")
    counts, broken, orphans = _check_projects(read_ssot())
    claude_ok, _, notes = check_claude_dir()
    if claude_ok is False or any("  x [" in note for note in notes):
        broken.append(str(CLAUDE_DIR))
    other_broken, other_notes = _check_tool_instructions()
    broken.extend(other_broken)
    skills_failed, skill_notes = _check_skills()
    if skills_failed:
        broken.append("skill 副本／索引")
    for note in notes + other_notes + skill_notes:
        print(note)
    for key, value in sorted(counts.items()):
        print(f"  {key}: {value}")
    if counts.get("ADOPT"):
        print("[可接管] 無標頭但內容一致，sync 會補標頭。")
    for orphan in orphans:
        print(f"[重複命名] {orphan}（sync 不動）")
    if broken:
        print(f"[需修復] {len(broken)} 項：{', '.join(broken)}")
        print("執行 `python3 sync_config.py sync`（Windows 用 python）。")
        return 1
    print("[OK] 設定、SSOT skill 內容與索引一致；不代表各工具行為皆已驗證。")
    return 0


def cmd_sync():
    sys.stdout.reconfigure(encoding="utf-8")
    # metadata 預檢在所有寫入之前，避免半套索引部署。
    try:
        sources = {SSOT_SKILLS} | {target["source"] for target in _skill_targets()}
        for source in sources:
            read_skills(source)
    except (ValueError, OSError) as error:
        print(f"[INVALID] {error}")
        return 1
    ssot_body = read_ssot()
    _, content = build_copy(ssot_body, socket.gethostname())
    print(f"真相源: {SSOT}")
    for directory in registry_dirs():
        target = directory / "AGENTS.md"
        status, note = classify(target, ssot_body)
        if status == "FOREIGN":
            print(f"  - 略過 {directory.name}/AGENTS.md（{note}）")
            continue
        if status == "OK":
            print(f"  v 保留 {directory.name}/AGENTS.md（內容一致）")
            continue
        if target.is_symlink():
            target.unlink()
        target.write_text(content, encoding="utf-8")
        print(f"  v 寫入 {directory.name}/AGENTS.md")
    try:
        for note in deploy_claude_dir() + deploy_other_tools():
            print(note)
        for target in _skill_targets():
            for note in deploy_skill_set(**target):
                print(note)
    except (ValueError, OSError) as error:
        print(f"[ERROR] 部署失敗：{error}")
        return 1
    # 不把部分部署／被舊邏輯略過的例外當成功。
    return cmd_check()


def cmd_register():
    sys.stdout.reconfigure(encoding="utf-8")
    hostname = socket.gethostname()
    osname = f"{platform.system()} {platform.release()}"
    root = str(REPO_ROOT)
    now = ts()
    if not MACHINES.exists():
        sys.exit(f"[錯誤] 找不到 {MACHINES}，請先確認 machines.md 存在。")
    text = MACHINES.read_text(encoding="utf-8")
    line = f"| {hostname} | {osname} | `{root}` | (待填) | {now} |"
    lines = text.splitlines()
    found = False
    for i, l in enumerate(lines):
        if l.startswith(f"| {hostname} |"):
            cols = [c.strip() for c in l.strip().strip("|").split("|")]
            alias = cols[3] if len(cols) > 3 else "(待填)"
            lines[i] = f"| {hostname} | {osname} | `{root}` | {alias} | {now} |"
            found = True
            break
    if not found:
        lines.append(line)
        print(f"[新機器] 已登錄: {hostname} ({osname})")
        print(f"  根路徑: {root}")
        print("  建議稍後到 machines.md 填入『別名』欄方便辨識。")
    else:
        print(f"[已存在] 已更新最後出現時間: {hostname}")
    MACHINES.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


def _git_state(d):
    """回傳專案 git 一句話狀態（branch + clean/dirty + ahead/behind）。"""
    if not (d / ".git").exists():
        return "non-git"
    try:
        out = subprocess.run(["git", "-C", str(d), "status", "--porcelain", "--branch"],
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=10)
        lines = out.stdout.splitlines()
        branch = lines[0][3:].strip() if lines and lines[0].startswith("##") else "?"
        dirty = sum(1 for l in lines[1:] if l.strip())
        return f"{branch}｜{'dirty('+str(dirty)+')' if dirty else 'clean'}"
    except Exception as e:
        return f"git?（{e}）"


def _index_now(d):
    """從專案 _context/INDEX.md 取『## 現況』後第一行非空內容。"""
    idx = d / "_context" / "INDEX.md"
    if not idx.exists():
        return "（無 INDEX.md）"
    txt = idx.read_text(encoding="utf-8", errors="replace").splitlines()
    for i, line in enumerate(txt):
        if line.startswith("## 現況"):
            for nl in txt[i + 1:]:
                if nl.strip():
                    return nl.strip()[:90]
    return "（INDEX 無現況段）"


def cmd_status():
    """治理/可視：彙整本機所有註冊專案的現況＋git＋最新 TaskLog（唯讀）。"""
    sys.stdout.reconfigure(encoding="utf-8")
    host = socket.gethostname()
    dirs = registry_dirs()
    print(f"WTF 專案現況彙整（本機 {host}，{len(dirs)} 個專案）\n")
    for d in dirs:
        tasklogs = sorted(d.glob("_context/TaskLog_*.md"))
        latest = (tasklogs[-1].name[len("TaskLog_"):-3] if tasklogs else "—")
        print(f"● {d.name}")
        print(f"   現況: {_index_now(d)}")
        print(f"   git : {_git_state(d)}   |  最新 TaskLog: {latest}")
    return 0


def _latest_tasklog(d):
    tls = sorted(d.glob("_context/TaskLog_*.md"))
    return tls[-1] if tls else None


def _todos(d, limit=8):
    """從最新 TaskLog 抽待辦：優先未勾選 checkbox，否則抓『下一步/未完成/待辦…』段條列。"""
    tl = _latest_tasklog(d)
    if not tl:
        return []
    txt = tl.read_text(encoding="utf-8", errors="replace").splitlines()
    box = [l.strip()[5:].strip() for l in txt if l.strip().startswith("- [ ]")]
    if box:
        return box[:limit]
    todos, capturing = [], False
    for l in txt:
        if l.lstrip().startswith("#"):
            capturing = bool(re.search(r"(下一步|未完成|未解決|待辦|TODO|建議)", l))
            continue
        if capturing:
            s = l.strip()
            if re.match(r"^([-*]|\d+[.、)])\s+", s):
                item = re.sub(r"^([-*]|\d+[.、)])\s+", "", s)
                if item and not item.startswith("~~"):   # 跳過刪節線(已完成)
                    todos.append(item)
    return todos[:limit]


def _md_inline(s):
    """inline markdown → HTML：先 escape，再 **粗體**、`code`（解決 todo 文字未渲染）。"""
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


def cmd_dashboard():
    """治理/可視：產 outputs/dashboard.html — Fire Evening 主題＋stats＋即時專案卡（待辦 markdown 渲染）。"""
    sys.stdout.reconfigure(encoding="utf-8")
    host = socket.gethostname()
    now = ts()
    dirs = registry_dirs()
    rows = []
    n_dirty = n_todo = n_drive = 0
    for d in dirs:
        gits = _git_state(d)
        cls = ("clean" if "clean" in gits else
               "ahead" if ("ahead" in gits or "behind" in gits) else
               "nogit" if gits == "non-git" else "dirty")
        if cls == "dirty":
            n_dirty += 1
        if gits == "non-git":
            n_drive += 1
        tl = _latest_tasklog(d)
        tlname = tl.name[len("TaskLog_"):-3] if tl else "—"
        todos = _todos(d)
        if todos:
            n_todo += 1
        todo_html = ("".join(f"<li>{_md_inline(t)}</li>" for t in todos)
                     if todos else '<li class="none">（無待辦或無 TaskLog）</li>')
        rows.append(f"""    <div class="card {cls}">
      <div class="card-h"><h2>{html.escape(d.name)}</h2>
        <span class="git {cls}">{html.escape(gits)}</span></div>
      <p class="now">{_md_inline(_index_now(d))}</p>
      <div class="tl">📋 {html.escape(tlname)}</div>
      <ul class="todos">{todo_html}</ul>
    </div>""")
    stats = [("專案", len(dirs), "blue"), ("git dirty", n_dirty, "orange"),
             ("有待辦", n_todo, "purple"), ("Drive(非git)", n_drive, "red")]
    stat_html = "".join(
        f'<div class="stat {c}"><div class="sl">{l}</div><div class="sv">{v}</div></div>'
        for l, v, c in stats)
    page = f"""<!DOCTYPE html><html lang="zh-Hant"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>WTF 專案儀表板</title>
<style>
:root{{--blue:#4F51FE;--purple:#8C1E92;--orange:#FF4E0B;--red:#CD2019;
--bg:#110a0d;--card:#221219;--card2:#2a1520;--border:#3d1f28;--text:#f0e6f0;--t2:#9a7d90;--t3:#6a5060}}
@media(prefers-color-scheme:light){{:root{{--bg:#faf4f7;--card:#fff;--card2:#f5eef2;--border:#e0cdd6;--text:#1a0810;--t2:#6b4a5a;--t3:#a07888}}}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,"Segoe UI","Microsoft JhengHei",sans-serif;background:var(--bg);color:var(--text);padding:20px 16px 48px}}
.wrap{{max-width:1100px;margin:0 auto}}
h1{{font-size:24px;background:linear-gradient(90deg,var(--orange),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.sub{{color:var(--t2);font-size:13px;margin:2px 0 18px}}
.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}}
.stat{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:14px 16px}}
.sl{{font-size:11px;color:var(--t3);text-transform:uppercase;letter-spacing:.05em}}
.sv{{font-size:24px;font-weight:700;margin-top:4px}}
.stat.blue .sv{{color:var(--blue)}}.stat.orange .sv{{color:var(--orange)}}.stat.purple .sv{{color:var(--purple)}}.stat.red .sv{{color:var(--red)}}
.grid{{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}}
.card{{background:var(--card);border:1px solid var(--border);border-left:5px solid var(--t3);border-radius:14px;padding:16px 18px}}
.card.clean{{border-left-color:var(--blue)}}.card.dirty{{border-left-color:var(--orange)}}
.card.ahead{{border-left-color:var(--purple)}}.card.nogit{{border-left-color:var(--t3)}}
.card-h{{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:8px}}
.card-h h2{{font-size:15px;font-weight:600}}
.git{{font-size:10px;font-weight:700;padding:3px 8px;border-radius:20px;white-space:nowrap;color:#fff}}
.git.clean{{background:var(--blue)}}.git.dirty{{background:var(--orange)}}.git.ahead{{background:var(--purple)}}.git.nogit{{background:var(--t3)}}
.now{{font-size:12.5px;color:var(--t2);line-height:1.45;margin-bottom:8px}}
.tl{{font-size:11px;color:var(--t3);margin-bottom:8px;font-family:monospace}}
.todos{{padding-left:18px;font-size:12.5px;line-height:1.6}}
.todos li{{margin-bottom:3px;color:var(--text)}}
.todos .none{{list-style:none;margin-left:-18px;color:var(--t3)}}
code{{background:var(--card2);padding:1px 5px;border-radius:4px;font-size:.92em}}
footer{{margin-top:22px;font-size:12px;color:var(--t3)}}
footer a{{color:var(--blue);text-decoration:none;margin-right:14px}}
@media(max-width:720px){{.stats{{grid-template-columns:1fr 1fr}}}}
</style></head><body><div class="wrap">
<h1>WTF 專案儀表板</h1>
<div class="sub">本機 {html.escape(host)}｜產生 {now}｜資料源：registry × INDEX × 最新 TaskLog × git</div>
<div class="stats">{stat_html}</div>
<div class="grid">
{chr(10).join(rows)}
</div>
<footer>
<a href="https://github.com/coldjokenewbie-code/WTF_Under_Construction">GitHub</a>
<a href="wtf-config/GLOBAL.md">GLOBAL.md</a>
<a href="wtf-config/projects-registry.md">registry</a>
重生：<code>python wtf-config/sync_config.py dashboard</code>
</footer>
</div></body></html>"""
    out_dir = REPO_ROOT / "outputs"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / "dashboard.html"
    out.write_text(page, encoding="utf-8")
    print(f"已產生儀表板：{out}（{len(dirs)} 個專案）")
    return 0


def _md_section(text, key):
    """取標題含 key 的第一個 '## ' 節內容（不含標題行，含子節），找不到回 None。"""
    out, on = [], False
    for ln in text.splitlines():
        if ln.startswith("## "):
            if on:
                break
            on = key in ln
            continue
        if on:
            out.append(ln)
    body = "\n".join(out).strip()
    body = re.sub(r"\n?-{3,}\s*$", "", body).strip()
    return body or None


def cmd_chat_instruction():
    """部署：組 Claude Chat 的 Project Instruction（正本：AGENTS.md＋GLOBAL.md＋CLAUDE_CHAT.md）。"""
    sys.stdout.reconfigure(encoding="utf-8")
    agents = read_ssot()
    global_md = (SCRIPT_DIR / "GLOBAL.md").read_text(encoding="utf-8")
    chat = (SCRIPT_DIR / "CLAUDE_CHAT.md").read_text(encoding="utf-8")

    rules = re.search(r"<!-- rules-start -->(.*?)<!-- rules-end -->", chat, re.S)
    parts = [
        ("效益優先溝通原則", _md_section(agents, "效益優先溝通原則")),
        ("溝通與意圖解讀", _md_section(agents, "溝通與意圖解讀")),
        ("「做到好」原則", _md_section(global_md, "「做到好」原則")),
        ("Chat 工具特性與限制", _md_section(chat, "工具特性與限制")),
        ("Chat 固定規則", rules.group(1).strip() if rules else None),
        ("Lesson 候選輸出格式", _md_section(chat, "Lesson 候選輸出格式")),
        ("Session 結束協議", _md_section(chat, "Session 結束協議")),
    ]
    missing = [t for t, b in parts if not b]
    doc = "\n\n".join(
        ["# WTF Project Instruction（Claude Chat）",
         f"> 自動產生：`python wtf-config/sync_config.py chat-instruction`（{ts()}）。"
         "正本＝wtf-config/AGENTS.md、GLOBAL.md、CLAUDE_CHAT.md；手改本檔無效，改正本後重產。"]
        + [f"## {t}\n{b}" for t, b in parts if b]) + "\n"

    out_dir = REPO_ROOT / "outputs"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / "chat-project-instruction.md"
    out.write_text(doc, encoding="utf-8")
    print(f"已產生：{out}（{len(doc)} 字元）")
    print("→ 複製全文貼回 claude.ai 該 Project 的 Instructions 欄。")
    if missing:
        print(f"[警告] 正本缺節，未收入：{'、'.join(missing)}（檢查標題是否被改名）")
        return 1
    return 0


def main():
    cmds = {"check": cmd_check, "sync": cmd_sync, "register": cmd_register,
            "status": cmd_status, "dashboard": cmd_dashboard, "inbox-info": cmd_inbox_info,
            "chat-instruction": cmd_chat_instruction}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__)
        return 2
    return cmds[sys.argv[1]]()


if __name__ == "__main__":
    sys.exit(main())
