---
name: to-codex
description: 把工作直接交辦給 Codex CLI（OpenAI，走 ChatGPT 帳號登入、非 API 計費）執行。首次用會先檢查 codex 是否已安裝、是否已登入，缺一就停下引導使用者處理；備妥後把指令後的文字整段轉發給 codex exec，回報結果。
---

# /to-codex — 把工作交給 Codex CLI 執行

用法：`/to-codex <要交辦的工作內容>`。`/to-codex` 後面的文字整段原文當 prompt 轉發給 codex——不論是直接下指令（「幫我修 XX bug」）還是描述性交代（「先前 OO 功能已經交給 codex 處理，繼續把 YY 也做掉」），都原樣帶入，不要重新詮釋或摘要。

## 執行步驟

### 1. 檢查 codex 是否已安裝

```bash
command -v codex || where codex   # Windows 用 where，其餘用 command -v
```

- 找不到 → **停下**，回報：「codex CLI 尚未安裝，執行 `npm install -g @openai/codex`（或 macOS 用 `brew install codex`）後再試一次 `/to-codex`」。不要往下執行任何步驟。

### 2. 檢查是否已用 ChatGPT 帳號登入（非 API key）

讀取 `~/.codex/auth.json`（Windows 是 `%USERPROFILE%\.codex\auth.json`），只看結構、不印出 token 內容：

```bash
python3 -c "
import json, sys
try:
    with open('$HOME/.codex/auth.json') as f:
        d = json.load(f)
except FileNotFoundError:
    print('MISSING'); sys.exit()
mode = d.get('auth_mode')
has_token = bool(d.get('tokens', {}).get('access_token'))
print('OK' if (mode == 'chatgpt' and has_token) else 'MISSING')
"
```

- 印出 `MISSING`（檔案不存在／不是 chatgpt 模式／沒有 access_token）→ **停下**，回報：「尚未用 ChatGPT 帳號登入 Codex，執行 `codex login`，瀏覽器選『Sign in with ChatGPT』（不要選 API key）完成登入後再試一次 `/to-codex`」。這一步需要使用者本人在瀏覽器操作，不能代為登入。不要往下執行。
- 找不到 `python3` 時改用 `codex exec "ping" -s read-only --skip-git-repo-check < /dev/null` 探測：若輸出包含未登入／未授權字樣，比照上面回報並停下。

### 3. 兩項都通過 → 轉發給 codex 執行

把使用者文字整段寫進變數（避免內含雙引號／反引號／`$` 破壞 shell 語法），再執行：

```bash
TASK=$(cat <<'TOCODEX_EOF'
<使用者在 /to-codex 後打的原文，原樣貼入，不要修改措辭>
TOCODEX_EOF
)
codex exec "$TASK" -s read-only --skip-git-repo-check < /dev/null
```

- `< /dev/null` 必加，否則 codex 會卡住等 stdin 輸入，指令不會回應。
- **預設 `-s read-only`**：codex 只讀檔案、給建議／診斷／方案，不會動使用者的檔案——安全，但看完建議要自己動手套用。
- 使用者交辦文字裡若明講「直接改」「幫我修好」「不用問直接動手」等授權字樣，才改用 `-s workspace-write`（codex 會直接寫入/修改檔案，風險：可能改到非預期的檔案或引入非預期改動，事後要自己 review diff）。不確定時維持 read-only，不要自行判斷升級權限。
- **升級 `-s workspace-write` 前務必確認寫入範圍收在單一專案資料夾**（`pwd` 核對），不要在使用者家目錄或跨專案的上層資料夾開寫入權限——workspace-write 的寫入範圍＝執行當下的工作目錄，開太上層等於讓 codex 對整片資料夾都有寫入權。
  - **cd 由 Claude Code 自己執行，不要求使用者操作終端機**：使用者交辦文字裡若有講到資料夾名稱／路徑（例如「/to-codex 在 ~/Documents/A專案 這個資料夾裡，直接把 XX 修好」），Claude Code 先用 Bash `cd` 進該資料夾，再執行 codex。
  - 使用者要求寫入、但交辦文字裡沒講清楚是哪個資料夾，且當下工作目錄不明確對應到單一專案 → **停下用一句話反問**使用者要在哪個資料夾操作（例如給資料夾名稱或路徑即可），拿到答案後才 cd 執行，不要自己瞎猜、也不要在不確定的目錄下直接放行寫入。

### 4. 回報

- 開頭一句「已交辦 codex：『<任務一句話摘要>』（<read-only／workspace-write>）」，接著附上 codex 的實際輸出。
- codex 回傳非 0 結束碼 → 如實附上錯誤訊息，最多自動重試一次（例如補上遺漏的 `< /dev/null`），仍失敗就停下回報，不要無限重試。
- 不要把使用者的交辦內容重新改寫成別的措辭再回報——原任務摘要要讓使用者認得出自己說了什麼。
