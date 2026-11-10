function actionError(error,control){
  const status=control?.closest(".act,.row,.td")?.querySelector(".st")||$("#say-st");status.className="st bad";status.textContent=error.message;
}
async function changeTodo(event){
  const control=event.target.closest("select[data-td]");if(!control)return;
  const [project,exhibit,id]=keyParts(control.dataset.td);control.disabled=true;
  try{await post("/api/todo",{project_id:project,exhibit,id,state:control.value});await tick();renderStage(true)}
  catch(error){control.disabled=false;actionError(error,control)}
}
function rememberInput(event){
  if(event.target.id==="say-t"){saveSayDraft();return}
  const item=event.target.closest("[data-k]");if(!item)return;
  if(event.target.tagName==="TEXTAREA")store.set("draft_"+item.dataset.k,event.target.value);
  if(event.target.type==="radio")store.set("sel_"+item.dataset.k,event.target.value);
}
async function sendItem(button){
  const item=button.closest("[data-k]"),status=item.querySelector(".st"),radio=item.querySelector("input[type=radio]:checked"),text=item.querySelector("textarea").value;
  if(item.dataset.kind==="review"&&!radio){status.className="st bad";status.textContent="請選通過或退回";return}
  if(radio?.value==="其它"&&!text.trim()){status.className="st bad";status.textContent="選「其它」請在補充寫你的決定";item.querySelector("textarea").focus();return}
  if(item.dataset.kind==="review"&&radio.value==="退回"&&!text.trim()){status.className="st bad";status.textContent="退回請寫原因";return}
  if(item.dataset.kind==="note"&&!text.trim()){status.className="st bad";status.textContent="請輸入指示";return}
  const originProject=activeProject,originView=view,originSelection=sel;
  button.disabled=true;status.className="st";status.textContent="送出中…";
  try{
    const result=await post("/api/answer",{project_id:item.dataset.p,exhibit:item.dataset.ex,id:item.dataset.id,kind:item.dataset.kind,choice:radio?radio.value:"",text});
    status.className="st "+deliveryClass(result.delivery);status.textContent=deliveryText(result.delivery);store.set("draft_"+item.dataset.k,"");
    if(item.dataset.kind==="note"){item.querySelector("textarea").value="";button.disabled=false}
    setTimeout(async()=>{await tick();if(item.dataset.kind==="review"&&activeProject===originProject&&view===originView&&sel===originSelection){const next=nextRv(item.dataset.k);next?setView("rv",next):setView("rvlist")}},900);
  }catch(error){button.disabled=false;status.className="st bad";status.textContent="送出失敗："+error.message}
}
async function resendItem(button){
  button.disabled=true;
  try{const result=await post("/api/resend",{project_id:button.dataset.p,exhibit:button.dataset.ex,uid:button.dataset.resend,...(button.dataset.rebind==="true"?{rebind:true}:{})});const status=button.closest(".act").querySelector(".st");status.className="st "+deliveryClass(result.delivery);status.textContent=deliveryText(result.delivery);await tick()}
  catch(error){button.disabled=false;actionError(error,button)}
}
async function openFile(button){
  if(/\.html?(#|$)/i.test(button.dataset.open)){setView("ref",keyOf(button.dataset.p,button.dataset.open));return}
  try{await post("/api/open",{project_id:button.dataset.p,path:button.dataset.open})}catch(error){actionError(error,button)}
}
function handleClick(event){
  const target=event.target;
  if(target.closest("[data-arch]")){store.set("archOpen",store.get("archOpen")==="1"?"0":"1");renderList();return}
  if(target.closest("[data-fin]")){store.set("finOpen",store.get("finOpen")==="1"?"0":"1");renderList();return}
  const bind=target.closest("[data-bind]");if(bind){bindLineDialog(...keyParts(bind.dataset.bind));return}
  const read=target.closest("[data-read]");if(read){setView("ref",read.dataset.read);return}
  const tab=target.closest("[data-view]");if(tab){setView(tab.dataset.view);return}
  const exhibit=target.closest("[data-ex]:not(.card):not(.rv)");if(exhibit&&(exhibit.classList.contains("ex")||exhibit.classList.contains("bar"))){setView("ex",exhibit.dataset.ex);return}
  if(target.closest("select[data-td]"))return;
  const filter=target.closest("[data-tdf]");if(filter){tdFilter=filter.dataset.tdf;store.set("tdf",tdFilter);renderStage(true);return}
  const todo=target.closest("[data-tdx]");if(todo){const key=todo.dataset.tdx;openTd.has(key)?openTd.delete(key):openTd.add(key);renderStage(true);return}
  const page=target.closest("[data-pg]");if(page){setView("pg",page.dataset.pg);return}
  const review=target.closest("[data-rv]");if(review){setView("rv",review.dataset.rv);return}
  const mode=target.closest("[data-mode]");if(mode){store.set("cmpmode",mode.dataset.mode);renderStage(true);return}
  const send=target.closest("[data-send]");if(send){sendItem(send);return}
  const resend=target.closest("[data-resend]");if(resend){resendItem(resend);return}
  const file=target.closest("[data-open]");if(file){openFile(file);return}
  const image=target.closest(".cmp img,.card img.ref,.td-bd .th img");if(image){const box=$("#lb");box.querySelector("img").src=image.src;box.classList.remove("big");box.style.display="flex";return}
  if(target===$("#lb img")){$("#lb").classList.toggle("big");return}
  if(target.closest("#lb")){$("#lb").style.display="none";return}
  if(target.id==="refresh")tick();
}
function keyboardSend(event){
  if(event.key!=="Enter"||!(event.metaKey||event.ctrlKey)||event.isComposing||event.target.tagName!=="TEXTAREA")return;
  event.preventDefault();const form=event.target.closest("form");if(form){form.requestSubmit();return}
  let element=event.target.parentElement;while(element&&!element.querySelector("[data-send]"))element=element.parentElement;
  const button=element?.querySelector("[data-send]");if(button&&!button.disabled)button.click();
}
async function sendInstruction(event){
  event.preventDefault();const item=exOf(sel),status=$("#say-st"),box=$("#say-t"),text=box.value.trim();
  if(!item){status.className="st bad";status.textContent="先在上方點選要下指示的工作項目";return}
  if(!text){status.className="st bad";status.textContent="請輸入指示";return}
  const originProject=activeProject,key=box.dataset.key,button=$("#say button[type=submit]");
  button.disabled=true;status.className="st";status.textContent="送出中…";
  try{
    const result=await post("/api/answer",{project_id:item.p,exhibit:item.ex.exhibit,id:"指示-"+Date.now(),kind:"note",choice:"",text});
    store.set("draft_note_"+key,"");
    if(activeProject===originProject&&box.dataset.key===key){status.className="st "+deliveryClass(result.delivery);status.textContent=deliveryText(result.delivery);box.value=""}
    await tick();
  }catch(error){if(activeProject===originProject&&box.dataset.key===key){status.className="st bad";status.textContent="送出失敗："+error.message}}
  finally{button.disabled=!exOf(sel)}
}
document.addEventListener("change",changeTodo);
document.addEventListener("input",rememberInput);
document.addEventListener("change",event=>{if(event.target.type==="radio")rememberInput(event)});
document.addEventListener("click",handleClick);
$("#deck-hd").addEventListener("click",()=>{const key="deck_"+(view==="rv"?"rv":"main");store.set(key,$(".deck").classList.contains("min")?"open":"min");deckState()});
document.addEventListener("keydown",event=>{if(event.key==="Escape")$("#lb").style.display="none";if(event.key==="Enter"&&event.target.classList.contains("ex"))event.target.click()});
document.addEventListener("keydown",keyboardSend);
$("#say").addEventListener("submit",sendInstruction);
tick();setInterval(tick,5000);
