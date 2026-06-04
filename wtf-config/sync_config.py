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

SCRIPT_DIR = Path(__file__).resolve().parent          # .../wtf-config
SSOT = SCRIPT_DIR / "AGENTS.md"                        # 真相源
SSOT_CLAUDE = SCRIPT_DIR / "CLAUDE_CODE.md"            # ~/.claude/CLAUDE.md 真相源
SSOT_SKILLS = SCRIPT_DIR / "skills"                    # ~/.claude/skills/ 真相源
REPO_ROOT = SCRIPT_DIR.parent                         # WTF repo 根（已移出 Drive，供 register 記錄）
MACHINES = SCRIPT_DIR / "machines.md"
CLAUDE_DIR = Path.home() / ".claude"
REGISTRY = SCRIPT_DIR / "projects-registry.md"         # 專案註冊表（取代 extra-scan-dirs.txt 與 PROJECTS_DIR 推導）

MARK_BEGIN = "<!-- WTF-AUTOGEN:AGENTS"
MARK_END = "WTF-AUTOGEN:END -->"


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


def registry_dirs():
    """讀 projects-registry.md，回傳本機 hostname 對應的專案目錄清單。

    取代舊的 PROJECTS_DIR 推導與 extra-scan-dirs.txt。
    registry 為 markdown 表格：| project | machine (hostname) | path |
    只取 machine == 本機 hostname、path 非佔位且實際存在的列。
    """
    if not REGISTRY.exists():
        sys.exit(f"[錯誤] 找不到專案註冊表: {REGISTRY}")
    hostname = socket.gethostname()
    dirs = []
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 3:
            continue
        project, machine, path = cols[0], cols[1], cols[2]
        if machine == "machine (hostname)":          # 表頭
            continue
        if set(project) <= {"-", " "}:                # 分隔列 |---|
            continue
        if machine != hostname:                       # 非本機
            continue
        if not path or path.startswith("（"):          # 佔位/未部署
            continue
        p = Path(path)
        if p.is_dir():
            dirs.append(p)
        else:
            print(f"  ! [WARN] registry 路徑不存在，略過: {project} → {path}", file=sys.stderr)
    return dirs


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
    skills_dst = CLAUDE_DIR / "skills"

    if not SSOT_CLAUDE.exists():
        notes.append(f"  ! [SKIP  ] ~/.claude/CLAUDE.md — 真相源 {SSOT_CLAUDE} 不存在")
        claude_md_ok = None
    elif not claude_md.exists():
        notes.append(f"  x [MISSING] ~/.claude/CLAUDE.md")
        claude_md_ok = False
    elif claude_md.is_symlink():
        notes.append(f"  x [SYMLINK] ~/.claude/CLAUDE.md — 仍為 symlink，需改為實體檔")
        claude_md_ok = False
    elif claude_md.read_text(encoding="utf-8", errors="replace").rstrip() == SSOT_CLAUDE.read_text(encoding="utf-8").rstrip():
        notes.append(f"  v [OK     ] ~/.claude/CLAUDE.md")
        claude_md_ok = True
    else:
        notes.append(f"  x [STALE  ] ~/.claude/CLAUDE.md — 內容與真相源不符")
        claude_md_ok = False

    if not SSOT_SKILLS.exists():
        notes.append(f"  ! [SKIP  ] ~/.claude/skills/ — 真相源 {SSOT_SKILLS} 不存在")
        skills_ok = None
    elif not skills_dst.exists():
        notes.append(f"  x [MISSING] ~/.claude/skills/")
        skills_ok = False
    elif skills_dst.is_symlink():
        notes.append(f"  x [SYMLINK] ~/.claude/skills/ — 仍為 symlink，需改為實體目錄")
        skills_ok = False
    else:
        ssot_skills = sorted([p.name for p in SSOT_SKILLS.iterdir() if p.is_dir()])
        dst_skills = sorted([p.name for p in skills_dst.iterdir() if p.is_dir()])
        if ssot_skills == dst_skills:
            notes.append(f"  v [OK     ] ~/.claude/skills/ （{len(ssot_skills)} 個 skill）")
            skills_ok = True
        else:
            notes.append(f"  x [STALE  ] ~/.claude/skills/ — skill 清單不符")
            skills_ok = False

    return claude_md_ok, skills_ok, notes


