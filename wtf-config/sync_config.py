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


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("check", "sync", "register"):
        print(__doc__)
        return 2
    return {"check": cmd_check, "sync": cmd_sync, "register": cmd_register}[sys.argv[1]]()


if __name__ == "__main__":
    sys.exit(main())
