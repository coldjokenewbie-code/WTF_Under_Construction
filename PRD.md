# WTF_Under_Construction — 專案需求書 (PRD)

> 版本：v0.1 草稿｜2026-04-03｜待 Product Owner 確認

---

## 一、專案定位

**WTF = Workflows That Flow**

目標：系統性優化 User ↔ Claude 協作工作流，每次互動都比上一次更高效，形成**複利累積**，而非頭痛醫頭。

可延伸適用於其他 AI 工具，但以 Claude 協作效益為優先。

---

## 二、角色定義

| 角色 | 職責 |
|------|------|
| **Product Owner（User）** | 任務分配、需求定義、品質把關、工作效益控管 |
| **AI Team Lead（Claude）** | 任務執行、AI 團隊管理與協調、成果交付、流程持續優化 |

---

## 三、核心需求

### 3.1 設定同步（跨裝置、跨工具）
- Web Claude Code：雲端 `~/.claude/` 自動通用 ✅
- Desktop / Antigravity：本機設定需與 WTF repo 同步
- Claude Chat：（待確認）Profile Preferences 可設定範圍
- 目標：新裝置上線成本 < 5 分鐘

### 3.2 知識累積機制
- WTF repo 為**唯一真理來源（Single Source of Truth）**
- 每次 session 的決策、錯誤、改進點都記錄在案
- 儀錶板即時呈現當前狀態與待辦
- 禁止讓知識散落在不同 session、無法復原

### 3.3 AI 開發團隊架構
- Claude 擔任 Tech Lead：任務分解、品質把關、最終交付
- 其他 AI agents（Antigravity 平台）：執行特定模組或任務
- 分工原則：Claude 決定 what & why，agents 執行 how
- 成果驗收：自動截圖 + Claude 自行判斷，通過才交 PO 測試

### 3.4 工作流自動化
- **Skills 套組**：`/commit`、`/review-ui`、`/consolidate`、`/optimize-flow`
- **Hooks**：file 編輯後自動 lint/format
- **Headless Mode**：可從 CI/腳本呼叫 Claude 執行任務
- **目標**：減少人工介入，PO 只做驗收決策

### 3.5 品質管控
- Dev_Workflow skill：規劃→執行→驗證三階段強制執行
- Quality_Guard skill：函式長度、命名、熔斷機制
- Token 用量監控：定期（或觸發式）優化 prompt 與 workflow

### 3.6 持續改進機制
- 每個 session 結束：記錄本次的問題點與改進項目
- 定期（每月或每里程碑）：回顧 WTF dashboard，更新優先序
- Insight 報告：定期執行 `/insights`，量化工作流效能

---

## 四、成功指標

| 指標 | 現況 | 目標 |
|------|------|------|
| 新裝置上線時間 | 手動設定，30+ 分鐘 | < 5 分鐘 |
| PO 介入次數 | 每個小步驟都要確認 | 只在里程碑驗收 |
| Token 用量 | 未追蹤 | 建立 baseline 後逐步下降 |
| 跨 session 知識保留 | 依賴手動貼上 | WTF repo 自動記錄 |

---

## 五、待討論事項（請 PO 確認）

1. **Antigravity 其他 AI agents 的角色**：是輔助執行，還是也能獨立決策某些模組？
2. **自動截圖驗收的邊界**：哪些類型的成果需要截圖驗收？哪些 Claude 可自行決定？
3. **session 知識記錄的觸發時機**：session 結束時主動記錄，還是 PO 下指令才記？
4. **Token 用量優化的頻率**：每個 session 結束自動跑，還是每月一次？
5. **Chat / Cowork 同步方案**：Profile Preferences 的實際可設定範圍確認後，再決定策略。

---

## 六、不在範圍內（Out of Scope）

- 特定應用程式的功能開發（如 Planner2Line）— 那是獨立專案
- 非 Claude 生態的 AI 工具深度整合（未來可擴充）
