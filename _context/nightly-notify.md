# 全域設定修改建議（nightly → 用戶核准）

> 夜間 routine **不可自行修改全域設定**（GLOBAL.md／wtf-config SSOT），只能在此 append `- [ ]` **建議**。
> 本機 session-start 開場讀此檔，有未勾項即醒目提醒：「nightly 建議改全域設定：X，要採用嗎？」
> 用戶核准 → 自行套用該建議並移除/勾掉該行；不採用 → 直接刪該行。（lessons 加性更新不在此，routine 可自動加）
> 機制：routine 寫建議 → commit main → 本機 hook pull → session-start 浮出。

---

- [ ] 2026-06-30 nightly 建議修改全域設定（待用戶核准）
  - `wtf-config/CLAUDE_CODE.md`：補充 macOS git 卡 Xcode 授權繞法——`/usr/bin/git` 遇 Xcode 授權未簽報錯時，直呼 CLT 路徑 `/Library/Developer/CommandLineTools/usr/bin/git` 可繞過（不需 sudo）；長期解須用戶親跑 `sudo xcodebuild -license accept`。理由：此為 macOS 開發通用踩坑、不限單一專案，值得進全局工具設定以供所有 session 參考。
