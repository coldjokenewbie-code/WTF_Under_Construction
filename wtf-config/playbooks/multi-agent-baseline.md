# Multi-Agent 協作底線（ai-team／cross-IDE agent）
> 適用：啟用 `ai-team` skill 或跨工具（Codex／Antigravity）派工時開啟；平時不載入
> 來源：原 GLOBAL.md 抽出（2026-07-03）

- **沒 CLI 介面的外部 agent 本質是「半自動」**：tail signal 只是顯示，agent 不會自動消費；MONITOR_INSTRUCTION 待辦清單比 tail signal 更可靠。派發時雙路徑同時走（log 寫 REQUEST + MONITOR_INSTRUCTION 列待辦）。不要對使用者承諾「全自動」。
- **派發 REQUEST 後 60 秒沒動 = 假設 agent 重啟過 monitor**：用 `_RESEND` 後綴重發一次，不要等使用者通知。`tail -n 0 -f` 只看啟動後新增的行，重啟前的 signal 會漏掉。
- **agent 退場立即動態切人**：若某 agent 持續無回應、CLI 不存在、或使用者要求換人，立刻把任務重新打包派給其他 agent 或降為單人制（自主執行）。不要硬等死掉的 agent 拖延任務。
- **Content Pack 隔離模式**（業務內容 + 純技術實作的混合任務）：Tech Lead 主筆撰寫 content pack（JSON/Markdown，含完整文案、資料對應、視覺需求），agent 只做技術整合（資料填入、UI 渲染、CSS 套用）。文案掌控不外包，避免 agent 自行創作偏離需求。
- **跨機雙向 monitor 只在密集協作才啟動**：Drive 即時信號（per-machine `signals_*`）＋雙方常駐 monitor，**僅用於 `ai-team` ＋ 使用者明示「跨機討論」的密集即時協作**。一般情況：一端處理完更新 `INDEX`／`TaskLog`，對方**新對話開場自然讀到**（非同步交棒），**不需常駐 monitor**。常駐 monitor 對 Drive 檔另有鎖檔（Windows）／漏訊（Mac）風險（見 lessons）。
