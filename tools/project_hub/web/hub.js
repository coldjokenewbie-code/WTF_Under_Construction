const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const PAL=["var(--blue)","var(--magenta)","var(--gold)","var(--teal)","var(--coral)","var(--cyan)"];
const HEAD=["#2e5c86","#a8445f","#3f8f86","#c7622f","#8a6a2a"];
let S=null,view=store.get("view")||"ov",sel=store.get("sel")||"",stageSig="",softwareError="";
const img=(p,rel)=>rel?`/f/${encodeURIComponent(p)}/${rel.split("/").map(encodeURIComponent).join("/")}`:"";
const ago=m=>m==null?"—":m<1?"剛剛":m<60?`${Math.round(m)} 分`:m<1440?`${Math.round(m/60)} 時`:`${Math.round(m/1440)} 天`;
const code=n=>{const m=n.match(/^([A-Z]-\d)/);return m?m[1].replace("-",""):n.slice(0,2)};
const itemKind=(ex,item)=>(ex.decisions||[]).includes(item)?"decision":"review";
const isAns=(ex,item)=>(ex.answers||[]).some(answer=>answer.kind===itemKind(ex,item)&&answer.id===item.id&&answer.at>=(item.at||""));
// 已結束：status 標 closed，或你驗通過且沒有待決／待審／未完成待辦
const isFin=ex=>ex.closed===true||(/通過|PASS/.test((ex.verify||{}).po||"")&&!(ex.decisions||[]).some(d=>!isAns(ex,d))&&!(ex.reviews||[]).some(r=>!isAns(ex,r))&&!(ex.todos||[]).some(t=>["todo","doing","wait"].includes(t.state)));
const allInc=()=>S?scopedProjects().flatMap(p=>p.exhibits.map(ex=>({p:p.project_id,ex}))):[];
const all=()=>allInc().filter(o=>!o.ex.exhibit.startsWith("_")&&o.ex.archived!==true);
const archived=()=>allInc().filter(o=>!o.ex.exhibit.startsWith("_")&&o.ex.archived===true);
const ST={todo:"未開始",doing:"進行中",wait:"等確認",submitted:"已提交",done:"已完成"};
const openTd=new Set();let tdFilter=store.get("tdf")||"open";
const todosAll=()=>allInc().filter(o=>o.ex.archived!==true).flatMap(({p,ex})=>(ex.todos||[]).map(t=>({p,ex,t,k:keyOf(p,ex.exhibit,t.id,"note")})));
const exOf=k=>all().concat(archived()).find(o=>keyOf(o.p,o.ex.exhibit)===k);
function mosaic(cls,n){let h="";for(let i=0;i<n;i++)h+=`<i style="background:${Math.random()<.35?"transparent":PAL[(Math.random()*6)|0]};opacity:${(.3+Math.random()*.7).toFixed(2)}"></i>`;return`<div class="mosaic" style="${cls}">${h}</div>`}
const MOS1=mosaic("right:30px;bottom:18px",24),MOS2=mosaic("left:26px;bottom:24px",18);
async function requestJson(url,options={}){const response=await fetch(url,options);const data=await response.json();if(!response.ok)throw new Error(data.error||`HTTP ${response.status}`);return data}
async function post(url,body){return requestJson(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)})}
function setView(v,s){saveSayDraft();view=v;if(s!==undefined)sel=s;store.set("view",view);store.set("sel",sel);stageSig="";render(true)}

