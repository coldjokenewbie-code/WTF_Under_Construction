let currentSlide = 1;
const totalSlides = 6;

const taskData = {
  archive: {
    rec: '機械格式與逐字可驗任務用 Haiku 4.5；要理解內容的搜尋摘要用 Sonnet 5。',
    reason: '驗收容易，不必每件都用高階。'
  },
  feature: {
    rec: 'Sonnet 5 起步；高度牽動其他檔案時由主 agent 處理。',
    reason: '看測試能否抓錯，也看交辦成本。'
  },
  policy: {
    rec: '主 agent 負責連動判斷；Claude 搭檔可用 Opus 5，需第二意見用 Fable 5.1。',
    reason: '不是固定 Fable 比 Opus 更高，也不強制把 Codex 換成 Opus。'
  },
  review: {
    rec: 'Fable 5.1 另開對話，拿產物與驗收條件檢查；作者不能自己核准。',
    reason: '這次工程由 Codex 實作、Fable 複驗；本簡報由 agy 製作、Codex 檢查。'
  }
};

const manualData = {
  full: {
    before: 'Codex 已能讀所需 SKILL.md。',
    after: '優先沿用工具已列出的名稱/描述/路徑，不額外讀索引。',
    impact: '正常流程不增加一層負擔。'
  },
  missing: {
    before: '缺統一的查找備援。',
    after: '「專案索引 → 全域索引 → 命中才讀完整手冊」，索引也缺就查看來源名稱/描述；讀不到要回報。',
    impact: '查找方法有明文，容易核對，而非保證自動觸發。'
  }
};

const slimData = {
  global: { name: 'GLOBAL 單檔', before: 8343, after: 5414, reduction: '35.1%' },
  claude: { name: 'Claude 開場三檔', before: 13093, after: 10271, reduction: '21.6%' },
  codex: { name: 'Codex 開場三檔', before: 13035, after: 10383, reduction: '20.3%' },
  gemini: { name: 'Gemini 開場三檔', before: 13539, after: 10896, reduction: '19.5%' }
};

const driftData = {
  same: {
    draft: '原稿「讀到」',
    copy: '副本「讀到」',
    beforeRes: '通過',
    afterRes: '通過'
  },
  diff: {
    draft: '原稿「讀到」',
    copy: '副本「讀錯」',
    beforeRes: '只看資料夾或入口是否存在，可能放過',
    afterRes: '比較內容，標示需要同步'
  },
  missing: {
    draft: '原稿支援檔「有」',
    copy: '副本支援檔「缺少」',
    beforeRes: '可能放過',
    afterRes: '檢查支援檔，標示缺檔需要同步'
  }
};

function goToSlide(targetIndex) {
  if (targetIndex < 1 || targetIndex > totalSlides || targetIndex === currentSlide) {
    return;
  }
  const prevSlideElem = document.getElementById('slide-' + currentSlide);
  const targetSlideElem = document.getElementById('slide-' + targetIndex);
  const prevTabElem = document.getElementById('tab-' + currentSlide);
  const targetTabElem = document.getElementById('tab-' + targetIndex);

  if (prevSlideElem) prevSlideElem.hidden = true;
  if (targetSlideElem) targetSlideElem.hidden = false;

  if (prevTabElem) prevTabElem.removeAttribute('aria-current');
  if (targetTabElem) targetTabElem.setAttribute('aria-current', 'page');

  currentSlide = targetIndex;
  updateNavControls();

  if (targetSlideElem) {
    targetSlideElem.focus();
  }
}

function updateNavControls() {
  const progressBar = document.getElementById('slide-progress');
  const pageCountElem = document.getElementById('page-count');
  const prevBtn = document.getElementById('prev');
  const nextBtn = document.getElementById('next');

  if (progressBar) progressBar.value = currentSlide;
  if (pageCountElem) pageCountElem.textContent = '頁次 ' + currentSlide + ' / ' + totalSlides;
  if (prevBtn) prevBtn.disabled = (currentSlide === 1);
  if (nextBtn) nextBtn.disabled = (currentSlide === totalSlides);
}

function handleKeyNavigation(e) {
  if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
  const target = e.target;
  if (target && target.closest('input, select, textarea, button, a, details, summary, [contenteditable="true"]')) {
    return;
  }
  e.preventDefault();
  if (e.key === 'ArrowLeft') {
    goToSlide(currentSlide - 1);
  } else if (e.key === 'ArrowRight') {
    goToSlide(currentSlide + 1);
  }
}

