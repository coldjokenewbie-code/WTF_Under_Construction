# 本機 AI 額度監控

於專案根目錄執行，僅使用 Python 標準函式庫：

```sh
python3 tools/ai_usage/monitor.py serve --port 8766
```

開啟 `http://127.0.0.1:8766`。服務常駐，每 300 秒採集三家供應商，每 15 秒更新心跳；Ctrl+C 停止。只綁定 `127.0.0.1`，不開放公開網路。相同 runtime 僅允許一個服務，重複啟動會拒絕。

需要背景運作時，可在專案根目錄執行以下命令；啟動後以 status 的心跳與瀏覽器確認運作，PID 檔不是健康檢查。重開機後須重新啟動。

```sh
mkdir -p workingfiles/outputs/_shared/ai-usage-20261019/runtime
nohup python3 tools/ai_usage/monitor.py serve --port 8766 > workingfiles/outputs/_shared/ai-usage-20261019/runtime/server.log 2>&1 &
echo $! > workingfiles/outputs/_shared/ai-usage-20261019/runtime/server.pid
```

停止背景服務前先用 `ps -p "$(cat workingfiles/outputs/_shared/ai-usage-20261019/runtime/server.pid)" -o command=` 確認 PID 仍是本服務，再執行。SIGTERM 與 Ctrl+C 都會停止新採集、回收採集中 CLI 的程序群組，等待刷新結束，寫入 `monitor.running=false` 與 `stopped_at`，保留最後有效心跳。不要以 SIGKILL 作為正常停止方式：

```sh
kill "$(cat workingfiles/outputs/_shared/ai-usage-20261019/runtime/server.pid)"
```

所有 agent 共用 CLI；共同 check 契約可以供派工工具阻擋新任務，但不等於所有既有 Claude／agy／Codex session 已受強制 hook 管制。目前沒有安裝或強制任何全域 hooks。派工前讀取狀態，必要時刷新後檢查，任務結束後再刷新：

```sh
python3 tools/ai_usage/monitor.py status
python3 tools/ai_usage/monitor.py refresh
python3 tools/ai_usage/monitor.py check --provider codex
python3 tools/ai_usage/monitor.py check --provider codex --pool primary
```

`--pool` 須使用快照中的實際池 ID；範例 `primary` 不保證每個帳戶存在。`check` 必須指定供應商（`claude`、`codex`、`agy`）。指定池僅供聚焦；共享額度映射未完整驗證，指定與未指定池皆保守檢查供應商全部池，未知池或缺資料一律阻擋。JSON 的 `scope` 說明選取範圍。結束碼：0 正常、1 警告（已用 ≥80%）、2 保留（≥95%）／耗盡／帳戶禁止使用、3 未知／過期。這些閾值是本機派工政策，並非供應商保證。

採集超過 600 秒、重置時間已到、採集時間在未來超過 60 秒、百分比非法或採集失敗，都不可當成可用額度。讀 API 與 `status/check` 時重新判斷，因此監控停止後仍會過期。採集失敗會取代舊快照，不能靠舊成功值放行。不會把舊 `observed_at` 改成新時間。各供應商以 `attempted_at` 計算 60 秒冷卻，跨程序逐家檔案鎖避免重複刷新；三家並行採集，各筆採集結果原子合併。Python API `refresh_provider(provider, runtime)` 只採指定家，不更動其他家的採集時間或冷卻。額度不代表模型能力；工具不自動付費、不自動切換供應商。

runtime 固定為 `workingfiles/outputs/_shared/ai-usage-20261019/runtime/`；`snapshot.json`、`history.jsonl` 原子替換，歷史保留七日且最多 10080 筆。`monitor.json` 為獨立心跳；舊心跳時間保留供介面判定停止。僅保存正規化欄位，不保存完整 stdout/stderr、帳戶識別資料或 token。

API：

- `GET /api/status`：`{schema_version:1,generated_at,providers:[...],monitor:{interval_seconds:300,ttl_seconds:600,heartbeat_at,started_at,refreshing}}`。
- provider 保留採集欄位，增加 `state`、`exit_code`；bucket 增加 `state`。狀態為 `ok/warning/reserve/exhausted/stale/unknown`；`usage_blocked:true` 表示帳戶限制。
- `GET /api/history`：`{entries:[snapshot,...]}`；歷史狀態依各筆採樣時間判定，非法採樣時間排除，原百分比不改動。當前 `/api/status` 仍依目前時間判定過期。
- `POST /api/refresh`：須加 `X-Usage-Request: 1`；202 `{accepted:true}` 後背景採集，可輪詢 status；429 `{error:"cooldown"}`、409 `{error:"refresh_in_progress"}`。
- Host 須為實際 `127.0.0.1:port`；跨站 Origin/Fetch Metadata 會被拒絕，不允許 CORS。所有回應 `Cache-Control: no-store`。
- 靜態路徑僅 `/`、`/index.html`、`/style.css`、`/app.js`，來源為 `workingfiles/outputs/ai-usage-dashboard/`。

驗證（不呼叫供應商、不生成模型內容）：

```sh
python3 -m unittest tools.ai_usage.test_monitor -v
```