def deploy_claude_dir():
    """複製 CLAUDE_CODE.md → ~/.claude/CLAUDE.md，skills/ → ~/.claude/skills/"""
    results = []
    CLAUDE_DIR.mkdir(exist_ok=True)

    # 絕對路徑錨點：供 session-start／CLAUDE.md 從任何 cwd（含非 WTF 專案）定位 WTF repo 讀 SSOT
    try:
        (CLAUDE_DIR / "wtf-root.txt").write_text(str(REPO_ROOT), encoding="ascii")
        results.append(f"  v 寫入 ~/.claude/wtf-root.txt（{REPO_ROOT}）")
    except Exception as e:
        results.append(f"  ! 略過 ~/.claude/wtf-root.txt（{e}）")

    if SSOT_CLAUDE.exists():
        dst = CLAUDE_DIR / "CLAUDE.md"
        if dst.is_symlink():
            dst.unlink()
        shutil.copy2(SSOT_CLAUDE, dst)
        results.append(f"  v 寫入 ~/.claude/CLAUDE.md")
    else:
        results.append(f"  - 略過 ~/.claude/CLAUDE.md（真相源不存在）")

    if SSOT_SKILLS.exists():
        dst_root = CLAUDE_DIR / "skills"
        if dst_root.is_symlink():
            dst_root.unlink()
        dst_root.mkdir(parents=True, exist_ok=True)
        # 逐 skill 複製：dirs_exist_ok 合併、單一鎖定只略過該項，不整批 rmtree
        ssot_names = set()
        ok = 0
        for skill_src in sorted(SSOT_SKILLS.iterdir()):
            if not skill_src.is_dir():
                continue
            ssot_names.add(skill_src.name)
            try:
                shutil.copytree(skill_src, dst_root / skill_src.name, dirs_exist_ok=True)
                ok += 1
            except Exception as e:
                results.append(f"  ! 略過 skills/{skill_src.name}（{e}）")
        results.append(f"  v 寫入 ~/.claude/skills/（{ok} 個 skill）")
        # 容錯移除 SSOT 已不存在的舊 skill
        for old in sorted(dst_root.iterdir()):
            if old.is_dir() and old.name not in ssot_names:
                try:
                    shutil.rmtree(old)
                    results.append(f"  - 移除舊 skill skills/{old.name}（SSOT 已無）")
                except Exception as e:
                    results.append(f"  ! 無法移除 skills/{old.name}（{e}）")
    else:
        results.append(f"  - 略過 ~/.claude/skills/（真相源不存在）")

    return results


# 其他工具（Codex／Gemini）skills 部署目標：僅對「已安裝」工具部署
OTHER_TOOL_SKILL_DIRS = [Path.home() / ".codex" / "skills",
                         Path.home() / ".gemini" / "skills"]


def deploy_other_tools():
    """把 SSOT skills 實體複製到 codex／gemini 的 skills/（present 才做）。
    保守 prune 孤兒 WTF skill：只刪「實體目錄、名稱非 . 開頭、且不在 SSOT 集」者；
    保護工具自有 skill（symlink 如 find-skills、dotted 如 .system）。"""
    results = []
    if not SSOT_SKILLS.exists():
        return results
    ssot_names = {s.name for s in SSOT_SKILLS.iterdir() if s.is_dir()}
    for dst_root in OTHER_TOOL_SKILL_DIRS:
        base = dst_root.parent
        if not base.is_dir():
            continue  # 工具未安裝，跳過
        dst_root.mkdir(parents=True, exist_ok=True)
        # 同寫錨點到工具 home，供該工具從任何 cwd 定位 WTF repo
        try:
            (base / "wtf-root.txt").write_text(str(REPO_ROOT), encoding="ascii")
        except Exception:
            pass
        ok = 0
        for name in sorted(ssot_names):
            try:
                shutil.copytree(SSOT_SKILLS / name, dst_root / name, dirs_exist_ok=True)
                ok += 1
            except Exception as e:
                results.append(f"  ! 略過 {base.name}/skills/{name}（{e}）")
        # 保守 prune：刪 SSOT 已移除的孤兒 WTF skill。
        # 保護工具自有 skill：dotted（.system）跳過；symlink（find-skills）由 rmtree 自身拒刪
        # 並靜默略過（Windows MSYS symlink 之 is_symlink() 偵測不可靠，故靠 rmtree 守門）。
        for entry in sorted(dst_root.iterdir()):
            if (entry.is_dir() and not entry.name.startswith(".")
                    and entry.name not in ssot_names):
                try:
                    shutil.rmtree(entry)
                    results.append(f"  - 移除 {base.name}/skills/{entry.name}（SSOT 已無）")
                except Exception:
                    pass  # symlink 或鎖定 → 視為工具自有，保留
        results.append(f"  v 寫入 ~/{base.name}/skills/（{ok} 個 WTF skill；保護 symlink/dotted 自有 skill）")
    return results


