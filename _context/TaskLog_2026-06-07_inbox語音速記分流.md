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

- [x] **補 Windows vault 路徑**（2026-06-07 [Claude@Win]）：用戶提供 `E:\CJN_drive\我的雲端硬碟\ObsidianCJN`，已填入 inbox-config.md DESKTOP 列；`inbox-info` 驗證 vault/clippings/ingested 解析成功、11 專案路由表完整、pending 空。**兩機 vault 路徑齊備，`/inbox` 可雙機跑。**
- [x] **確認 3 專案 github**（2026-06-07 用戶已補，registry 已填）：Aseembly_Plant_Interactive_machine、出勤專案（repo `attendance-dashboard`）、南科再生水廠（repo `S-reclaimed-water-plant`）。**11 專案全有 github，`/inbox` 可分流到全部。**

## 4. 待用戶（找時間補）

- ~~3 專案 github URL~~ ✅ 2026-06-07 已補齊，11 專案全有 github。
- 剩餘待辦：Windows vault 路徑（claude@windows，§3 第一項）。

## 5. 注意

- 全域技能數 10→**11**（加 inbox），超過 GLOBAL「>10 提示精簡」門檻。下次審查可評估是否合併/精簡。

## 6. 首次實跑（2026-06-07 晚，三輪）

- **第 1 輪**：pending 空 → 回報無待分流。
- **第 2 輪（2 筆）**：
  - `工作修正出勤專案的儀表板` → **出勤專案** ✅（commit `17f5ddb`）
  - `工作檔案 Assembly…加入導覽App` → **Aseembly_Plant_Interactive_machine** ✅（commit `00d5804`，連 `_context/` 一併建立）
  - 兩 Drive 鏡像 repo 皆有既存未暫存改動 → `pull --rebase` 拒絕，但 push 為 fast-forward 成功，無衝突。
- **第 3 輪（3 筆）**：
  - `工作相關_cdic_要作電子導覽書` → **cowork_CDIC** ✅（commit `df7d52e`；兩個 CDIC 候選，依近期活躍/性質自行歸納，未問用戶）
  - `工作相關_remotion動態測試` → **Remotion_fun** ✅（commit `6919b0d`）
  - `工作修正出勤專案的儀表板`（與第 2 輪同名）→ 判為**重複**，未再寫入 INBOX，僅移檔到 Ingested 清掉。

### 實跑校準（用戶當場定調 → 已落 lesson + memory）

- **`/inbox` 是快速捕捉工具，下指令後一路處理完、禁中途問**（問歸屬＝浪費用戶時間，他自己標注更快）。本輪我用 AskUserQuestion 問 CDIC 歸屬被打斷糾正。
- **標題式速記（正文空）是多數常態**，不是異常，不必當問題回報。
- **重複速記不重收**（同名/同內容 → 只移檔清掉）。
- 觀察：原 SKILL.md 第 2 步寫「判定有疑慮先列給用戶確認」與此定調衝突，建議下次修 skill 源（`wtf-config/skills/inbox/SKILL.md`）改為「自行歸納、不中途問；判不出才落 WTF 未分類」。
