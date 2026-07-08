# backlog：o4-soundtrack
> 2026-07-08 更新：定調書已出（out/配樂定調書_2026-07-08.md）；路線已收斂＝**C×方向二**（lyria-002 同質脈衝材料＋後製接合，66.3s 五幕，見 _blockers 實測紀錄）。唯一未決＝使用者對「方向二」點頭；**點頭前禁生成音檔**，但以下路線無關項可先做。

- [x] 研究：lyria-002 上限（30s，官方 notebook）＋三路線查證 → out/music-research_2026-07-08.md
- [x] 時間軸抽取：Opening 66.3s/11段/兩段旁白、Event1985 40.0s、現行 prompt 與掛載缺陷 → 定調書第一、三節
- [x] 定調書（負錨解剖/五幕情緒任務/兩方向/接線必修）→ out/配樂定調書_2026-07-08.md
- [ ] 【討論閘】使用者拍板方向二（或改方向一）——見 _blockers
- [x] （路線無關，可先做）o4 repo 修 `MusicTrack.tsx`：淡入(1s)/結尾淡出(1s，用 useVideoConfig 總長自動算，免外部傳總幀數)/旁白 ducking 音量包絡(duckingWindows prop)、音量參數化（預設 0.3）；tsc 過(npm install 後乾淨)、只動此檔不碰 comps 其他部分。**分支改用 harness 指定的 `claude/sharp-gates-uebbk0`**（非 backlog 原訂 `music-redo`——本 session 的 GitHub 存取受 per-repo designated branch 限制，禁推非指定分支；已推 origin，PR 未開）。commit d8b50d8。
- [x] （路線無關，可先做）生成腳本重寫：按定調書第三節五幕表產 lyria-002 prompt 組（方向二語彙、材料同質、每段標注目標秒數區間與接合點）＋後製接合腳本（ffmpeg crossfade/automation，輸出 66.3s 的 `Opening_v4.mp3` 與 40s `Event1985_v4.mp3`）→ 存 o4 repo `outputs/配樂重做_20260708/`，含使用者一鍵執行說明。6 段素材（opening_S1~S4／event1985_E1~E2）切法按「動機狀態」非畫面幕數（lyria-002 無 continuation 參數，演變靠跨素材 crossfade 非單次生成內部漸變）；crossfade 接合點秒數已用公式反推核對＝Opening 26.0/48.6/60.5s、Event1985 23.25s，全長精確等於 66.3s/40.0s（見 prompts 檔末節算式）。**未執行測試**：沙盒無 ffmpeg（apt 源 404）、無 GCP 憑證，靠人工算式覆核，未實跑生成或接合，留待使用者本機驗證。
- [ ] （拍板後＋使用者本機生成後）接線：Root.tsx music_version=4、重渲兩支、實播驗收（使用者）
- [ ] 對抗審查：接縫聽感（拼接感=負錨）、五幕事件點對時、音量/ducking 實聽
- [ ] 【M2 界＝最後】→ done
