# CDIC O4 — Chat 專案知識庫

> 由 `/lesson-add 專案 CDIC-O4 [內容]` 維護。

## 專案背景

CDIC 史料館 O 區投影牆歷史事件影片，以 Remotion 製作，共 6 支 1920×1080 MP4。
GitHub repo：`coldjokenewbie-code/claude_CDIC_O4`
本機無 clone，開發透過 GitHub MCP。

## 慣例與限制

- 影片素材放置時需含數字前綴（`_1_`/`_2_`/`_3_`/`_4_`），Agent 建檔時容易遺漏，需在 prompt 明確指定
- Composition props 採 schema + inline literal 架構，自動儲存正常運作

---

## 累積 Lessons

<!-- lessons-start -->
**[2026-04-25] Remotion OffthreadVideo 靜音**
用 `volume={0}` 而非僅 `muted`；Studio preview 在只有 `muted` 時仍洩漏音軌。

**[2026-04-25] KenBurnsClip 負 frame 保護**
加 `extrapolateLeft:'clamp'`，保護 premount 場景下 frame 為負時不出錯。

**[2026-04-25] Agent 建檔命名前綴**
指示 Agent 建立圖檔路徑時，需明確說明完整命名規則（如含 `_1_`/`_2_` 前綴），否則前綴易被省略導致路徑錯誤。
<!-- lessons-end -->
