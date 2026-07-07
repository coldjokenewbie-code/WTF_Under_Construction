# 交接:O4 影片頭兩支(Mac 本機接手)

目標:交付兩支成品 MP4——開場白 60s、E1 1985 35s。TTS 佔位配音(業主日後換錄)、配樂合軌、品質升級版視覺、**無字幕**。

## 已就緒的事實(雲端 Fable session 完成,全在 GitHub main)
1. repo `claude_CDIC_O4`:新增 `src/compositions/OpeningV2.tsx`、`Event1985V2.tsx`、`src/components/CineLayer.tsx`(品質層:開場字卡/年代標記/膠片顆粒/統一調色/金色數字卡),字型已本地打包(@fontsource/noto-serif-tc),Root 已註冊。
2. 音訊路徑約定(gitignore 中,檔案要自己生):`public/audio/vo/opening_vo.wav`、`e1_vo.wav`;`public/audio/music/A_影片四開場_60s.wav`、`B_…`。
3. 生成腳本:`outputs/配樂_20260707/cloudshell_generate.sh`——Lyria 音樂 A/B 10 段+Cloud TTS 配音+自動 push。Mac 有 gcloud ADC 可直接本機跑(把尾段 clone/push 改成 cp 到本 repo)。
4. 分鏡權威=`information/W主題影片四_歷史與制度_0506.xlsx`(場景層級);旁白文字=7/7 v2 docx;0506 的互動轉場段(4-02、各-R)v2 已刪,不做。
5. 時間軸段界(v2 文案,幀@30fps,props 可調):開場白=字卡0-150/原理150-600/大蕭條→FDIC 600-990/台灣990-1350/300萬卡1350-1800;E1=年份卡0-90/十信90-420/成立420-750/70萬卡750-1050。

## 你(Mac session)的步驟
1. **先推 6/15 版(只推程式碼,素材不推)**:本機 repo `git log --oneline -8` 確認 6/15 那批 commit → 若大素材(渲染輸出/新影片檔)未被 gitignore,先補:`printf 'outputs/**/*.mp4\nworkingfiles/agy_clips/**\n' >> .gitignore` → `git checkout -b v615 && git push -u origin v615`。素材全在本機、渲染也在本機,git 只負責程式碼與紀錄;新增的大素材跑一次 `python3 <WTF_ROOT>/tools/asset_inventory.py` 留清單即可。
2. **合流**:以 v615 的 comps 為底,把 main 上的 CineLayer 品質層+V2 時間軸/文案疊上(cherry-pick 或手動移植;Root.tsx 兩邊註冊都保留)。衝突以 6/15 版畫面編排為準、v2 文案與品質層為準。
3. **生音檔**:跑 cloudshell_generate.sh(本機版);TTS 文字中「19世紀初期」是 v2 docx 誤植——**念「1929年」**,並提醒使用者回報英審稿修正。
4. **校時**:量 opening_vo.wav 實長,調 `vo_offset` 與 b1-b4 使旁白段落與畫面段界對齊(±0.5s);音樂音量以不壓旁白為準(約 0.24-0.30)。
5. **渲染**:`npx remotion render OpeningV2 outputs/V3draft/opening_v3.mp4`、`Event1985V2 → e1_v3.mp4`(Mac 無 proxy 限制,Remotion 自帶瀏覽器可下載)。
6. **驗收(硬底線,遵 WTF anchors/README 鐵律)**:實際播放全片看+聽;無字幕;轉場對位;結尾數字卡(300萬/70萬)完整;已知限制=opening_2/8 等佔位影片待 Veo,可暫用但在交付註記。截圖與結果記回 WTF repo `missions/20260706-o4-soundtrack/journal.md`。
7. 交付:兩支 mp4 push(或放 outputs/ 供使用者看),向使用者回報+附已知限制清單。

## 禁忌
- 不動 0506 xlsx 與 v2 docx;不做字幕;不自評分數(只交實播結果);main 上今天的 commits 不要 revert。
