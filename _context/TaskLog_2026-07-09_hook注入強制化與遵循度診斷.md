# TaskLog 2026-07-09：SessionStart hook 強制注入 GLOBAL/AGENTS + 遵循度診斷

> 承接 `TaskLog_2026-07-03_fable5制度建置.md`「派 claude@windows」節發現的問題：另一 session 查證出 SessionStart hook 只注入三檔制，GLOBAL.md／AGENTS.md 從未被結構讀取。本 session 驗證同一問題發生在自己身上，並動手修正。

## 起因

本 session 開場（跑 `/session-start`）同樣沒有讀 GLOBAL.md／AGENTS.md——CLAUDE.md 寫「強制初始化協議」，仍被跳過，直到使用者在對話中質問才補讀。與另一 session 的發現是同一故障模式。

## 完成項目

1. 確認根因：`wtf-config/hooks/wtf-session-context.sh` 原本只注入 `_context/INDEX.md`、`lessons-learned.md`、當前 TaskLog；GLOBAL.md／AGENTS.md 純靠開場協議文字指示模型「自己去讀」——不可靠，已證實。
2. 改 hook（黃區，經核准）：新增 `WTF_ROOT` 錨點解析（讀 `~/.claude/wtf-root.txt`），強制注入 GLOBAL.md／AGENTS.md 全文，比照既有三檔制做法。本機（Mac）已部署驗證（commit `f49f131`）。
3. 追加的「回報要求」banner（要求模型印確認字串以供人工判斷 hook 是否生效）被證實是假陰性指標：在 `cowork_CDIC` 專案一個獨立 session 實測，hook stdout 確實送達（查該 session transcript 的 `hook_success` attachment 證實內容完整），但模型未印出該 banner——讀到了，沒照做。banner 已移除（commit `829ade6`）。
4. 查證 Claude Code hook 機制（claude-code-guide agent ×2）：
   - plain stdout 注入層級＝**system reminder**，非普通 tool_result，已是目前可用的最高層級。
   - 另有 JSON `additionalContext` 格式，但有 **10,000 字元上限**；現有注入內容實測 **63,779 字元**，遠超上限，無法改用 JSON 全量注入。官方文件對「模型是否保證遵循 hook 注入內容」**無任何承諾**——確認是 Claude Code 本身的空白，非配置錯誤。
5. 討論 PreToolUse 攔阻式強制（B 方案）：使用者判斷只能到專案層級、無法覆蓋通用原則，不採用。

## 未解決問題

- P1：模型遵循度無結構性保證手段。原本靠「回報要求」banner 當稽核對象，已證實是假陰性指標並刪除（見上）——banner 既已刪，不存在稽核對象，**不建稽核腳本**。此問題目前無解法，維持現況（system reminder 已是可用最高層級）。
- P1：Windows 端 hook 部署仍未確認（詳見 `TaskLog_2026-07-03_fable5制度建置.md`「派 claude@windows」節，本次未變動，待辦持續有效）。

## 主要輸入檔案

- `wtf-config/hooks/wtf-session-context.sh`（黃區，本次改動已提案核准）
- 官方文件：https://code.claude.com/docs/en/hooks.md（經 claude-code-guide agent 查證，未落檔另存，結論見上）

## 下一步建議

1. Windows 端補跑 hook 部署（見 07-03 TaskLog 待辦）並回勾 `nightly-notify.md`。
2. 結論：現有機制已是 Claude Code 能給的最高保證（system reminder 層級），遵循度問題無法單靠 hook 工程解決，也不建稽核腳本（無稽核對象）。維持現況，不再投入。
