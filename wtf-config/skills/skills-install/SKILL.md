---
name: skills-install
description: 部署 WTF skills（混合架構：共用 skill 走全域 ~/.claude/skills，專案只放專屬 skill；全程實體複製不用 symlink）。用法：/skills-install（部署全域）| /skills-install check（檢查狀態）
---

# Skills Install

## 架構：共用走全域、專案放專屬（混合架構）

- **共用 skill（SSOT 12 個）**：Dev_Workflow、Quality_Guard、ai-team、cowork-start、handover、lesson-add、merge-main、session-start、session-end、skills-install、tasklog-naming、ui-review。
  - 來源（SSOT）：`wtf-config/skills/`
  - 部署目標：**全域** `~/.claude/skills/`（每台機器各自一份實體副本，任何專案都讀得到）。
  - 部署方式：`python sync_config.py sync`（實體複製，順帶部署 `~/.claude/CLAUDE.md`）。
- **專案專屬 skill**（如 `data-verify`、`thumbnail-aware-images`、`codex-global-instruction`、`remotion-best-practices`）：
  - 直接存活在該專案 `.claude/skills/`，隨專案（git repo 或 Drive）一起走，**不進全域、不進 SSOT**。

> 🔸 **`ai-team` 是特例（共用範本＋專案就地實例）**：其 SKILL.md 規定 Tech Lead 把專案文件（`AI_TEAM_DIVISION.md`、`AI_TEAM_WORKFLOW.md`、`agent-specs/*`）就地建立在 `.claude/skills/ai-team/` 內、與 `_TEMPLATE` 範本並存。因此**有客製內容的專案要保留完整的 `.claude/skills/ai-team/`**（SKILL.md＋3 範本＋專案實例），當作覆蓋全域的專案級 skill；**清理共用副本時，絕不可整個刪掉含專案實例的 ai-team**。未客製 ai-team 的專案則靠全域即可。

> ⚠️ **兩條鐵律**
> 1. **絕不用 symlink**。Drive／git 跨平台同步（Mac↔Windows）後 symlink 變死檔（見 lessons-learned「symlink 去中心化方案已被推翻」）。一律實體複製。
> 2. **共用 skill 不再複製進各專案 `.claude/skills/`**。那會造成每個專案各自過期的孤兒副本（過去 skills 漂移的根因）。共用一律靠全域。

---

## 用法

### `/skills-install`（部署全域共用 skill）
等同 `python sync_config.py sync`：把 SSOT 11 個 skill 實體複製到 `~/.claude/skills/`，並部署 `~/.claude/CLAUDE.md`。
- 新機器首次設定、或改過 `wtf-config/skills/` 後執行。
- 各機器都要各跑一次（全域副本是 per-machine）。

### `/skills-install check`（檢查狀態）
等同 `python sync_config.py check`：回報全域 `~/.claude/skills/` 與各專案 `AGENTS.md` 是否與 SSOT 一致，並列出 symlink 殘跡／孤兒檔。

---

## 新增 / 修改 skill
- **共用 skill**：改 `wtf-config/skills/<name>/`（SSOT）→ 各機器跑 `sync_config.py sync` 重新部署全域。
- **專案專屬 skill**：直接在該專案 `.claude/skills/<name>/` 編輯，隨專案版控／同步。

## 重要限制
- 不覆蓋 `.claude/CLAUDE.md`、專案 `AGENTS.md`（由 sync_config 另行管理）。
- 專案層 `.claude/skills/` 只應含「專屬 skill」；若發現共用 skill 的孤兒副本，應刪除（改靠全域）。
