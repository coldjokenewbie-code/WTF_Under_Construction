# 續作點 — session gate 階段4 收尾（2026-07-19 暫停）

## 一句話現況
gate 在觀察模式（安全、不鎖）。根因已定＝import 手改部署副本被 wtf-sync 洗掉（非 headless 不相容）。正在讓 sync_config.py 自動維護 import 以根治。

## 系統當前狀態（暫停時）
- `~/.claude/settings.json`：**PreToolUse 已移除**＝觀察模式，無任何 hook 擋工具。備份在 `~/.claude/settings.json.pre-observe.*`。
- `~/.claude/CLAUDE.md`：無 import（被 sync 洗掉，＝與 SSOT 同 hash 594e62cd）。
- gate 記錄型 hook（SessionStart init／InstructionsLoaded／PostToolUse）仍掛著，只記錄不阻擋。
- bundle 已存在：`~/.claude/wtf-session-bundles/ba55340b…/`（GLOBAL＋AGENTS，hash 對得上當前 SSOT）。
- 契約 `wtf-session-gate-impl-20260716`：階段1-3 已 commit（5f85454）＋ody PASS。
- 契約 `wtf-session-gate-headless-20260719`：進行中（本次收尾）。

## 待續（依序）
1. **codex 改 sync_config.py**（背景 task bxlfjadye 進行中）：新增 deploy_session_bundle()——部署 CLAUDE.md 後自動寫入當代 SHA 的 managed import block；check 加三處 SHA 一致機檢。產出 PHASE_FIX_REPORT.md。
   - **續作第一步：驗證 codex 改動**——`python3 wtf-config/sync_config.py check` 與 `sync` 能跑、冪等、不回歸（18 專案 AGENTS.md／skills 照舊）；`ast.parse` 語法確認。若改壞先 `git checkout wtf-config/sync_config.py` 還原（觀察模式下還原安全）。
2. **canary 三格**（主 session 跑，需 claude 認證）：user-only／project-only／user+project，各驗 claude -p 下 InstructionsLoaded include 收據自動簽成＋工具放行、import 缺失時 fail-closed。第一手事件留證。
3. **agy 對抗質疑** codex 的 sync 改動（headless）。
4. **coach check ＋ ody-verifier 獨立複驗**。
5. **PO 恢復強制**（最後一步，需 PO 執行）——把 PreToolUse 加回 settings.json：
   ```
   ! python3 -c "import json; p='/Users/coma/.claude/settings.json'; c=json.load(open(p)); c['hooks']['PreToolUse']=[{'matcher':'*','hooks':[{'type':'command','command':'bash /Users/coma/git_mirror/WTF_Under_Construction/wtf-config/hooks/wtf-session-gate.sh pretool'}]}]; json.dump(c,open(p,'w'),indent=2,ensure_ascii=False); print('PreToolUse 已恢復')"
   ```
   恢復前務必先跑 sync（讓 CLAUDE.md 有 import）＋機檢三處 SHA 一致，否則會再次鎖死。

## 已知安全網
- 觀察模式下 sync 壞掉只是「沒同步」，不鎖死（wtf-sync.sh 非阻擋型）。
- 恢復強制後若又鎖：`! cp ~/.claude/settings.json.pre-observe.<最新> ~/.claude/settings.json` 即回觀察模式。

## 教訓（待 session-end 整併）
- 部署 gate＋bundle SHA＋CLAUDE.md import 是同一版本單元，必須原子部署由 sync 統一產生；手改部署副本必被 sync 洗掉（本次事故）。
- 恢復強制前的機檢：CLAUDE.md import SHA＝bundle 目錄＝manifest digest 三者一致才准開 PreToolUse。
