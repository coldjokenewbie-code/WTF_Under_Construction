# Inbox 設定（inbox-config）

> WTF 控制面 Phase B：語音速記 inbox 的「來源 vault 路徑」per-machine 設定。
> `/inbox` skill 依本機 hostname（見 machines.md）取對應 `vault_path`，掃其中標題開頭為「工作」的檔分流。
> 來源 vault 在 Google Drive，**各機掛載點不同**，故逐機登記；path 留空＝該機尚未設定。

## 來源 vault（Obsidian on Google Drive）

| machine (hostname) | vault_path | inbox 子夾 |
|---|---|---|
| comaMacBookAir.local | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/我的雲端硬碟/ObsidianCJN | Clippings |
| DESKTOP-7SF21LR | E:\CJN_drive\我的雲端硬碟\ObsidianCJN | Clippings |

## 分流規則

- **判定**：`Clippings/` 中檔名**開頭為「工作」**者＝WTF 任務速記（vault CLAUDE.md 已設 wiki ingest 跳過這些）。
- **落地**：寫進**目標專案自己的 github repo**（git 同步跨機），不寫進中央 INBOX，也不寫 Drive 鏡像資料夾。
  - 由 `projects-registry.md` 取目標專案 本機路徑（`path`）＋`github`。
  - 落地檔：該專案 `_context/INBOX.md`（append；無則建）。
  - 完成後 commit/push 該專案 repo。
  - **無 github / 無 .git 的專案**（registry github 欄標「待確認」）暫無法落地 → 列入「待用戶補 github」清單，先不分流。
  - 判不出歸屬 → 落到 WTF repo `_context/INBOX.md` 的「（未分類）」區待人工分。
- **完成**：原檔移入 vault `Ingested/`。

## 備註

- 雲端 routine 跑在 Anthropic 雲端、讀不到本機 Drive 掛載 → inbox 分流**只能本機手動跑 `/inbox`**（先手動，不排程）。
- 專案清單與各機路徑見 `projects-registry.md`。
