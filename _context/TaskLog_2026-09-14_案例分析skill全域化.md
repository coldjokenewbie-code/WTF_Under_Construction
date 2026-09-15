# TaskLog 2026-09-14 — 案例分析 skill 全域化（跨專案彙整已完成，skill 未動工）

> session：`claude_wtf`（id `908f5241-8947-4ee4-a941-437d68b14273`）。狀態：**暫停，等三藏指示再動工**。

## 三藏已拍板（2026-09-14）
1. 以南科 `reference-study` skill（`南科再生水廠/._agents/skills/reference-study/SKILL.md`，67 行）為底升到全域 `wtf-config/skills/`，再補其他專案教訓；不重寫。
2. 決策檔（評分表、定案、被砍項理由、不採納項理由）列為必產物。
3. 骨架先做一個，不分大小樣本兩模式。

## 跨專案彙整結論（兩個 opus 子代理掃 Drive 16 份＋git_mirror 9 份報告、37 條回饋）
- 形式收斂：單檔可離線 HTML 卡片 gallery，資料抽 JSON 由產生器重生；結論在最前；比較表以 PO 判準為列；「建議（供裁決非定案）」＋「待 PO 裁決」＋驗證聲明；勾選複製清單；連結新分頁。
- 退件原因依頻率：決策層次混淆＞載體不符＞首頁截圖非作品圖＞動態只給單張＞前提未問就推定＞湊數弱案／主題無關／內部註記塞給業主。「補強」多半指換研究層次，不是加案例數。
- 派工固定：每軸一個子代理平行，主 agent 主編複核剔弱案。
- 給 PO 拍板的 HTML 研究報告與給業主的正式報告書（docx）是兩套格式，不可混。
- 既有可引用規範：`AGENTS.md` 連結必實開、`playbooks/data-citation.md`、`anchors/README.md`（無截圖無分數、打回寫正負錨一對）、`playbooks/extraction-process.md`、`HsinchuScienceEducationCenter/rules/citation-rules.md`＋`report-tone-rules.md`。

## 首次實跑（ChildrenFuture 兒童互動案例，12 分鐘限時，7 分鐘完成）新增教訓
- 子代理會重複提名同一標竿案（Connected Worlds 三軸皆提）→ skill 加「跨軸重複由主編歸屬一次」。
- 子代理來源頁只憑搜尋摘要 → skill 加「主 agent 至少 HEAD 驗來源頁，403 標站方封鎖」。
- 第 0 步四問在 PO 不在線時：假設明標在報告頂部橫幅＋決策檔，不阻塞。
- 產生器雛形：`ChildrenFuture/tools/gen_case_report.py`（cases.json → index.html，含 shots/ 抓圖與 contact sheet QC），可直接搬進全域 skill 當附件。

## 待辦
- [ ] 讀南科 SKILL.md 全文＋上列教訓，寫 `wtf-config/skills/reference-study/SKILL.md`（全域版）＋附 `gen_case_report.py`
- [ ] 補「決策檔範本」節；補「第 0 步 PO 不在線」處理
- [ ] `sync_config.py sync` 部署三工具，`check` 全綠
- [ ] 建 `wtf-config/anchors/報告書.md` 錨點檔（README 已預留但未建）
- [ ] 南科專案層同名 skill 保留（專案版優先），或改為指向全域＋專案差異
