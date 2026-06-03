# Handover 2026-06-03 — 階段二：wtf-config 移出 Drive

> 接手者請先讀本檔，再讀 `workingfiles/SSOT同步架構討論_2026-06-03.md`「結論段＋MAC-R2 補強」。
> 本檔承接階段一（已 commit＋push `120fb16`）。

## 一、現況（階段一已完成並上 origin/main）

- SSOT 同步架構已定案、階段一 T1–T8 全數完成驗收、已 push `120fb16`。
- 關鍵既成事實：
  - `wtf-config/projects-registry.md`：專案×機器×路徑單一註冊表（取代 extra-scan-dirs.txt）。`sync_config.py` 已改讀它（`registry_dirs()`，絕對路徑）。
  - `sync_config.py`：`classify` 有 ADOPT 自動接管；`deploy_claude_dir()` 逐 skill 容錯覆蓋（非破壞性 rmtree）。
  - root `AGENTS.md`：已 gitignore（`/AGENTS.md`）＋解除追蹤（原 git 記為 symlink 120000，typechange 根除）。
  - hook：兩端 UserPromptSubmit + 5 分冷卻已上線。Windows `~/.claude/wtf-sync.ps1`（本 session 已實測觸發成功）、Mac `~/.claude/wtf-sync.sh`。**目前 hook 仍 pull「Drive 內」WTF repo**——這正是階段二要改的。
  - session-start skill 已去重（check→fallback，不與 hook 重工）。

## 二、階段二目標

把 `wtf-config/` 抽成 **Drive 外的獨立 git repo**，兩端 clone 到 Drive 外，**讓 hook 只 pull Drive 外那份**、不再碰 Drive 內的 `.git` → 根除 Google Drive 同步 `.git` 造成的 `*.lock` 衝突（現靠 wtf-sync 清 lock 緩解，治標）。

## 三、為什麼（問題根因，勿忘）

- WTF_Under_Construction 整個 repo（含 `.git`）躺在 Drive 內 → git 操作與 Drive 同步搶同一份 `.git` → `refs/` 留 `.lock`、pull 失敗。
- 階段一只把 wtf-config「邏輯上」當 SSOT，**實體 `.git` 仍在 Drive**，故衝突未根除。
- **MAC-R2 盲點 6（關鍵）**：就算抽出 wtf-config，WTF 主 repo 的 `.git` 仍在 Drive。所以階段二的真正解法不只是「搬 wtf-config」，而是**讓 hook 完全不 pull Drive 內 .git**：
  - SSOT（wtf-config）→ Drive 外獨立 repo，hook 只 pull 它。
  - `_context` 知識（TaskLog/Handover/lessons）→ **靠 Drive 自身同步**就夠（append/取最新，無需跨機 git merge；權威 lessons 索引 `LESSONS.md` 隨 wtf-config 走 git 受保護）。
  - WTF 主 repo 的 git → 僅作歷史備份，**移出 hook 流程**。

## 四、階段二設計（討論已定案 + 補強）

