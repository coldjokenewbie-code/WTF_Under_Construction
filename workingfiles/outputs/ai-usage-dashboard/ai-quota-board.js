/* <ai-quota-board> — 可嵌入的 AI 額度板（Claude／Codex／agy 各一列，五小時｜本週兩張卡）
 * 用法：<script src="http://127.0.0.1:8766/ai-quota-board.js"></script>
 *       <ai-quota-board></ai-quota-board>
 * 屬性（皆可省略）：src="http://127.0.0.1:8766"（資料來源，預設＝載入本檔的來源）
 *                  providers="claude,codex,agy"（列順序）  refresh="60"（秒）
 *                  pools="agy=Gemini Models"（同供應商多個週池時指定要顯示哪一個，分號分隔）
 * 樣式：吃宿主的 CSS 變數 --panel --panel-2 --line --accent --ink --ink-2 --ink-3 --ok --warn --bad --font --font-mono；
 *       未定義時用內建深色預設。資料源沒開＝全部空白卡，不丟錯誤。
 */
(() => {
  const ORIGIN = (() => { try { return new URL(document.currentScript.src).origin; } catch { return 'http://127.0.0.1:8766'; } })();
  const NAMES = { claude: 'Claude', codex: 'Codex', agy: 'agy' };
  const PRIORITY = { claude: [/^session/, /^weekly_all/, /^weekly_scoped/], codex: [/./],
                     agy: [/^Gemini Models:/, /^Gemini 4 Argon:/, /^Claude and GPT models:/] };
  const WINDOWS = [[300, '五小時'], [10080, '本週']];
  const TIME = new Intl.DateTimeFormat('zh-TW', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false });
  const CSS = `
:host{display:block;--_panel:var(--panel,#1b2e39);--_panel2:var(--panel-2,#233b48);--_line:var(--line,#5a4f35);--_accent:var(--accent,#c79a3e);
--_ink:var(--ink,#eee3c9);--_ink2:var(--ink-2,#a89b7d);--_ink3:var(--ink-3,#6e6550);--_ok:var(--ok,#8fbf6a);--_warn:var(--warn,#d9a84a);--_bad:var(--bad,#d35c5c);
font:13px/1.45 var(--font,"PingFang TC","Noto Sans TC",sans-serif);color:var(--_ink)}
*{box-sizing:border-box}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.card{background:var(--_panel);border:1px solid var(--_line);border-radius:6px;padding:8px 10px;min-height:86px;display:flex;flex-direction:column;gap:4px}
.card.blank{background:var(--_panel2);border-style:dashed;opacity:.55}
.hd{display:flex;justify-content:space-between;gap:6px;font-size:11px;color:var(--_ink2);white-space:nowrap;overflow:hidden}
.hd b{color:var(--_ink);font-weight:600;overflow:hidden;text-overflow:ellipsis}
.pct{font:600 22px/1.1 var(--font-mono,"IBM Plex Mono",Menlo,monospace);color:var(--_ink);font-variant-numeric:tabular-nums}
.pct.warning{color:var(--_warn)}.pct.reserve,.pct.exhausted{color:var(--_bad)}.pct.state{font-size:13px;color:var(--_ink3);font-family:inherit}
progress.bar{display:block;width:100%;height:6px;margin:0;border:1px solid var(--_line);border-radius:3px;overflow:hidden;background:#0003;appearance:none;-webkit-appearance:none;color:var(--_accent);accent-color:var(--_accent)}
progress.bar::-webkit-progress-bar{background:transparent}
progress.bar::-webkit-progress-value{background:var(--_accent)}
progress.bar::-moz-progress-bar{background:var(--_accent)}
progress.bar.warning{color:var(--_warn);accent-color:var(--_warn)}progress.bar.warning::-webkit-progress-value{background:var(--_warn)}progress.bar.warning::-moz-progress-bar{background:var(--_warn)}
progress.bar.reserve,progress.bar.exhausted{color:var(--_bad);accent-color:var(--_bad)}
progress.bar.reserve::-webkit-progress-value,progress.bar.exhausted::-webkit-progress-value{background:var(--_bad)}
progress.bar.reserve::-moz-progress-bar,progress.bar.exhausted::-moz-progress-bar{background:var(--_bad)}
.rs{font:11px/1.3 var(--font-mono,"IBM Plex Mono",Menlo,monospace);color:var(--_ink2);font-variant-numeric:tabular-nums;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ft{margin-top:6px;font-size:10px;color:var(--_ink3);text-align:right}
`;
  const parse = (v) => (typeof v === 'string' ? Date.parse(v) : NaN);
  const pct = (v) => (typeof v === 'number' && Number.isFinite(v) && v >= 0 && v <= 100 ? v : null);
  const pctText = (v) => (v === null ? '' : v < 10 && v % 1 ? `${v.toFixed(1)}%` : `${Math.round(v)}%`);
  const countdown = (iso) => {
    const ms = parse(iso) - Date.now();
    if (!Number.isFinite(ms)) return '';
    if (ms <= 0) return '已重置';
    const m = Math.floor(ms / 60000), d = Math.floor(m / 1440), h = Math.floor((m % 1440) / 60), mm = m % 60;
    return d ? `${d}d${h}h` : h ? `${h}h${String(mm).padStart(2, '0')}m` : `${mm}m`;
  };
  const rank = (id, bucket) => { const l = PRIORITY[id] || []; const i = l.findIndex((p) => p.test(bucket.id)); return i < 0 ? l.length : i; };
  let SHEET = null;
  try { SHEET = new CSSStyleSheet(); SHEET.replaceSync(CSS); } catch { SHEET = null; }
  const el = (tag, cls = '', text = '') => { const n = document.createElement(tag); if (cls) n.className = cls; if (text) n.textContent = text; return n; };

  class AIQuotaBoard extends HTMLElement {
    static get observedAttributes() { return ['src', 'providers', 'refresh', 'pools']; }
    constructor() {
      super();
      this.attachShadow({ mode: 'open' });
      this.snapshot = null; this.online = false; this.timers = [];
    }
    get src() { return (this.getAttribute('src') || ORIGIN).replace(/\/$/, ''); }
    get providers() { return (this.getAttribute('providers') || 'claude,codex,agy').split(',').map((s) => s.trim()).filter(Boolean); }
    get poolPick() {
      const out = {};
      (this.getAttribute('pools') || '').split(';').forEach((pair) => { const [k, v] = pair.split('='); if (k && v) out[k.trim()] = v.trim(); });
      return out;
    }
    connectedCallback() { this.render(); this.start(); }
    disconnectedCallback() { this.timers.forEach(clearInterval); this.timers = []; }
    attributeChangedCallback() { if (this.isConnected) { this.disconnectedCallback(); this.start(); } }
    start() {
      const seconds = Math.max(15, Number(this.getAttribute('refresh')) || 60);
      this.load();
      this.timers = [setInterval(() => this.load(), seconds * 1000), setInterval(() => this.tick(), 30000)];
    }
    async load() {
      try {
        const r = await fetch(`${this.src}/api/status`, { cache: 'no-store' });
        if (!r.ok) throw new Error(String(r.status));
        this.snapshot = await r.json(); this.online = true;
      } catch { this.online = false; }
      this.render();
    }
    tick() { this.shadowRoot.querySelectorAll('time[data-reset]').forEach((t) => { t.textContent = countdown(t.dataset.reset); }); }
    pick(provider, minutes) {
      const want = this.poolPick[provider.id];
      const list = (provider.buckets || []).filter((b) => b.window_minutes === minutes).sort((a, b) => rank(provider.id, a) - rank(provider.id, b));
      return (want && list.find((b) => b.group === want || b.id.startsWith(want))) || list[0] || null;
    }
    fresh(iso) { const ttl = this.snapshot?.monitor?.ttl_seconds; const t = parse(iso); return Number.isFinite(t) && Number.isFinite(ttl) && Date.now() - t <= ttl * 1000; }
    card(provider, label, bucket) {
      const name = NAMES[provider.id] || provider.label || provider.id;
      const card = el('div', 'card');
      const hd = el('div', 'hd'); hd.append(el('b', '', name), el('span', '', label)); card.append(hd);
      const remaining = bucket ? pct(bucket.remaining_percent) : null;
      const stale = bucket && (!this.fresh(provider.observed_at) || parse(bucket.resets_at) <= Date.now());
      if (!bucket || remaining === null) {
        card.classList.add('blank');
        card.append(el('div', 'pct state', bucket ? (bucket.state || '') : (provider.status === 'error' ? provider.error_code || '來源錯誤' : '')));
        return card;
      }
      const state = stale ? 'stale' : bucket.state || 'ok';
      card.title = `${name} · ${bucket.label || bucket.id} · 採樣 ${TIME.format(parse(provider.observed_at))}`;
      card.append(el('div', `pct ${state}`, pctText(remaining)));
      const bar = el('progress', `bar ${state}`); bar.max = 100; bar.value = remaining; card.append(bar);
      const rs = el('div', 'rs'); const t = el('time'); t.dataset.reset = bucket.resets_at || ''; t.textContent = countdown(bucket.resets_at);
      const at = Number.isFinite(parse(bucket.resets_at)) ? TIME.format(parse(bucket.resets_at)) : '';
      rs.title = '重置時間 · 倒數'; rs.append(at, at ? ' · ' : '', t); if (stale) rs.append(' · 過期'); card.append(rs);
      return card;
    }
    render() {
      const root = this.shadowRoot; root.replaceChildren();
      if (SHEET && 'adoptedStyleSheets' in root) root.adoptedStyleSheets = [SHEET];
      else { const style = el('style'); style.textContent = CSS; root.append(style); }
      const grid = el('div', 'grid');
      this.providers.forEach((id) => {
        const provider = this.online ? (this.snapshot?.providers || []).find((p) => p.id === id) || { id } : { id };
        WINDOWS.forEach(([minutes, label]) => grid.append(this.card(provider, label, this.online ? this.pick(provider, minutes) : null)));
      });
      root.append(grid);
      const at = this.snapshot?.generated_at;
      root.append(el('div', 'ft', this.online ? `AI 額度 · 採樣 ${Number.isFinite(parse(at)) ? TIME.format(parse(at)) : ''}` : 'AI 額度 · 資料源未連線'));
    }
  }
  if (!customElements.get('ai-quota-board')) customElements.define('ai-quota-board', AIQuotaBoard);
})();
