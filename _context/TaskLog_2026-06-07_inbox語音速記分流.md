# 工作紀錄 2026-06-07 — Inbox 語音速記分流（控制面 Phase B 起手）

> 承接控制面規劃。把 Phase B「語音 inbox → 分流入專案」從構想落為可跑的 `/inbox` skill＋設定。
> 作者：[Claude@Mac]

## 1. 決策定案

- **來源 inbox**：Obsidian vault（Google Drive）`ObsidianCJN/Clippings/`，沿用既有 Web Clipper inbox，**非 git repo**（符合「inbox 放 Drive 不放 repo」）。
- **辨識慣例**：檔名**開頭為「工作」**＝WTF 任務速記（不用底線，方便手機語音輸入）；其餘＝知識剪藏走原 wiki ingest。
- **落地**：寫進**目標專案自己的 github repo** `_context/INBOX.md`（git 跨機同步），commit/push；不寫中央 INBOX、不寫 Drive 鏡像。判不出歸屬 → WTF repo `_context/INBOX.md`「（未分類）」。
- **觸發**：**本機手動 `/inbox`**。雲端 routine 讀不到本機 Drive 掛載，無法代跑；hook 自動偵測浮出＝未來選配（目前先手動）。

## 2. 完成項目

- **vault `ObsidianCJN/CLAUDE.md`**：加分流規則——wiki ingest 跳過「工作」開頭檔，留給 `/inbox`。
- **`wtf-config/inbox-config.md`**（新）：per-machine vault 路徑（Mac 已填／Win 待補）＋分流落地規則。
- **`wtf-config/projects-registry.md`**：重構為**專案為主**格式 `| project | github | <hostname欄...> |`，補各專案 github。
- **`wtf-config/sync_config.py`**：
  - `registry_rows()`／`registry_dirs()` 改讀表頭依 hostname 對應欄（相容新格式）；`check`／`sync` 已驗證通過。
  - 新增 `inbox-info` 子指令：輸出 JSON（vault／clippings／ingested／pending／projects 路由表）供 skill 跨平台取資料。
- **`wtf-config/skills/inbox/SKILL.md`**（新）：`/inbox` 分流流程。已 sync 部署（11 skills，含 Codex／Gemini）。
- 煙霧測試：建「工作」開頭檔→`inbox-info` 正確列入 pending→清除 OK。

## 3. 派 claude@windows（待辦）

> claude@windows 下次開場讀到此段即執行。完成後回寫本段打勾。

- [ ] **補 Windows vault 路徑**：在 `wtf-config/inbox-config.md` 把 `DESKTOP-7SF21LR` 列的 `vault_path` 由佔位改為實際 My Drive 掛載點（如 `G:\我的雲端硬碟\ObsidianCJN`，請實查磁碟機代號）。改完跑 `python sync_config.py inbox-info` 確認 vault 非 null。
- [ ] **確認 3 專案 github**（Mac 鏡像無 .git，可能 Windows 端才有）：Aseembly_Plant_Interactive_machine、出勤專案、南科再生水廠。各跑 `git -C "E:\Claude_cowork\projects\<專案>" remote get-url origin`，有就把 registry github 欄佔位換成實際 URL；確無 git 則註明。

## 4. 待用戶（找時間補）

- 3 專案 github URL（同上，若 Windows 端也無，需用戶決定是否建 repo）。
- Aseembly_Plant_Interactive_machine、出勤專案、南科再生水廠 在 has_github=false 期間，`/inbox` 不分流到它們（會列「待補 github」跳過）。

## 5. 注意

- 全域技能數 10→**11**（加 inbox），超過 GLOBAL「>10 提示精簡」門檻。下次審查可評估是否合併/精簡。
