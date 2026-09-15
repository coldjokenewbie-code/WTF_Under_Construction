const { chromium } = require('/Users/coma/.npm/_npx/705bc6b22212b352/node_modules/playwright');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL, fileURLToPath } = require('node:url');
const out = path.join(__dirname, process.argv[2] || 'ui-review');
const deck = path.resolve(__dirname, '../outputs/簡報_2026-09-14_制度優化/index.html');
const failures = [], checks = [], errors = [], network = [];
fs.mkdirSync(out, { recursive: true });
function check(condition, label, detail = '') {
  checks.push({ label, pass: !!condition });
  if (!condition) failures.push({ label, detail });
}
async function pageIs(page, number, context) {
  check((await page.locator('#page-count').textContent()).trim().endsWith(`${number} / 6`), `${context}: 頁碼 ${number}`);
  check(await page.locator('.slide:visible').count() === 1, `${context}: 只顯示一頁`);
  check(await page.locator(`#slide-${number}`).isVisible(), `${context}: 預期頁面可見`);
  check(await page.locator('.tab-btn[aria-current="page"]').count() === 1 && await page.locator(`#tab-${number}`).getAttribute('aria-current') === 'page', `${context}: 導覽當頁正確`);
  check(await page.locator('#slide-progress').getAttribute('value') === String(number), `${context}: 進度正確`);
}
async function fits(page, label) {
  const geometry = await page.evaluate(() => {
    const width = document.documentElement.clientWidth;
    const overflows = Array.from(document.querySelectorAll('body *')).filter(el => {
      const r = el.getBoundingClientRect();
      return r.width && r.height && (r.right > width + 1 || r.left < -1);
    }).map(el => `${el.tagName}.${el.className}`).slice(0, 12);
    const slide = document.querySelector('.slide:not([hidden])').getBoundingClientRect();
    const footer = document.querySelector('footer').getBoundingClientRect();
    return { overflows, width, scrollWidth: document.documentElement.scrollWidth,
      footerAfterContent: footer.top >= slide.bottom - 1 };
  });
  check(geometry.scrollWidth <= geometry.width + 1 && !geometry.overflows.length, `${label}: 無水平溢出`, geometry);
  check(geometry.footerAfterContent, `${label}: 頁尾不遮內文`, geometry);
}
async function chooseAll(page, selector, panel, expected, label) {
  for (let i = 0; i < expected.length; i++) {
    await page.locator(selector).nth(i).click();
    const text = await page.locator(panel).textContent();
    check(expected[i].every(part => text.includes(part)), `${label} 情境 ${i + 1}: 內容`, text);
    check(await page.locator(`${selector}[aria-pressed="true"]`).count() === 1, `${label} 情境 ${i + 1}: 唯一選項`);
    check(await page.locator(selector).nth(i).getAttribute('aria-pressed') === 'true', `${label} 情境 ${i + 1}: 選項正確`);
    check(!!(await page.locator(panel).getAttribute('aria-live')), `${label}: 動態區域`);
    if (panel === '#slimming-detail') {
      const expectedRatio = [[8343,5414],[13093,10271],[13035,10383],[13539,10896]][i];
      const bars = await page.locator('.chart-track').evaluateAll(tracks => tracks.map(track => ({
        track: track.getBoundingClientRect().width,
        fill: track.firstElementChild.getBoundingClientRect().width
      })));
      check(bars.length === 2 && Math.abs(bars[0].track - bars[1].track) < 1, `${label} 情境 ${i + 1}: 比較尺度一致`, bars);
      check(Math.abs(bars[0].fill / bars[0].track - 1) < 0.003 && Math.abs(bars[1].fill / bars[1].track - expectedRatio[1] / expectedRatio[0]) < 0.003, `${label} 情境 ${i + 1}: 圖形比例正確`, bars);
    }
    await fits(page, `${label} 情境 ${i + 1}`);
  }
}
async function interactions(page, width) {
  await page.locator('#tab-2').click();
  await chooseAll(page, '.task-btn', '#task-detail', [['Haiku','Sonnet'],['Sonnet','主'],['Opus','Fable'],['Fable','Codex','agy']], `${width} 派工`);
  await page.locator('.task-btn').first().focus();
  await page.keyboard.press('ArrowRight');
  await pageIs(page, 2, '按鈕焦點不翻頁');
  await page.locator('#slide-2 summary').first().focus();
  await page.keyboard.press('ArrowRight');
  await pageIs(page, 2, 'details焦點不翻頁');
  await page.locator('#tab-3').click();
  await chooseAll(page, '.manual-btn', '#manual-detail', [['Codex','不額外'],['專案索引','全域索引','回報']], `${width} 手冊`);
  await page.locator('#tab-4').click();
  await chooseAll(page, '.slim-btn', '#slimming-detail', [['8,343','5,414','35.1%'],['13,093','10,271','21.6%'],['13,035','10,383','20.3%'],['13,539','10,896','19.5%']], `${width} 量測`);
  await page.locator('#tab-5').click();
  await chooseAll(page, '.drift-btn', '#drift-detail', [['通過'],['同步'],['缺']], `${width} 副本`);
}
async function navigation(page) {
  await page.locator('#tab-1').click();
  check(await page.locator('#prev').isDisabled(), '第一頁上一頁禁用');
  await page.keyboard.press('ArrowLeft');
  await pageIs(page, 1, '首邊界');
  for (let i = 2; i <= 6; i++) await page.keyboard.press('ArrowRight');
  await pageIs(page, 6, '快速五次右鍵');
  check(await page.locator('#next').isDisabled(), '最後頁下一頁禁用');
  await page.keyboard.press('ArrowRight');
  await pageIs(page, 6, '末邊界');
  await page.locator('#prev').click();
  await pageIs(page, 5, '上一頁按鈕');
  await page.locator('#next').click();
  await pageIs(page, 6, '下一頁按鈕');
  check(await page.evaluate(() => !document.activeElement.closest('[hidden]')), '焦點未留在隱藏內容');
  await page.locator('#slide-6 summary').click();
  await page.locator('#slide-6 a').first().focus();
  await page.keyboard.press('ArrowLeft');
  await pageIs(page, 6, '證據連結焦點不翻頁');
  await page.locator('#slide-6 summary').click();
}
async function screenshots(page, width) {
  for (let n = 1; n <= 6; n++) {
    await page.locator(`#tab-${n}`).click();
    await pageIs(page, n, `${width} 頁面 ${n}`);
    await fits(page, `${width} 頁面 ${n}`);
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.screenshot({ path: path.join(out, `${width}-slide-${n}.png`), fullPage: true });
    await page.locator(`#slide-${n} details`).evaluateAll(els => els.forEach(el => el.open = true));
    await fits(page, `${width} 頁面 ${n} 展開`);
    if (n === 4) await page.screenshot({ path: path.join(out, `${width}-slide-4-expanded.png`), fullPage: true });
    await page.locator(`#slide-${n} details`).evaluateAll(els => els.forEach(el => el.open = false));
  }
}
(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    for (const [width, height] of [[375,812],[768,1024],[1280,800]]) {
      const page = await browser.newPage({ viewport: { width, height }, reducedMotion: 'reduce', locale: 'zh-TW' });
      page.on('pageerror', e => errors.push(e.message));
      page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
      page.on('request', req => { if (/^https?:/.test(req.url())) network.push(req.url()); });
      await page.goto(pathToFileURL(deck).href);
      await interactions(page, width);
      await navigation(page);
      await screenshots(page, width);
      for (const href of await page.locator('#slide-6 a').evaluateAll(els => els.map(el => el.href))) {
        check(href.startsWith('file:') && fs.existsSync(fileURLToPath(href)), '本地證據連結存在', href);
      }
      await page.close();
    }
  } finally { await browser.close(); }
  check(!errors.length, '無瀏覽器錯誤', errors);
  check(!network.length, '無外網請求', network);
  const report = { checks: checks.length, passed: checks.filter(c=>c.pass).length, failures, errors, network };
  fs.writeFileSync(path.join(out, 'result.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
  process.exitCode = failures.length ? 1 : 0;
})().catch(e => { console.error(e); process.exitCode = 1; });
