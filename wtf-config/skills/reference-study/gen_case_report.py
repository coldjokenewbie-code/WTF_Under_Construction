#!/usr/bin/env python3
"""案例研究報告產生器：cases.json → index.html（依 reference-study skill 規格）。
每案可加 "tags":["拓展組"|"爭議組"|"跨軸"] 與 "bias_note"；頂層可加 "deliberate":[…] 刻意違反清單。
用法：python3 gen_case_report.py <報告資料夾>   （資料夾內需有 cases.json，圖抓進 shots/）"""
import json, sys, html, subprocess, pathlib, re, datetime

root = pathlib.Path(sys.argv[1]); data = json.loads((root/"cases.json").read_text(encoding="utf-8"))
shots = root/"shots"; shots.mkdir(exist_ok=True)
E = html.escape

def fetch_shot(url, name):
    """抓縮圖存本地；失敗回 None。python subprocess timeout，不用 shell timeout（macOS 無）。"""
    if not url: return None
    dst = shots/f"{name}.jpg"
    if dst.exists() and dst.stat().st_size > 2000: return dst.name
    try:
        r = subprocess.run(["curl","-sL","-A","Mozilla/5.0","-o",str(dst),url], timeout=20)
        if r.returncode == 0 and dst.exists() and dst.stat().st_size > 2000: return dst.name
    except subprocess.TimeoutExpired: pass
    if dst.exists(): dst.unlink()
    return None

BADGE = {"高":"b-hi","中":"b-mid","低":"b-lo"}
def card(c, i):
    img = fetch_shot(c.get("image"), f"{c['axis']}{i:02d}")
    link = c.get("video") or c.get("source")
    imgtag = (f'<a href="{E(link)}" target="_blank" rel="noopener"><img src="shots/{img}" alt="{E(c["name"])}" loading="lazy"></a>'
              if img else f'<div class="noimg">站方封鎖／無可驗證代表圖<br><a href="{E(link)}" target="_blank" rel="noopener">開影片／來源頁</a></div>')
    return f'''<article class="card" data-id="{c['axis']}{i:02d}">
  {imgtag}
  <div class="body">
    <label class="pick"><input type="checkbox" data-name="{E(c['name'])}"> 有興趣</label>
    <span class="badge {BADGE.get(c.get('relevance','低'),'b-lo')}">相關度 {E(c.get('relevance','低'))}</span>{''.join(f' <span class="badge b-tag">{E(x)}</span>' for x in c.get('tags',[]))}
    <h3>{E(c['name'])}</h3>
    <p class="meta">{E(c.get('author',''))}｜{E(str(c.get('year','不明')))}｜{E(c.get('venue',''))}</p>
    <p class="mech">{E(c['mechanism'])}</p>
    <p class="why"><b>為什麼適用本案：</b>{E(c['why'])}</p>{'<p class="why"><b>拓展／爭議理由：</b>'+E(c['bias_note'])+'</p>' if c.get('bias_note') else ''}
    <p class="tags">{E(c.get('spectrum',''))} · 年齡 {E(c.get('age','—'))} · 多人共玩：{E(c.get('multi','—'))}</p>
    <p class="links">{'<a href="%s" target="_blank" rel="noopener">▶ 影片</a> ' % E(c['video']) if c.get('video') else ''}<a href="{E(c.get('source',link))}" target="_blank" rel="noopener">來源頁</a>
      <span class="verify">{E(c.get('verified',''))}</span></p>
  </div></article>'''

def axis_section(ax):
    cards = "\n".join(card(c, i+1) for i, c in enumerate(ax["cases"]))
    quad = "".join(f'<div><b>{E(k)}</b><p>{E(v)}</p></div>' for k, v in ax["summary"].items())
    return f'''<section class="axis" id="axis-{E(ax['key'])}">
  <h2>{E(ax['title'])}</h2><p class="axis-desc">{E(ax['desc'])}</p>
  <div class="grid">{cards}</div>
  <div class="quad">{quad}</div>
  <p class="cut"><b>主編剔除：</b>{E(ax.get('cut','無'))}</p>
</section>'''

def table(cmp):
    head = "".join(f"<th>{E(a)}</th>" for a in cmp["axes"])
    rows = ""
    for r in cmp["rows"]:
        cells = "".join(f'<td><span class="badge {BADGE.get(v[0],"b-lo")}">{E(v[0])}</span> {E(v[1])}</td>' for v in r["cells"])
        rows += f"<tr><th>{E(r['criterion'])}</th>{cells}</tr>"
    return f'<table><thead><tr><th>PO 判準 ＼ 軸</th>{head}</tr></thead><tbody>{rows}</tbody></table>'