def cmd_check():
    sys.stdout.reconfigure(encoding="utf-8")
    ssot_body = read_ssot()
    print(f"真相源: {SSOT}")
    print(f"掃描來源: {REGISTRY.name}（本機 {socket.gethostname()}）\n")
    counts = {}
    broken = []
    orphans = []
    for d in registry_dirs():
        target = d / "AGENTS.md"
        status, note = classify(target, ssot_body)
        counts[status] = counts.get(status, 0) + 1
        flag = "v" if status == "OK" else "x"
        print(f"  {flag} [{status:7}] {d.name}/AGENTS.md  — {note}")
        if status in ("MISSING", "BROKEN", "STALE"):
            broken.append(d.name)
        for dup in d.glob("AGENTS (*).md"):
            orphans.append(str(dup))

    print("\n--- ~/.claude/ ---")
    _, _, notes = check_claude_dir()
    for n in notes:
        print(n)

    print("\n--- 統計 ---")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")
    adopt_n = counts.get("ADOPT", 0)
    if adopt_n:
        print(f"\n[可接管] {adopt_n} 個無標頭但內容與真相源一致，跑 `sync` 自動補標頭接管。")
    if orphans:
        print("\n--- 重複命名孤兒檔（Drive 產生，sync 不動，建議確認後手動清理）---")
        for o in orphans:
            print(f"  {o}")
    if broken:
        print(f"\n[需修復] {len(broken)} 個專案 AGENTS.md 失效/過期: {', '.join(broken)}")
        print("執行 `python sync_config.py sync` 修復。")
        return 1
    print("\n[OK] 全部與真相源一致。")
    return 0


def cmd_sync():
    sys.stdout.reconfigure(encoding="utf-8")
    ssot_body = read_ssot()
    hostname = socket.gethostname()
    _, content = build_copy(ssot_body, hostname)
    print(f"真相源: {SSOT}")
    print(f"本機: {hostname}\n")
    written, skipped = 0, []
    for d in registry_dirs():
        target = d / "AGENTS.md"
        status, note = classify(target, ssot_body)
        if status == "FOREIGN":
            skipped.append(d.name)
            print(f"  - 略過 {d.name}/AGENTS.md（{note}）")
            continue
        if target.is_symlink():            # 防寫穿 symlink 污染真相源（root AGENTS.md）
            target.unlink()
        target.write_text(content, encoding="utf-8")
        written += 1
        tag = "接管" if status == "ADOPT" else "寫入"
        print(f"  v {tag} {d.name}/AGENTS.md")
    print(f"\n完成: 寫入 {written} 個專案 AGENTS.md。")
    if skipped:
        print(f"略過 {len(skipped)} 個 FOREIGN: {', '.join(skipped)}")

    print("\n--- ~/.claude/ 部署 ---")
    for r in deploy_claude_dir():
        print(r)

    other = deploy_other_tools()
    if other:
        print("\n--- 其他工具（Codex／Gemini）skills 部署 ---")
        for r in other:
            print(r)
    return 0


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


def main():
    cmds = {"check": cmd_check, "sync": cmd_sync, "register": cmd_register,
            "status": cmd_status, "dashboard": cmd_dashboard}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__)
        return 2
    return cmds[sys.argv[1]]()


if __name__ == "__main__":
    sys.exit(main())