function softwareWarnings(){
  if(softwareError)return [softwareError];
  const warnings=[];
  for(const project of scopedProjects())for(const diagnostic of project.diagnostics||[]){
    const message=typeof diagnostic==="string"?diagnostic:diagnostic.message||diagnostic.reason||"資料讀取失敗";
    warnings.push(`${project.name}｜${message}`);
  }
  const failed=all().reduce((count,{ex})=>count+(ex.answers||[]).filter(answer=>deliveryClass(answer.delivery)==="bad").length,0);
  if(failed)warnings.push(`有 ${failed} 則回覆投遞異常，請到「已送出」查看`);
  return warnings;
}
function renderSoftwareStatus(){
  const warnings=softwareWarnings(),ticker=$("#tick");
  $("#n-warn").textContent=warnings.length;
  const count=$("#software-warn-count");if(count)count.textContent=warnings.length;
  ticker.className=warnings.length?"tick bad":"tick calm";
  ticker.innerHTML=warnings.length?`<b>軟體異常</b><span>${esc(warnings.join("　／　"))}</span>`:"<span>指揮中心運作正常</span>";
}
function renderTop(){
  const p=deadlineProject();$("#pname").textContent=activeProject==="*"?"指揮中心｜全部專案":`指揮中心｜${projectName(activeProject)}`;$("#due").textContent="—";$("#due-l").textContent="未設定交付";
  if(p&&p.deadline){const m=(new Date(p.deadline)-new Date())/60000;
    $("#due").textContent=m<=0?"已到期":`${String(Math.floor(m/1440)).padStart(2,"0")}天 ${String(Math.floor(m%1440/60)).padStart(2,"0")}:${String(Math.floor(m%60)).padStart(2,"0")}`;
    $("#due-l").textContent=`${activeProject==="*"?p.name+"｜":""}距離 ${p.deadline_label||"交付"}`;}
  const items=all();
  const revs=items.reduce((n,o)=>n+(o.ex.reviews||[]).filter(r=>!isAns(o.ex,r)).length,0);
  const bad=items.reduce((n,o)=>n+(o.ex.answers||[]).filter(a=>deliveryClass(a.delivery)==="bad").length,0);
  const tdo=todosAll().filter(x=>["todo","doing","wait"].includes(x.t.state||"todo")).length,ntd=$("#n-todo");ntd.textContent=tdo||"";ntd.classList.toggle("z",!tdo);const nr=$("#n-rev");nr.textContent=revs||"";nr.classList.toggle("z",!revs);
  const nb=$("#n-bad");nb.textContent=bad?"!":"";nb.classList.toggle("z",!bad);
  renderSoftwareStatus();
  document.querySelectorAll(".tab").forEach(b=>b.classList.toggle("on",b.dataset.view===view||(view==="rv"&&b.dataset.view==="rvlist")||(view==="pg"&&b.dataset.view==="pages")));
}
function renderList(){
  const row=({p,ex},i)=>{const k=keyOf(p,ex.exhibit);
    const nd=(ex.decisions||[]).filter(d=>!isAns(ex,d)).length,nr=(ex.reviews||[]).filter(r=>!isAns(ex,r)).length;
    const col=ex.light==="red"?"var(--bad)":ex.light==="green"?"var(--teal)":ex.light==="amber"?"var(--gold)":"var(--dim)";
    return`<div class="ex ${view==="ex"&&sel===k?"on":""} ${isFin(ex)?"fin":""}" data-ex="${esc(k)}" tabindex="0">
      <div class="av" style="background:${col}">${esc(code(ex.exhibit))}</div>
      <div style="min-width:0"><div class="nm">${esc(projectLabel(p)+ex.exhibit)}</div><div class="dn">${esc(ex.doing||"—")}</div></div>
      <div><div class="rt">${esc(ago(ex.age_min))}</div><div class="bd">${nd?`<i class="d">決 ${nd}</i>`:""}${nr?`<i class="r">審 ${nr}</i>`:""}${ex.warnings.length?`<i class="w">!</i>`:""}</div></div></div>`};
  const items=all(),act=items.filter(o=>!isFin(o.ex)),fin=items.filter(o=>isFin(o.ex)),open=store.get("finOpen")==="1";
  $("#list").innerHTML=(act.map(row).join("")+(fin.length?`<div class="fin-hd" data-fin>已結束 ${fin.length}<span>${open?"收起 ▲":"展開 ▼"}</span></div>${open?fin.map(row).join(""):""}`:"")+(()=>{const ar=archived(),ao=store.get("archOpen")==="1";if(!ar.length)return"";const g={};ar.forEach(o=>{const b=(o.ex.batch||"封存").split("、")[0];(g[b]=g[b]||[]).push(o)});const ks=Object.keys(g).sort().reverse();return`<div class="fin-hd" data-arch>封存（${ks.join("／")}）${ar.length}<span>${ao?"收起 ▲":"展開 ▼"}</span></div>${ao?ks.map(b=>`<div class="empty" style="padding:6px 12px 2px;font-size:12px">${esc(b)}</div>`+g[b].map(row).join("")).join(""):""}`})())||`<div class="empty">還沒有工作線回報</div>`;
  const o=exOf(sel);$("#say-to").textContent=o?projectLabel(o.p)+o.ex.exhibit:"（先在上方點選工作項目）";
}
function ticks(){let s="";for(let i=0;i<60;i++){const a=i*6*Math.PI/180,r1=i%5?104:98,r2=108;s+=`<line x1="${150+r1*Math.cos(a)}" y1="${150+r1*Math.sin(a)}" x2="${150+r2*Math.cos(a)}" y2="${150+r2*Math.sin(a)}" stroke="${i%5?"#6e6550":"#c79a3e"}" stroke-width="${i%5?1:2}"/>`}return s}
function ringSVG(items){
  const n=items.length||1,R=128,C=2*Math.PI*R,gap=6,seg=C/n-gap;let s="";
  items.forEach(({ex},i)=>{const pg=ex.progress||{},f=pg.total?pg.done/pg.total:(ex.light==="green"?1:0);
    const col=ex.light==="red"?"#b83a34":ex.light==="green"?"#5f9a6e":ex.light==="amber"?"#d3a23f":"#6e6550";
    const off=-(i*(C/n));
    s+=`<circle cx="150" cy="150" r="${R}" fill="none" stroke="#2b4250" stroke-width="10" stroke-dasharray="${seg} ${C-seg}" stroke-dashoffset="${off}"/>`;
    s+=`<circle class="seg" cx="150" cy="150" r="${R}" fill="none" stroke="${col}" stroke-width="10" stroke-dasharray="${Math.max(2,seg*f)} ${C-Math.max(2,seg*f)}" stroke-dashoffset="${off}"><title>${esc(ex.exhibit)}</title></circle>`;});
  return`<svg viewBox="0 0 300 300" role="img" aria-label="各工作項目進度環"><g transform="rotate(-90 150 150)">${s}</g><circle cx="150" cy="150" r="145" fill="none" stroke="#c79a3e" stroke-width="1"/><circle cx="150" cy="150" r="111" fill="none" stroke="#c79a3e" stroke-width="1"/>${ticks()}</svg>`;
}
function stageOv(){
  const items=all(),tot=items.reduce((a,o)=>a+((o.ex.progress||{}).total||0),0),done=items.reduce((a,o)=>a+((o.ex.progress||{}).done||0),0);
  const decs=items.reduce((n,o)=>n+(o.ex.decisions||[]).filter(d=>!isAns(o.ex,d)).length,0),revs=items.reduce((n,o)=>n+(o.ex.reviews||[]).filter(r=>!isAns(o.ex,r)).length,0);
  const warn=softwareWarnings().length;
  return`<div class="ghost l">STATUS</div><div class="ghost r">LIVE</div>${MOS1}
  <p class="h-stage">OVERVIEW　各工作項目戰情</p>
  <div class="ov">
    <div class="kpis"><div class="kpi"><b>${items.length}</b><span>工作項目</span></div><div class="kpi m"><b>${decs}</b><span>待你決定</span></div>
      <div class="kpi g"><b>${revs}</b><span>待你審閱</span></div><div class="kpi x"><b id="software-warn-count">${warn}</b><span>軟體異常</span></div><div class="kpi"><b>${todosAll().filter(x=>x.t.state==="submitted").length}</b><span>待你驗收</span></div><div class="kpi"><b>${todosAll().filter(x=>x.t.ask&&x.t.state!=="done").length}</b><span>要問中鼎</span></div></div>
    <div class="ring">${ringSVG(items)}<div class="c"><small>待辦完成</small><b>${done}／${tot}</b><em>${tot?Math.round(100*done/tot):0}%</em></div></div>
    <div><div class="eq">${items.map(({p,ex},i)=>{const pg=ex.progress||{},f=pg.total?pg.done/pg.total:(ex.light==="green"?1:.04);
      return`<div class="bar" data-ex="${esc(keyOf(p,ex.exhibit))}" title="${esc(ex.exhibit)}　${pg.total?pg.done+"／"+pg.total:"無待改"}" style="color:${PAL[i%6]}"><i style="height:${Math.max(4,f*100)}%;background:currentColor"></i><span>${esc(code(ex.exhibit))}</span></div>`}).join("")}</div>
      <div class="eq-cap">各工作項目待辦完成比例（點長條看該工作項目）</div></div>
  </div>`;
}
function stageEx(){
  const o=exOf(sel);if(!o)return stageOv();const {p,ex}=o,pg=ex.progress||{},v=ex.verify||{};
  const vc=k=>/通過|PASS/.test(v[k]||"")?"ok":/退回|FAIL/.test(v[k]||"")?"no":"";
  const revs=ex.archived===true?[]:(ex.reviews||[]).filter(r=>!isAns(ex,r));
  return`<div class="ghost r">${esc(code(ex.exhibit))}</div>${MOS2}<div class="det"><p class="h-stage">EXHIBIT　工作項目</p><h2>${projectChip(p)}${esc(ex.exhibit)}</h2>
  <div class="who"><button class="chip" data-bind="${esc(keyOf(p,ex.exhibit))}">重新連結工作線</button>　負責：${esc(ex.line||"未指派")}　·　更新 ${esc(ago(ex.age_min))}前</div>
  <div class="big"><div>${esc(ex.doing||"—")}</div>
  ${pg.total?`<div><div class="pbar"><i style="width:${Math.round(100*pg.done/pg.total)}%"></i></div><small style="color:var(--mute)">${esc(pg.label||"進度")}　${pg.done}／${pg.total}</small></div>`:""}
  <div class="chips"><span class="chip ${vc("self")}">自驗：${esc(v.self||"未驗")}</span><span class="chip ${vc("peer")}">非作者驗：${esc(v.peer||"未驗")}</span><span class="chip ${vc("po")}">你驗：${esc(v.po||"未驗")}</span></div>
  ${(ex.files||[]).length?`<div class="files">${ex.files.map(f=>`<div><a data-open="${esc(f.path)}" data-p="${esc(p)}" title="背景開啟">${esc(f.path.split("/").pop())}</a>${f.open?'<span class="open">● PowerPoint 開著</span>':""}${f.md5?`<span>MD5 ${esc(f.md5.slice(0,8))}</span>`:""}</div>`).join("")}</div>`:""}
  ${ex.warnings.length?`<div class="warns">${ex.warnings.map(w=>`<div>${esc(w)}</div>`).join("")}</div>`:""}
  ${(()=>{const ts=ex.todos||[],op=ts.filter(t=>["todo","doing","wait"].includes(t.state||"todo")),sb=ts.filter(t=>t.state==="submitted"),dn=ts.filter(t=>t.state==="done"),r=t=>tdRow({p,ex,t,k:keyOf(p,ex.exhibit,t.id,"note")});
    return (op.length?`<div><small style="color:var(--mute)">未完成待辦 ${op.length}（點列展開、左邊改狀態）</small><div style="margin-top:6px">${op.map(r).join("")}</div></div>`:ts.length?`<div><small style="color:var(--mute)">沒有未完成的待辦</small></div>`:"")
     +(sb.length?`<details><summary style="cursor:pointer;color:var(--mute);font-size:12px">已提交、待你驗收 ${sb.length}（左邊改成「已完成」即驗收）</summary><div style="margin-top:6px">${sb.map(r).join("")}</div></details>`:"")
     +(dn.length?`<details><summary style="cursor:pointer;color:var(--dim);font-size:12px">已完成 ${dn.length}</summary><div style="margin-top:6px">${dn.map(r).join("")}</div></details>`:"")})()}
  ${revs.length?`<div><small style="color:var(--mute)">待審閱</small><div class="rlist">${revs.map(r=>`<button data-rv="${esc(keyOf(p,ex.exhibit,r.id,"review"))}">${esc(r.id)}　${esc(r.title)}</button>`).join("")}</div></div>`:""}
  </div></div>`;
}
function reviewsAll(){return all().flatMap(({p,ex})=>(ex.reviews||[]).filter(r=>!isAns(ex,r)).map(r=>({p,ex,r,k:keyOf(p,ex.exhibit,r.id,"review")})))}
// 一項一審：同工作項目的下一項優先，沒有再跳別的工作項目
const exKey=k=>keyOf(...keyParts(k).slice(0,2));
function nextRv(k){const rs=reviewsAll().filter(x=>x.k!==k);return(rs.find(x=>exKey(x.k)===exKey(k))||rs[0]||{}).k||null}
function stageRvList(){
  const rs=reviewsAll();
  if(!rs.length)return`<div class="ghost l">REVIEW</div>${MOS1}<p class="h-stage">REVIEW　審閱</p><div class="empty">目前沒有待你審閱的項目。工作線送出審閱後會出現在這裡。</div>`;
  const grp=[...new Set(rs.map(x=>exKey(x.k)))];
  return`<div class="ghost l">REVIEW</div><p class="h-stage">REVIEW　審閱（${rs.length}）　一項一審，送出後自動跳下一項</p>${grp.map(g=>{const xs=rs.filter(x=>exKey(x.k)===g);return`<div style="max-width:820px;margin-bottom:14px"><div style="display:flex;gap:10px;align-items:center;margin-bottom:6px"><b>${esc(projectLabel(xs[0].p)+xs[0].ex.exhibit)}</b><small style="color:var(--mute)">${xs.length} 項</small><button class="go ghostb" data-rv="${esc(xs[0].k)}" style="margin-left:auto">從第 1 項開始審</button></div><div class="rlist">${xs.map(x=>`<button data-rv="${esc(x.k)}"><span style="color:var(--cyan);font-family:var(--f-mono)">${esc(x.r.id)}</span>　${esc(x.r.title)}${x.r.pages?`　<small style="color:var(--mute)">${esc(x.r.pages)}</small>`:""}</button>`).join("")}</div></div>`}).join("")}`;
}
function stageRv(){
  const x=reviewsAll().find(x=>x.k===sel);if(!x){view="rvlist";return stageRvList();}
  const {p,ex,r,k}=x,mode=store.get("cmpmode")||"side",draft=store.get("draft_"+k)||"",chosen=store.get("sel_"+k);
  const both=r.before&&r.after;
  const view2=r.page?`<iframe sandbox="allow-scripts" class="frame" src="${pgurl(p,r.page)}" title="${esc(r.title)}"></iframe>`:!both?`<div class="cmp" style="grid-template-columns:1fr"><figure><img src="${img(p,r.after)}" alt="本次"><figcaption>本次</figcaption></figure></div>`
   :mode==="swipe"?`<div class="swipe" id="sw"><img src="${img(p,r.after)}" alt="改後"><div class="top-img" style="width:50%"><img src="${img(p,r.before)}" alt="改前"></div><input type="range" min="0" max="100" value="50" aria-label="改前改後分界"></div>`
   :`<div class="cmp"><figure><img src="${img(p,r.before)}" alt="改前"><figcaption>BEFORE　改前</figcaption></figure><figure><img src="${img(p,r.after)}" alt="改後"><figcaption>AFTER　改後</figcaption></figure></div>`;
  return`<div class="rv${r.page?" haspage":""}" data-k="${esc(k)}" data-p="${esc(p)}" data-ex="${esc(ex.exhibit)}" data-id="${esc(r.id)}" data-kind="review">
   <div class="rv-hd">${(()=>{const xs=reviewsAll().filter(y=>exKey(y.k)===exKey(k)),i=xs.findIndex(y=>y.k===k),pv=xs[i-1],nx=xs[i+1];return`<span class="chip">第 ${i+1}／${xs.length} 項</span>${pv?`<button class="chip" data-rv="${esc(pv.k)}">◂ 上一項</button>`:""}${nx?`<button class="chip" data-rv="${esc(nx.k)}">下一項 ▸</button>`:""}`})()}<span class="id">${esc(r.id)}</span>${projectChip(p)}<span class="chip">${esc(ex.exhibit)}</span>${r.pages?`<span class="chip">${esc(r.pages)}</span>`:""}${r.page?`<button class="chip" data-read="${esc(keyOf(p,r.page))}">單項閱讀</button>`:""}
    ${both&&!r.page?`<div class="mode"><button data-mode="side" class="${mode==="side"?"on":""}">並排</button><button data-mode="swipe" class="${mode==="swipe"?"on":""}">滑桿</button></div>`:""}
    <h2>${esc(r.title)}</h2>${r.note?`<div style="color:var(--mute);font-size:13px">${esc(r.note)}</div>`:""}</div>
   ${view2}
   <div class="verdict"><div class="vbtns"><label><input type="radio" name="v_${esc(k)}" value="通過" ${chosen==="通過"?"checked":""}>✓ 通過</label><label><input type="radio" name="v_${esc(k)}" value="退回" ${chosen==="退回"?"checked":""}>✕ 退回</label></div>
    <textarea class="f" rows="2" id="rvt" placeholder="退回原因或補充">${esc(draft)}</textarea>
    <div class="act"><button class="go" data-send>送出審閱</button><span class="st"></span></div></div></div>`;
}
function pagesAll(){if(!S)return[];return scopedProjects().flatMap(p=>(p.pages||[]).map(g=>({p:p.project_id,ex:"全案",g})).concat(p.exhibits.flatMap(ex=>(ex.pages||[]).map(g=>({p:p.project_id,ex:ex.exhibit,g,arch:ex.archived===true})))))}
const pgurl=(p,path)=>{const [f,h]=path.split("#");return img(p,f)+(h?"#"+h:"")};
function stagePages(){const pa=pagesAll(),ps=pa.filter(x=>!x.arch),qs=pa.filter(x=>x.arch);
  return`<div class="ghost l">PAGES</div>${MOS1}<p class="h-stage">PAGES　審閱網頁</p>${ps.length?`<div class="pglist">${ps.map(x=>`<button data-pg="${esc(keyOf(x.p,x.g.path))}"><span>${esc(x.g.title)}</span><small>${esc(projectLabel(x.p)+x.ex)}　${esc(x.g.path.split("/").pop())}</small></button>`).join("")}</div>`:`<div class="empty">還沒有掛上的審閱網頁。</div>`}${qs.length?`<details style="margin-top:14px"><summary style="cursor:pointer;color:var(--mute);font-size:13px">封存的審閱網頁 ${qs.length}</summary><div class="pglist" style="margin-top:8px">${qs.map(x=>`<button data-pg="${esc(keyOf(x.p,x.g.path))}"><span>${esc(x.g.title)}</span><small>${esc(projectLabel(x.p)+x.ex)}　${esc(x.g.path.split("/").pop())}</small></button>`).join("")}</div></details>`:""}`}
