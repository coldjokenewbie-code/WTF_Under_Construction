# Plan 2026-09-14｜ai-team 制度優化

> [Codex@comaMacBookAir] Tech Lead。PO 已授權共識後動工、交互驗收後交 PO；禁止自行 commit。2026-09-14 第 4 輪 Fable 5.1 確認無分歧。

## 原因與目標

- 型號與派工規則過時；一次更新模型表、管道、重試和驗收規則。
- Codex 已能載入 skill，且本 session 有原生 metadata 清單。補可查核的備援索引，不新建觸發引擎或重複維護 triggers。
- GLOBAL 細則過度內聯。保留常駐防線，完整細則搬入按需 playbook，不弱化 PO 裁定。
- 既有 check 只比技能資料夾名，漏掉內容漂移；舊 prune 會刪非 WTF 本地 skill，部署前須修正。

## 順序、檔案與驗收

| 步驟 | 修改範圍 | 驗收 |
|---|---|---|
| 1 型號與派工 | `wtf-config/playbooks/model-dispatch.md` | V4/V5 四列、Agent fable 與 fresh CLI 分開、最多 4 輪且高階終局一次、ai-team 不自驗 |
| 2 備援索引 | `wtf-config/skill_catalog.py`、`sync_config.py`、`tests/test_skill_catalog.py`、`tests/test_sync_skills.py`、`AGENTS.md`、`CLAUDE_CODE.md`、`CODEX.md`、`GEMINI.md` | metadata 唯一來源、索引內容/副本位元組檢查、故障 exit 1、缺工具 skip、原生清單優先、專案優先、實體複製、保留非 SSOT 目錄 |
| 3 常駐瘦身 | `GLOBAL.md`、`playbooks/maintenance-protocol.md`、`git-mirror.md`、`delivery-conventions.md`、`data-citation.md`、`pitfalls-frontend.md`、`pitfalls-office-docs.md` | 原條目→新節對照；字元/UTF-8 bytes/行數；版控、W_、數據/預覽/FSA 防線可達；session bundle 更新 |
| 4 記錄與驗收 | 本 Plan、當前 TaskLog、INDEX 一行、`workingfiles/ai-team-20260914/` 討論與驗收證據 | fresh Fable 審查 Codex 產出；fixture sync 兩次+check；驗收後實機部署兩次+check；交 PO，不 commit |

`sync_config.py` 原長 951 行，已超過 Quality_Guard 的 300 行門檻。本輪把 skill 共用邏輯抽成小模組，不全面重構 dashboard/register 等無關功能；新增模組及各函式遵守 300/50 行限制。

## 設計契約

- 索引三欄：name、description（沿用 SKILL.md 觸發描述）、path。全域產物在各工具 home 的 `wtf-skills-index.md`，路徑為本機絕對值；專案 `._agents/skills-index.md` 路徑相對專案根。都不把機器絕對路徑寫入跨機 SSOT。
- 只收錄 SSOT，原生清單完整時不另讀索引；缺列/截斷/沒有原生清單時讀 metadata 索引；索引缺失才列來源 metadata。讀不到要回報，不宣稱已套用。
- 索引改善可發現與可稽核，不能保證模型語意觸發。V1–V7 沿用；Antigravity 本輪不呼叫，行為未驗證。
- 缺 name/description、重複鍵/同層重名或非法 metadata：失敗。名稱與資料夾不一致：警告；不同技能描述相同並非重名。
- sync 只新增/覆蓋 SSOT 同名內容，不自動刪任何多餘技能；check 列出額外目錄但不宣稱它們都是已退役 WTF skill。
- GLOBAL 精簡目標為字元數至少減少 35%，不等同 token/帳單減幅；另列所有常駐入口與新增 playbook 的量測。
- 同角色不並派兩個高階；執行和獨立驗收可各用高階。任務失敗與不可得/額度失敗分開，品質條件不能因備援降低。
- 無 UI 變更，視覺驗收不適用。完整驗收後才部署真實環境，避免中間狀態散播。

## 邊界

- WTF 本體就在 `git_mirror/`，是 Drive 工作規則唯一例外。
- 保留既有 `machines.md` 變更與 20 個未追蹤檔；不拉取、不提交、不改其他任務。
- `.claude/settings.local.json` 警告本輪只存證，建議移除該條已禁路徑 allow 規則；不改權限。
- 修改授權來自本次 PO 指令，涵蓋本計畫所列制度與部署修正；不另設動工核准關卡。最後由 PO 驗收。

> 實際執行補記：測試與本機只讀check已過，但環境在審查前自動同步新版入口；正式獨立驗收仍待外傳授權，詳見TaskLog，不能將自動部署視為驗收通過。

> Fable退修後補回指：`skills/session-start/SKILL.md`與`skills/session-end/SKILL.md`只改版控規則指標；CODEX/GEMINI存入協議改指maintenance。測試技能數改讀SSOT，避免新增技能使測試固定在17。

> 最終：Fable第二輪獨立複驗PASS；32tests、7項遷移、99個部署檔sync兩次+check皆過。PO尚未驗收，未commit。詳細證據見當前TaskLog。
