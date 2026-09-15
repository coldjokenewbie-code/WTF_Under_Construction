# 工作位置與鏡像版控
> 在決定讀寫位置、啟動服務或執行 git 前讀；來源：GLOBAL.md 原條文，2026-09-14 搬移。

## Claude_cowork 專案版控鐵律

**Claude_cowork 專案版控鐵律**（只要出現「git」「推」「commit」「push」等字眼，或要決定「在哪個資料夾讀寫檔案、啟動服務」，一律先查此規則）：
- **所有專案一律「Drive 工作＋git_mirror 鏡像版控」，不存在「純程式 repo」分類**；唯一例外＝WTF_Under_Construction（控管架構 repo＝所有專案的原則與系統架構，本體直接在 `git_mirror/`）。舊 `Git_work`／`git_work_bk` 資料夾已禁用，registry 未登記的路徑不得當工作位置（PO 2026-07-20 裁定）。
- Drive 內任何專案，一律不得原地 git（`init`/`add`/`commit`/`push` 皆禁）——git 與 Drive 同步會互相衝突、鎖檔（已有先例）。
- 查本機是否存在 `git_mirror/<專案名>/`（Mac＝`/Users/coma/git_mirror/`，Windows＝`E:\git_mirror\`；不隨 Drive 同步，各機獨立）：
  - 存在 → **Drive 為唯一真相源，工作在 Drive 做**；`git_mirror/` 只是版控出口。
  - 不存在 → 查 GitHub remote（見 `projects-registry.md`）：有就 clone 到 `git_mirror/<專案名>/`；沒有就在該處建新 repo。都不碰 Drive 端。
- **使用者說「推上 git」＝一整套動作的簡稱，不是字面指令**：
  - 推送前（Drive→mirror）：依副檔名白名單（html/css/js/json/md/ts/tsx/jsx/mjs/py/txt/yaml/yml/sh）複製 Drive→mirror（單向覆蓋，含 `_context/*.md`，不是只有程式碼），再從 mirror `commit`＋`push`。大型二進位（docx/pptx/pdf/圖片/影片）不複製，留在 Drive。
  - 開工前（mirror→Drive，反向對稱）：先在 mirror `git pull`（拉其他機器已推的新 commit），再依同一白名單複製 mirror→Drive，才開始在 Drive 讀改檔案——避免改在別人已推過的舊版本上。
- **複製後必核**：對照 Drive 與 mirror 的 `_context/` 檔案清單一致；缺檔＝漏複製，不是「這次沒改」。
- **後果提醒**：鏡像不全＝工作紀錄只存單機、未進版控＝遺失風險。