function stagePg(){const [p,path]=keyParts(sel);const x=pagesAll().find(x=>x.p===p&&x.g.path===path);
  if(!x){view="pages";return stagePages();}
  return`<div class="pgv"><div class="pg-hd"><button data-view="pages">◂ 審閱網頁</button><b>${esc(x.g.title)}</b><span class="chip">${esc(x.ex)}</span></div><iframe sandbox="allow-scripts" class="frame" src="${pgurl(p,path)}" title="${esc(x.g.title)}"></iframe></div>`}
function tdRow({p,ex,t,k}){const o=openTd.has(k);
  return`<div class="td s-${esc(t.state||"todo")}"><div class="td-hd" data-tdx="${esc(k)}">
   <select data-td="${esc(k)}" aria-label="${esc(t.id)} 狀態">${Object.entries(ST).map(([v,l])=>`<option value="${v}" ${(t.state||"todo")===v?"selected":""}>${l}</option>`).join("")}</select>
   <b>${esc(t.id)}</b><span class="at">${esc(t.at||"")}</span><span class="sum">${esc((t.todo||[])[0]||t.quote)}</span>${t.ask?'<span class="ask">要問中鼎</span>':"<span></span>"}</div>
   ${o?`<div class="td-bd"><div><blockquote>${esc(t.quote)}<small>${esc(t.src)}${t.origin?"　"+esc(t.origin):""}</small></blockquote>
    ${t.meet?`<blockquote style="border-left-color:var(--dim)">${esc(t.meet)}</blockquote>`:""}
    ${t.decided?`<div class="dec">你的裁決：${esc(t.decided)}</div>`:""}
    ${(t.todo||[]).length?`<ul>${t.todo.map(x=>`<li>${esc(x)}</li>`).join("")}</ul>`:""}
    ${t.ask?`<div class="q">要問中鼎：${esc(t.ask)}</div>`:""}${t.note?`<div class="dec" style="border-left-color:var(--gold);background:rgba(211,162,63,.15)">工作線備註：${esc(t.note)}</div>`:""}</div>
    <div class="th">${(t.imgs||[]).concat(t.photos||[]).map(f=>`<img src="${img(p,f)}" alt="" loading="lazy">`).join("")}</div>
    <div class="td-say" data-k="${esc(k)}" data-p="${esc(p)}" data-ex="${esc(ex.exhibit)}" data-id="${esc(t.id)}" data-kind="note">
     ${(ex.answers||[]).filter(a=>a.kind==="note"&&a.id===t.id).map(a=>`<div class="sent1"><b>已送指示 ${esc(a.at.slice(5,16).replace("T"," "))}</b>　${esc(a.text)}${"（"+esc(deliveryText(a.delivery))+"）"}</div>`).join("")}
     <textarea class="f" placeholder="對 ${esc(t.id)} 下指示，送進負責的工作線">${esc(store.get("draft_"+k)||"")}</textarea>
     <button class="go" data-send>送出</button><span class="st"></span></div></div>`:""}</div>`}
