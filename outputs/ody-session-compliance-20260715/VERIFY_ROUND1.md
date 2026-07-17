# 第一輪核驗紀錄：agy 對 BRIEF 事實核查＋裁決

> agy 原始輸出：`/tmp/agy_factcheck.log`（agy --print，沙箱模式）
> 裁決：Claude 提證、逐條可重跑 [Claude@Mac] 2026-07-15

## agy 判定總覽

| 條目 | agy 判定 | 裁決後 |
|---|---|---|
| 1-1 Studio 開在 mirror＋答案與 SSOT 相反 | CONFIRMED | 成立 |
| 1-2 GLOBAL.md 42-51 行版控鐵律內容 | CONFIRMED | 成立 |
| 1-3 「使用者第三次質疑後才完整 Read」 | **REFUTED（判捏造）** | **推翻 agy——agy 查錯 session 檔** |
| 2a hook 註冊與 CAP=150 注入設計 | CONFIRMED | 成立 |
| 2b stdout 30,968 bytes／2KB 預覽／鐵律在預覽外 | CONFIRMED（offset 3611 vs 3613 微差） | 成立；微差原因見下 |
| 2c banner 矛盾＋窄 grep＋跳過開場 Read | CONFIRMED | 成立 |
| 2d 2026-07-05/07-09 設計沿革 | CONFIRMED | 成立 |
| 2e 零機器強制＋PreToolUse 閘早已列為下一步 | CONFIRMED | 成立 |

## 對 [1-3] REFUTED 的裁決：agy 誤判，證據如下

本專案 transcript 目錄有兩個 session JSONL：
- `56490f3e-…jsonl`（5.2MB，最後修改 07-15 12:19）＝**較舊 session**
- `c3967ce4-…jsonl`（810KB，仍在寫入）＝**本案 session**

本案 session JSONL 內含 Read 紀錄（重跑命令見下）：
```
2026-07-15T13:26:28.823Z Read /Users/coma/git_mirror/WTF_Under_Construction/wtf-config/GLOBAL.md
2026-07-15T13:26:29.473Z Read /Users/coma/git_mirror/WTF_Under_Construction/wtf-config/AGENTS.md
```
13:26Z＝21:26 台北時間，晚於舊 session 檔最後修改（12:19），故 agy 檢索的只可能是舊 session——在錯誤的檔案裡找不到紀錄，不等於紀錄不存在。BRIEF [1-3] 原敘述「直到使用者第三次質疑才執行完整 Read」成立：既記錄「先前未讀」的違規，也記錄「後來讀了」的事實。

重跑驗證：
```bash
python3 - <<'EOF'
import json
F="/Users/coma/.claude/projects/-Users-coma-Library-CloudStorage-GoogleDrive-coldjokenewbie-gmail-com------tachart-ihuy-Claude-cowork-projects-claude-CDIC-O4/c3967ce4-835f-41e7-a915-0c4afae5168f.jsonl"
for line in open(F):
    try: d=json.loads(line)
    except: continue
    for c in (d.get('message',{}).get('content') or []):
        if isinstance(c,dict) and c.get('type')=='tool_use' and c.get('name')=='Read':
            fp=c.get('input',{}).get('file_path','')
            if 'GLOBAL.md' in fp: print(d.get('timestamp'), fp)
EOF
```

## 2b offset 微差（3611 vs 3613）解釋

該行原文為 `**Claude_cowork 專案版控鐵律…`。BRIEF 的 grep pattern 不含前導 `**`（match 起點 3613）；agy 量到 3611＝行首 `**` 起點。兩數相差恰 2 bytes（`**`），同一位置，無矛盾。

## 本輪結論

- BRIEF 無捏造。agy 唯一 REFUTED 經物證推翻，其餘 7 條全 CONFIRMED。
- 對抗流程本身產生教訓：**驗證者引用 transcript 證據時必須先報告「查的是哪個 session 檔＋該檔時間範圍」**，否則「查無紀錄」可能只是查錯檔——此教訓同樣適用於未來任何「已讀判定」機制設計（多 session 併存時的檔案選擇）。
