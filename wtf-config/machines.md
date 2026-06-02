# 機器登錄表（machines registry）

> 由 `sync_config.py register` 自動維護，用於區分不同電腦。
> 各電腦首次使用時，在本機（Claude Code／終端機）執行一次：
> `python sync_config.py register`
> 之後可手動填入「別名」欄方便辨識（如：桌機、筆電）。

## 重要限制（未驗證部分已標明）

- `register` 偵測的是**執行當下那台機器**的 hostname／OS／根路徑。
- **在 Claude Cowork 沙盒內執行會抓到沙盒名稱，不是你的實體電腦**，故請勿在 Cowork 內跑 `register`。
- Cowork 內可正常執行 `check`／`sync`（內容式判斷，與機器無關）。

## 登錄清單

| hostname | OS | workspace_root | 別名 | 最後出現 |
|---|---|---|---|---|
| DESKTOP-7SF21LR | Windows 10 | `E:\Claude_cowork` | tachart_ihuy | 2026-06-02 17:24:02 |
