# 2026-06-08 Nightly Routine 修正（v2.0 雲端掃描修復）

## 完成項目
- 審查 claude code routine v2.0 prompt（`wtf-config/nightly-prompt.md`），實測 registry 解析 pipeline（正確抓 11 repo）。
- 定位致命問題：v2.0 第 1 步改用動態 `git clone https://github.com/...`，雲端直連 github.com 無憑證必失敗（實測 `could not read Username`），反而比 v1.0「靠 trigger 預掛載」掃得更少。
- 修正 `nightly-prompt.md`：移除無效 clone、改為只 pull/log 已掛載 repo（未掛載明確標出）、加 `TZ='Asia/Taipei'` 定義「今日」、去掉被 `--format` 覆蓋的多餘 `--oneline`、修第 2 步 mojibake、第 6 步加未掛載提醒。
- SSOT 收斂：用戶刪除舊 `projects.md`（與 registry 分岔），統一到 `projects-registry.md`（確認 repo 內無殘留引用）。
- 用戶端：`/schedule update` 成功，確認 CLI 對話式可改 routine repo 清單（無 flag 式批次）。

## 未解決／下一步
- 本次產出仍在分支 `claude/optimistic-galileo-eCz2c`，尚未 merge main（待用戶確認）。
- 建議用戶把 trigger Repositories 對齊 registry（或只掛活躍 repo），registry 增刪後回 `/schedule update` 同步。

## 環境
- Claude@雲端 ephemeral container，repo `/home/user/WTF_Under_Construction`。
