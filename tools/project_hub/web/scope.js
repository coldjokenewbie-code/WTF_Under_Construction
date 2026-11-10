// 穩定識別與本機檢視狀態；項目草稿跨單案／全部檢視共用。
const rawStore={get(k){try{return localStorage.getItem(k)}catch{return null}},set(k,v){try{localStorage.setItem(k,v)}catch{}}};
let activeProject=rawStore.get("project_hub:v2:project")||"";
const keyOf=(...parts)=>parts.map(x=>encodeURIComponent(String(x??""))).join("|");
const keyParts=k=>String(k||"").split("|").map(x=>decodeURIComponent(x));
const storeKey=k=>"project_hub:v2:"+(/^(draft_|sel_)/.test(k)?"item":activeProject||"*")+":"+k;
const store={get(k){return rawStore.get(storeKey(k))},set(k,v){rawStore.set(storeKey(k),v)}};
const scopedProjects=()=>S?S.projects.filter(p=>activeProject==="*"||p.project_id===activeProject):[];
const projectName=id=>{const project=S?.projects.find(p=>p.project_id===id);return project?project.name+(S.projects.filter(p=>p.name===project.name).length>1?"（"+id+"）":""):id};
const projectLabel=id=>activeProject==="*"?projectName(id)+"｜":"";
const projectChip=id=>activeProject==="*"?`<span class="chip project-chip">${esc(projectName(id))}</span>`:"";
function deadlineProject(){
  const projects=scopedProjects().filter(p=>p.deadline&&Number.isFinite(new Date(p.deadline).getTime()));
  return projects.sort((a,b)=>new Date(a.deadline)-new Date(b.deadline))[0]||null;
}
function rememberView(){store.set("view",view);store.set("sel",sel);store.set("tdf",tdFilter);saveSayDraft()}
function restoreView(){
  view=store.get("view")||"ov";sel=store.get("sel")||"";tdFilter=store.get("tdf")||"open";
  stageSig="";openTd.clear();document.querySelector("#say-st").textContent="";
  document.querySelector("#say-t").dataset.key="";document.querySelector("#say-t").value="";
}
function switchProject(id){
  if(id!=="*"&&!S.projects.some(p=>p.project_id===id))return;
  rememberView();activeProject=id;rawStore.set("project_hub:v2:project",id);restoreView();render(true);
  document.dispatchEvent(new CustomEvent("projectchange"));
}
function reconcileProject(){
  if(activeProject==="*"||S.projects.some(p=>p.project_id===activeProject))return;
  const hadSelection=!!activeProject;activeProject=hadSelection?"*":S.projects[0]?.project_id||"*";
  rawStore.set("project_hub:v2:project",activeProject);restoreView();migrateLegacy();document.dispatchEvent(new CustomEvent("projectchange"));
  if(hadSelection)document.querySelector("#say-st").textContent="原專案目前未啟用，已切換全部專案。";
}
function saveSayDraft(){
  const box=document.querySelector("#say-t");if(box?.dataset.key)store.set("draft_note_"+box.dataset.key,box.value);
}
function syncSayDraft(){
  const box=document.querySelector("#say-t"),item=exOf(sel),key=item?keyOf(item.p,item.ex.exhibit):"";
  if(box.dataset.key!==key){saveSayDraft();box.dataset.key=key;box.value=key?store.get("draft_note_"+key)||"":""}
  box.disabled=!item;document.querySelector("#say button[type=submit]").disabled=!item;
  document.querySelector("#say-bind").disabled=!item;
}
function migrateLegacy(){
  for(const project of S.projects){
    if(rawStore.get("project_hub:v2:migrated:"+project.project_id))continue;
    if(S.projects.filter(p=>p.name===project.name).length!==1)continue;
    for(const exhibit of project.exhibits){
      const groups=[["decision",exhibit.decisions||[]],["review",exhibit.reviews||[]],["note",exhibit.todos||[]]];
      for(const [kind,items] of groups)for(const item of items){
        if(groups.flatMap(([,rows])=>rows).filter(row=>row.id===item.id).length!==1)continue;
        const old=[project.name,exhibit.exhibit,item.id].join("|"),key=keyOf(project.project_id,exhibit.exhibit,item.id,kind);
        for(const prefix of ["draft_","sel_"]){const value=rawStore.get(prefix+old);if(value!==null&&store.get(prefix+key)===null)store.set(prefix+key,value)}
      }
    }
    rawStore.set("project_hub:v2:migrated:"+project.project_id,"1");
  }
}
function migrateLegacyView(){
  if(rawStore.get("project_hub:v2:legacy-view")||!S.projects.length)return;
  rawStore.set("project_hub:v2:legacy-view","1");if(store.get("view"))return;
  const oldView=rawStore.get("view"),oldSelection=rawStore.get("sel");
  if(!["ov","todos","rvlist","pages","sent","ex","rv","pg"].includes(oldView))return;
  const matches=[];
  for(const project of scopedProjects()){
    if(S.projects.filter(p=>p.name===project.name).length!==1)continue;
    for(const exhibit of project.exhibits){
      if(oldView==="ex"&&oldSelection===project.name+"|"+exhibit.exhibit)matches.push(keyOf(project.project_id,exhibit.exhibit));
      if(oldView==="rv")for(const review of exhibit.reviews||[])if(oldSelection===project.name+"|"+exhibit.exhibit+"|"+review.id)matches.push(keyOf(project.project_id,exhibit.exhibit,review.id,"review"));
    }
    if(oldView==="pg")for(const page of (project.pages||[]).concat(project.exhibits.flatMap(ex=>ex.pages||[])))if(oldSelection===project.name+"|"+page.path)matches.push(keyOf(project.project_id,page.path));
  }
  if(["ex","rv","pg"].includes(oldView)&&matches.length!==1)return;
  view=oldView;sel=matches[0]||"";store.set("view",view);store.set("sel",sel);
}
const deliveryState=d=>d?.state||(d?.ok?"legacy_delivered":d?.retrying?"queued":d?"failed":"sending");
function deliveryText(d){
  const labels={retargeted:"已改投目前工作線（另筆紀錄）",queued:"已排隊，尚未確認送達",delivered:"已送達，尚未確認已讀",read:"已讀",failed:"未送達",uncertain:"送達結果不明，請先確認",awaiting_binding:"等待重新連結工作線",disabled:"候選模式：已記錄，未傳送",sending:"傳送中",gave_up:"未送達，已停止重送",legacy_delivered:"已送進對話（舊版記錄，未確認已讀）"};
  const state=deliveryState(d);return(labels[state]||"傳送狀態未知")+(d?.err?"："+d.err:"");
}
const deliveryClass=d=>["read","delivered","legacy_delivered"].includes(deliveryState(d))?"ok":["failed","uncertain","gave_up","awaiting_binding"].includes(deliveryState(d))?"bad":"";
function deliveryMarkup(d,p,ex,uid){
  const state=deliveryState(d),retry=state==="failed"&&S.delivery_mode!=="disabled";
  const binding=["awaiting_binding","uncertain","failed","gave_up"].includes(state);
  const can_rebind=state==="awaiting_binding"&&d?.can_rebind&&S.delivery_mode!=="disabled";
  return`<span class="st ${deliveryClass(d)}">${esc(deliveryText(d))}</span>${retry?`<button class="go ghostb" data-resend="${esc(uid)}" data-p="${esc(p)}" data-ex="${esc(ex)}">重新投遞</button>`:""}${can_rebind?`<button class="go ghostb" data-resend="${esc(uid)}" data-rebind="true" data-p="${esc(p)}" data-ex="${esc(ex)}">投遞到目前工作線</button>`:""}${binding?`<button class="go ghostb" data-bind="${esc(keyOf(p,ex))}">重新連結工作線</button>`:""}`;
}