function tdFilt(t){return tdFilter==="all"||(tdFilter==="open"&&["todo","doing","wait"].includes(t.state||"todo"))||(tdFilter==="sub"&&t.state==="submitted")||(tdFilter==="ask"&&t.ask&&t.state!=="done")||(tdFilter==="done"&&t.state==="done")}
function stageTodos(){const all2=todosAll(),n=f=>all2.filter(x=>{const o=tdFilter;tdFilter=f;const r=tdFilt(x.t);tdFilter=o;return r}).length;
  const groups=new Map();all2.filter(x=>tdFilt(x.t)).forEach(x=>{const g=keyOf(x.p,x.ex.exhibit);if(!groups.has(g))groups.set(g,[]);groups.get(g).push(x)});
  return`<div class="ghost r">TASKS</div><p class="h-stage">TASKS　各工作項目待辦（點列展開、左邊改狀態；已提交＝工作線做完，已完成＝你驗收通過）</p>
  <div class="tdbar">${[["open","未完成"],["sub","待你驗收"],["ask","要問中鼎"],["done","已完成"],["all","全部"]].map(([f,l])=>`<button data-tdf="${f}" class="${tdFilter===f?"on":""}">${l} ${n(f)}</button>`).join("")}</div>
  ${groups.size?[...groups].map(([g,xs])=>{const ex=xs[0].ex,ts=ex.todos||[];return`<div class="tdg"><h4>${esc(projectLabel(xs[0].p)+(ex.exhibit==="_全案"?"全案共通":ex.exhibit))}<small>已完成 ${ts.filter(t=>t.state==="done").length}・已提交 ${ts.filter(t=>t.state==="submitted").length}／共 ${ts.length}</small></h4>${xs.map(tdRow).join("")}</div>`}).join(""):`<div class="empty">這個篩選沒有項目。</div>`}`}