1. **新 repo**：建立 GitHub repo（建議名 `wtf-config`），內容＝現 `wtf-config/` 全部。
2. **clone 位置（Drive 外）**：
   - Mac：`~/Git_work/wtf-config`（與現有 Git_work 4 repo 一致，registry 已用此根）。
   - Windows：待定（建議 `C:\Users\2025.DESKTOP-7SF21LR\Git_work\wtf-config`，比照 Mac；注意別放回已廢棄的 `Documents\Git_foler_anti\`）。
3. **sync_config.py 根參數化**：
   - `SSOT_ROOT = SCRIPT_DIR`（腳本隨 wtf-config 搬到新 repo，天然成立）。
   - 專案副本目標：續讀 `projects-registry.md` 絕對路徑（已相容，無需改）。
   - **要處理**：`register` 的 `workspace_root` 不能再靠 `SCRIPT_DIR.parents[2]`（搬出後失準）。改由 registry 推導（Drive 專案路徑的共同父層）或簡化 register 只記 hostname/OS/時間。
4. **hook 改寫（wtf-sync.ps1 / .sh）**：
   - `WTF` 路徑 → 改指 Drive 外 wtf-config clone。
   - 只 `git pull` wtf-config（清該 repo 的 lock；Drive 外其實已無 lock 問題）。
   - sync 後：若 wtf-config 有變動（如 register 改 machines.md）→ **自動 `git add/commit/push`** wtf-config，否則他機 pull 不到。
   - **移除對 Drive 內 WTF 主 repo 的 pull**。
5. **WTF 主 repo（Drive 內）**：保留作專案內容（`_context`/`outputs`/工作檔）的歷史備份，但不進 hook。`_context` 跨機靠 Drive。

## 五、執行步驟（建議順序）

1. **抽 wtf-config 成新 repo（保留歷史）**：
   - `git subtree split -P wtf-config -b wtf-config-only`（在 WTF repo）→ 得只含 wtf-config 歷史的分支。
   - 在 GitHub 建空 repo `wtf-config` → `git push <new-remote> wtf-config-only:main`。
   - 兩端 clone 到 Drive 外選定路徑。
   - （或求快：新 repo 直接複製檔案 initial commit，放棄歷史。）
2. **改 sync_config.py 根參數化**（見四-3）→ 在新 repo 內改、commit。
3. **改兩端 hook**（見四-4）→ 指新 clone、加 commit+push、移除主 repo pull。
4. **WTF 主 repo 清理**：從 WTF repo 移除 wtf-config（`git rm -r wtf-config`）或改為 submodule（submodule 跨 Drive 較複雜，建議直接移除、不留）。更新 CLAUDE.md/指標檔的 SSOT 路徑指向新 repo。
5. **驗收**：兩端各跑一次 hook → 確認 pull 新 repo、sync 寫副本進 Drive 專案、無 .git lock、register 變動能 commit+push 傳到他機。
6. **更新 INDEX/lessons**：記「wtf-config 已移出 Drive」、修 GLOBAL.md 內 SSOT 路徑描述。

## 六、待你拍板的決策點

- **D1**：Windows clone 路徑（建議 `C:\Users\...\Git_work\wtf-config`）。
- **D2**：保留歷史（subtree split）還是求快新建（放棄歷史）。
- **D3**：WTF 主 repo 內的 wtf-config 直接移除，還是改 submodule。（建議直接移除）
- **D4**：hook 每次 register 改 machines.md 時間戳就 commit+push → 歷史會很多瑣碎 commit。要不要「只在實質變動才 commit」（忽略純時間戳）？
- **D5**：SSOT 路徑改了，散落引用要一起改（`e:\Claude_cowork\CLAUDE.md`、各 `.claude/CLAUDE.md`、AGENTS.md 來源註記、skills 內路徑字串）。需全域 grep `wtf-config/` 與 Drive 絕對路徑後逐一更新。

## 七、風險與注意

- **`.claude/CLAUDE.md` 與 `~/.claude/CLAUDE.md` 的 SSOT 指標**現指向 Drive 內 wtf-config；移出後要同步改指標，否則開場載入失敗。
- **register 的 commit+push 競爭**：兩機同時開 session 各自 register→commit→push 可能撞 non-fast-forward。hook 內 push 失敗要容錯（pull --rebase 再 push 或略過，不阻擋使用者）。
- **跨機分工沿用階段一模式**：建議仍由一端主改 sync_config.py/hook（同檔不雙改），另一端驗。協調檔可沿用 `workingfiles/階段一執行_*` 模式新開一份。
- **Mac 對齊**：Mac hook 下次 `git pull` 會 ff 到 `120fb16`（先清 .git/*.lock）。開階段二前確認 Mac 已對齊。

## 八、關鍵檔／連結

- 架構決策：`workingfiles/SSOT同步架構討論_2026-06-03.md`（結論段、MAC-R2 補強、盲點 6/7）
- 階段一執行/驗收：`workingfiles/階段一執行_2026-06-03.md`（信號區含各項驗收）
- SSOT：`wtf-config/sync_config.py`、`wtf-config/projects-registry.md`、`wtf-config/GLOBAL.md`、`wtf-config/AGENTS.md`
- hook：`~/.claude/wtf-sync.ps1`（Win）、`~/.claude/wtf-sync.sh`（Mac）
- lessons：`_context/lessons-learned.md`、`wtf-config/LESSONS.md`
