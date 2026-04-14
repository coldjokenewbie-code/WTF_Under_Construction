import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';
import { mkdirSync } from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TARGET = process.argv[2];
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

  await page.waitForTimeout(500);

  mkdirSync(OUT_DIR, { recursive: true });
  const screenshotPath = path.join(OUT_DIR, `${vp.name}.png`);
  await page.screenshot({ path: screenshotPath, fullPage: true });

  const issues = await page.evaluate(() => {
    const problems = [];
    document.querySelectorAll('*').forEach(el => {
      const rect = el.getBoundingClientRect();
      const style = window.getComputedStyle(el);
      if (rect.right > window.innerWidth + 5) {
        problems.push(`overflow: ${el.tagName}.${[...el.classList].join('.')}`);
      }
      if (style.overflow === 'hidden' && el.scrollWidth > el.clientWidth && el.textContent?.trim()) {
        problems.push(`text-clip: ${el.tagName}.${[...el.classList].join('.')}`);
      }
    });
    const nav = document.querySelector('nav, [class*="nav"], header');
    if (!nav) problems.push('nav-missing: 找不到 nav 或 header 元素');
    return [...new Set(problems)].slice(0, 10);
  });

  results.push({ viewport: vp.name, screenshot: screenshotPath, issues });
  await page.close();
}

await browser.close();

console.log('\n===== UI Review 結果 =====');
for (const r of results) {
  const status = r.issues.length === 0 ? '✅ PASS' : '❌ FAIL';
  console.log(`\n[${r.viewport}] ${status}`);
  console.log(`  截圖：${r.screenshot}`);
  r.issues.forEach(i => console.log(`  ⚠ ${i}`));
}
const totalFail = results.filter(r => r.issues.length > 0).length;
console.log(`\n===========================`);
console.log(`總結：${results.length - totalFail}/${results.length} 通過`);
if (totalFail > 0) process.exit(1);