function stageSent(){
  const rows=all().flatMap(({p,ex})=>(ex.answers||[]).map(a=>({p,ex,a,open:(ex.decisions||[]).concat(ex.reviews||[]).some(d=>d.id===a.id&&itemKind(ex,d)===a.kind)}))).sort((x,y)=>y.a.at.localeCompare(x.a.at));
  return`<div class="ghost l">SENT</div><p class="h-stage">SENT　已送出的回覆</p>${rows.length?`<div class="sent">${rows.map(({p,ex,a,open})=>{const d=a.delivery;
    return`<div class="row"><div class="hd"><span style="color:var(--cyan);font-family:var(--f-mono)">${esc(a.id)}</span><span>${esc(projectLabel(p)+ex.exhibit)}</span><span>${esc(a.at.slice(5,16).replace("T"," "))}</span><span class="chip ${open?"":"ok"}">${a.kind==="note"?"指示":open?"等待工作線處理":"已處理"}</span></div>
     <div>${esc(a.choice||"")}${a.text?(a.choice?"；":"")+esc(a.text):""}</div>
     <div class="act">${deliveryMarkup(d,p,ex.exhibit,a.uid)}</div></div>`}).join("")}</div>`:`<div class="empty">還沒有送出過回覆。</div>`}`;
}
function renderStage(force){
  if(!force&&view==="rv"&&$("#stage .rv"))return; // 審閱中不重畫，避免洗掉輸入
  if(!force&&document.activeElement&&document.activeElement.closest("#stage textarea"))return; // 打字中不重畫
  const html=view==="ex"?stageEx():view==="rv"?stageRv():view==="rvlist"?stageRvList():view==="sent"?stageSent():view==="pages"?stagePages():view==="todos"?stageTodos():view==="pg"?stagePg():view==="ref"?stageRef():stageOv();
  $("#stage").classList.toggle("full",["pg","ref"].includes(view)||(view==="rv"&&/haspage/.test(html)));
  if(html!==stageSig){$("#stage").innerHTML=html;stageSig=html;bindSwipe();}
}
function bindSwipe(){const sw=$("#sw");if(!sw)return;const top=sw.querySelector(".top-img"),ti=top.querySelector("img"),r=sw.querySelector("input");
  const fit=()=>{ti.style.height=sw.querySelector(":scope>img").offsetHeight+"px";ti.style.width=sw.offsetWidth+"px"};
  sw.querySelector(":scope>img").addEventListener("load",fit);fit();window.addEventListener("resize",fit);
  r.addEventListener("input",()=>top.style.width=r.value+"%");}
