#!/usr/bin/env python3
"""ody Coach（Verifier 機檢引擎）— 三道閘的落地件。

來源設計：_context/Plan_2026-07-01_discipline-harness.md
  閘1 接任務→立契約（無契約不動工）
  閘2 宣稱完成→機檢驗收（scope／自驗證據／冗長／機械品質＋coach_rules 全套用）
  閘3 每次留紀錄→FAIL 轉可機檢規則（add-rule，Mentor 維護）

用法（一律於 WTF repo 根執行）：
  python3 tools/ody/squad/coach.py new <task_id> --goal "..." \
      --scope "tools/ody/squad/*" "outputs/ody*" --accept "標準1" "標準2" \
      [--verify-cmd "python3 tools/ody/tests/test_safety.py"] [--permission "授權點"]
  python3 tools/ody/squad/coach.py evidence <task_id> <標準編號> (--cmd "..." | --note "...")
  python3 tools/ody/squad/coach.py check <task_id>
  python3 tools/ody/squad/coach.py add-rule --rule-id R00x --desc "..." \
      --type banned_path_in_diff --patterns "path/**" --msg "失敗訊息"

零外部依賴；事件寫 events.jsonl（複用 ody.core.events，schema 驗證）。
"""
from __future__ import annotations
import argparse
import fnmatch
import json
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SQUAD_DIR = Path(__file__).resolve().parent
ODY_ROOT = SQUAD_DIR.parent
WTF_ROOT = ODY_ROOT.parent.parent
CONTRACTS_DIR = ODY_ROOT / "data" / "contracts"
COACH_RULES_PATH = SQUAD_DIR / "coach_rules.json"

sys.path.insert(0, str(ODY_ROOT.parent))
from ody.core.events import EventLog  # noqa: E402

