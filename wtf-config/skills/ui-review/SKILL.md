---
name: ui-review
description: Playwright 無頭截圖驗收。對 HTML/UI 頁面執行自動化視覺驗證，取代手動截圖。在協作中由 Tech Lead（指揮層）執行驗收，執行層修改後以此驗收，執行層亦可用於自行驗證。
---

# UI Review — Playwright 驗收

## 啟動時機

- 完成 UI 修改後需驗收
- Execution Agent 交回 handoff report 後由 Tech Lead 執行驗收
- 使用者下 `/ui-review` 指令
- 執行層 Agent 交付前進行自我品質檢查

---

## 執行流程

### 1. 建立驗收腳本

在專案根目錄建立 `_ui_review.mjs`（暫時檔，驗收後可刪除）：

```js
import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TARGET = process.argv[2]; // 傳入 HTML 檔案路徑或 URL
const OUT_DIR = path.join(__dirname, '_screenshots');

const VIEWPORTS = [
  { name: 'mobile', width: 375, height: 812 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1280, height: 800 },
];

const browser = await chromium.launch();
const results = [];

for (const vp of VIEWPORTS) {
  const page = await browser.newPage();
  await page.setViewportSize({ width: vp.width, height: vp.height });

  if (TARGET.startsWith('http')) {
    await page.goto(TARGET, { waitUntil: 'networkidle' });
  } else {
    await page.goto('file:///' + path.resolve(TARGET).replace(/\\/g, '/'), { waitUntil: 'networkidle' });
  }

  // 等待內容穩定
  await page.waitForTimeout(500);

  // 截圖
  import('fs').then(fs => fs.mkdirSync(OUT_DIR, { recursive: true }));
  const { mkdirSync } = await import('fs');
  mkdirSync(OUT_DIR, { recursive: true });
  const screenshotPath = path.join(OUT_DIR, `${vp.name}.png`);
  await page.screenshot({ path: screenshotPath, fullPage: true });

  // 驗收檢查
  const issues = await page.evaluate(() => {
    const problems = [];
    const elements = document.querySelectorAll('*');

    elements.forEach(el => {
      const rect = el.getBoundingClientRect();
      const style = window.getComputedStyle(el);

      // 元素超出視窗右側
      if (rect.right > window.innerWidth + 5) {
        problems.push(`overflow: ${el.tagName}.${el.className} right=${Math.round(rect.right)}`);
      }

      // 文字截斷（overflow hidden + 有文字內容）
      if (style.overflow === 'hidden' && el.scrollWidth > el.clientWidth && el.textContent?.trim()) {
        problems.push(`text-clip: ${el.tagName}.${el.className}`);
      }
    });

    // nav bar 存在檢查
    const nav = document.querySelector('nav, [class*="nav"], header');
    if (!nav) problems.push('nav-missing: 找不到 nav 或 header 元素');

    return [...new Set(problems)].slice(0, 10); // 最多回報 10 個
  });

  results.push({ viewport: vp.name, screenshot: screenshotPath, issues });
  await page.close();
}

await browser.close();

// 輸出結果
console.log('\n===== UI Review 結果 =====');
for (const r of results) {
  const status = r.issues.length === 0 ? '✅ PASS' : '❌ FAIL';
  console.log(`\n[${r.viewport}] ${status}`);
  console.log(`  截圖：${r.screenshot}`);
  if (r.issues.length > 0) {
    r.issues.forEach(i => console.log(`  ⚠ ${i}`));
  }
}

const totalFail = results.filter(r => r.issues.length > 0).length;
console.log(`\n===========================`);
console.log(`總結：${results.length - totalFail}/${results.length} 通過`);
if (totalFail > 0) process.exit(1);
```

### 2. 確認專案內已安裝 playwright

```bash
npm install --save-dev playwright
```

> ESM 模式下 NODE_PATH 不生效，需本地安裝。全域安裝僅供 CJS require 使用。

### 3. 執行指令

```bash
node _ui_review.mjs <目標檔案或URL>
```

範例：
```bash
node _ui_review.mjs dashboard.html
node _ui_review.mjs http://localhost:3000
```

### 3. 驗收標準

| 項目 | 條件 |
|---|---|
| 元素爆版 | 無元素超出視窗寬度 |
| 文字截斷 | 無文字被 overflow:hidden 截掉 |
| Nav 存在 | 找得到 nav / header |
| 三種寬度 | 375px / 768px / 1280px 全部通過 |

### 4. 結果處理

- **全部 PASS** → 驗收完成，截圖存於 `_screenshots/`，可刪除 `_ui_review.mjs`
- **有 FAIL** → Tech Lead 接手或退回執行層修正，修完重跑

---

## 在協作中的角色

| 步驟 | 執行者 |
|---|---|
| 撰寫 / 執行驗收腳本 | Tech Lead（指揮層） |
| 修改 UI 元件 | Execution Agent（執行層） |
| 最終驗收確認 | Tech Lead 執行 ui-review，PASS 才回寫驗收通過 |
| 交收前自行檢查 | 執行層 Agent（鼓勵自主使用以防退件） |

**原則：驗收標準由 Tech Lead 掌握與把關，執行層被動服從檢驗。**

---

## 注意事項

- 每個需要驗收的專案都要執行一次 `npm install --save-dev playwright`（ESM 不支援全域 NODE_PATH）
- 截圖輸出至 `_screenshots/`，不 commit 進 git（加入 `.gitignore`）
- GIF 格式避免使用（曾卡死 session）