// 待決與審閱同一項時，在待決卡片上提示先看審閱頁（以頁碼／來信編號或同一審閱網頁比對）
const itemKeys=s=>((s||"").match(/[Pp]\d{2,3}|信-\d+/g)||[]).map(x=>x.toUpperCase());
function relRv(p,ex,d){const dk=itemKeys(d.id),ref=d.ref||"",rs=(ex.reviews||[]).filter(r=>!isAns(ex,r));
  const byKey=rs.filter(r=>itemKeys(r.id).some(k=>dk.includes(k)));if(byKey.length)return byKey;
  // 沒有共同編號時才比網頁：兩邊都有錨點就要錨點相同，否則比到檔名
  return ref?rs.filter(r=>{const pg=r.page||"";if(!pg)return false;return pg.includes("#")&&ref.includes("#")?pg===ref:pg.split("#")[0]===ref.split("#")[0];}):[];}
function decisionRef(project,reference){
  if(!reference)return"";
  if(/\.html?(?:#.*)?$/i.test(reference))return`<button class="relrv" data-read="${esc(keyOf(project,reference))}">閱讀參考頁</button>`;
  if(/\.(?:png|jpe?g|gif|webp|svg|avif|bmp)(?:[?#].*)?$/i.test(reference))return`<img class="ref" src="${img(project,reference)}" alt="">`;
  return`<div class="ref-text">參考：${esc(reference)}</div>`;
}
function renderCards(){
  const scope=view==="ex"?sel:view==="rv"?exKey(sel):""; // 看單一工作項目時只列該工作項目的題
  const items=all().filter(({p,ex})=>!scope||keyOf(p,ex.exhibit)===scope).flatMap(({p,ex})=>(ex.decisions||[]).filter(d=>!isAns(ex,d)).map(d=>({p,ex,d,k:keyOf(p,ex.exhibit,d.id,"decision")})));
  $("#deck-n").textContent=`${scope?keyParts(scope)[1]+"　":""}${items.length} 題　選好按送出，直接送進負責的工作線`;
  const box=$("#cards"),want=new Set(items.map(x=>x.k));
  [...box.children].forEach(el=>{if(!want.has(el.dataset.k))el.remove()});
  items.forEach((x,i)=>{if(box.querySelector(`[data-k="${CSS.escape(x.k)}"]`))return;const {p,ex,d,k}=x,s=store.get("sel_"+k);
    box.insertAdjacentHTML("beforeend",`<div class="card" data-k="${esc(k)}" data-p="${esc(p)}" data-ex="${esc(ex.exhibit)}" data-id="${esc(d.id)}" data-kind="decision">
     <div class="ch" style="background:${HEAD[i%HEAD.length]}"><span>${esc(projectLabel(p)+ex.exhibit)}</span><b>${esc(d.id)}</b></div>
     <div class="cb">${relRv(p,ex,d).map(r=>`<button class="relrv" data-rv="${esc(keyOf(p,ex.exhibit,r.id,"review"))}">審閱頁已有修改：${esc(r.title||r.id)} ▸ 先看</button>`).join("")}<div class="q">${esc(d.q)}</div>${decisionRef(p,d.ref)}
      ${(d.options||[]).map((o,j)=>/^其它/.test(o)?"":`<label class="opt"><input type="radio" name="d_${esc(k)}" value="${esc(o)}" ${(s!==null?s===o:j===d.rec)?"checked":""}><span>${esc(o)}${j===d.rec?'<span class="rec">建議</span>':""}</span></label>`).join("")}
      <label class="opt"><input type="radio" name="d_${esc(k)}" value="其它" ${s==="其它"?"checked":""}><span>其它（寫在下方補充）</span></label>
      <textarea class="f" placeholder="補充（可留空）">${esc(store.get("draft_"+k)||"")}</textarea>
      <div class="act"><button class="go" data-send>送出</button><span class="st"></span></div></div></div>`);});
  if(!items.length)box.innerHTML=`<div class="empty">${scope?"這個工作項目沒有待你決定的事。":"目前沒有待你決定的事。"}</div>`;
  if(items.length)box.querySelector(".empty")?.remove();
}
function deckState(){const pref=store.get("deck_"+(view==="rv"?"rv":"main"));const none=!$("#cards .card");const min=none?true:pref?pref==="min":view==="rv";$(".deck").classList.toggle("min",min);$("#deck-tg").textContent=min?"展開 ▲":"收起 ▼";}
function render(force){if(!S)return;$("#qb").hidden=view!=="ov";$("#stage").classList.toggle("has-qb",view==="ov");renderProjectControls();renderTop();renderList();syncSayDraft();renderStage(force);renderCards();deckState();}
async function tick(){
  const status=$("#srv");let next;
  try{next=await requestJson("/api/state",{cache:"no-store"});if(!Array.isArray(next.projects)||typeof next.now!=="string")throw new Error("狀態資料格式無效")}
  catch(error){softwareError="指揮中心無法讀取狀態，請確認服務連線";status.className="srv off";status.querySelector("span").textContent="狀態讀取失敗";renderSoftwareStatus();return}
  S=next;softwareError="";
  try{reconcileProject();migrateLegacy();migrateLegacyView();render();status.className="srv";status.querySelector("span").textContent="服務正常 "+S.now.slice(11,16)}
  catch(error){softwareError="指揮中心畫面更新失敗，請重新整理";status.className="srv off";status.querySelector("span").textContent="畫面更新失敗";renderSoftwareStatus()}
}