# 契約/事件本身永遠允許寫入（否則 coach 自我否定）
DEFAULT_ALLOW = ["tools/ody/data/**"]
GENERIC_NOTES = {"已確認", "已完成", "ok", "done", "完成", "確認", "pass"}
VERIFY_TIMEOUT = 300


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _git(*args: str, repo: Path = WTF_ROOT) -> str:
    # core.quotepath=false：非 ASCII 檔名（中文）預設會被八進位跳脫，路徑就對不上實體檔
    r = subprocess.run(["git", "-C", str(repo), "-c", "core.quotepath=false", *args],
                       capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


def _contract_path(task_id: str) -> Path:
    return CONTRACTS_DIR / f"{task_id}.contract.json"


def _load(task_id: str) -> dict:
    p = _contract_path(task_id)
    if not p.exists():
        sys.exit(f"FAIL: 無契約 {p}（閘1：無契約不動工，先 coach.py new）")
    return json.loads(p.read_text(encoding="utf-8"))


def _save(c: dict) -> None:
    CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)
    _contract_path(c["task_id"]).write_text(
        json.dumps(c, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _dirty_files(repo: Path = WTF_ROOT) -> list[str]:
    # 不用 _git()：它 strip 整段 stdout，會吃掉第一行的前導狀態空白使 l[3:] 錯位
    r = subprocess.run(["git", "-C", str(repo), "-c", "core.quotepath=false",
                        "status", "--porcelain"],
                       capture_output=True, text=True, timeout=60)
    return [l[3:].strip().strip('"') for l in r.stdout.splitlines() if l.strip()]


def _repo_of(c: dict) -> Path:
    return Path(c.get("repo_root", str(WTF_ROOT)))


def _match(path: str, patterns: list[str]) -> bool:
    for pat in patterns:
        if pat.endswith("/**"):
            if path.startswith(pat[:-2]):
                return True
        elif fnmatch.fnmatch(path, pat):
            return True
    return False


def cmd_new(a) -> int:
    if _contract_path(a.task_id).exists():
        sys.exit(f"已有同名契約 {a.task_id}，換 ID 或刪舊檔")
    # 目標 repo：--repo 指定，否則 cwd 所在 git repo，最後 fallback WTF
    repo = Path(a.repo).resolve() if a.repo else Path(
        _git("rev-parse", "--show-toplevel", repo=Path.cwd()) or WTF_ROOT)
    c = {
        "task_id": a.task_id,
        "goal": a.goal,
        "created": _now(),
        "repo_root": str(repo),
        "base_ref": _git("rev-parse", "HEAD", repo=repo),
        "preexisting_dirty": _dirty_files(repo),  # 開工前既髒檔，scope 檢查排除
        "scope_allowlist": a.scope,
        "preflight_permissions": a.permission or [],
        "po_authorized_protected_paths": bool(a.po_authorized),
        "acceptance": [{"no": i + 1, "desc": d, "evidence": None}
                       for i, d in enumerate(a.accept)],
        "verify_cmds": a.verify_cmd or [],
        "handoff_file": a.handoff_file,
        "status": "open",
    }
    _save(c)
    EventLog(a.task_id, f"coach-{_now()}").emit(
        "contract_created", ok=True,
        detail={"scope": c["scope_allowlist"], "n_acceptance": len(c["acceptance"])})
    print(f"契約已立：{_contract_path(a.task_id)}")
    print(f"  scope={c['scope_allowlist']}\n  驗收 {len(c['acceptance'])} 條、"
          f"授權點 {len(c['preflight_permissions'])} 項（開工前向 PO 一次講定）")
    return 0


def cmd_evidence(a) -> int:
    c = _load(a.task_id)
    item = next((x for x in c["acceptance"] if x["no"] == a.no), None)
    if not item:
        sys.exit(f"無驗收標準 #{a.no}")
    if a.cmd:
        r = subprocess.run(a.cmd, shell=True, capture_output=True, text=True,
                           cwd=str(_repo_of(c)), timeout=VERIFY_TIMEOUT)
        item["evidence"] = {"cmd": a.cmd, "exit": r.returncode,
                            "output_tail": (r.stdout + r.stderr)[-400:], "ts": _now()}
        print(f"#{a.no} 證據（cmd exit={r.returncode}）已記錄")
    else:
        item["evidence"] = {"note": a.note, "ts": _now()}
        print(f"#{a.no} 證據（note）已記錄")
    _save(c)
    EventLog(a.task_id, f"coach-{_now()}").emit(
        "evidence_added", ok=True, detail={"no": a.no, "kind": "cmd" if a.cmd else "note"})
    return 0


def _load_rules() -> list[dict]:
    if not COACH_RULES_PATH.exists():
        return []
    return json.loads(COACH_RULES_PATH.read_text(encoding="utf-8")).get("rules", [])


def _apply_rules(c: dict, changed: list[str], fails: list[str]) -> None:
    repo = _repo_of(c)
    for r in _load_rules():
        t = r.get("type")
        if t == "banned_path_in_diff":
            hit = [f for f in changed if _match(f, r["patterns"])]
            if hit and not c.get("po_authorized_protected_paths"):
                fails.append(f"[{r['rule_id']}] {r['msg']}：{hit}")
        elif t == "evidence_note_not_generic":
            for x in c["acceptance"]:
                ev = x.get("evidence") or {}
                note = str(ev.get("note", "")).strip().lower()
                if "cmd" not in ev and note and note in GENERIC_NOTES:
                    fails.append(f"[{r['rule_id']}] {r['msg']}（#{x['no']} note='{note}'）")
        elif t == "require_cmd_pass":
            rr = subprocess.run(r["cmd"], shell=True, capture_output=True, text=True,
                                cwd=str(repo), timeout=VERIFY_TIMEOUT)
            if rr.returncode != 0:
                fails.append(f"[{r['rule_id']}] {r['msg']}（exit={rr.returncode}）")


def cmd_check(a) -> int:
    c = _load(a.task_id)
    repo = _repo_of(c)
    fails: list[str] = []
    # 閘1 契約完整
    if not c.get("scope_allowlist"):
        fails.append("[閘1] 契約缺 scope_allowlist")
    if not c.get("acceptance"):
        fails.append("[閘1] 契約缺驗收標準")
    # 閘2a scope 越界（比對 base_ref diff＋現況 dirty，排除開工前既髒檔）
    changed = set(_git("diff", "--name-only", c["base_ref"], repo=repo).splitlines()) \
        | set(_dirty_files(repo))
    changed -= set(c.get("preexisting_dirty", []))
    allow = c["scope_allowlist"] + DEFAULT_ALLOW
    out_of_scope = sorted(f for f in changed if f and not _match(f, allow))
    if out_of_scope:
        fails.append(f"[閘2 scope] 越界檔案：{out_of_scope}（還原或經 PO 擴 scope）")
    # 閘2b 自驗證據逐條
    for x in c["acceptance"]:
        ev = x.get("evidence")
        if not ev:
            fails.append(f"[閘2 自驗] 驗收 #{x['no']}「{x['desc']}」無證據")
        elif "cmd" in ev and ev.get("exit") != 0:
            fails.append(f"[閘2 自驗] #{x['no']} 證據命令 exit={ev.get('exit')} 非 0")
    # 閘2c 冗長（handoff 檔行數）
    if c.get("handoff_file"):
        hp = repo / c["handoff_file"]
        if hp.exists():
            n = len(hp.read_text(encoding="utf-8").splitlines())
            if n > 60:
                fails.append(f"[閘2 冗長] handoff {n} 行 > 60，改條列證據")
    # 閘2d 機械品質
    for cmd in c.get("verify_cmds", []):
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           cwd=str(repo), timeout=VERIFY_TIMEOUT)
        if r.returncode != 0:
            fails.append(f"[閘2 機械] `{cmd}` exit={r.returncode}："
                         f"{(r.stdout + r.stderr)[-200:]}")
    # 閘3 學習規則全套用
    _apply_rules(c, sorted(changed), fails)

    ok = not fails
    c["status"] = "passed" if ok else "failed"
    c["last_check"] = {"ts": _now(), "ok": ok, "fails": fails}
    _save(c)
    EventLog(a.task_id, f"coach-{_now()}").emit(
        "coach_check", ok=ok, detail={"fails": fails, "n_changed": len(changed)})
    if ok:
        print(f"PASS：{a.task_id} 全閘通過（{len(c['acceptance'])} 條驗收、"
              f"{len(changed)} 檔變更皆在 scope）")
        return 0
    print(f"FAIL：{a.task_id} 共 {len(fails)} 項", file=sys.stderr)
    for f in fails:
        print(" - " + f, file=sys.stderr)
    print("（FAIL 處置：修正→重驗；重複同型錯誤→Mentor add-rule 轉可機檢規則）",
          file=sys.stderr)
    return 1


def cmd_add_rule(a) -> int:
    data = {"_doc": "ody coach 學習規則庫（Mentor 維護）。每次 FAIL/糾正轉一條可機檢規則，"
                    "coach check 每次全套用。", "rules": []}
    if COACH_RULES_PATH.exists():
        data = json.loads(COACH_RULES_PATH.read_text(encoding="utf-8"))
    if any(r["rule_id"] == a.rule_id for r in data["rules"]):
        sys.exit(f"規則 {a.rule_id} 已存在")
    rule = {"rule_id": a.rule_id, "desc": a.desc, "type": a.type, "msg": a.msg,
            "added": _now()}
    if a.patterns:
        rule["patterns"] = a.patterns
    if a.cmd:
        rule["cmd"] = a.cmd
    data["rules"].append(rule)
    COACH_RULES_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8")
    EventLog("mentor", f"coach-{_now()}").emit("rule_added", ok=True,
                                               detail={"rule_id": a.rule_id, "type": a.type})
    print(f"規則 {a.rule_id} 已入庫（現 {len(data['rules'])} 條，下次 check 自動套用）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="ody coach — 契約/機檢/學習")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("new", help="閘1：立契約")
    p.add_argument("task_id")
    p.add_argument("--goal", required=True)
    p.add_argument("--repo", help="目標專案 repo 根（預設：cwd 所在 git repo）")
    p.add_argument("--scope", nargs="+", required=True)
    p.add_argument("--accept", nargs="+", required=True)
    p.add_argument("--verify-cmd", nargs="*", default=[])
    p.add_argument("--permission", nargs="*", default=[])
    p.add_argument("--handoff-file")
    p.add_argument("--po-authorized", action="store_true",
                   help="PO 已明授本任務可動保護路徑（全域設定等）")
    p.set_defaults(fn=cmd_new)

    p = sub.add_parser("evidence", help="填驗收證據（cmd 會執行並記 exit/輸出）")
    p.add_argument("task_id")
    p.add_argument("no", type=int)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--cmd")
    g.add_argument("--note")
    p.set_defaults(fn=cmd_evidence)

    p = sub.add_parser("check", help="閘2：機檢驗收 PASS/FAIL")
    p.add_argument("task_id")
    p.set_defaults(fn=cmd_check)

    p = sub.add_parser("add-rule", help="閘3：Mentor 學習——FAIL 轉可機檢規則")
    p.add_argument("--rule-id", required=True)
    p.add_argument("--desc", required=True)
    p.add_argument("--type", required=True,
                   choices=["banned_path_in_diff", "evidence_note_not_generic",
                            "require_cmd_pass"])
    p.add_argument("--msg", required=True)
    p.add_argument("--patterns", nargs="*")
    p.add_argument("--cmd")
    p.set_defaults(fn=cmd_add_rule)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