function renderTaskDetail(key) {
  const container = document.getElementById('task-detail');
  const item = taskData[key];
  if (!container || !item) return;
  container.innerHTML =
    '<div class="detail-row"><span class="detail-label">推薦配置：</span>' + item.rec + '</div>' +
    '<div class="detail-row"><span class="detail-label">派工理由：</span>' + item.reason + '</div>';
}

function renderManualDetail(key) {
  const container = document.getElementById('manual-detail');
  const item = manualData[key];
  if (!container || !item) return;
  container.innerHTML =
    '<div class="detail-row"><span class="detail-label">以前：</span>' + item.before + '</div>' +
    '<div class="detail-row"><span class="detail-label">現在：</span>' + item.after + '</div>' +
    '<div class="detail-row"><span class="detail-label">影響：</span>' + item.impact + '</div>';
}

function renderSlimmingDetail(key) {
  const container = document.getElementById('slimming-detail');
  const item = slimData[key];
  if (!container || !item) return;
  const pct = ((item.after / item.before) * 100).toFixed(1);

  container.innerHTML =
    '<div class="chart-box" aria-label="' + item.name + ' 減少前與減少後圖表">' +
      '<div class="chart-line">' +
        '<span class="chart-name">修改前 (100%)</span>' +
        '<div class="chart-track"><div class="chart-fill before" style="width: 100%;"></div></div>' +
        '<span class="chart-num">' + item.before.toLocaleString() + ' 字元</span>' +
      '</div>' +
      '<div class="chart-line">' +
        '<span class="chart-name">修改後 (' + pct + '%)</span>' +
        '<div class="chart-track"><div class="chart-fill after" style="width: ' + pct + '%;"></div></div>' +
        '<span class="chart-num">' + item.after.toLocaleString() + ' 字元</span>' +
      '</div>' +
    '</div>' +
    '<div class="chart-badge-wrap">' +
      '<span class="reduction-badge">字元減幅：減少 ' + item.reduction + '</span>' +
    '</div>';
}

function renderDriftDetail(key) {
  const container = document.getElementById('drift-detail');
  const item = driftData[key];
  if (!container || !item) return;

  container.innerHTML =
    '<div class="compare-grid">' +
      '<div class="compare-box"><strong>原稿狀態：</strong>' + item.draft + '</div>' +
      '<div class="compare-box"><strong>副本狀態：</strong>' + item.copy + '</div>' +
    '</div>' +
    '<div class="detail-row"><span class="detail-label">以前結果：</span>' + item.beforeRes + '</div>' +
    '<div class="detail-row"><span class="detail-label">現在結果：</span>' + item.afterRes + '</div>';
}

function setupButtonGroup(selector, attrName, renderFn) {
  const buttons = document.querySelectorAll(selector);
  buttons.forEach(function(btn) {
    btn.addEventListener('click', function() {
      buttons.forEach(function(b) {
        b.classList.remove('active');
        b.setAttribute('aria-pressed', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-pressed', 'true');
      const val = btn.getAttribute(attrName);
      renderFn(val);
    });
  });
}

function initTabs() {
  for (let i = 1; i <= totalSlides; i++) {
    const tab = document.getElementById('tab-' + i);
    if (tab) {
      tab.addEventListener('click', function() {
        goToSlide(i);
      });
    }
  }
}

function initApp() {
  initTabs();

  const prevBtn = document.getElementById('prev');
  const nextBtn = document.getElementById('next');
  if (prevBtn) prevBtn.addEventListener('click', function() { goToSlide(currentSlide - 1); });
  if (nextBtn) nextBtn.addEventListener('click', function() { goToSlide(currentSlide + 1); });

  document.addEventListener('keydown', handleKeyNavigation);

  setupButtonGroup('.task-btn', 'data-task', renderTaskDetail);
  setupButtonGroup('.manual-btn', 'data-scenario', renderManualDetail);
  setupButtonGroup('.slim-btn', 'data-target', renderSlimmingDetail);
  setupButtonGroup('.drift-btn', 'data-drift', renderDriftDetail);

  renderTaskDetail('archive');
  renderManualDetail('full');
  renderSlimmingDetail('global');
  renderDriftDetail('same');
  updateNavControls();
}

document.addEventListener('DOMContentLoaded', initApp);
