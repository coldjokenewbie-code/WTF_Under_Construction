# backlog：session-gate-fix

> 規格見 `MISSION.md`。逐項一棒可完成＋可驗證；勾掉即算增量完成。

- [ ] 重現故障：寫 pytest 情境 fixture（generation 綁舊 SHA、receipts 必缺、`recovery.json` 不存在），確認現況 `cmd_postread` 拋 GateError（紅燈基準）
- [ ] 修 `cmd_postread`：`recovery.json` 讀取比照 `recovery_read` L225 補 `path.exists()` 防禦（不存在時視為 `{"used": {}}`），非復原 Read 靜默放行、不誤寫收據
- [ ] 補 pytest 三案：缺 `recovery.json` 的一般 Read 不 crash／偽復原 Read 不產生收據（防誤放行）／合法 full-read 復原仍正確寫收據（防回歸）→ M1 可簽核
- [ ] settings.json 讀取 helper（純函式）：解析 `~/.claude/settings.json`，從 SessionStart hook 抽出 `WTF_BUNDLE_SHA256=<sha>`，回傳 sha 或 None
- [ ] settings.json 覆寫 helper（純函式）：給定 settings 內容＋當代 SHA，回傳把 `WTF_BUNDLE_SHA256` 換成新 SHA 的結果，其餘設定原封不動；找不到該 env 時行為明確定義（略過並回報）
- [ ] 擴充 `check_bundle_integrity` 為四方機檢：新增 settings.json `WTF_BUNDLE_SHA256` == 當代 SHA 一項，不符回 STALE（helper 純函式＋fixture 測試）
- [ ] 在 `deploy_session_bundle` 部署流程後串接 settings.json 自動同步（比照對 CLAUDE.md 的做法）：先讀既有內容、只改 env 值、保留其餘；fixture 覆蓋「舊 SHA→當代 SHA」
- [ ] 整合測試（tmp home／`WTF_GATE_HOME` override）：模擬含舊 SHA 的 settings.json＋舊 CLAUDE.md，跑 sync 邏輯後四方一致、check 回綠 → M2 可簽核
- [ ] （次要／防護縱深）設計 sync 時清理殘留舊 bundle 目錄，使 `choose_bundle` 單候選免用 env var；預設保守（僅回報不自動刪），設計後列 HANDOFF 待業主裁決
- [ ] lessons-learned 記錄根因鏈（settings.json env 未隨換代同步 → `choose_bundle` 選錯目錄 → generation 綁舊代 → 收據必敗 → postread 無防禦而 crash）與修法
- [ ] 撰寫 HANDOFF：明列「使用者本機需執行 `python sync_config.py sync` 才生效」＋「重跑 canary 驗證後方可考慮 PreToolUse/Stop 接線」為交付後步驟，非本棒 blocker
- [ ] 收尾機檢：全套 pytest 綠、確認未觸碰 `wtf-session-gate.py` 除 `cmd_postread` 外任何行、未接線 PreToolUse/Stop、未改任何 `~/.claude` 真實檔 → M3 可簽核
