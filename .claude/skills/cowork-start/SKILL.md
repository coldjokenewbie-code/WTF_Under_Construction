---
name: cowork-start
description: 輸出 Claude Cowork 開場設定載入指令。每次開啟新 Cowork session 時使用。
---

# Cowork Start

Cowork 的設定存在沙盒中，每次 session 結束後清除。

每次開啟新 Cowork session，將以下文字貼到對話開頭：

---

請先讀取以下設定後再開始工作：
https://raw.githubusercontent.com/coldjokenewbie-code/WTF_Under_Construction/main/claude-config/CLAUDE.md
https://raw.githubusercontent.com/coldjokenewbie-code/WTF_Under_Construction/main/claude-config/cowork.md

本次任務：[在這裡填入任務描述]

---

提醒：
- 展演腳本、文件類任務建議切換 Haiku 模型節省額度
- 設定載入後確認 Claude 有回應「已讀取設定」再開始工作
