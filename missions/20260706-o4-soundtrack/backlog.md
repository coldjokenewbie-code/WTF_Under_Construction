# backlog：o4-soundtrack
> 2026-07-08 更新：定調書已出（out/配樂定調書_2026-07-08.md）；路線已收斂＝**C×方向二**（lyria-002 同質脈衝材料＋後製接合，66.3s 五幕，見 _blockers 實測紀錄）。唯一未決＝使用者對「方向二」點頭；**點頭前禁生成音檔**，但以下路線無關項可先做。

- [x] 研究：lyria-002 上限（30s，官方 notebook）＋三路線查證 → out/music-research_2026-07-08.md
- [x] 時間軸抽取：Opening 66.3s/11段/兩段旁白、Event1985 40.0s、現行 prompt 與掛載缺陷 → 定調書第一、三節
- [x] 定調書（負錨解剖/五幕情緒任務/兩方向/接線必修）→ out/配樂定調書_2026-07-08.md
- [ ] 【討論閘】使用者拍板方向二（或改方向一）——見 _blockers
- [ ] （路線無關，可先做）o4 repo 開分支 `music-redo`：修 `MusicTrack.tsx`——淡入(~1s)/65.3s 起淡出/旁白 ducking 音量包絡、音量參數化（預設 0.3）；tsc 過、不動 comps 其他部分；推分支禁推 main
- [ ] （路線無關，可先做）生成腳本重寫：按定調書第三節五幕表產 lyria-002 prompt 組（方向二語彙、材料同質、每段標注目標秒數區間與接合點）＋後製接合腳本（ffmpeg crossfade/automation，輸出 66.3s 的 `Opening_v4.mp3` 與 40s `Event1985_v4.mp3`）→ 存 o4 repo `outputs/配樂重做_20260708/`，含使用者一鍵執行說明
- [ ] （拍板後＋使用者本機生成後）接線：Root.tsx music_version=4、重渲兩支、實播驗收（使用者）
- [ ] 對抗審查：接縫聽感（拼接感=負錨）、五幕事件點對時、音量/ducking 實聽
- [ ] 【M2 界＝最後】→ done
