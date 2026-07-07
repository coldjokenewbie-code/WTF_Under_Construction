# blockers：o4-soundtrack
- [ ] 2026-07-08｜**需使用者決策｜配樂重做路線三選一**（依據 `out/music-research_2026-07-08.md`，查證摘要如下）：
  - **A 單段 Lyria 生成**：lyria-002 上限 **30 秒**（官方範例 notebook 證實，無 continuation 參數）→ 60s 單段**做不到**；唯一達 60s+ 的是 **Lyria 3 Pro（最長 3 分鐘，2026-04 起 Public Preview）**。前置：需在本機（有 ADC 的環境）確認專案能否呼叫 Lyria 3 Pro。
  - **B 授權曲庫（envato 等）**：技術最穩，但「政府展場循環播放」是否在授權範圍內**未能查證**（雲端網路白名單擋 envato 全系網域）——需使用者瀏覽器查 license 頁或問客服。
  - **C 30s 無縫 loop 鋪底**：不需新權限、成本最低，但 crossfade 接縫失手＝重蹈拼接感覆轍，建議只當 fallback。
  - 建議順序：先花 5 分鐘在本機 GCP 確認 Lyria 3 Pro 可用性 → 可用選 A；不可用查 B 授權；都不行才 C。
- [ ] 2026-07-08｜需本機/使用者查證（雲端 403 實測主 session 與 subagent 皆擋）：docs.cloud.google.com 的 Lyria API 正式參考頁（lyria-002 現行上限交叉核對）＋ envato 授權條款頁。
- [ ] 2026-07-07｜需使用者轉知｜V2 docx 文案誤植「19世紀初期」應為 1929，待使用者回報英審。
