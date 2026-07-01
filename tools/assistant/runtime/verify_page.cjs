/* verify_page.cjs — 靜態視覺驗證執行器（由 kiosk_build_verify handler 呼叫）。
 *
 * 用 absolute require 載入既有 playwright（省，免重裝；CJS require 對全域/外部安裝有效）。
 * 載入本地 file:// 頁面 → 截圖 → 對 assertions 逐項機檢 → 印 JSON 結果。
 * 只做「渲染+檢視」本地檔，不操作任何活站。
 *
 * argv: node verify_page.cjs <playwrightPath> <targetHtml> <assertionsJson> <outDir> [W] [H] [settleMs]
 */
const fs = require('fs');
const path = require('path');

async function main() {
  const [pwPath, target, assertionsPath, outDir] = process.argv.slice(2);
  const W = parseInt(process.argv[6] || '1080', 10);
  const H = parseInt(process.argv[7] || '1920', 10);
  const settleMs = parseInt(process.argv[8] || '800', 10);

  const { chromium } = require(pwPath);
  const assertions = JSON.parse(fs.readFileSync(assertionsPath, 'utf-8'));
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H } });

  const consoleErrors = [];
  page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text()); });
  page.on('pageerror', (e) => consoleErrors.push(String(e)));

  const fileUrl = 'file://' + encodeURI(path.resolve(target));
  // 用 domcontentloaded（非 networkidle）：避免頁面載 Google Fonts/CDN 卡 timeout
  await page.goto(fileUrl, { waitUntil: 'domcontentloaded', timeout: 15000 });
  await page.waitForTimeout(settleMs);

  const shot = path.join(outDir, 'shot.png');
  await page.screenshot({ path: shot, fullPage: false });

  const checked = await page.evaluate((asserts) => {
    const out = [];
    const vis = (el) => {
      const r = el.getBoundingClientRect();
      const s = getComputedStyle(el);
      return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
    };
    for (const a of asserts) {
      let pass = true, detail = '';
      try {
        if (a.rule === 'no_broken_img') {
          const bad = [...document.images]
            .filter((im) => im.getAttribute('src') && (!im.complete || im.naturalWidth === 0))
            .map((im) => im.getAttribute('src'));
          pass = bad.length === 0;
          detail = pass ? `${document.images.length} 張圖皆正常` : `斷圖 ${bad.length}：` + bad.slice(0, 5).join(', ');
        } else if (a.rule === 'no_overflow') {
          const el = a.selector ? document.querySelector(a.selector) : document.documentElement;
          if (!el) { pass = true; detail = `選擇器無此元素(略過)：${a.selector}`; }
          else {
            const over = el.scrollWidth - el.clientWidth;
            pass = over <= 4;
            detail = pass ? '無水平溢出' : `水平溢出 ${over}px @ ${a.selector || 'html'}`;
          }
        } else if (a.rule === 'text_len') {
          const els = [...document.querySelectorAll(a.selector)];
          const bad = els.filter((e) => (e.textContent || '').trim().length > a.max)
            .map((e) => (e.textContent || '').trim().length);
          pass = bad.length === 0;
          detail = `${els.length} 個 ${a.selector}，上限 ${a.max} 字` + (pass ? '，皆符合' : `，超限 ${bad.length} 個(最長 ${Math.max(...bad)})`);
        } else if (a.rule === 'exists') {
          const el = document.querySelector(a.selector);
          pass = !!el; detail = pass ? `找到 ${a.selector}` : `找不到 ${a.selector}`;
        } else if (a.rule === 'vcenter_within') {
          const el = document.querySelector(a.selector), c = document.querySelector(a.container);
          if (!el || !c) { pass = false; detail = `元素或容器不存在`; }
          else {
            const er = el.getBoundingClientRect(), cr = c.getBoundingClientRect();
            const off = Math.abs((er.top + er.height / 2) - (cr.top + cr.height / 2));
            pass = off <= (a.tol || 12); detail = `垂直中心偏移 ${Math.round(off)}px (容許 ${a.tol || 12})`;
          }
        } else if (a.rule === 'page_renders') {
          const n = [...document.body.querySelectorAll('*')].filter(vis).length;
          pass = n >= (a.min || 1); detail = `可見元素 ${n} 個`;
        } else {
          pass = true; detail = `未知規則，略過：${a.rule}`;
        }
      } catch (e) { pass = false; detail = '檢查例外：' + String(e); }
      out.push({ rule: a.rule, selector: a.selector || null, pass, detail });
    }
    return out;
  }, assertions);

  await browser.close();

  // console error 視為一項斷言
  checked.unshift({
    rule: 'no_console_error', selector: null,
    pass: consoleErrors.length === 0,
    detail: consoleErrors.length === 0 ? '無 console error' : `${consoleErrors.length} 個：` + consoleErrors.slice(0, 3).join(' | '),
  });

  console.log(JSON.stringify({ ok: true, screenshot: shot, assertions: checked }, null, 0));
}

main().catch((e) => {
  console.log(JSON.stringify({ ok: false, error: String(e), assertions: [] }));
  process.exit(0); // 完成即 exit 0；pass/fail 由 handler 讀 JSON 判定
});
