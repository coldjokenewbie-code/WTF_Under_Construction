# Agent 額度檢查與派工

只有經過 `dispatch.py` 的派工會強制檢查；既有手動 CLI 不受接管。
模型能力與模型名稱由指揮者判定，本工具不依模型名稱推測額度池，也不自動換供應商或啟用付費。

在 repo 根目錄執行：

```sh
python3 tools/ai_usage/monitor.py refresh
python3 tools/ai_usage/monitor.py check --provider claude
python3 tools/ai_usage/dispatch.py --provider claude --model MODEL --prompt-file /absolute/path/task.txt
python3 tools/ai_usage/dispatch.py --provider codex --model MODEL --prompt-file /absolute/path/task.txt
python3 tools/ai_usage/dispatch.py --provider agy --model MODEL --prompt-file /absolute/path/task.txt
```

每家 agent 可自行執行 `monitor.py refresh/check`。派工先刷新，再檢查相同快照；刷新遇到冷卻時只能使用仍有效的快照，正在採集或刷新失敗則拒絕派工。
每次檢查都會重新判斷 600 秒有效期與重置時間，過期、未知值及找不到的池不放行。
同一家供應商的派工鎖涵蓋檢查、執行與後續採樣；同時派工回傳 `3`。
開始執行便留下待更新標記；取得晚於該次執行結束的成功額度觀測前，不允許下一次派工。
因此短任務結束後若仍在採集冷卻期，即使原快照未滿 600 秒，也必須等待新觀測。

- 檢查碼 `0`：放行。
- 檢查碼 `1`：預設暫停；經指揮者決定，可加 `--allow-warning` 明確放行。
- 檢查碼 `2/3`：保留、耗盡、未知或過期，拒絕派工；`--allow-warning` 無法豁免。

不選 `--pool` 時，以供應商所有額度池中最嚴格的狀態判斷。
指定 `--pool ID` 僅聚焦已知池，不豁免該供應商其他池；必須是快照中存在的完整 ID。
不得為了規避阻擋擅自換供應商。額度充足不代表模型適合任務。

模型 CLI 以參數陣列啟動，未加跳過權限檢查的旗標；標準輸出與標準錯誤直接交給呼叫者。
單次上限 600 秒，逾時與中斷會清理子程序群組。子程序完成後仍嘗試刷新；若受到冷卻限制，會明示「派工後額度尚未更新」，不能視為已取得最新數字。
收到 `SIGTERM` 時會清理任務及額度採集子程序，不再啟動後續採集；紀錄標示 `cancelled` 並保留待更新標記。
放行後回傳模型 CLI 結束碼；逾時為 `124`、找不到 CLI 為 `127`、無法啟動為 `126`、中斷為 `130`。

派工紀錄與額度資料同在 `workingfiles/outputs/_shared/ai-usage-20261019/runtime/`。
`dispatch.jsonl` 最多保留 1000 筆，只記任務 ID、供應商、模型、時間、狀態、結束碼、刷新狀態與檢查摘要，不記 prompt、模型輸出、帳戶或憑證。
模型 CLI 自身的歷史紀錄由各工具控制；此 wrapper 沒有更動其設定。
