# 獨立驗收條件（不依賴討論脈絡）

產物由 Codex 修改；Fable 5.1 以新 CLI 對話獨立審查。找出阻擋通過的實際缺陷，不預設 PASS。

1. 模型表以 2026-09-14 PO 指定交接 V4/V5 為來源：Opus5/claude-opus-5/opus；Fable5.1/claude-fable-5-1/fable；Sonnet5/claude-sonnet-5/sonnet；Haiku4.5/claude-haiku-4-5-20251001/haiku。Agent fable 和 CLI fable 的情境不同，不能假定必然繼承脈絡或共用額度。一般實作不無條件用高階，任務失敗4輪上限、高階終局一次；不可得備援只一次，不重設品質要求。ai-team 禁止自驗自過、通過後交 PO、禁止 commit。
2. 原生 skill 清單優先；缺列/截斷/未提供才查備援。索引只使用SSOT name/description/path；不新增triggers平行真相、不強讀17份全文。專案同名優先，專案索引path相對根；全域索引path指向各工具本機部署。生成目錄不收工具內建skill。沒有 Skill 工具不等於不能使用技能；索引不保證模型會觸發。
3. 同步不刪非SSOT目錄；普通本地skill、.system和工具自有symlink須保留。WTF同名目的symlink須拆成實體而非寫穿外部。有效metadata缺漏/重複name應報錯，name與資料夾不同只警告。只比目錄名不得算同步通過；必比附檔及本文內容。索引竄改、部署檔缺失/竄改、bundle缺失/錯誤必exit1；缺Codex/Gemini安裝應skip；sync兩次內容一致。
4. GLOBAL原規則不能在搬移中消失：WTF唯一git_mirror本體例外、Drive禁git、Git_work禁用、先確認讀寫位置、跨向白名單含_context、異常.git停用、W_最新內容/增量/備份、數據期間口徑/不補參數/同期/排除不可驗證、預覽-g/影音不播放/批次/無GUI、FSA目標位置與handle/文件夾禁作保底/覆蓋原檔、Excel字體、HTML適用對象。新playbook可由常駐指標抵達，舊回指要更新。
5. GLOBAL來源字元至少縮35%；常駐三檔數字需把AGENTS和各入口增量計入。不得把字元量當token或帳單，不保證小模型遵從率。maintenance只保留一份詳細規則並要求遷移證據。
6. 範圍只限模型派工、skill同步/索引、GLOBAL搬移及記錄。這輪無UI、無agy行為測試；V1–V7不重驗。Antigravity只能說檔案部署已驗，Windows未實機部署。權限警告只存證，.claude/settings.local.json不修改。machines.md是既存變更且期間時間戳再更新，不屬本任務作者修改；不覆蓋。
7. 此輪是程式碼/制度靜態審查，附件有真實機檢輸出，但你不可假裝自己執行過。實際環境部署的最終read-back另在程式碼通過後確認。

回覆首行 PASS 或 FAIL。FAIL 每項附檔名、具体觸發、影響、最小修正；建議與阻擋項分開。任何無法驗證處標未驗證。繁體中文，1200字內。只輸出文字，不讀寫檔、不執行工具或初始化，不引用作者推理。
