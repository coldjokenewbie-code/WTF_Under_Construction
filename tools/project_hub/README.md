# 共用指揮中心

共用程式安裝於WTF的 `tools/project_hub/`，此處是唯一可編輯實作；各專案保留薄入口與 `workingfiles/總控台/` 原資料。

## 候選執行

`python3 project_hub/server.py --settings /absolute/fixture-settings.json --port 8781 --delivery-mode disabled`

設定包含 `projects:[{project_id,name,root}]`、`registry_path`、`machine`、`runtime_dir`。未啟用專案不讀資料；只有一個主工作root的純code專案亦可登記，有Drive+mirror時只選Drive。

候選禁送模式在answer/recover/retry/resend全部生效。共用啟動入口與水廠compat均透過本機設定的quota_delegate_command，委託水廠原monitor／原watcher；原鎖與去重資料維持不變。disabled模式跳過委託，直接測試server也不啟額度服務。不要在測試執行正式模式的start_hub.py。

## 工作線回報

`python3 /absolute/WTF/tools/project_hub/project_hub/report.py --project-root /absolute/project set 工作項目 --doing 處理中`

保留set/ask/review/page/todo/done/inbox所有原選項；工作線todo的done轉為submitted，PO在UI驗收才設done。CLI完整核對當前cmux caller身分才自動綁定，否則需在UI點連結。

## 通知狀態

queued＝cmux接受排隊；delivered＝工具回報投遞；read＝有精確收件者與receipt對應的read_at。uncertain須人工查核，不盲重送。安全失敗每30秒重試、最多1小時；更換綁定不改投既有回覆。只有awaiting_binding可明確按「投遞到目前工作線」新增信件，原target與UID保留。

## 啟停與安裝

安裝後可直接執行WTF `tools/project_hub/start_hub.sh`，共用入口與水廠入口使用同一設定／同一8780。共用 `project_hub/cli.py start|stop|restart|status --settings ...` 只操作自己保存PID且程序身分一致的服務。沒有全域pkill，不接管既有8780；既有服務port／mode不同時明確拒絕。

`installer.py plan --target-root /absolute/WTF --water-root /absolute/water` 只在staging產manifest；apply才寫allowlist，備份留staging。設定初始只啟用水廠與CDIC。安裝不包含live服務切換、通知、git或全域設定同步。rollback先核對所有SHA，已被其他人修改則拒絕覆蓋。
