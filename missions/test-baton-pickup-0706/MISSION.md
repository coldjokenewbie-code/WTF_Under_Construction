# MISSION：test-baton-pickup-0706
## 方向（一句話）
管線探針：驗證「當前面所有 active/待核准 項目都被擋住時，循環棒能正確輪到這條 待規劃 項並完成建 MISSION＋journal＋推 night-relay」這條路徑本身是通的。

## 模糊標準錨點（2-3 個正例＋反例）
- 正例：本棒建出這份 MISSION.md＋journal.md 首筆紀錄，並成功 push 到 night-relay，不觸發任何 git 衝突。
- 正例：QUEUE 狀態機轉換（待規劃→待核准）依規範正確執行，未跳過使用者核准步驟。
- 反例：探針本身被當成真實任務投入多輪 subagent/opus 資源——探針只驗證管線，不是真實產出，過度投入即偏離目的。

## 硬底線（可機檢）
1. 本目錄含 MISSION.md、backlog.md、journal.md 三檔。
2. journal.md 至少一條 append 紀錄，含日期時間＋棒型＋做了什麼＋進展。
3. 本次改動已 commit 且 push 到 origin night-relay（`git log origin/night-relay` 可見對應 commit）。

## Milestone（每個=一次使用者簽核點）
1.（唯一 milestone）探針三檔齊備＋成功推上 night-relay → 即完成，改「待核准」等使用者確認管線探針本身是否可結案（因無實質產出，通常直接核准關閉）。

## 邊界（禁改清單／不做什麼／僅限 repo 內可完成）
- 不產生任何實質對外交付物；不派多方案規劃 subagent（探針性質不需要）。
- 不影響其他 mission 的檔案。
