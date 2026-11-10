// 專案選擇、明確註冊與經驗證的收件工作線。
let dialogVersion=0;
function renderProjectControls(){
  const control=$("#project-select"),signature=JSON.stringify(S.projects.map(p=>[p.project_id,p.name]));
  if(control.dataset.signature!==signature){control.innerHTML=`<option value="*">全部專案</option>`+S.projects.map(p=>`<option value="${esc(p.project_id)}">${esc(p.name)}</option>`).join("");control.dataset.signature=signature}
  control.value=activeProject;
  $("#srv").title=S.delivery_mode==="disabled"?"候選模式：回覆只記錄，不傳送":"";
  let banner=$("#candidate-mode");
  if(S.delivery_mode==="disabled"&&!banner){banner=document.createElement("span");banner.id="candidate-mode";banner.className="candidate-mode";$("#say").prepend(banner)}
  if(banner){banner.hidden=S.delivery_mode!=="disabled";banner.textContent="候選模式：回覆只記錄，不傳送"}
}
function openDialog(title,html){
  dialogVersion++;
  $("#dialog-title").textContent=title;$("#dialog-body").innerHTML=html;
  if(!$("#hub-dialog").open)$("#hub-dialog").showModal();
}
function dialogError(error){const status=$("#dialog-status");if(status){status.className="st bad";status.textContent=error.message}}
async function addProjectDialog(){
  openDialog("新增專案",'<p role="status">讀取已註冊的專案候選…</p>');const version=dialogVersion;
  try{
    const data=await requestJson("/api/projects/catalog",{cache:"no-store"});
    if(!$("#hub-dialog").open||version!==dialogVersion)return;
    const candidates=data.candidates||[];
    $("#dialog-body").innerHTML=`<p>選一個專案加入此指揮中心；只讀取你選定的專案。</p><form id="register-form"><div class="candidate-list">${candidates.map(candidate=>candidateRow(candidate)).join("")||'<p class="empty">沒有可加入的專案。</p>'}</div><p class="st" id="dialog-status" role="status"></p><button class="go" type="submit" ${candidates.some(c=>c.can_enable&&!c.enabled)?"":"disabled"}>加入選定專案</button></form>`;
    $("#register-form").addEventListener("submit",registerProject);
  }catch(error){if(version===dialogVersion)$("#dialog-body").textContent="讀取失敗："+error.message}
}
function candidateRow(candidate){
  const is_disabled=candidate.enabled||!candidate.can_enable;
  return`<label class="candidate ${is_disabled?"unavailable":""}"><input type="radio" name="candidate" value="${esc(candidate.candidate_id)}" ${is_disabled?"disabled":""}><span><b>${esc(candidate.name)}</b><small>${esc(candidate.root)}</small><small>${esc(candidate.enabled?"已加入":candidate.reason||"可加入")}</small></span></label>`;
}
async function registerProject(event){
  event.preventDefault();const form=event.currentTarget,choice=form.querySelector('input[name="candidate"]:checked');
  if(!choice){dialogError(new Error("先選擇要加入的專案"));return}
  const button=form.querySelector("button[type=submit]");button.disabled=true;
  try{const result=await post("/api/projects/register",{candidate_id:choice.value});await tick();$("#hub-dialog").close();switchProject(result.project.project_id)}
  catch(error){dialogError(error);button.disabled=false}
}
async function bindLineDialog(project,exhibit){
  openDialog("重新連結工作線",`<p>${esc(projectName(project))}｜${esc(exhibit)}</p><p role="status">讀取可連結的對話…</p>`);const version=dialogVersion;
  try{
    const data=await requestJson("/api/targets?project_id="+encodeURIComponent(project),{cache:"no-store"});
    if(!$("#hub-dialog").open||version!==dialogVersion)return;
    $("#dialog-body").innerHTML=`<p>${esc(projectName(project))}｜${esc(exhibit)}</p><p>選擇經驗證的收件對話。重新連結後，先前回覆不會自動重送。</p><form id="bind-form"><div class="candidate-list">${(data.targets||[]).map(target=>targetRow(target)).join("")||'<p class="empty">目前沒有可驗證的工作線，請先開啟負責的對話。</p>'}</div>${(data.diagnostics||[]).map(note=>`<p class="st">${esc(typeof note==="string"?note:note.message||note.reason||JSON.stringify(note))}</p>`).join("")}<p class="st" id="dialog-status" role="status"></p><button class="go" type="submit" ${(data.targets||[]).some(t=>t.can_bind)?"":"disabled"}>連結選定工作線</button></form>`;
    $("#bind-form").addEventListener("submit",event=>bindLine(event,project,exhibit));
  }catch(error){if(version===dialogVersion)$("#dialog-body").textContent="讀取失敗："+error.message}
}
function targetRow(target){
  const identity=[["對話",target.session_id],["分頁",target.surface_id],["工作區",target.workspace_id]].filter(([,value])=>value).map(([label,value])=>label+" …"+String(value).slice(-8)).join(" · ");
  return`<label class="candidate ${target.can_bind?"":"unavailable"}"><input type="radio" name="target" value="${esc(target.target_id)}" ${target.can_bind?"":"disabled"}><span><b>${esc(target.name||target.line_id)}</b><small>${esc(target.provider||"")}${identity?" · "+esc(identity):""}</small><small>${esc(target.reason||(target.can_bind?"已驗證，可連結":"收件對話尚未驗證"))}</small></span></label>`;
}
async function bindLine(event,project,exhibit){
  event.preventDefault();const form=event.currentTarget,choice=form.querySelector('input[name="target"]:checked');
  if(!choice){dialogError(new Error("先選擇可連結的工作線"));return}
  const button=form.querySelector("button[type=submit]");button.disabled=true;
  try{await post("/api/bind",{project_id:project,exhibit,target_id:choice.value});$("#dialog-status").className="st ok";$("#dialog-status").textContent="已重新連結。先前回覆未重送。";await tick()}
  catch(error){dialogError(error);button.disabled=false}
}
function stageRef(){
  const [project,path]=keyParts(sel);
  if(!scopedProjects().some(p=>p.project_id===project)){view="ov";return stageOv()}
  return`<div class="pgv"><div class="pg-hd"><button data-view="ov">◂ 總覽</button><b>${esc(projectName(project))}｜單項閱讀</b></div><iframe sandbox="allow-scripts" class="frame" src="${pgurl(project,path)}" title="單項閱讀"></iframe></div>`;
}
$("#project-select").addEventListener("change",event=>switchProject(event.target.value));
$("#project-add").addEventListener("click",addProjectDialog);
$("#dialog-close").addEventListener("click",()=>$("#hub-dialog").close());
$("#say-bind").addEventListener("click",()=>{const item=exOf(sel);if(item)bindLineDialog(item.p,item.ex.exhibit)});

$("#hub-dialog").addEventListener("close",()=>dialogVersion++);
