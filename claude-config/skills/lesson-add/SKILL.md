---
name: lesson-add
description: 將觀察或教訓加入對應層級的 Lessons-learned.md。用法：/lesson-add [層級] [內容]
---

# Lesson Add

用法：`/lesson-add [層級] [觀察內容]`

層級選項：
- `全域` — 適用所有 Claude 工具
- `工具` — 特定工具（Claude Code / Cowork / Chat）
- `專案` — 特定專案（WTF / Planner2Line / 其他）

執行步驟：

1. 讀取 `Lessons-learned.md`（若不存在則建立）。

2. 在對應層級段落加入新條目，格式：
   ```
   - [YYYY-MM-DD] [觀察內容] → [建議做法]
   ```

3. 若觀察內容適合做成 Skill，標註：`→ 建議建立 /[skill名稱]`

4. Commit：
   ```
   git add Lessons-learned.md
   git commit -m "lesson-add: [層級] [一句話摘要]"
   git push
   ```

5. 回報：已加入哪個層級，完整條目內容。
