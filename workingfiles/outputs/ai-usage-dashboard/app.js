'use strict';
const $ = (selector) => document.querySelector(selector);
const ids = ['claude', 'codex', 'agy'];
const names = {claude:'Claude',codex:'Codex',agy:'agy'};
const labels = {ok:'正常',warning:'接近上限',reserve:'保留額度',exhausted:'額度耗盡',stale:'資料過期',unknown:'尚未取得',error:'來源異常',offline:'連線中斷',stopped:'監控已停止'};
const validStates = ['ok','warning','reserve','exhausted'];
const colors = ['#e0257a','#f2b134','#22b6cf','#ee6a2b','#2f6fd1','#f4e7c6'];
let snapshot = null, history = [], selected = 'claude', is_connected = false;
let is_loading = false, is_refreshing = false, history_error = '', last_signature = '';
const timeFormat = new Intl.DateTimeFormat('zh-TW',{timeZone:'Asia/Taipei',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false});
const resetTimeFormat = new Intl.DateTimeFormat('zh-TW',{timeZone:'Asia/Taipei',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23'});
function node(tag, className = '', text = '') {
  const element = document.createElement(tag);
  element.className = className;
  element.textContent = text;
  return element;
}
function parsedTime(value) { return typeof value === 'string' ? Date.parse(value) : NaN; }
function formatTime(value) { const date = parsedTime(value); return Number.isFinite(date) ? timeFormat.format(date) : '尚未取得'; }
function formatResetTime(value) {
  const date = parsedTime(value);
  if (!Number.isFinite(date)) return '尚未取得';
  const parts = Object.fromEntries(resetTimeFormat.formatToParts(date).map((part) => [part.type,part.value]));
  return `${parts.year}/${parts.month}/${parts.day} ${parts.hour}:${parts.minute}:${parts.second}（台北）`;
}
function percent(value) { return typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 100 ? value : null; }
function percentText(value) {
  if (value === null) return '—';
  if (value > 0 && value < 0.1) return '<0.1%';
  if (value < 100 && value > 99.9) return '>99.9%';
  return `${Math.round(value * 10) / 10}%`;
}
function isFresh(value, ttl) {
  const age = Date.now() - parsedTime(value);
  return Number.isFinite(age) && age >= -60000 && age <= ttl * 1000;
}
function providerState(provider) {
  if (!is_connected) return 'offline';
  if (snapshot?.monitor?.running === false) return 'stopped';
  const ttl = snapshot?.monitor?.ttl_seconds;
  if (!Number.isFinite(ttl) || ttl <= 0) return 'unknown';
  if (!isFresh(snapshot?.monitor?.heartbeat_at, ttl)) return 'stale';
  if (provider.status === 'error') return 'error';
  if (!isFresh(provider.observed_at, ttl)) return 'stale';
  return labels[provider.state] ? provider.state : 'unknown';
}
function bucketState(bucket, state) {
  if (!validStates.includes(state)) return state;
  if (Number.isFinite(parsedTime(bucket.resets_at)) && parsedTime(bucket.resets_at) <= Date.now()) return 'stale';
  return validStates.includes(bucket.state) ? bucket.state : 'unknown';
}
function bucketLabel(bucket) {
  const text = bucket.label || bucket.id || '未命名額度池';
  const translated = {session:'本期額度',weekly_all:'所有模型週額度',weekly_scoped:`${bucket.scope || 'Fable'} 週額度`};
  if (translated[bucket.id] || translated[text]) return translated[bucket.id] || translated[text];
  if (/codex.*primary/i.test(text)) return bucket.window_minutes >= 10080 ? '週額度' : bucket.window_minutes === 300 ? '五小時額度' : '本期額度';
  if (/argon/i.test(text)) return 'Argon 週額度';
  if (/weekly limit remaining/i.test(text)) return '週額度';
  if (/five hour/i.test(text)) return '五小時額度';
  return text;
}
function sourceLabel(source) { return {local_cli:'官方 CLI',local_cli_rpc:'官方 RPC'}[source] || source || '尚未取得'; }
function miniName(provider, bucket) {
  const base = names[provider.id] || provider.id;
  if (provider.id === 'claude') return bucket.scope ? `${base} ${bucket.scope}` : /weekly_all/.test(bucket.id) ? `${base} 全部` : base;
  if (provider.id === 'agy') {
    const group = {'Gemini Models':'Gemini','Claude and GPT models':'Claude/GPT','Gemini 4 Argon':'Argon'}[bucket.group] || bucket.group || '';
    return `${base} ${group}`.trim();
  }
  const pool = bucket.group && bucket.group !== provider.id ? ` ${bucket.group}` : '';
  return `${base}${pool}`;
}
function miniCell(provider, bucket, state) {
  const current = bucketState(bucket, state), is_valid = validStates.includes(current);
  const remaining = is_valid ? percent(bucket.remaining_percent) : null;
  const cell = node('div', `cell ${provider.id} ${remaining === null ? 'invalid' : ''}`);
  cell.title = `${names[provider.id]} · ${bucketLabel(bucket)} · ${labels[current]} · 來源 ${sourceLabel(provider.source)} · 採樣 ${formatTime(provider.observed_at)}`;
  cell.append(node('span', 'nm', miniName(provider, bucket)));
  cell.append(node('strong', `pct ${remaining === null ? 'state' : current}`, remaining === null ? labels[current] : percentText(remaining)));
  const bar = node('span', 'bar'); const fill = node('i'); fill.style.width = `${remaining ?? 0}%`; bar.append(fill);
  const pace = weeklyPace(bucket, current, provider);
  if (pace) { const tick = node('b'); tick.style.left = `${pace.timePercent}%`; tick.title = `本週時間剩餘 ${percentText(pace.timePercent)}`; bar.append(tick); }
  cell.append(bar);
  const reset = node('span', 'rs', 'T− ');
  const countdown = node('time'); countdown.dataset.reset = bucket.resets_at || '';
  countdown.title = `重置時間：${formatResetTime(bucket.resets_at)}`;
  reset.append(countdown);
  if (pace?.isFast) reset.append(node('span', 'fast', `偏快 −${pace.gap.toFixed(0)} 點`));
  cell.append(reset);
  return cell;
}
const poolPriority = {
  claude:[/^session/, /^weekly_all/, /^weekly_scoped/],
  codex:[/./],
  agy:[/^Gemini Models:/, /^Gemini 4 Argon:/, /^Claude and GPT models:/]
};
function poolRank(id, bucket) {
  const list = poolPriority[id] || [];
  const index = list.findIndex((pattern) => pattern.test(bucket.id));
  return index < 0 ? list.length : index;
}
function emptyCell(id, text) {
  const cell = node('div', `cell ${id} empty-cell`);
  cell.append(node('span', 'nm', names[id]), node('strong', 'pct state', text));
  return cell;
}
function renderBoard() {
  const windows = {300:'#mini-period', 10080:'#mini-weekly'};
  Object.entries(windows).forEach(([minutes, selector]) => {
    const columns = ids.map((id) => {
      const provider = snapshot?.providers?.find((item) => item.id === id) || {id};
      const state = providerState(provider);
      const buckets = (provider.buckets || []).filter((bucket) => bucket.window_minutes === Number(minutes))
        .sort((first, second) => poolRank(id, first) - poolRank(id, second));
      const fallback = !validStates.includes(state) && !(provider.buckets || []).length ? labels[state]
        : id === 'codex' && Number(minutes) === 300 ? '無限制' : '無此區塊';
      return {cells: buckets.map((bucket) => miniCell(provider, bucket, state)), fallback};
    });
    const rows = Math.max(1, ...columns.map((column) => column.cells.length));
    const cells = [];
    for (let row = 0; row < rows; row += 1) {
      columns.forEach((column, index) => cells.push(column.cells[row] || emptyCell(ids[index], row === 0 ? column.fallback : '無此區塊')));
    }
    $(selector).replaceChildren(...cells);
  });
}
function renderStatus() {
  renderBoard();
  const ttl = snapshot?.monitor?.ttl_seconds;
  const is_stopped = snapshot?.monitor?.running === false;
  const is_alive = is_connected && !is_stopped && Number.isFinite(ttl) && isFresh(snapshot?.monitor?.heartbeat_at,ttl);
  $('#service-status').textContent = !is_connected ? '連線中斷' : is_stopped ? '監控已停止' : is_alive ? '監控中' : '心跳過期';
  $('#service-dot').className = `dot ${is_alive ? 'ok' : 'warning'}`;
  const interval = snapshot?.monitor?.interval_seconds;
  const cadence = Number.isFinite(interval) ? interval % 60 === 0 ? `${interval / 60} 分鐘` : `${interval} 秒` : '未知間隔';
  $('#cadence').textContent = cadence;
  $('#service-detail').textContent = !is_connected ? '舊數字已失效' : is_stopped ? '舊數字已失效' : snapshot?.monitor?.refreshing ? '背景採樣中' : '';
  $('#heartbeat').textContent = formatTime(snapshot?.monitor?.heartbeat_at);
  const monitor = snapshot?.monitor;
  if (monitor) $('#monitor-config').textContent = `本機每 ${monitor.interval_seconds ?? '未知'} 秒採樣，資料有效期限 ${monitor.ttl_seconds ?? '未知'} 秒。`;
  const sources = (snapshot?.providers || []).map((provider) => {
    const extra = [provider.error_code ? `來源回報 ${provider.error_code}` : '', provider.usage_blocked === true ? '帳戶用量受限' : ''].filter(Boolean).join('，');
    return `${names[provider.id] || provider.id}：${sourceLabel(provider.source)}，採樣 ${formatTime(provider.observed_at)}${extra ? `，${extra}` : ''}`;
  });
  $('#sources').textContent = sources.join('　');
  last_signature = statusSignature();
  updateCountdowns();
  renderResetSchedule();
}
function updateCountdowns() {
  document.querySelectorAll('[data-reset]').forEach((element) => {
    const remaining = parsedTime(element.dataset.reset) - Date.now();
    if (!Number.isFinite(remaining)) { element.textContent = '時間未取得'; return; }
    if (remaining <= 0) { element.textContent = '已到，待採樣'; return; }
    const seconds = Math.ceil(remaining / 1000), days = Math.floor(seconds / 86400);
    const hours = Math.floor(seconds % 86400 / 3600), minutes = Math.floor(seconds % 3600 / 60);
    element.textContent = days ? `${days}天${hours}時` : hours ? `${hours}時${minutes}分` : `${minutes}分${seconds % 60}秒`;
  });
}
async function request(path, options = {}) {
  const response = await fetch(path,{...options,cache:'no-store',signal:AbortSignal.timeout(10000)});
  const data = await response.json().catch(() => ({}));
  return {response,data};
}
async function loadStatus() {
  if (is_loading) return;
  is_loading = true;
  try {
    const {response,data} = await request('/api/status');
    if (!response.ok || data.schema_version !== 1 || !Array.isArray(data.providers)) throw new Error('invalid_status');
    snapshot = data; is_connected = true;
  } catch { is_connected = false; }
  finally { is_loading = false; renderStatus(); }
}
async function loadHistory() {
  try {
    const {response,data} = await request('/api/history');
    if (!response.ok) throw new Error('history_unavailable');
    history = Array.isArray(data) ? data : data.entries;
    if (!Array.isArray(history)) throw new Error('invalid_history');
    history_error = '';
  } catch { history = []; history_error = '歷史紀錄暫時無法讀取'; }
  renderChart();
}
async function refresh() {
  if (is_refreshing) return;
  is_refreshing = true; $('#refresh').disabled = true;
  $('#refresh-result').textContent = '送出中…';
  try {
    const {response} = await request('/api/refresh',{method:'POST',headers:{'X-Usage-Request':'1'}});
    const messages = {202:'背景採樣中，畫面會自動更新',429:'冷卻中，稍後再試',409:'已有採樣進行中'};
    $('#refresh-result').textContent = messages[response.status] || '刷新未成功';
    if (response.ok) { await loadStatus(); await loadHistory(); }
  } catch { $('#refresh-result').textContent = '無法連到本機服務'; }
  finally { is_refreshing = false; $('#refresh').disabled = false; }
}
function svgNode(tag, attributes = {}, text = '') {
  const element = document.createElementNS('http://www.w3.org/2000/svg',tag);
  Object.entries(attributes).forEach(([key,value]) => element.setAttribute(key,String(value)));
  element.textContent = text; return element;
}
function getSeries() {
  const series = new Map(), cutoff = Date.now() - 7 * 86400000;
  const entries = [...history].sort((first,second) => parsedTime(first.generated_at) - parsedTime(second.generated_at));
  entries.forEach((entry) => entry.providers?.find((item) => item.id === selected)?.buckets?.forEach((bucket) => {
    if (!series.has(bucket.id)) series.set(bucket.id,{label:[bucket.group,bucketLabel(bucket)].filter(Boolean).join(' · '),points:[]});
  }));
  entries.forEach((entry) => {
    const timestamp = parsedTime(entry.generated_at), provider = entry.providers?.find((item) => item.id === selected);
    if (!Number.isFinite(timestamp) || timestamp < cutoff || timestamp > Date.now()) return;
    const ttl = entry.monitor?.ttl_seconds, age = timestamp - parsedTime(provider?.observed_at);
    const is_fresh = Number.isFinite(ttl) && ttl > 0 && Number.isFinite(age) && age >= -60000 && age <= ttl * 1000;
    series.forEach((item,id) => {
      const bucket = provider?.buckets?.find((bucket) => bucket.id === id);
      const is_valid = provider?.status === 'ok' && validStates.includes(provider.state) && validStates.includes(bucket?.state);
      item.points.push({time:timestamp,value:is_valid && is_fresh ? percent(bucket.remaining_percent) : null});
    });
  });
  return [...series.values()].filter((series) => series.points.some((point) => point.value !== null));
}
function drawSeries(svg, series, index, start, end, width) {
  let segment = [];
  const flush = () => { if (segment.length) svg.append(svgNode('polyline',{points:segment.join(' '),fill:'none',stroke:colors[index % colors.length],'stroke-width':2.5,'stroke-linejoin':'round'})); segment = []; };
  series.points.forEach((point) => {
    if (point.value === null) { flush(); return; }
    const x = 44 + (point.time - start) / (end - start) * (width - 56), y = 205 - point.value * 1.85;
    segment.push(`${x},${y}`);
    const dot = svgNode('circle',{cx:x,cy:y,r:3,fill:colors[index % colors.length]});
    dot.append(svgNode('title',{},`${series.label} · ${formatTime(new Date(point.time).toISOString())} · 剩餘 ${percentText(point.value)}`));
    svg.append(dot);
  }); flush();
}
function renderChart() {
  const host = $('#chart'), legend = $('#chart-legend'), series = getSeries();
  host.replaceChildren(); legend.replaceChildren();
  if (!series.length) { host.append(node('p','empty-chart',history_error || '有效採樣累積後才有軌跡')); return; }
  const end = Date.now(), start = end - 7 * 86400000, width = Math.max(240,host.clientWidth);
  const svg = svgNode('svg',{viewBox:`0 0 ${width} 245`,role:'img','aria-label':`${names[selected]} 七日各額度池剩餘比例折線圖`});
  [0,25,50,75,100].forEach((value) => {
    const y = 205 - value * 1.85;
    svg.append(svgNode('line',{x1:44,y1:y,x2:width-12,y2:y,stroke:'#2a4f86','stroke-dasharray':'3 5'}),svgNode('text',{x:0,y:y+5},`${value}%`));
  });
  [0,2,4,6].forEach((offset) => {
    const date = new Date(start + offset * 86400000), text = new Intl.DateTimeFormat('zh-TW',{timeZone:'Asia/Taipei',month:'numeric',day:'numeric'}).format(date);
    svg.append(svgNode('text',{x:44 + offset / 7 * (width-56),y:236},text));
  });
  series.forEach((item,index) => {
    drawSeries(svg,item,index,start,end,width);
    const label = node('span'), swatch = node('i','legend-color'); swatch.style.background = colors[index % colors.length];
    label.append(swatch,document.createTextNode(item.label)); legend.append(label);
  }); host.append(svg);
}
function statusSignature() {
  return ids.map((id) => {
    const provider = snapshot?.providers?.find((item) => item.id === id) || {};
    const state = providerState(provider);
    return [state,...(provider.buckets || []).map((bucket) => bucketState(bucket,state))].join();
  }).join();
}
$('#refresh').addEventListener('click',refresh);
window.addEventListener('resize',renderChart);
$('#history').addEventListener('toggle',renderChart);
document.querySelectorAll('[data-provider]').forEach((button) => button.addEventListener('click',(event) => {
  event.preventDefault(); event.stopPropagation();
  selected = button.dataset.provider;
  document.querySelectorAll('[data-provider]').forEach((item) => item.setAttribute('aria-pressed',String(item === button)));
  if (!$('#history').open) $('#history').open = true;
  renderChart();
}));
renderStatus(); loadStatus(); loadHistory();
setInterval(loadStatus,15000); setInterval(loadHistory,60000);
setInterval(() => {
  const signature = statusSignature();
  if (signature !== last_signature) renderStatus();
  else updateCountdowns();
},1000);
