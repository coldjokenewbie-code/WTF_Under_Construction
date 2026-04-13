# Claude Code 工具層設定
> 適用：Claude Code CLI / IDE Extension
> 載入方式：`~/.claude/CLAUDE.md` 指向此檔；本機自動載入

## Trigger A — 新專案（首次開啟）

偵測到專案內無 `.claude/` 設定時，執行：

1. 讀取 `~/.claude/skills/`，列出可用 skills。若未找到，詢問處理方式。
2. 確認摘要：列出啟用的 skills（例：Dev_Workflow、Quality_Guard）。
3. 詢問目前任務或目標。

## Trigger B — 現有專案（後續 session）

1. 重新載入 `~/.claude/skills/`（或 `.claude/skills/`，優先用專案層級）。若未找到，詢問處理方式。
2. 簡述啟用規則（例：`[Dev_Workflow 啟用中] [Quality_Guard 啟用中]`）。
3. 詢問目前任務或目標。

## 溝通慣例與意圖解讀

1. 使用者以繁體中文（台灣用語）溝通。短指令（如座標、表單 ID、「長這樣」）視為字面意義直接執行，不重新詮釋、不捨棄。真正模糊才詢問，其餘不問。
2. 以「簡介」、「說明」、「討論」開頭的輸入，只討論不改動——確認決定後再執行。
3. 「更新儀表板」隱含「merge main」——使用者說要更新儀表板，代表要看到結果，執行後必須 merge main。

## 截圖與圖片

GIF 格式與過大圖片（實測曾卡死 session）建議避免使用；改貼 PNG/JPG 或文字描述。PNG/JPG 上限約 5MB。

## 程式編輯

主要語言：TypeScript、HTML、Python。UI 編輯採增量修改，每次只動一個元素。修改後確認 nav bar 與版面框架完整保留。

## UI 樣式修改

字體大小每次只調 1-2px。套用前若幅度較大須確認。禁止連帶修改未被要求的元素。