li = lambda xs: "".join(f"<li>{E(x)}</li>" for x in xs)
m = data["meta"]
out = f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(m['title'])}</title>
<style>
:root{{--bg:#fbf8f2;--ink:#1f2328;--mut:#6b7280;--card:#fff;--line:#e5e0d6;--acc:#e0552b;--hi:#1b7f5a;--mid:#b7791f;--lo:#8a8f98}}
*{{box-sizing:border-box}}body{{margin:0;padding-block:24px;padding-inline:clamp(16px,4vw,48px);background:var(--bg);color:var(--ink);font:15px/1.6 -apple-system,"PingFang TC","Noto Sans TC",sans-serif}}
h1{{font-size:clamp(24px,3.4vw,36px);margin:0 0 4px}}h2{{font-size:22px;margin:40px 0 4px;border-left:6px solid var(--acc);padding-left:12px}}h3{{margin:6px 0 2px;font-size:17px}}
.sub{{color:var(--mut);margin:0 0 18px}}.assume{{background:#fff4e5;border:1px solid #f3c98b;border-radius:10px;padding:12px 16px;margin:14px 0}}
.howto{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 16px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;margin-top:14px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;display:flex;flex-direction:column}}
.card img{{width:100%;aspect-ratio:16/9;object-fit:cover;display:block;max-width:100%}}.noimg{{aspect-ratio:16/9;display:grid;place-items:center;text-align:center;background:#eee;color:var(--mut);font-size:13px;padding:8px}}
.body{{padding:10px 14px 14px}}.meta{{color:var(--mut);font-size:13px;margin:0 0 6px}}.mech{{margin:0 0 6px}}.why{{margin:0 0 6px}}.tags{{font-size:13px;color:var(--mut);margin:0 0 6px}}
.links a{{margin-right:10px}}.verify{{font-size:12px;color:var(--hi)}}.pick{{float:right;font-size:13px;user-select:none}}
.badge{{display:inline-block;font-size:12px;padding:1px 8px;border-radius:999px;color:#fff;background:var(--lo)}}.b-hi{{background:var(--hi)}}.b-mid{{background:var(--mid)}}.b-lo{{background:var(--lo)}}.b-tag{{background:#6d28d9}}
.quad{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;margin-top:16px}}.quad div{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px}}.quad p{{margin:4px 0 0;font-size:14px}}
.cut{{color:var(--mut);font-size:13px}}.axis-desc{{color:var(--mut);margin:0}}
.tblwrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;min-width:640px;background:var(--card)}}th,td{{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top;font-size:14px}}thead th{{background:#f1ede4}}
.rec{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 18px}}.rec ol li{{margin-bottom:8px}}
.bar{{position:sticky;bottom:0;background:#1f2328;color:#fff;padding:10px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:30px -16px -24px;font-size:14px}}.bar button{{background:var(--acc);color:#fff;border:0;border-radius:8px;padding:6px 14px;cursor:pointer}}
a{{color:#0b57d0}}footer{{color:var(--mut);font-size:13px;margin-top:30px}}
</style></head><body>
<h1>{E(m['title'])}</h1><p class="sub">{E(m['subtitle'])}</p>
<div class="assume"><b>第 0 步假設（PO 未確認，錯了整份重定向）：</b><ul>{li(m['assumptions'])}</ul></div>
<div class="howto"><b>怎麼讀這份報告：</b>{E(m['howto'])}</div>
<h2>一頁看完</h2><div class="rec"><ol>{li(m['tldr'])}</ol></div>
{"".join(axis_section(a) for a in data["axes"])}
<h2>綜合比較（以 PO 判準為列）</h2><div class="tblwrap">{table(data['compare'])}</div>
{'<h2>刻意違反清單（拓展組／爭議組）</h2><div class="rec"><ul>'+li(data['deliberate'])+'</ul></div>' if data.get('deliberate') else ''}
<h2>建議（供裁決，非定案）</h2><div class="rec"><ol>{li(data['recommend'])}</ol></div>
<h2>待 PO 裁決</h2><div class="rec"><ol>{li(data['pending'])}</ol></div>
<h2>驗證聲明</h2><div class="rec"><ul>{li(data['verification'])}</ul></div>
<footer>{E(m['footer'])}</footer>
<div class="bar"><span id="cnt">已勾 0 案</span><button id="copy">複製勾選清單</button><span>貼回對話即可</span></div>
<script>
const boxes=[...document.querySelectorAll('.pick input')],cnt=document.getElementById('cnt');
const upd=()=>cnt.textContent='已勾 '+boxes.filter(b=>b.checked).length+' 案';boxes.forEach(b=>b.addEventListener('change',upd));
document.getElementById('copy').onclick=async()=>{{const t=boxes.filter(b=>b.checked).map(b=>'- '+b.dataset.name).join('\\n')||'（未勾選）';try{{await navigator.clipboard.writeText(t);cnt.textContent='已複製 '+boxes.filter(b=>b.checked).length+' 案'}}catch(e){{prompt('複製失敗，手動複製：',t)}}}};
</script></body></html>'''
(root/"index.html").write_text(out, encoding="utf-8")
n = sum(len(a["cases"]) for a in data["axes"]); print(f"寫出 {root/'index.html'}：{len(data['axes'])} 軸 {n} 案，shots/ {len(list(shots.glob('*.jpg')))} 圖")
