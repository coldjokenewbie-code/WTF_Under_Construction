#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_config.py — WTF 設定真相源同步腳本
真相源(SSOT): wtf-config/AGENTS.md
用途: 把 SSOT 實體複製到各專案 AGENTS.md（取代跨平台失效的 symlink）

子命令:
  python sync_config.py check     掃描所有專案 AGENTS.md，回報 OK / 失效，不改檔
  python sync_config.py sync      把 SSOT 實體複製到每個專案 AGENTS.md
  python sync_config.py register  偵測本機並寫入 machines.md（每台電腦首次執行）

設計備註:
  - Drive 不支援跨平台 symlink，故改用實體複製。
  - 產生的副本頂部含 HTML 註記標頭，用於辨識「自動產生」並比對是否過期。
  - 失效偵測為內容式判斷，與機器無關，Cowork 沙盒內亦可執行。
"""
import sys
import socket
import platform
import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent          # .../wtf-config
SSOT = SCRIPT_DIR / "AGENTS.md"                        # 真相源
ROOT = SCRIPT_DIR.parents[2]                           # .../Claude_cowork
PROJECTS_DIR = ROOT / "projects"
MACHINES = SCRIPT_DIR / "machines.md"

MARK_BEGIN = "<!-- WTF-AUTOGEN:AGENTS"                  # 標頭辨識字串
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
    """若為自動產生檔，回傳標頭之後的內容；否則回傳 None。"""
    if MARK_BEGIN in text and MARK_END in text:
        idx = text.find(MARK_END)
        return text[idx + len(MARK_END):].lstrip("\n")
    return None


def looks_like_symlink_remnant(text):
    """Drive 同步壞掉的 symlink：通常是單行檔案路徑字串。"""
    lines = [l for l in text.splitlines() if l.strip()]
    if len(lines) == 1 and "wtf-config/AGENTS.md" in lines[0]:
        return True
    return False


def project_dirs():
    if not PROJECTS_DIR.exists():
        sys.exit(f"[錯誤] 找不到 projects 目錄: {PROJECTS_DIR}")
    return sorted([d for d in PROJECTS_DIR.iterdir() if d.is_dir()])


def classify(target, ssot_body):
    """回傳 (狀態, 說明)"""
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
    return ("FOREIGN", "非自動產生的內容（疑似手改或他用），sync 不會覆蓋")


def cmd_check():
    ssot_body = read_ssot()
    print(f"真相源: {SSOT}")
    print(f"掃描範圍: {PROJECTS_DIR}\n")
    counts = {}
    broken = []
    orphans = []
    for d in project_dirs():
        target = d / "AGENTS.md"
        status, note = classify(target, ssot_body)
        counts[status] = counts.get(status, 0) + 1
        flag = "✓" if status == "OK" else "✗"
        print(f"  {flag} [{status:7}] {d.name}/AGENTS.md  — {note}")
        if status in ("MISSING", "BROKEN", "STALE"):
            broken.append(d.name)
        # 偵測 Drive 重複命名孤兒檔
        for dup in d.glob("AGENTS (*).md"):
            orphans.append(str(dup.relative_to(ROOT)))
    print("\n--- 統計 ---")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")
    if orphans:
        print("\n--- 重複命名孤兒檔（Drive 產生，sync 不動，建議確認後手動清理）---")
        for o in orphans:
            print(f"  {o}")
    if broken:
        print(f"\n[需修復] {len(broken)} 個專案 AGENTS.md 失效/過期: {', '.join(broken)}")
        print("執行 `python sync_config.py sync` 修復。")
        return 1
    print("\n[OK] 全部 AGENTS.md 與真相源一致。")
    return 0


def cmd_sync():
    ssot_body = read_ssot()
    hostname = socket.gethostname()
    _, content = build_copy(ssot_body, hostname)
    print(f"真相源: {SSOT}")
    print(f"本機: {hostname}\n")
    written, skipped = 0, []
    for d in project_dirs():
        target = d / "AGENTS.md"
        status, note = classify(target, ssot_body)
        if status == "FOREIGN":
            skipped.append(d.name)
            print(f"  - 略過 {d.name}/AGENTS.md（{note}）")
            continue
        target.write_text(content, encoding="utf-8")
        written += 1
        print(f"  ✓ 寫入 {d.name}/AGENTS.md")
    print(f"\n完成: 寫入 {written} 個。")
    if skipped:
        print(f"略過 {len(skipped)} 個 FOREIGN（需人工確認）: {', '.join(skipped)}")
    return 0


def cmd_register():
    hostname = socket.gethostname()
    osname = f"{platform.system()} {platform.release()}"
    root = str(ROOT)
    now = ts()
    if not MACHINES.exists():
        sys.exit(f"[錯誤] 找不到 {MACHINES}，請先確認 machines.md 存在。")
    text = MACHINES.read_text(encoding="utf-8")
    line = f"| {hostname} | {osname} | `{root}` | (待填) | {now} |"
    lines = text.splitlines()
    found = False
    for i, l in enumerate(lines):
        if l.startswith(f"| {hostname} |"):
            # 更新最後出現時間，保留別名欄
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
