'use strict';
// Weekly calculations are independent of DOM; render helpers run after app.js initializes.
const WEEK_MILLISECONDS = 7 * 86400000;
function taipeiDay(timestamp) {
  return new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Taipei',
    year:'numeric',month:'2-digit',day:'2-digit'}).format(timestamp);
}
function weeklyPace(bucket, state, provider = {}, now = Date.now()) {
  const remaining = bucket.remaining_percent, reset = Date.parse(bucket.resets_at);
  const duration = reset - now;
  if (bucket.window_minutes !== 10080 || !['ok','warning','reserve','exhausted'].includes(state)) return null;
  if (typeof remaining !== 'number' || !Number.isFinite(remaining) || remaining < 0 || remaining > 100) return null;
  if (!Number.isFinite(duration) || duration <= 0 || duration > WEEK_MILLISECONDS) return null;
  const days = duration / 86400000, timePercent = duration / WEEK_MILLISECONDS * 100;
  return {remaining,timePercent,days,gap:timePercent - remaining,
    isFast:timePercent - remaining >= 15,
    isSoon:days <= 1 && remaining >= 20,
    isToday:taipeiDay(now) === taipeiDay(reset),
    isRestricted:provider.usage_blocked === true || provider.state !== 'ok' || state !== 'ok'};
}
function createPacePanel(pace) {
  if (!pace) return null;
  const panel = node('div','weekly-pace');
  panel.append(node('p','pace-comparison','本週分配節奏 · 共用 0–100% 刻度'));
  [['額度剩餘',pace.remaining,'allowance'],['週期剩餘',pace.timePercent,'period']].forEach(([label,value,type]) => {
    const row = node('div','pace-row'), meter = node('div',`pace-meter ${type}`);
    meter.setAttribute('role','img'); meter.setAttribute('aria-label',`${label} ${percentText(value)}`);
    const fill = node('span','pace-fill'); fill.style.width = `${value}%`; meter.append(fill);
    row.append(node('span','',label),meter,node('span','pace-value',percentText(value)));
    panel.append(row);
  });
  if (pace.isSoon) {
    const when = pace.isToday ? '今日重置' : '24小時內重置';
    panel.append(node('p','pace-advice',pace.isRestricted
      ? `${when}，派工仍受額度限制` : `${when}，可優先安排既有合適工作（仍須通過派工檢查）`));
  }
  if (pace.isFast) panel.append(node('p','pace-advice fast',`使用偏快：額度剩餘低於週期剩餘 ${pace.gap.toFixed(1)} 個百分點。`));
  const allocation = pace.days > 1
    ? `參考每日可分配 ${percentText(pace.remaining / pace.days).replace('%','')} 個本週總額百分點／天`
    : `本次重置前仍餘 ${percentText(pace.remaining)}`;
  panel.append(node('p','pace-allocation',allocation),node('p','pace-note','均勻分配參考，非官方限制；週池與五小時池不能相加。'));
  return panel;
}
function resetEntries() {
  const future = new Map(), pending = [];
  (snapshot?.providers || []).forEach((provider) => {
    const state = providerState(provider);
    (provider.buckets || []).forEach((bucket) => {
      const current = bucketState(bucket,state), timestamp = parsedTime(bucket.resets_at);
      const item = {id:provider.id,label:`${names[provider.id]} · ${bucketLabel(bucket)}`,timestamp,current};
      if (!validStates.includes(current) || percent(bucket.remaining_percent) === null || !Number.isFinite(timestamp)) {
        pending.push(item); return;
      }
      const key = Math.floor(timestamp / 1000) * 1000;
      if (!future.has(key)) future.set(key,[]);
      future.get(key).push(item);
    });
  });
  return {future:[...future].sort(([first],[second]) => first-second),pending};
}
function renderResetSchedule() {
  const host = $('#reset-schedule'), {future,pending} = resetEntries();
  host.replaceChildren();
  const timeline = node('ol','reset-timeline');
  future.forEach(([timestamp,items]) => {
    const entry = node('li','reset-node'), date = new Date(timestamp).toISOString();
    entry.dataset.resetAt = date;
    const time = node('time','',formatResetTime(date)); time.dateTime = date;
    entry.append(time);
    items.forEach((item) => entry.append(node('p',`reset-event ${item.id}`,item.label)));
    timeline.append(entry);
  });
  host.append(future.length ? timeline : node('p','schedule-empty','目前沒有已驗證的未來重置時間。'));
  if (!pending.length) return;
  const unavailable = node('div','reset-pending');
  unavailable.append(node('h3','','待更新／未取得'));
  pending.forEach((item) => {
    const detail = Number.isFinite(item.timestamp) ? `上次取得 ${formatResetTime(new Date(item.timestamp).toISOString())}` : '重置時間尚未取得';
    unavailable.append(node('p',`reset-event ${item.id}`,`${item.label}｜${detail} · 待更新`));
  });
  host.append(unavailable);
}
