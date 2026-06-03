# 工作紀錄 2026-06-03 — 階段一：SSOT 同步架構重構

> 跨機協作（Claude@Windows TL + Claude@Mac）。承接「全域設定自動同步架構重整」，完成架構討論並執行階段一。

## 1. 本次完成項目

**架構討論（4 輪收斂）** → `workingfiles/SSOT同步架構討論_2026-06-03.md`
- 定案：放棄 symlink、全實體副本；自動觸發＝UserPromptSubmit hook＋5 分冷卻；單一專案註冊表；SSOT 最終態抽 Drive 外（階段二）；跨工具先共用 AGENTS.md。

**階段一執行 T1–T8（全數驗收 PASS）** → `workingfiles/階段一執行_2026-06-03.md`（信號區）
1. T1 `classify` 加 ADOPT：無標頭但 body==SSOT 自動補標頭接管（收編 Mac 7 FOREIGN→0）。
2. T2 `sync_config.py` 改讀 `projects-registry.md`（registry_dirs），廢 extra-scan-dirs.txt 與相對路徑推導。Windows 跨平台實測掃描正確。
3. T3 `.gitignore` 加 `/AGENTS.md`、root AGENTS.md 解除追蹤（原 git 記為 symlink 120000，typechange 根除）。
4. T4 Windows 補掛 UserPromptSubmit hook（`~/.claude/wtf-sync.ps1`）+ 清 settings.json 死路徑（T5）。**hook 已實測本 session 觸發成功**。
5. T6 `deploy_claude_dir()` 改逐 skill `copytree(dirs_exist_ok)` 容錯覆蓋，廢破壞性 `rmtree(~/.claude/skills)`（修 Windows ai-team 鎖定整批失敗）。
6. T7 `session-start` skill 去重：check→僅 STALE/BROKEN/MISSING fallback，不與 hook 重工。
7. T8 `tasklog-naming` 加「INDEX 只指路、不複製 todo」規則；更新過時 INDEX.md。
8. 新增 `projects-registry.md`（專案×機器×路徑單一註冊表）。

**版控**：已 commit＋push `120fb16`（14 檔，+718/−63）到 origin/main。

## 2. 未解決問題（依優先度）

- **P1 — 階段二：wtf-config 移出 Drive**（本次交接主題）：抽成 Drive 外獨立 git repo、hook 只 pull 它、主 repo 退出 hook、`_context` 靠 Drive。詳見 `Handover_2026-06-03_階段二-wtf-config移出Drive.md`。
- **P2 — 跨工具副本**：Antigravity 原生 Gemini 是否只認 `GEMINI.md`、不讀 `AGENTS.md`，需用戶實測；確認前不產第二種副本。
- **P2 — Mac git 對齊**：Mac hook 下次 `git pull` 需 ff 到 `120fb16`（先清 .git/*.lock）。
- **P2 — hook 載入時機**：settings.json 中途新增的 hook 本 session 已生效（實測），但其他機器/工具未驗。

## 3. 主要輸入檔案

- `wtf-config/sync_config.py`（已重構）、`wtf-config/projects-registry.md`（新建）
- `wtf-config/skills/session-start/`、`skills/tasklog-naming/SKILL.md`、`skills/skills-install/SKILL.md`
- `~/.claude/wtf-sync.ps1`（新建）、`~/.claude/settings.json`（hook + 清死路徑）
- `_context/INDEX.md`、`_context/lessons-learned.md`、`wtf-config/LESSONS.md`

## 4. 下一步建議

1. 開始階段二（移出 Drive）→ 讀 `Handover_2026-06-03_階段二-wtf-config移出Drive.md`，先定 D1–D5 決策點。
2. 階段二前確認 Mac 已 `git pull` 對齊 `120fb16`。
3. 實測 Antigravity 原生 Gemini 的規範檔讀取，決定是否產 GEMINI.md 副本。
