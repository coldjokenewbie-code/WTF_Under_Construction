# WTF_Under_Construction — 專案需求書 (PRD)

> 版本：v0.2｜2026-04-07｜已整合 Insight 報告四項決策 + Session 實作確認

---

## 一、專案定位

**WTF = Workflows That Flow**

目標：系統性優化 User ↔ Claude 協作工作流，以**複利方式**累積效率與效益——每次工作都比上一次更快、更準、更少摩擦。設定、Skills、流程皆為可累積資產，不做一次性修補。

可延伸適用於其他 AI 工具，但以 Claude 協作效益為優先。

---

## 二、角色定義

| 角色 | 職責 |
|------|------|
| **Product Owner（User）** | 任務分配、需求定義、品質把關、里程碑驗收 |
| **AI Team Lead（Claude）** | 任務執行、AI 團隊管理與協調、成果交付、流程持續優化 |

---

## 三、核心需求

### 3.1 設定同步（跨裝置、跨工具）
- Web Claude Code：雲端 `~/.claude/` 自動通用 ✅
- Desktop / Antigravity：本機設定需與 WTF repo 同步（symlink 或手動複製）
- Cowork：沙盒環境，每次 session 需貼入 CLAUDE.md + cowork.md 載入指令
- Claude Chat：Profile Preferences（帳號層級同步，設定範圍有限）
- 目標：新裝置上線成本 < 5 分鐘

### 3.2 知識累積機制
- WTF repo 為**唯一真理來源（Single Source of Truth）**
- 三層累積架構：
  - **全域**（`~/.claude/CLAUDE.md`）：跨所有工具、所有專案共用
  - **工具層**（`claude-config/claude-code.md`、`cowork.md`）：各工具專屬慣例
  - **專案層**（各專案 `.claude/CLAUDE.md`）：專案特定規則，透過 `/skills-install` 部署
- `/lesson-add` skill：隨時將觀察整合進對應層級，去冗餘後存檔
- `/session-end` skill：每次 session 結束記錄產出、更新儀表板

### 3.3 AI 開發團隊架構（Insight 確認）
- Claude 擔任 Tech Lead：任務分解、決定 what & why、品質把關、最終交付
- Agents（Antigravity 平台）：有明確 scope 邊界，執行 how，不做獨立決策
- 成果驗收：**Playwright 自動化取代截圖**（截圖易卡 session，改用程式化驗證）
- 通過驗收才交 PO 做里程碑確認

### 3.4 工作流自動化
- **Skills 套組**（已建立）：`/merge-main`、`/session-end`、`/lesson-add`、`/cowork-start`、`/skills-install`
- **Skills 套組**（待建立）：`/commit`、`/consolidate`、`/optimize-flow`
- **排程**：凌晨三點（台北時間）自動執行文件整理、PRD 更新、儀表板同步，push branch 供早上確認
- **Hooks**：檔案編輯後自動 lint/format（待設定）
- **跨專案部署**：`/skills-install` 將 WTF skills 複製到其他專案，統一升級

### 3.5 品質管控
- Dev_Workflow skill：規劃→執行→驗證三階段強制執行
- Quality_Guard skill：函式長度、命名、熔斷機制
- Token 用量優化：**里程碑觸發**（非每次 session），達到里程碑時回顧 prompt 與 workflow 效能（Insight 確認）

### 3.6 持續改進機制（Insight 確認）
- Session 結束：`/session-end` 自動記錄（不需 PO 下指令）
- 里程碑：回顧 WTF dashboard，更新優先序，執行 `/insights`
- 排程：半夜自動執行低互動任務，早上 PO 確認 merge

---

## 四、成功指標

| 指標 | 現況 | 目標 |
|------|------|------|
| 新裝置上線時間 | 手動設定，30+ 分鐘 | < 5 分鐘 |
| PO 介入次數 | 每個小步驟都要確認 | 只在里程碑驗收 |
| Token 用量 | 未追蹤 | 建立 baseline 後逐步下降 |
| 跨 session 知識保留 | 依賴手動貼上 | WTF repo 自動記錄 ✅（session-end 建立）|
| 跨專案知識加乘 | 各自分散 | skills-install 統一部署，lesson-add 三層累積 |

---

## 五、待確認事項

1. **Playwright 驗收範圍**：哪些成果類型需要 Playwright 驗證？哪些 Claude 可自行判斷？
2. **Antigravity agents 獨立決策邊界**：輔助執行已確認，但特定模組可否授權獨立決策？
3. **排程設定**：`/schedule` 連線問題待解決後設定凌晨三點自動任務

---

## 六、不在範圍內（Out of Scope）

- 特定應用程式的功能開發（如 Planner2Line）— 那是獨立專案
- 非 Claude 生態的 AI 工具深度整合（未來可擴充）

---

## 七、版本紀錄

| 版本 | 日期 | 主要變更 |
|------|------|----------|
| v0.1 | 2026-04-03 | 初稿，定義角色、核心需求、待討論事項 |
| v0.2 | 2026-04-07 | 整合 Insight 四項決策；新增跨專案累積架構；確認 session 自動記錄、里程碑觸發 token 優化；更新排程計畫 |
