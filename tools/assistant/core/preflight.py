"""preflight — 任務前置授權評估（硬規則）。

接到任何任務、真正動工前，先評估 5 類「需使用者授權」的點，產一張清單：
  A 打計費 API key
  B 登入 + 操作活站（Power Automate / PA Studio / 需帳密網站）
  C 連網下載/安裝（npm/pip install、git clone/pull）
  D 動使用者既有成品/設定（改檔、commit/push）
  E 破壞性操作（刪檔、覆寫、reset）

規則：任一類被觸發且未事先授權 → 不動工，把清單交使用者一次談定；
全清 → 直接一路做完，過程中不再要權限。
"""
from __future__ import annotations
from dataclasses import dataclass, field

CATEGORIES = {
    "A_paid_api": "打計費 API key（按 token 收費）",
    "B_live_site": "登入 + 操作活站（Power Automate / PA Studio / 需帳密網站）",
    "C_network_install": "連網下載 / 安裝（npm·pip install、git clone·pull·fetch）",
    "D_touch_user_files": "動你既有成品/設定（改檔、commit、push）",
    "E_destructive": "破壞性操作（刪檔、覆寫、git reset）",
}


@dataclass
class Assessment:
    triggered: list = field(default_factory=list)   # [(cat, reason)]
    approved: list = field(default_factory=list)     # 已在 spec 事先授權的 cat
    blocked: list = field(default_factory=list)      # 觸發但未授權 → 擋
    llm_note: str = ""                               # LLM 用量提示（非授權類）

    @property
    def clear(self) -> bool:
        return len(self.blocked) == 0


def assess(spec: dict, entry) -> Assessment:
    con = spec.get("constraints", {})
    caps = getattr(entry, "capabilities", {}) or {}
    approved = set(con.get("approvals", []))  # spec 可事先授權：["C_network_install", ...]
    trig: list = []

    def hit(cat, reason):
        trig.append((cat, reason))

    # A 計費 API：框架預設一律不打；只有 spec 明示或 handler 宣告才觸發
    if con.get("use_paid_api") or caps.get("paid_api"):
        hit("A_paid_api", "spec/handler 宣告要打計費 API")

    # B 活站操作
    if con.get("operate_live_site") or caps.get("live_site"):
        hit("B_live_site", "需登入並在活站點擊操作")

    # C 連網 / 安裝
    if con.get("install") or caps.get("install"):
        hit("C_network_install", "需連網下載或安裝套件")
    elif con.get("allow_network") or caps.get("network"):
        hit("C_network_install", "任務開啟了連網（allow_network=true）")

    # D 動使用者既有檔
    if con.get("touch_user_files") or con.get("commit") or caps.get("writes_user_files"):
        hit("D_touch_user_files", "會寫入/覆蓋你的既有成品或設定")

    # E 破壞性
    if con.get("allow_destructive") or caps.get("destructive"):
        hit("E_destructive", "含刪檔/覆寫/reset 等破壞性動作")

    blocked = [(c, r) for c, r in trig if c not in approved]

    # LLM 用量提示（非授權類，僅告知）
    if con.get("allow_llm"):
        llm = "會用 LLM 做 fallback，但走訂閱 CLI（claude -p / codex / agy），非計費 API"
    else:
        llm = "不呼叫任何 LLM（純本地確定性）"

    return Assessment(triggered=trig, approved=sorted(approved),
                      blocked=blocked, llm_note=llm)


def render(a: Assessment) -> str:
    lines = ["【前置授權評估】"]
    lines.append(f"  LLM：{a.llm_note}")
    if not a.triggered:
        lines.append("  ✅ 不觸發任何需授權項（A–E 全無）→ 可直接一路做完，過程中不會再要權限")
    else:
        for cat, reason in a.triggered:
            mark = "🟢已授權" if cat not in [c for c, _ in a.blocked] else "🔴需你授權"
            lines.append(f"  {mark} {cat}｜{CATEGORIES[cat]}｜因：{reason}")
        if a.clear:
            lines.append("  ✅ 觸發項皆已事先授權 → 可一路做完")
        else:
            need = "、".join(c for c, _ in a.blocked)
            lines.append(f"  ⛔ 未授權，暫停動工。請一次授權：{need}"
                         f"（在 spec.constraints.approvals 加入，或授權後重跑）")
    return "\n".join(lines)
