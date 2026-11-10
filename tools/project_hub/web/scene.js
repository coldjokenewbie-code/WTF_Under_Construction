/*SCENE-JS-START*/
// 工作室場景：各工作線對話的健康看板。資料來自 /api/lines（每 15 秒），放在舞台外，不隨 renderStage 重畫。?scene=demo 才用假資料。
// 2:1 等角小房間：每個專案一張長桌，同專案的線圍坐桌邊、朝桌心（所以有背對、側面、斜側面）；總控坐自己專案的桌頭。
// 正常＝圍坐工作、輪流起身沿地板格走動再回座；需要壓縮＝趴在桌上；需要重啟＝倒在座位旁地板。
(function(){
const box=document.getElementById("scene"),qb=document.getElementById("qb");if(!box)return;
const cv=box.querySelector("canvas"),ctx=cv.getContext("2d"),layer=box.querySelector(".sc-layer"),tip=box.querySelector(".sc-tip"),msg=box.querySelector(".sc-msg"),lg=box.querySelector(".sc-lg");
const Q=new URLSearchParams(location.search),DEMO=Q.get("scene")==="demo",MAX=14,POLL=15000,STEP=125,SPEED=.0015;
const calm=window.matchMedia("(prefers-reduced-motion: reduce)");
const WORD={normal:"正常",tired:"需要壓縮",down:"需要重啟"},SW={busy:"忙碌中",idle:"閒置",shell:"閒置"};
let rawLines=null,lines=null,failed=false,hidden=0,L=null,bg=null,glow=null,frame=0,last=0,lastTs=0,raf=0,lastPull=0,pulling=false,sig="",pinned=null,hoverNm=null,listChars=[],nextPick=600;

/* ── 外型：由名稱雜湊決定，重新整理不變 ── */
function hash(s){let h=2166136261;for(const ch of s){h^=ch.codePointAt(0);h=Math.imul(h,16777619)}h^=h>>>16;h=Math.imul(h,0x85ebca6b);h^=h>>>13;h=Math.imul(h,0xc2b2ae35);h^=h>>>16;return h>>>0}
function mix(a,b,k){const f=x=>[parseInt(x.slice(1,3),16),parseInt(x.slice(3,5),16),parseInt(x.slice(5,7),16)],A=f(a),B=f(b);return"#"+A.map((v,i)=>Math.round(v+(B[i]-v)*k).toString(16).padStart(2,"0")).join("")}
const dark=(c,k=.3)=>mix(c,"#0a1116",k),lite=(c,k=.28)=>mix(c,"#fff4d8",k);
const SKINS=["#f2c9a2","#e6b288","#f7dcc0"],HAIRS=["#23262e","#3d2b20","#6a3a24","#1f3e58","#70707a","#2e4f3f","#74395a","#a87a3a"],CLOTHS=["#3f8f86","#c7622f","#6fa9b8","#a8445f","#2e5c86","#7b6aa6","#5f9a6e","#b7b09c","#c0516a","#4a7f9c"];
function lookOf(name,master){const h=hash(name),l={id:name,master,hair:h%8,hc:HAIRS[(h>>>3)%8],skin:SKINS[(h>>>6)%3],cloth:CLOTHS[(h>>>9)%10],top:(h>>>13)%4,acc:(h>>>16)%4,shift:(h>>>19)%64,side:(h>>>25)&1?1:-1,bev:(h>>>26)%3};
  if(master){l.hair=0;l.hc="#23262e";l.cloth="#d9cfb4";l.top=9;l.acc=1;}return l}

/* ── 像素精靈：畫好後補外框並快取；左右向由右向鏡射 ── */
const sprites=new Map();
function outlineC(g,SW,SH){const im=g.getImageData(0,0,SW,SH),d=im.data,o=new Uint8ClampedArray(d);
  for(let y=0;y<SH;y++)for(let x=0;x<SW;x++){const i=(y*SW+x)*4;if(d[i+3])continue;
    if((x>0&&d[i-1])||(x<SW-1&&d[i+7])||(y>0&&d[i-SW*4+3])||(y<SH-1&&d[i+SW*4+3])){o[i]=10;o[i+1]=17;o[i+2]=22;o[i+3]=255}}
  im.data.set(o);g.putImageData(im,0,0)}
function mk(key,w,h,ox,oy,draw){let c=sprites.get(key);if(c)return c;c=document.createElement("canvas");c.width=w;c.height=h;const g=c.getContext("2d",{willReadFrequently:true});
  draw((x,y,ww,hh,col)=>{g.fillStyle=col;g.fillRect(ox+x,oy+y,ww,hh)});outlineC(g,w,h);sprites.set(key,c);return c}
function flipped(key,src){const k=key+"|m";let c=sprites.get(k);if(c)return c;c=document.createElement("canvas");c.width=src.width;c.height=src.height;const g=c.getContext("2d");g.translate(src.width,0);g.scale(-1,1);g.drawImage(src,0,0);sprites.set(k,c);return c}
function limb(P,x0,y0,x1,y1,col){const n=Math.max(Math.abs(x1-x0),Math.abs(y1-y0),1);for(let i=0;i<=n;i++)P(Math.round(x0+(x1-x0)*i/n),Math.round(y0+(y1-y0)*i/n),1,1,col)}
function ell(P,cx,cy,rx,ry,col){for(let dy=-ry;dy<=ry;dy++){const hw=Math.round(rx*Math.sqrt(Math.max(0,1-(dy/(ry+.5))**2)));P(cx-hw,cy+dy,2*hw+1,1,col)}}
const YSKIN="#ecd25a",YSKINS="#b8982f",YBASE="#d4bb3e";
function paletteOf(lk,thin){const sk=thin?YSKIN:lk.skin,cl=thin?mix(lk.cloth,YBASE,.74):lk.cloth,hc=thin?mix(lk.hc,YBASE,.4):lk.hc;
  return{sk,skS:thin?YSKINS:dark(sk,.26),skH:lite(sk,.25),cb:cl,cs:thin?mix(cl,"#6a5a14",.45):dark(cl,.3),ch:lite(cl,.22),hb:hc,hs:dark(hc,.3),hh:lite(hc,.22),pt:thin?mix(cl,"#6a5a14",.6):dark(mix(lk.cloth,"#283240",.7),.1)}}

// 八個朝向（畫面方向，S＝面向鏡頭）；SW/W/NW 由 SE/E/NE 鏡射
const FACES=["E","SE","S","SW","W","NW","N","NE"],BASE={E:["E",0],SE:["SE",0],S:["S",0],SW:["SE",1],W:["E",1],NW:["NE",1],N:["N",0],NE:["NE",0]};
function faceOf(dx,dy){return FACES[((Math.round(Math.atan2(dy*2,dx)/(Math.PI/4))%8)+8)%8]}

// 人物：原點在腳下地面（坐姿為凳子落地點）。站高約 21px、坐高約 19px
const SPW=27,SPH=36,OX=13,OY=31;
function personSprite(lk,face,pose,k,thin,wf){const bm=BASE[face]||BASE.S,key=`${lk.id}|${bm[0]}|${pose}|${k}|${thin?1:0}|${wf}`;
  const s=mk(key,SPW,SPH,OX,OY,drawPerson(lk,bm[0],pose,k,thin,wf));return bm[1]?flipped(key,s):s}
function drawPerson(lk,b,pose,k,thin,wf){const c=paletteOf(lk,thin),SH="#1b1d24",ink="#191b22";
  const sit=pose!=="stand"&&pose!=="walk",isE=b==="E",backV=b==="N"||b==="NE",slump=pose==="slump";
  return P0=>{
    const yt=sit?-10:-12,yb=yt+6,tw=thin?2:3,tl=isE?1-tw:-tw,tr=isE?tw-1:tw;
    let bob=0;if(pose==="doze")bob=k&1;
    // 趴桌：頭往前、往下伏到手臂上
    const fx=slump?{S:0,SE:2,E:4,NE:2,N:0}[b]:0,fy=slump?(backV?2:5)+(k&1):0;
    const ht=yt-8+bob;
    let eye="open",mouth="line";
    if(pose==="work"){eye="down";mouth=k%3?"line":"open"}
    if(pose==="sip"){eye=k===2?"closed":"open";mouth=k===2?"none":"smile"}
    if(pose==="stretch"){eye=k>=1?"closed":"open";mouth=k>=2?"open":"smile"}
    if(pose==="doze"){eye="closed";mouth=k&1?"open":"line"}
    if(slump){eye="hollow";mouth="wavy"}
    const legs=()=>{const P=P0;
      if(!sit){
        if(isE){if(wf===0){const bk=dark(c.pt,.3);P(-1,-5,2,2,bk);P(-2,-3,2,2,bk);P(-3,-1,2,1,SH);P(0,-5,2,2,c.pt);P(1,-3,2,2,c.pt);P(2,-1,3,1,SH)}
          else{P(-1,-5,3,4,c.pt);P(-1,-1,4,1,SH)}return}
        for(const s of [-1,1]){const x=s<0?-2:1,up=(wf===0&&s<0)||(wf===1&&s>0)?1:0;P(x,-5,2,4-up,c.pt);P(x,-1-up,2,1,SH)}return}
      if(b==="S"){P(-3,-3,7,1,c.pt);P(-3,-2,2,1,c.pt);P(2,-2,2,1,c.pt);P(-3,-1,2,1,SH);P(2,-1,2,1,SH)}
      if(b==="SE"){P(-2,-3,6,1,c.pt);P(-1,-2,2,1,c.pt);P(3,-2,2,1,c.pt);P(-1,-1,2,1,SH);P(3,-1,2,1,SH)}
      if(isE){P(-1,-4,5,2,c.pt);P(3,-2,2,1,c.pt);P(3,-1,3,1,SH)}};
    const torso=()=>{const P=P0,w=tr-tl+1;
      P(tl+1,yt,w-2,1,c.cb);P(tl,yt+1,w,6,c.cb);
      if(isE){P(tl,yt+1,1,6,c.cs);P(tr,yt+1,1,6,c.ch)}else if(backV){P(tl,yt+1,1,6,c.cs);P(tr,yt+1,1,6,c.cs)}else{P(tl,yt+1,1,6,c.ch);P(tr,yt+1,1,6,c.cs)}
      P(tl,yb,w,1,c.cs);
      if(thin){if(!backV){P(-1,yt+3,2,1,c.cs);P(-1,yt+5,2,1,c.cs)}return}
      const t=lk.top;
      if(backV){if(t===3){P(-2,yt,1,3,"#3a3f46");P(1,yt,1,3,"#3a3f46")}if(t===9)P(tl,yt,w,2,"#c79a3e");if(t===1){P(tl,yt+2,w,1,c.cs);P(tl,yt+4,w,1,c.cs)}return}
      const cx=b==="S"?0:1;
      if(t===0)P(cx-1,yt,3,1,lite(c.cb,.5));
      if(t===1){P(tl,yt+2,w,1,c.cs);P(tl,yt+4,w,1,c.cs)}
      if(t===2){P(cx-1,yt,2,2,"#eee3c9");P(cx,yt+1,1,3,c.cs)}
      if(t===3){P(isE?0:-2,yt+2,isE?2:5,4,"#3a3f46");if(!isE){P(-2,yt,1,2,"#3a3f46");P(2,yt,1,2,"#3a3f46")}}
      if(t===9){P(tl,yt,w,2,"#c79a3e");P(cx+1,yt+2,1,2,"#a97f2e")}};
    const head=()=>{const P=(x,y,w,h,col)=>P0(x+fx,y+fy,w,h,col),H=c.hb,HS=c.hs,HH=c.hh,hs=lk.hair;
      P(-3,ht+1,7,6,c.sk);P(-2,ht+7,5,1,c.skS);
      if(b==="S"){P(-3,ht,7,1,H);P(-4,ht+1,9,2,H);P(-4,ht+3,1,2,H);P(4,ht+3,1,2,H)}
      if(b==="SE"){P(-3,ht,7,1,H);P(-4,ht+1,9,1,H);P(-4,ht+2,7,1,H);P(-4,ht+3,2,3,H);P(4,ht+2,1,1,HS)}
      if(isE){P(-3,ht,6,1,H);P(-4,ht+1,8,1,H);P(-4,ht+2,6,1,H);P(-4,ht+3,3,3,H);P(-3,ht+6,2,1,HS);P(-1,ht+4,1,1,c.skS);P(4,ht+5,1,1,c.sk)}
      if(b==="NE"){P(-3,ht,7,1,H);P(-4,ht+1,9,2,H);P(-4,ht+3,7,4,H);P(-3,ht+7,4,1,HS)}
      if(b==="N"){P(-3,ht,7,1,H);P(-4,ht+1,9,6,H);P(-3,ht+7,7,1,HS)}
      P(-2,ht,3,1,HH);if(backV)P(-2,ht+1,2,1,HH);
      if(hs===1)for(const x of [-3,-1,1,3])P(x,ht-1,1,1,H);
      if(hs===2||hs===3){const n=hs===2?6:4;
        if(b==="S"){P(-4,ht+3,1,n,H);P(4,ht+3,1,n,H)}
        if(b==="SE")P(-4,ht+3,2,n,H);
        if(isE)P(-4,ht+3,3,n,H);
        if(backV)P(-4,ht+7,b==="N"?9:7,n-3,H)}
      if(hs===4){if(b==="S")P(5,ht+2,1,3,HS);if(b==="SE"||isE){P(-5,ht+2,1,4,H);P(-6,ht+4,1,2,HS)}if(backV)P(-1,ht+7,2,4,H)}
      if(hs===5){P(-5,ht-1,2,2,H);if(!isE)P(b==="S"||b==="N"?4:3,ht-1,2,2,H)}
      if(hs===6&&(b==="S"||b==="SE"))P(b==="S"?-3:-2,ht+3,3,1,H);
      if(hs===7)P(-3,ht-1,isE?6:7,1,H);
      if(lk.acc===2){P(-4,ht+1,isE?8:9,1,"#f0e7cf");if(!backV)P(b==="S"?0:b==="SE"?1:2,ht+1,1,1,"#c23a30")}
      if(lk.acc===3&&!backV)P(isE?-1:4,ht,1,2,"#c79a3e");
      if(lk.master){ // 白毛巾綁頭：額頭一圈，後腦打結垂兩條布尾
        const T="#f2efe6",TS="#cfcabb";P(-4,ht+1,isE?8:9,2,T);P(-4,ht+2,isE?8:9,1,TS);
        if(b==="S"){P(-2,ht+1,1,1,TS);P(5,ht+2,1,2,T);P(6,ht+3,1,2,TS)}
        if(b==="SE"){P(-6,ht+1,2,2,T);P(-6,ht+3,1,3,TS);P(-7,ht+3,1,2,T)}
        if(isE){P(-6,ht+1,2,2,T);P(-6,ht+3,1,3,TS);P(-7,ht+3,1,3,T)}
        if(b==="NE"){P(-2,ht+1,3,3,T);P(-2,ht+2,3,1,TS);P(-3,ht+4,1,3,TS);P(0,ht+4,1,2,T)}
        if(b==="N"){P(-1,ht+1,3,3,T);P(-1,ht+2,3,1,TS);P(-2,ht+4,1,3,TS);P(1,ht+4,1,3,T)}}
      if(backV){if(b==="NE")P(3,ht+4,1,1,c.skS);return}
      const ex=b==="S"?[-2,2]:b==="SE"?[-1,2]:[2];
      if(lk.acc===1&&!thin){const f="#d6d0be";for(const x of ex){P(x-1,ht+4,1,1,f);P(x+1,ht+4,1,1,f)}if(ex.length>1)P(ex[0]+1,ht+4,ex[1]-ex[0]-1,1,f);if(isE)P(-1,ht+4,2,1,f)}
      for(const x of ex){
        if(eye==="open")P(x,ht+4,1,2,ink);
        else if(eye==="down")P(x,ht+5,1,1,ink);
        else if(eye==="closed")P(x,ht+5,1,1,"#5a3f36");
        else if(eye==="hollow")P(x,ht+4,1,2,"#6f6230")}
      const mx=b==="S"?0:b==="SE"?1:3,mw=isE?1:2,mo=isE?0:1;
      if(mouth==="line")P(mx,ht+6,1,1,"#a4574a");
      if(mouth==="open")P(mx-mo,ht+6,mw,1,"#7a2a2a");
      if(mouth==="smile")P(mx-mo,ht+6,mw,1,"#c0605a");
      if(mouth==="wavy")P(mx-mo,ht+6,mw,1,"#5d5320");
      if(b==="S"&&!thin){P(-3,ht+5,1,1,"#eba58e");P(3,ht+5,1,1,"#eba58e")}};
    const arms=()=>{const P=P0,shL=tl-1,shR=tr+1,far=b==="SE"||b==="NE"?c.cs:c.cb;
      const arm=(sx,sy,hx,hy,col,hand=true)=>{limb(P,sx,sy,hx,hy,col);if(hand)P(hx,hy,1,1,c.sk)};
      if(!sit){
        if(isE){arm(0,yt+1,wf===0?2:wf===1?-1:0,yt+4,c.cs);return}
        const sL=wf===0?1:0,sR=wf===1?1:0;arm(shL,yt+1,shL,yt+5-sL,far);arm(shR,yt+1,shR,yt+5-sR,c.cb);return}
      if(slump){ // 雙臂伏在桌上，頭枕在上面
        if(b==="S"){P(-5,yt+3,11,2,c.cb);P(-5,yt+3,1,2,c.cs);P(5,yt+3,1,2,c.cs);P(-4,yt+5,2,1,c.sk);P(3,yt+5,2,1,c.sk)}
        if(b==="SE"){P(-3,yt+3,10,2,c.cb);P(-3,yt+3,1,2,c.cs);P(6,yt+4,2,1,c.sk)}
        if(isE){P(1,yt+3,7,2,c.cs);P(7,yt+4,2,1,c.sk)}
        if(b==="NE"){P(shL-1,yt+2,2,2,far);P(shR,yt+1,3,2,c.cb)}
        if(b==="N"){P(shL-1,yt+2,2,2,c.cb);P(shR,yt+2,2,2,c.cb)}
        return}
      const typing=pose==="work",t1=typing?k&1:0,t2=typing?(k>>1)&1:0;
      const rest=()=>{
        if(b==="S"){arm(shL,yt+1,-2,yt+5-t1,c.cb);arm(shR,yt+1,2,yt+5-t2,c.cb)}
        if(b==="SE"){arm(shL,yt+1,1,yt+5-t1,far);arm(shR,yt+1,tr+2,yt+4-t2,c.cb)}
        if(isE)arm(0,yt+1,tr+2,yt+4-t1,c.cs);
        if(b==="NE"){arm(shL,yt+1,shL,yt+3,far,false);arm(shR,yt+1,tr+2,yt+2-t1,c.cb)}
        if(b==="N"){arm(shL,yt+1,shL,yt+3-t1,c.cb,false);arm(shR,yt+1,shR,yt+3-t2,c.cb,false)}};
      if(pose==="work"||pose==="doze"){rest();return}
      if(pose==="sip"){const H={S:[[3,yt+5],[4,yt+2],[1,ht+6]],SE:[[tr+2,yt+4],[tr+2,yt+1],[3,ht+6]],E:[[tr+2,yt+4],[tr+2,yt+1],[4,ht+6]],NE:[[tr+2,yt+2],[tr+2,yt],[5,ht+5]],N:[[shR,yt+3],[shR+1,yt],[5,ht+5]]}[b][Math.min(k,2)];
        if(b==="S")arm(shL,yt+1,-2,yt+5,c.cb);if(b==="SE")arm(shL,yt+1,1,yt+5,far);if(backV)arm(shL,yt+1,shL,yt+3,far,false);
        arm(isE?0:shR,yt+1,H[0],H[1],isE?c.cs:c.cb);
        const mc=lk.bev===1?"#d9d2c0":lk.bev===2?"#3f6d78":"#a6432f";if(!(backV&&k===2)){P(H[0]-1,H[1]-2,2,2,mc);P(H[0]+1,H[1]-2,1,1,dark(mc,.3))}return}
      if(pose==="stretch"){const up=k>=2?ht-2-(k&1):k===1?yt-1:yt+4,out=k===1?2:k>=2?1:0;
        if(isE){arm(0,yt+1,k===0?tr+2:1,up,c.cs);return}
        arm(shL,yt+1,shL-out,up,far);arm(shR,yt+1,shR+out,up,c.cb)}};
    if(!(isE&&sit))legs();torso();if(isE&&sit)legs();
    if(slump&&b!=="N"&&b!=="NE"){arms();head()}else{head();arms()}
  }}
// 倒地：原點在身體中央地面；橫躺約 20 寬
function downSprite(lk,k){return mk(`d|${lk.id}|${k}`,28,16,14,11,P=>{const c=paletteOf(lk,false),pale=mix(lk.skin,"#cfd8dd",.4),cb=mix(lk.cloth,"#55606a",.25),ink="#191b22";
  P(-8,-5,5,5,pale);P(-9,-5,2,5,c.hb);P(-8,-6,4,1,c.hb);
  P(-7,-4,1,1,ink);P(-5,-4,1,1,ink);P(-6,-3,1,1,ink);P(-7,-2,1,1,ink);P(-5,-2,1,1,ink);P(-4,-1,2,1,"#7a2a2a");
  if(lk.master){P(-8,-6,2,6,"#f2efe6");P(-7,-6,1,6,"#cfcabb");P(-10,-2,2,1,"#f2efe6");P(-11,-1,2,1,"#cfcabb")}
  P(-3,-5,7,5,cb);P(-3,-5,7,1,lite(cb,.2));P(-3,-1,7,1,dark(cb,.3));
  P(0,-2-(k&1),4,1,dark(cb,.15));P(4,-2-(k&1),1,1,pale);
  P(4,-4,4,4,c.pt);P(8,-5,2,5,"#1d2228")})}
function kindOf(l,lk,f){
  if(l.state==="down")return null;
  if(l.state==="tired")return["slump",(f>>>3)&1];
  if(l.status==="busy")return["work",f&3];
  const cyc=(f+lk.shift*5)>>>0,b=((cyc>>>6)+lk.bev)%3,ph=cyc&63;
  if(b===0){const k=ph<8?0:ph<14?1:ph<36?2:ph<44?1:0;return["sip",k]}
  if(b===1){const k=ph<10?0:ph<16?1:ph<24?2:ph<36?(ph&2?3:2):ph<44?1:0;return["stretch",k]}
  return["doze",(ph>>>3)&1];
}

/* ── 家具精靈 ── */
const RGBC={},hexRGB=s=>RGBC[s]||(RGBC[s]=[parseInt(s.slice(1,3),16),parseInt(s.slice(3,5),16),parseInt(s.slice(5,7),16)]);
// 專案長桌：沿 u 方向的等角木桌（桌面高 TDH），桌上依座位擺筆電／紙／杯／書。
// 整張畫好補外框後沿 u 切成每格一片，各片依自己的地面 y 排前後，桌邊的人才會正確地被桌子擋住或擋住桌子。
function tableParts(t){if(t._parts)return t._parts;const o=L,X=(u,v)=>o.X0+(u-v)*8,Y=(u,v)=>o.Y0+(u+v)*4;
  const bx=Math.floor(X(t.u0,t.v1))-3,ex=Math.ceil(X(t.u1,t.v0))+3,by=Math.floor(Y(t.u0,t.v0))-TDH-12,ey=Math.ceil(Y(t.u1,t.v1))+3,w=ex-bx,h=ey-by;
  const c=document.createElement("canvas");c.width=w;c.height=h;const g=c.getContext("2d",{willReadFrequently:true}),im=g.createImageData(w,h),d=im.data;
  const inR=(u,v)=>u>=t.u0&&u<t.u1&&v>=t.v0&&v<t.v1,wd=(x,y)=>{const a=(x-o.X0)/8,b=(y-o.Y0)/4;return[(a+b)/2,(b-a)/2]};
  const put=(i,col)=>{const v=hexRGB(col);d[i]=v[0];d[i+1]=v[1];d[i+2]=v[2];d[i+3]=255};
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){const ax=bx+x+.5,ay=by+y+.5,i=(y*w+x)*4;let [u,v]=wd(ax,ay+TDH);
    if(inR(u,v)){const e=Math.min(u-t.u0,t.u1-u,v-t.v0,t.v1-v);put(i,e<.13?"#6d5232":e<.25&&(t.v1-v<.25||t.u1-u<.25)?"#a07a48":(Math.floor((v-t.v0)*3)&1)?"#86663e":"#8e6e44");continue}
    for(let s=TDH-1;s>=0;s--){[u,v]=wd(ax,ay+s);if(inR(u,v)){put(i,(t.v1-v)<(t.u1-u)?(s>TDH-3?"#5d4630":"#55402a"):(s>TDH-3?"#463322":"#3d2c1c"));break}}}
  g.putImageData(im,0,0);
  const P=(x,y,ww,hh,col)=>{g.fillStyle=col;g.fillRect(x-bx,y-by,ww,hh)};
  for(const it of t.items){const x=it.x,y=it.y;
    if(it.k===0){P(x-2,y-1,5,2,"#efe9d6");P(x-1,y-2,3,1,"#efe9d6");P(x-1,y+1,3,1,"#d7d1be")}
    if(it.k===1){P(x-2,y-1,5,2,"#3a3d46");P(x-2,y-4,5,3,it.far?"#565a66":"#6fa9b8");if(it.far)P(x,y-3,1,1,"#8a8f9c");if(!it.far)P(x-1,y-3,3,1,"#bfe4f0")}
    if(it.k===2){const mc=it.c;P(x-1,y-3,3,3,mc);P(x-1,y-3,3,1,"#2a1b12");P(x+2,y-2,1,1,mc)}
    if(it.k===3){P(x-2,y-2,5,2,it.c);P(x-2,y-2,5,1,lite(it.c,.25))}}
  for(const p of t.papers||[]){const x=p[0],y=p[1];P(x-3,y-1,6,2,"#efe9d6");P(x-2,y-2,4,1,"#efe9d6");P(x-2,y+1,4,1,"#d7d1be");if(p[2]){P(x-1,y-1,3,1,"#9a9384");P(x+2,y-3,1,3,"#22262e")}}
  for(const p of t.plants){const x=p[0],y=p[1];P(x-1,y-3,3,3,"#5a3a24");P(x-1,y-3,3,1,"#7a5034");P(x-2,y-6,2,2,"#3f8f5e");P(x,y-7,2,3,"#5fae6e");P(x+1,y-5,2,2,"#2f6e48")}
  outlineC(g,w,h);
  // 切成每格一塊（1×1 世界格），每塊依自己的中心 y 排前後；只留有像素的範圍
  const nu=Math.max(1,Math.ceil(t.L-1e-6)),nv=Math.max(1,Math.ceil(t.W-1e-6)),src=g.getImageData(0,0,w,h).data,cell=new Int32Array(w*h).fill(-1),bb=[];
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){const i=y*w+x;if(!src[i*4+3])continue;const q=wd(bx+x+.5,by+y+.5+TDH*.5),ku=Math.max(0,Math.min(nu-1,Math.floor(q[0]-t.u0))),kv=Math.max(0,Math.min(nv-1,Math.floor(q[1]-t.v0))),k=ku*nv+kv;
    cell[i]=k;const b=bb[k]||(bb[k]=[x,y,x,y]);if(x<b[0])b[0]=x;if(y<b[1])b[1]=y;if(x>b[2])b[2]=x;if(y>b[3])b[3]=y}
  const parts=[];
  bb.forEach((b,k)=>{if(!b)return;const cw=b[2]-b[0]+1,chh=b[3]-b[1]+1,id=new ImageData(cw,chh),dd=id.data;
    for(let y=b[1];y<=b[3];y++)for(let x=b[0];x<=b[2];x++){const i=y*w+x;if(cell[i]!==k)continue;const j=((y-b[1])*cw+(x-b[0]))*4;dd[j]=src[i*4];dd[j+1]=src[i*4+1];dd[j+2]=src[i*4+2];dd[j+3]=src[i*4+3]}
    const sc=document.createElement("canvas");sc.width=cw;sc.height=chh;sc.getContext("2d").putImageData(id,0,0);
    const ku=(k/nv)|0,kv=k%nv,cu=(t.u0+ku+Math.min(t.u1,t.u0+ku+1))/2,cv2=(t.v0+kv+Math.min(t.v1,t.v0+kv+1))/2;
    parts.push({c:sc,x:bx+b[0],y:by+b[1],key:o.Y0+(cu+cv2)*4})});
  t._parts={bx,by,slices:parts};
  return t._parts}
const stoolSprite=()=>mk("stool",14,12,7,9,P=>{P(-1,-3,2,3,"#3d2c1c");P(-2,0,4,1,"#2a1f15");ell(P,0,-4,3,1,"#6a4a30");P(-2,-5,4,1,"#94704a")});
const chairSprite=()=>mk("mchair",18,28,9,24,P=>{P(-6,-17,12,12,"#5a2f22");P(-6,-17,12,1,"#7d4a35");P(-5,-15,10,1,"#4a261b");P(-1,-19,2,2,"#c79a3e");P(-5,-5,10,2,"#4a261b");P(-5,-3,1,3,"#2a1a12");P(4,-3,1,3,"#2a1a12")});
// 2:1 菱形：中心在像素邊界 (cx,cy)，半高 hh，寬 4hh-2
function dia(P,cx,cy,hh,col){for(let t=0;t<2*hh;t++){const u=t<hh?t:2*hh-1-t;P(cx-1-2*u,cy-hh+t,4*u+2,1,col)}}
// 等角方塊：地面中心 (0,0)，半高 hh，高 dh；cE＝頂面前緣亮邊
function isoBox(P,hh,dh,cT,cL,cR,cE){for(let s=0;s<dh;s++)for(let t=hh;t<2*hh;t++){const u=2*hh-1-t,y=-hh+t-s;P(-1-2*u,y,2*u+1,1,cL);P(0,y,2*u+1,1,cR)}
  dia(P,0,-dh,hh,cT);if(cE)for(let t=hh;t<2*hh;t++){const u=2*hh-1-t,y=-hh+t-dh;P(-1-2*u,y,2,1,cE);P(2*u-1,y,2,1,cE)}}

/* ── 排位：2:1 等角。世界格 (u,v)：x＝X0+(u−v)·8、y＝Y0+(u+v)·4；u、v≥0 為地板，牆角在 (X0,Y0) ──
   同專案一張大長桌（沿 u 方向）：桌寬＝2×放大倍數 f（預設 3 倍＝6 格），人多就拉長；
   兩長邊分散對坐、朝桌心；總控坐自己專案的桌頭（u 小的一端），桌尾可坐 1–2 人。放不下就把 f 往下調。 */
const TDH=7,FS=[3,2.5,2,1.5,1];
function ftAt(o,x){const X=x-o.X0;return o.Y0+Math.max(Math.ceil((-2*X-3)/4),Math.ceil((2*X-1)/4))}
function s2w(o,x,y){const a=(x-o.X0)/8,b=(y-o.Y0)/4;return[(a+b)/2,(b-a)/2]}
const w2s=(o,u,v)=>[Math.round(o.X0+(u-v)*8),Math.round(o.Y0+(u+v)*4)];
const uni=(a,b)=>[Math.min(a[0],b[0]),Math.min(a[1],b[1]),Math.max(a[2],b[2]),Math.max(a[3],b[3])];
const ov=(a,b,m=0)=>a[0]<=b[2]+m&&a[2]+m>=b[0]&&a[1]<=b[3]+m&&a[3]+m>=b[1];
const projOf=l=>l.project_id||"—";
const lineKey=l=>keyOf(l.project_id,l.line_id);
const sceneLabel=l=>{const name=projectName(l.project_id),short=name.slice(0,/^[A-Za-z0-9]/.test(name)?4:2);return(activeProject==="*"?short+"｜":"")+l.name};
// 依專案分組：總控所在專案排第一，其餘人多的在前；超過 3 個專案時，第 3 個起併成一桌
function groupsOf(list){const m=new Map();for(const l of list){const p=projOf(l);if(!m.has(p))m.set(p,[]);m.get(p).push(l)}
  let gs=[...m.entries()].map(([p,ls])=>({p,ls}));
  gs.sort((a,b)=>(b.ls.some(x=>x.master)-a.ls.some(x=>x.master))||(b.ls.length-a.ls.length));
  if(gs.length>3)gs=[gs[0],gs[1],{p:"其他",ls:gs.slice(2).flatMap(g=>g.ls)}];
  return gs.map(g=>{const M=g.ls.find(x=>x.master)||null,oth=g.ls.filter(x=>x!==M),h=oth.length,foot=h>=7?2:h>=3?1:0,top=Math.ceil((h-foot)/2),bot=h-foot-top;
    return{p:g.p,M,oth,foot,top,bot}})}
// 放大倍數 f 下的桌子尺寸：寬 2f 格；長度至少等寬，並讓長邊每人間隔約 2.5 格
function sized(s,f){const W=2*f,gap=f>=2.5?2.5:2;return Object.assign({},s,{f,W,L:Math.max(W,Math.max(1,s.top)*gap+1)})}
function mkChar(o,l,su,sv,face,out,above,master,t){const [x,y]=w2s(o,su,sv),lk=lookOf(l.name,master);
  // 倒地位置：座位往外一點；出畫面或上牆就改往左右兩側，再不行就倒在座位上
  let down=null;const [ou,ovv]=out;
  for(const [a,b] of [[ou,ovv],[-ovv,ou],[ovv,-ou],[0,0]]){const [dx,dy]=w2s(o,su+a*1.8,sv+b*1.8);
    down={x:dx,y:dy};if(dx-12>=1&&dx+12<=o.W-2&&dy+3<=o.H-2&&dy>=ftAt(o,dx-10)+2&&dy>=ftAt(o,dx+10)+2)break}
  return{l,lk,master,su,sv,sx:x,sy:y,face,above,down,t,box0:[x-7,y-22,x+7,y+2+(above?0:o.lab+1)]}}
function seatTable(o,s,u0,v0){const t={p:s.p,u0,v0,u1:u0+s.L,v1:v0+s.W,L:s.L,W:s.W,master:!!s.M},uc=u0+s.L/2,vc=v0+s.W/2,chars=[];
  t.vc=vc;[t.x,t.y]=w2s(o,uc,vc);
  const cl=a=>Math.max(-1.2,Math.min(1.2,a));
  const add=(l,su,sv,du,dv,out,above)=>chars.push(mkChar(o,l,su,sv,faceOf((du-dv)*8,(du+dv)*4),out,above,l===s.M,t));
  const nf=s.foot,sides=s.oth.slice(0,s.oth.length-nf),feet=s.oth.slice(s.oth.length-nf);
  let it=0,ib=0;
  sides.forEach((l,i)=>{ // 兩長邊輪流坐，沿邊平均分散
    if(i%2===0){const su=u0+(it+.5)*s.L/s.top;it++;add(l,su,v0-.6,cl((uc-su)*.3),1.6,[0,-1],true)}
    else{const su=u0+(ib+.5)*s.L/s.bot;ib++;add(l,su,t.v1+.6,cl((uc-su)*.3),-1.6,[0,1],false)}});
  feet.forEach((l,j)=>{const sv=v0+(j+.5)*s.W/nf;add(l,t.u1+.65,sv,-1.6,cl((vc-sv)*.3),[1,0],false)});
  if(s.M)add(s.M,u0-.65,vc,1,0,[-1,0],true);
  const X=(u,v)=>o.X0+(u-v)*8,Y=(u,v)=>o.Y0+(u+v)*4;let box=[X(u0,t.v1)-2,Y(u0,v0)-TDH-6,X(t.u1,v0)+2,Y(t.u1,t.v1)+3];
  for(const ch of chars)box=uni(box,ch.box0);
  // 地面佔用（世界座標）：桌面＋一圈座位；桌與桌之間至少留 1 格走道
  return{t,chars,box,wb:[u0-1.4,v0-1.4,t.u1+1.4,t.v1+1.4]}}
function fitsT(o,r,wbs){const b=r.box;if(b[0]<1||b[2]>o.W-2||b[1]<1||b[3]>o.H-2)return false;if(o.lg&&ov(b,o.lg,1))return false;
  if(wbs.some(q=>ov(r.wb,q,1)))return false;
  for(const ch of r.chars)if(ch.sy<ftAt(o,ch.sx)+3||ch.sx<8||ch.sx>o.W-9)return false;
  // 桌面四角也要在地板上（不壓到牆）
  const t=r.t;for(const [u,v] of [[t.u0,t.v0],[t.u1,t.v0],[t.u0,t.v1]]){const [x,y]=w2s(o,u,v);if(y-TDH<ftAt(o,x)+1)return false}
  return true}
// 桌位目標（畫面比例），候選桌位依離目標遠近逐一試，放得下就用
const TG={0:[[]],1:[[[.5,.5]],[[.5,.35]]],2:[[[.3,.26],[.72,.74]],[[.38,.32],[.66,.78]],[[.5,.36],[.3,.8]],[[.42,.46],[.78,.66]],[[.3,.3],[.7,.75]],[[.7,.3],[.3,.75]]],3:[[[.34,.36],[.78,.42],[.52,.8]],[[.5,.3],[.25,.75],[.75,.8]],[[.3,.3],[.75,.5],[.35,.85]]]};
function layTables(o,gs){for(const tg of TG[gs.length]){const r=layWith(o,gs,tg);if(r)return r}return null}
function layWith(o,gs,tg){const N=Math.ceil((o.H-o.Y0)/4)+3,boxes=[],wbs=[],tables=[],chars=[];
  for(let k=0;k<gs.length;k++){const s=gs[k],tx=o.W*tg[k][0],ty=o.Y0+(o.H-o.Y0)*tg[k][1],cands=[];
    for(let u0=1;u0<N;u0++)for(let v0=1;v0<N;v0++){const uc=u0+s.L/2,vc=v0+s.W/2,x=o.X0+(uc-vc)*8,y=o.Y0+(uc+vc)*4;if(x<0||x>o.W||y>o.H)continue;cands.push([(x-tx)**2+(y-ty)**2,u0,v0])}
    cands.sort((a,b)=>a[0]-b[0]);let ok=null;
    for(const c of cands){const r=seatTable(o,s,c[1],c[2]);if(fitsT(o,r,wbs)){ok=r;break}}
    if(!ok)return null;tables.push(ok.t);chars.push(...ok.chars);boxes.push(ok.box);wbs.push(ok.wb)}
  return{tables,chars,boxes}}
function place(list){const bw=box.clientWidth,bh=box.clientHeight,gs=list.length?groupsOf(list):[];
  let lgc=null;{const a=lg.getBoundingClientRect(),b=box.getBoundingClientRect();if(a.width)lgc=[a.left-b.left,a.top-b.top,a.right-b.left,a.bottom-b.top]}
  // 先求桌子夠大（f 由 3 倍往下試），同一倍數下再優先用較大的像素倍率
  for(const f of FS)for(const P of [3,2]){const W=Math.ceil(bw/P),H=Math.ceil(bh/P);if(W<90||H<80)continue;
    const o={P,W,H,X0:W>>1,Y0:Math.round(H*.2),WH:44,lab:Math.ceil(23/P),lgc,lg:lgc?[Math.floor(lgc[0]/P)-1,Math.floor(lgc[1]/P)-1,Math.ceil(lgc[2]/P),Math.ceil(lgc[3]/P)]:null};
    const r=layTables(o,gs.map(s=>sized(s,f)));if(!r)continue;
    Object.assign(o,r);o.f=f;
    o.tables.forEach((t,i)=>{const vc=t.vc,seats=o.chars.filter(c=>c.t===t);
      t.items=seats.map(ch=>{const h=hash(ch.l.name),mc=["#a6432f","#d9d2c0","#3f6d78"][h%3];
        let iu=ch.su,iv=ch.sv<t.v0?t.v0+.5:ch.sv>t.v1?t.v1-.5:ch.sv;if(ch.su<t.u0)iu=t.u0+.5;if(ch.su>t.u1)iu=t.u1-.5;
        const [x,y]=w2s(o,iu,iv);
        return{x,y:y-TDH,far:ch.sv<t.v0||ch.su<t.u0,k:ch.l.status==="busy"?1:[0,2,3][(h>>>2)%3],c:ch.l.status==="busy"?mc:["#a8445f","#2e5c86","#b7953f","#3f8f86"][(h>>>5)%4]}});
      // 桌心擺設：盆栽與散紙沿中線
      t.plants=[];t.papers=[];for(let a=t.u0+1.5;a<t.u1-1;a+=3){const [x,y]=w2s(o,a,vc);t.plants.push([x,y-TDH])}
      for(let a=t.u0+3;a<t.u1-1;a+=3)for(const dv of [-t.W/4,t.W/4]){const [x,y]=w2s(o,a,vc+dv);t.papers.push([x,y-TDH,(hash(t.p+a+dv)>>>3)&1])}
      t.key="tb|"+i+"|"+JSON.stringify([t.u0,t.v0,t.L,t.W,t.items])});
    o.key=JSON.stringify([P,W,H,f,o.chars.map(c=>[lineKey(c.l),projOf(c.l)])]);
    return o}
  return null}

/* ── 房間（靜態底圖，版面變動才重畫） ── */
function rng(seed){let a=seed>>>0;return()=>{a=(a+0x6D2B79F5)>>>0;let t=a;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return((t^(t>>>14))>>>0)/4294967296}}
// 畫在小畫布上補外框再貼回（局部原點 ox,oy）
function stamp(g,X,Y,w,h,ox,oy,fn){const c=document.createElement("canvas");c.width=w;c.height=h;const s=c.getContext("2d",{willReadFrequently:true});
  fn((x,y,ww,hh,col)=>{s.fillStyle=col;s.fillRect(ox+x,oy+y,ww,hh)});outlineC(s,w,h);g.drawImage(c,X-ox,Y-oy)}
function paintRoom(o){const {W,H,X0,Y0}=o,c=document.createElement("canvas");c.width=W;c.height=H;
  const g=c.getContext("2d",{willReadFrequently:true}),R=(x,y,w,h,col)=>{g.fillStyle=col;g.fillRect(x,y,w,h)},rnd=rng(20261106),WH=o.WH;
  // 每欄地板起點（兩面後牆與地板的交線）
  const ft=new Int16Array(W);for(let x=0;x<W;x++)ft[x]=ftAt(o,x);
  const T2=32,K={},rgb=s=>K[s]||(K[s]=[parseInt(s.slice(1,3),16),parseInt(s.slice(3,5),16),parseInt(s.slice(5,7),16)]);
  // 地毯：鋪在總控那張桌子底下
  const mt=o.tables.find(t=>t.master),rug=mt?{pl:(mt.u0-1)*T2,ph:(Math.ceil(mt.u1)+1)*T2,ql:(mt.v0-1)*T2,qh:(mt.v1+1)*T2}:null;
  const wallL=["#1f343e","#1c3039","#192b34","#16272f","#13232a"],wallR=["#172a33","#15262e","#13232b","#112027","#0f1c23"],band=Math.max(2,Math.round((WH-8)/5));
  // 地板菱形格＋牆面（逐像素）
  const im=g.createImageData(W,H),d=im.data;
  for(let y=0;y<H;y++)for(let x=0;x<W;x++){let col;const X=x-X0,Y=y-Y0;
    if(y>=ft[x]){const p=2*X+4*Y+3,qq=4*Y-2*X+1,pm=((p%T2)+T2)%T2,qm=((qq%T2)+T2)%T2,odd=(Math.floor(p/T2)+Math.floor(qq/T2))&1;
      if(rug&&p>=rug.pl&&p<rug.ph&&qq>=rug.ql&&qq<rug.qh){const e=Math.min(p-rug.pl,rug.ph-1-p,qq-rug.ql,rug.qh-1-qq);
        col=e<4?"#5d4a22":e<8?"#b58a3a":e<13?"#4a2230":e<16?"#8d6a2e":((((p-rug.pl)>>3)+((qq-rug.ql)>>3))&3)===0?"#6d3346":"#4a2230"}
      else if(pm<3||qm<3)col="#1a1814";
      else if(pm<6||qm<6)col=odd?"#3a342b":"#312d25";
      else col=odd?"#2f2b23":"#27241e";
      if((col==="#2f2b23"||col==="#27241e")&&((x*7919+y*104729)%89)===0)col="#3b362c";
    }else{const rel=ft[x]-y,Lw=X<0;
      if(rel>WH+1)col=((x*31+y*17)%23===0)?"#0f1a22":"#0a1218";
      else if(rel>WH-1)col=rel===WH+1?"#4a5d66":"#2f414a";
      else if(rel<=5)col=Lw?"#16222b":"#101a21";
      else if(rel===6)col=Lw?"#7a6534":"#5d4c28";
      else if(rel===7)col=Lw?"#2b3c45":"#22313a";
      else{let kk=Math.min(4,Math.floor((rel-8)/band));if(kk>0&&(rel-8)%band===0&&(((x>>1)+rel)&1))kk--;col=(Lw?wallL:wallR)[kk];
        if(X===-1||X===0)col="#0e1a22";else if(((Lw?-X:X)%18)===9)col=Lw?"#182c35":"#10202a"}}
    const v=rgb(col),i=(y*W+x)*4;d[i]=v[0];d[i+1]=v[1];d[i+2]=v[2];d[i+3]=255}
  g.putImageData(im,0,0);
  // 不可被牆飾／地面雜物蓋到的區域：桌群、人物、圖例
  const busy=o.boxes.map(b=>b.slice());if(o.lg)busy.push(o.lg);o.obst=[];
  const clear=(x0,y0,x1,y1)=>x0>=0&&x1<W&&y0>=0&&y1<H&&!busy.some(b=>x0<=b[2]&&x1>=b[0]&&y0<=b[3]&&y1>=b[1]);
  const onWall=(xa,xb,rb,h)=>{let y0=1e9,y1=-1e9;for(let x=xa;x<=xb;x++){y0=Math.min(y0,ft[x]-rb-h);y1=Math.max(y1,ft[x]-rb)}return[y0,y1]};
  const findWall=(xa,xb,h,rbMin)=>{for(let rb=rbMin;rb+h<=WH-3;rb++){const [y0,y1]=onWall(xa,xb,rb,h);if(y0<1)return null;if(clear(xa-1,y0-1,xb+1,y1+1))return rb}return null};
  // 截稿日曆（數字在 draw() 依牆斜度畫）：左牆靠牆角優先，放不下再試右牆
  o.cal=null;{const cw=14,ch=16,spots=[];
    for(let x=X0-6-cw;x>=4;x-=2)spots.push(x);for(let x=X0+8;x+cw<W-3;x+=2)spots.push(x);
    for(const ca of spots){const rb=findWall(ca,ca+cw-1,ch,9);if(rb==null)continue;
      const sh=[];for(let i=0;i<cw;i++)sh.push(ft[ca+i]-ft[ca]);
      for(let i=0;i<cw;i++){const x=ca+i,yt=ft[x]-rb-ch;R(x,yt+1,1,ch,"#0a1116");R(x,yt,1,ch,"#e6dcc0");R(x,yt,1,4,"#b83a34")}
      R(ca+3,ft[ca+3]-rb-ch-1,1,2,"#2a2a2a");R(ca+cw-4,ft[ca+cw-4]-rb-ch-1,1,2,"#2a2a2a");busy.push([ca-1,ft[ca+cw-1]-rb-ch-2,ca+cw,ft[ca]-rb+1]);
      o.cal={x:ca,y:ft[ca]-rb-ch,w:cw,h:ch,sh};break}}
  // 左牆：窗（夜景）
  let win=null;{const lim=o.cal&&o.cal.x<X0?o.cal.x-5:X0-10;
  for(const ww of [34,30,26,22,18]){const xa=Math.max(3,Math.min(Math.round(X0*.1),lim-ww+1)),xb=Math.min(lim,xa+ww-1);if(xb-xa<13)continue;
    for(let wh=24;wh>=12&&!win;wh-=3){const rb=findWall(xa,xb,wh,11);if(rb!=null)win={xa,xb,rb,wh}}if(win)break}}
  if(win){const {xa,xb,rb,wh}=win,city=[];let hc=0,run=0;for(let x=xa;x<=xb;x++){if(run<=0){hc=2+(rnd()*Math.max(3,wh*.42)|0);run=3+(rnd()*4|0)}city.push(hc);run--}
    for(let x=xa;x<=xb;x++){const yb=ft[x]-rb,yt=yb-wh+1,e=x===xa||x===xb,e2=x===xa+1||x===xb-1,mid=x===((xa+xb)>>1);
      for(let r=0;r<wh;r++){let col;
        if(e||r===0||r===wh-1)col="#4a3b25";else if(e2||r===1||mid||r===(wh>>1))col="#6d5a30";
        else{col=r<wh*.38?"#0a1626":r<wh*.72?"#0c1a2c":"#102136";const ch2=city[x-xa];
          if(wh-2-r<=ch2)col=(rnd()>.84&&r<wh-3)?(rnd()>.3?"#d9b45c":"#7fa6b5"):"#121f2d";else if(rnd()<.045)col=rnd()>.5?"#cdd8e8":"#6f8299"}
        R(x,yt+r,1,1,col)}
      R(x,yb+1,1,1,"#8d7134");R(x,yb+2,1,1,"#3a2e1c")}
    const mx=xb-7,my=ft[mx]-rb-wh+4;R(mx,my,4,4,"#e8dfb8");R(mx+1,my-1,2,1,"#e8dfb8");R(mx+1,my+4,2,1,"#e8dfb8");R(mx,my+1,2,2,"#cdc39a")}
  // 右牆：書架（兩層）
  {const sw=Math.min(36,Math.round((W-X0)*.42)),cands=[];for(let x=W-4-sw;x>X0+6;x-=3)cands.push(x);
    for(const sa of cands){const sb=sa+sw-1,rb=findWall(sa,sb,22,12);if(rb==null)continue;
      if(o.cal&&sa<=o.cal.x+o.cal.w+2&&sb>=o.cal.x-2)continue;
      for(let s=0;s<2;s++){const br=rb+s*11;let x=sa;
        while(x<=sb){const w=2+(rnd()*2|0),h=5+(rnd()*4|0),col=["#a8445f","#3f8f86","#c7622f","#2e5c86","#d9cfb4","#7b6aa6","#b7953f"][rnd()*7|0];
          for(let i=0;i<w&&x+i<=sb;i++){const yb=ft[x+i]-br-2;R(x+i,yb-h+1,1,h,i===0?lite(col,.18):col)}x+=w+(rnd()>.82?1:0)}
        for(let x2=sa-1;x2<=sb+1;x2++){const yb=ft[x2]-br;R(x2,yb-1,1,1,"#6d5a30");R(x2,yb,1,1,"#4a3b25");R(x2,yb+1,1,1,"#241c12")}}
      for(const x2 of [sa-2,sb+2]){const yb=ft[x2]-rb;R(x2,yb-22,1,24,"#3a2c1a")}
      busy.push([sa-2,onWall(sa,sb,rb,22)[0],sb+2,onWall(sa,sb,rb,22)[1]]);break}}
  // 右牆：流程藍圖
  {const pw=18,ph=13;for(let pa=X0+6;pa+pw<W-4;pa+=2){const rb=findWall(pa,pa+pw-1,ph,10);if(rb==null)continue;
    for(let i=0;i<pw;i++){const x=pa+i,yt=ft[x]-rb-ph,e=i===0||i===pw-1;R(x,yt+1,1,ph,"#0a1116");
      for(let r=0;r<ph;r++){const ed=e||r===0||r===ph-1;let col=ed?"#d9cfb4":"#1d4f7a";
        if(!ed&&(r===4||r===8)&&i>1&&i<pw-2)col="#8fc4e6";if(!ed&&(i===5||i===12)&&r>1&&r<ph-2)col="#8fc4e6";
        if(!ed&&((i===3&&r>=3&&r<=5)||(i===9&&r>=6&&r<=9)||(i===14&&r>=2&&r<=4)))col="#e8f4fb";R(x,yt+r,1,1,col)}}
    break}}
  // 地面雜物（避開桌群）；紙堆與植物記為障礙，走路會繞開
  const scatter=(n)=>{for(let i=0;i<n*10&&n>0;i++){const x=3+(rnd()*(W-14)|0),y=Math.max(ft[Math.min(W-1,x+5)],ft[x])+4+(rnd()*(H-6)|0);if(y>H-3||!clear(x-1,y-4,x+11,y+3))continue;
      const col=rnd()>.25?"#d8d2bf":"#c7c0ab";dia(R,x+5,y,2,col);R(x+3,y-1,3,1,"#8d8778");busy.push([x-1,y-4,x+11,y+3]);n--}};
  const cups=(n)=>{for(let i=0;i<n*5&&n>0;i++){const x=4+(rnd()*(W-10)|0),y=ft[x]+6+(rnd()*(H-8)|0);if(y>H-2||!clear(x-2,y-6,x+6,y+1))continue;
      stamp(g,x,y,10,10,3,7,P=>{P(-1,-4,5,4,"#d6d0be");P(-1,-5,5,1,"#e9e3d0");P(0,-4,3,1,"#a9a391");P(-1,-1,5,1,"#a9a391");P(1,-3,1,2,"#b83a34")});busy.push([x-2,y-6,x+6,y+1]);n--}};
  const stack=(x,y,n)=>{if(!clear(x-10,y-n*2-8,x+10,y+5))return false;busy.push([x-10,y-n*2-8,x+10,y+5]);o.obst.push([x-9,y-5,x+9,y+4]);
    stamp(g,x,y,24,n*2+18,12,n*2+11,P=>{isoBox(P,4,n*2,"#e8e2cf","#cfc9b6","#aaa492");for(let k=1;k<n;k++)for(let t=4;t<8;t++){const u=7-t,y=-4+t-2*k;P(-1-2*u,y,2,1,"#a29c89");P(2*u-1,y,2,1,"#837d6e")}
      P(-2,-4-n*2,4,1,"#cfc9b6");P(-4,-3-n*2,3,1,"#d8d2bf")});return true};
  const plant=(x)=>{const y=ft[x]+7;if(!clear(x-7,y-17,x+7,y+4))return false;busy.push([x-7,y-17,x+7,y+4]);o.obst.push([x-6,y-5,x+6,y+3]);
    stamp(g,x,y,20,26,10,20,P=>{isoBox(P,3,5,"#5a3a24","#8a5a34","#6a4428");const lf=["#3f8f5e","#2f6e48","#5fae6e"];
      for(const [a,b,w,h,k] of [[-6,-14,4,3,0],[2,-15,5,3,1],[-3,-17,5,4,2],[-7,-10,5,3,1],[3,-11,5,3,0],[-2,-12,4,4,0],[0,-19,2,3,2]])P(a,b,w,h,lf[k]);P(-1,-9,2,4,"#2f6e48")});return true};
  for(let x=4;x<X0-14;x+=3)if(plant(x))break;
  for(let x=W-6;x>X0+14;x-=3)if(plant(x))break;
  stacks:for(let n=5;n>=3;n--)for(let x=12;x<W/3;x+=4)if(stack(x,H-6,n))break stacks;
  stacks2:for(let n=4;n>=3;n--)for(let x=W-13;x>W*2/3;x-=4)if(stack(x,H-6,n))break stacks2;
  scatter(Math.round(W/16));cups(Math.max(2,Math.round(W/50)));
  // 光暈層：沿每張長桌中線的暖光（菱形階梯，低透明）
  const gc=document.createElement("canvas");gc.width=W;gc.height=H;const gg=gc.getContext("2d"),GP=(x,y,w,h)=>gg.fillRect(x,y,w,h);
  const lamps=[];for(const t of o.tables)for(let a=t.u0+1.5;a<t.u1;a+=3)for(let b=t.v0+1.5;b<t.v1;b+=3){const p=w2s(o,a,b);lamps.push({x:p[0],y:p[1]-8,n:8})}
  for(const l of lamps)for(let k=l.n;k>=2;k--){gg.fillStyle="rgba(255,172,76,.03)";dia(GP,l.x,l.y+2,k,null)}
  return{c,gc}}

/* ── 可走格：桌、總控桌、別人的座位、倒地的人、紙堆植物都不能走 ── */
function buildGrid(o){const N=Math.ceil((o.H-o.Y0)/4)+3,g=new Uint8Array(N*N);o.N=N;
  const inObst=(x,y)=>o.obst.some(b=>x>=b[0]-3&&x<=b[2]+3&&y>=b[1]&&y<=b[3]+3);
  for(let i=0;i<N;i++)for(let j=0;j<N;j++){const u=i+.5,v=j+.5,x=o.X0+(u-v)*8,y=o.Y0+(u+v)*4;
    if(x<7||x>o.W-8||y>o.H-3||y<ftAt(o,x)+3)continue;
    if(o.lg&&x+6>=o.lg[0]&&x-6<=o.lg[2]&&y-22<=o.lg[3]&&y+1>=o.lg[1])continue;
    if(o.tables.some(t=>i+1>t.u0-.2&&i<t.u1+.2&&j+1>t.v0-.2&&j<t.v1+.2))continue;
    if(inObst(x,y))continue;
    g[i*N+j]=1}
  const at=(u,v)=>{const i=Math.floor(u),j=Math.floor(v);return i>=0&&j>=0&&i<N&&j<N?i*N+j:-1};
  for(const ch of o.chars){const t=at(ch.su,ch.sv);if(t>=0&&g[t])g[t]=2;
    if(ch.l.state==="down"){const w=s2w(o,ch.down.x,ch.down.y);for(const [a,b] of [[0,0],[.7,-.7],[-.7,.7]]){const t2=at(w[0]+a,w[1]+b);if(t2>=0)g[t2]=0}}}
  for(const ch of o.chars){ch.own=at(ch.su,ch.sv);ch.acc=-1;let best=1e9;const i0=Math.floor(ch.su),j0=Math.floor(ch.sv);
    for(let di=-1;di<=1;di++)for(let dj=-1;dj<=1;dj++){const i=i0+di,j=j0+dj;if(i<0||j<0||i>=N||j>=N)continue;const t=i*N+j;
      if(!(g[t]===1||(g[t]===2&&t===ch.own)))continue;const d=(i+.5-ch.su)**2+(j+.5-ch.sv)**2;if(d<best){best=d;ch.acc=t}}}
  o.grid=g}
function planWalk(ch){const o=L,N=o.N,g=o.grid,r=ch.rt,src=ch.acc;if(src<0){r.cool=8000;return}
  const pass=t=>g[t]===1||t===src,dist=new Int16Array(N*N).fill(-1),par=new Int32Array(N*N).fill(-1),q=[src];dist[src]=0;
  for(let h=0;h<q.length;h++){const t=q[h],i=(t/N)|0,j=t%N;for(const [a,b] of [[1,0],[-1,0],[0,1],[0,-1]]){const i2=i+a,j2=j+b;if(i2<0||j2<0||i2>=N||j2>=N)continue;const t2=i2*N+j2;if(dist[t2]>=0||!pass(t2))continue;dist[t2]=dist[t]+1;par[t2]=t;q.push(t2)}}
  const taken=new Set(o.chars.filter(c=>c.rt&&c.rt.mode!=="seat"&&c.rt.target!=null).map(c=>c.rt.target));
  let tgt=-1,visit=null;
  const mates=o.chars.filter(c=>c!==ch&&c.acc>=0&&c.rt&&c.rt.mode==="seat");
  if(mates.length&&Math.random()<.6){const m=mates[Math.random()*mates.length|0],i=(m.acc/N)|0,j=m.acc%N,nb=[];
    for(const [a,b] of [[1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,-1],[1,-1],[-1,1]]){const i2=i+a,j2=j+b;if(i2<0||j2<0||i2>=N||j2>=N)continue;const t=i2*N+j2;if(g[t]===1&&dist[t]>=3&&!taken.has(t))nb.push(t)}
    if(nb.length){tgt=nb[Math.random()*nb.length|0];visit=m}}
  if(tgt<0){const c=[];for(let t=0;t<N*N;t++)if(g[t]===1&&dist[t]>=4&&dist[t]<=16&&!taken.has(t))c.push(t);if(c.length)tgt=c[Math.random()*c.length|0]}
  if(tgt<0){r.cool=5000;return}
  const tiles=[];for(let t=tgt;t>=0;t=par[t])tiles.push(t);tiles.reverse();
  r.pts=[[ch.su,ch.sv],...tiles.map(t=>[((t/N)|0)+.5,t%N+.5])];
  Object.assign(r,{mode:"walk",i:0,u:ch.su,v:ch.sv,ret:false,dist:0,visit,target:tgt})}
function startOne(){const cs=L.chars,walking=cs.filter(c=>c.rt&&c.rt.mode!=="seat").length,maxW=cs.length<=3?1:cs.length<=8?2:3;if(walking>=maxW)return;
  const cand=cs.filter(c=>c.rt&&c.rt.mode==="seat"&&c.rt.cool<=0&&c.acc>=0&&c.l.state==="normal"&&lineKey(c.l)!==pinned&&lineKey(c.l)!==hoverNm);
  if(cand.length)planWalk(cand[Math.random()*cand.length|0])}
function posOf(ch){const r=ch.rt;return!r||r.mode==="seat"?[ch.sx,ch.sy]:[Math.round(L.X0+(r.u-r.v)*8),Math.round(L.Y0+(r.u+r.v)*4)]}
function step(dt){if(!L||!L.grid)return false;let act=false;const hold=pinned||hoverNm;
  for(const ch of L.chars){const r=ch.rt;if(!r)continue;
    if(r.mode==="seat"){if(r.cool>0)r.cool-=dt;continue}
    act=true;if(lineKey(ch.l)===hold)continue;   // 滑過／釘選的人原地停下，方便點
    if(r.mode==="pause"){r.wait-=dt;if(r.wait<=0){r.pts.reverse();r.i=0;r.ret=true;r.mode="walk";r.visit=null}continue}
    let rem=SPEED*dt;
    while(rem>0&&r.i<r.pts.length-1){const n=r.pts[r.i+1],du=n[0]-r.u,dv=n[1]-r.v,d=Math.hypot(du,dv);
      if(d>1e-6)r.face=faceOf((du-dv)*8,(du+dv)*4);
      if(d<=rem){r.u=n[0];r.v=n[1];r.i++;rem-=d;r.dist+=d}else{r.u+=du/d*rem;r.v+=dv/d*rem;r.dist+=rem;rem=0}}
    if(r.i>=r.pts.length-1){
      if(r.ret){Object.assign(r,{mode:"seat",u:ch.su,v:ch.sv,face:ch.face,target:null,cool:9000+Math.random()*14000})}
      else{r.mode="pause";r.wait=1800+Math.random()*2600;const p=posOf(ch);r.face=r.visit?faceOf(r.visit.sx-p[0],r.visit.sy-p[1]):["S","SE","SW","E","W"][Math.random()*5|0]}}}
  nextPick-=dt;if(nextPick<=0){nextPick=1200+Math.random()*2400;startOne()}
  return act}

/* ── 每格繪製 ── */
const DIG={0:"111101101101111",1:"010110010010111",2:"111001111100111",3:"111001111001111",4:"101101111001001",5:"111100111001111",6:"111100111101111",7:"111001010010010",8:"111101111101111",9:"111101111001111","-":"000000111000000"};
function digits(x,y,s,col,sh){ctx.fillStyle=col;[...s].forEach((d,i)=>{const b=DIG[d]||DIG["-"];for(let j=0;j<15;j++)if(b[j]==="1"){const px=x+i*4+j%3;ctx.fillRect(px,y+Math.floor(j/3)+sh(x+i*4+1),1,1)}})}
const D=(x,y,w,h,col)=>{ctx.fillStyle=col;ctx.fillRect(x,y,w,h)};
function zzz(x,y){D(x,y,4,1,"#dfe9f0");D(x+2,y+1,1,1,"#dfe9f0");D(x+1,y+2,1,1,"#dfe9f0");D(x,y+3,4,1,"#dfe9f0")}
function drawChar(ch,f){const {l,lk}=ch,seed=lk.shift;
  if(l.state==="down"){const d=ch.down,s=downSprite(lk,(f>>>3)&1);ctx.fillStyle="rgba(0,0,0,.3)";ctx.fillRect(d.x-10,d.y,21,2);ctx.drawImage(s,d.x-14,d.y-11);zzz(d.x+11,d.y-8+((f>>>3)&1));return}
  const r=ch.rt,seated=!r||r.mode==="seat",p=posOf(ch),x=p[0],y=p[1],thin=l.state==="tired",frozen=lineKey(l)===(pinned||hoverNm);
  let pose="stand",k=0,wf=-1;
  if(seated){const kd=kindOf(l,lk,f);pose=kd[0];k=kd[1]}else if(r.mode==="walk"&&!frozen){pose="walk";wf=Math.floor(r.dist/.24)&1}
  ctx.drawImage(personSprite(lk,seated?ch.face:r.face,pose,k,thin,wf),x-OX,y-OY);
  const hy=y-(seated?18:20);
  if(thin){ // 趴桌＋喪氣縱線
    for(let i=-3;i<=3;i+=2){const h=2+((i*7+(f>>>1)+seed)&1);D(x+i,hy-1-h+3,1,h,"rgba(84,70,150,.85)")}
    if(((f+seed)&31)<14){D(x+5,hy-2,1,1,"#e8dc90");D(x+7,hy-2,1,1,"#e8dc90")}return}
  if(pose==="work"){for(let q=0;q<2;q++){const bx=x-2+q*4;for(let i=0;i<4;i++){const ox=Math.round(Math.sin((i+f*.9+q*2+seed)/1.7)),a=(.7-i*.15).toFixed(2);ctx.fillStyle=`rgba(240,246,244,${a})`;ctx.fillRect(bx+ox,hy-2-i,1,1)}}}
  if(pose==="doze"){const q=(f+seed)%24;zzz(x+5+(q>>>4),hy-4-(q>>>3))}
  if(r&&r.mode==="pause"&&r.visit&&((f+seed)>>>3)%3!==2){const bx=x+3,by=hy-8;D(bx-1,by-1,10,7,"#0a1116");D(bx,by,8,5,"#f4efe0");D(bx+1,by+5,2,2,"#f4efe0");D(bx,by+6,1,1,"#0a1116");
    const nd=1+((f>>>2)%3);for(let i=0;i<nd;i++)D(bx+1+i*2,by+2,1,1,"#30343c")}}
// 魂魄：從倒地的身體上方飄起
function ghost(ch,f){const sx=ch.down.x-4+Math.round(Math.sin((f+ch.lk.shift)/3)*1.5),sy=ch.down.y-19+Math.round(Math.sin((f+ch.lk.shift)/5)*1.5);
  D(sx,sy-1,7,8,"#0a1116");D(sx+1,sy-2,5,1,"#0a1116");D(sx+1,sy-1,5,1,"#f4fbff");D(sx+1,sy,5,5,"#f4fbff");D(sx+2,sy+5,3,1,"#d6e9f2");D(sx+2+((f>>>2)&1),sy+6,2,1,"#8fb4c6");
  D(sx+2,sy+1,1,2,"#1c2a33");D(sx+4,sy+1,1,2,"#1c2a33");D(sx+2,sy+3,3,1,"#6b8ea0");
  const zq=(f+ch.lk.shift)%24;zzz(sx+8+(zq>>>4),sy-2-(zq>>>3))}
function draw(){if(!bg||!L)return;const f=frame;
  ctx.drawImage(bg,0,0);
  if(L.cal){const cl=L.cal,sh=x=>cl.sh[x-cl.x]||0,dk=(x,y,w,col)=>{for(let i=0;i<w;i++)D(x+i,y+sh(x+i),1,1,col)},dl=window.__sceneDays,txt=dl==null?"--":String(Math.max(0,dl)).padStart(2,"0");
    digits(cl.x+3,cl.y+6,txt.slice(-2),"#b83a34",sh);const y2=cl.y+cl.h-3;for(let i=0;i<3;i++)dk(cl.x+2+i*3,y2,2,"#a79e85")}
  // 由後往前（依地面 y）畫：桌、凳、椅、人
  const it=[];
  for(const t of L.tables){const tp=tableParts(t);for(const s of tp.slices)it.push([s.key,0,s])}
  for(const ch of L.chars){it.push([ch.sy-.3,ch.master?2:3,ch]);it.push([ch.l.state==="down"?ch.down.y:posOf(ch)[1],4,ch])}
  it.sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
  for(const [,k,o] of it){
    if(k===0)ctx.drawImage(o.c,o.x,o.y);
    else if(k===2)ctx.drawImage(chairSprite(),o.sx-9,o.sy-24);
    else if(k===3)ctx.drawImage(stoolSprite(),o.sx-7,o.sy-9);
    else drawChar(o,f)}
  for(const ch of L.chars)if(ch.l.state==="down")ghost(ch,f);
  ctx.save();ctx.globalCompositeOperation="lighter";ctx.globalAlpha=(calm.matches?1:.92+.08*Math.sin(f/5));ctx.drawImage(glow,0,0);ctx.restore();
}

/* ── 名稱與說明（DOM，字才清楚；點、滑過、鍵盤焦點都會顯示）；按鈕跟著人物位置移動 ── */
function rosterSig(){return JSON.stringify([box.clientWidth,box.clientHeight,(lines||[]).map(x=>[lineKey(x),x.name,x.state,x.status,x.pct,x.model,x.reason,x.updated,x.project_id]),failed])}
function tipHtml(l){const pct=l.pct==null?"無資料":`${Math.round(l.pct)}%（${(l.used_tokens/10000).toFixed(1)} 萬／${Math.round(l.limit_tokens/10000)} 萬）`,e=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  return`<b>${e(projectLabel(l.project_id)+l.name)}</b><em class="${l.state}">${WORD[l.state]}</em><div>脈絡 <span>${e(pct)}</span></div><div>模型 <span>${e(l.model||"未知")}</span></div><div>原因 <span>${e(l.reason)}</span></div><div>活動 <span>${SW[l.status]||e(l.status)}${l.updated?"，更新 "+e(l.updated.slice(11,16)):""}</span></div>`}
function showTip(btn){const ch=(L?L.chars:listChars).find(c=>lineKey(c.l)===btn.dataset.nm);if(!ch)return;tip.innerHTML=tipHtml(ch.l);tip.hidden=false;
  const r=btn.getBoundingClientRect(),b=box.getBoundingClientRect(),tw=tip.offsetWidth,th=tip.offsetHeight;
  let x=r.left-b.left+r.width/2-tw/2,y=r.top-b.top-th-4;if(y<2)y=Math.min(r.bottom-b.top+4,box.clientHeight-th-2);
  tip.style.left=Math.max(2,Math.min(box.clientWidth-tw-2,x))+"px";tip.style.top=Math.max(2,y)+"px";
  box.querySelectorAll(".sc-c.on").forEach(n=>n.classList.remove("on"));btn.classList.add("on")}
function hideTip(){if(pinned)return;tip.hidden=true;box.querySelectorAll(".sc-c.on").forEach(n=>n.classList.remove("on"))}
// 命中範圍（畫布像素）：坐／站＝人形；趴桌＝人形；倒地＝身體＋上方魂魄
function hitBox(ch){if(ch.l.state==="down"){const d=ch.down;return[d.x-11,d.y-22,d.x+11,d.y+2]}
  const p=posOf(ch),seated=!ch.rt||ch.rt.mode==="seat";return[p[0]-7,p[1]-(seated?19:21),p[0]+7,p[1]+2]}
// 名牌錨點（CSS 像素，中心 x 與上緣 y）：桌後的人放頭上、其餘放腳下；總控放桌前；倒地放身體下
function labAnchor(ch,P){const lh=ch.lh||21;
  if(ch.l.state==="down")return[ch.down.x*P,(ch.down.y+3)*P];
  if(ch.above)return[ch.sx*P,(ch.sy-22)*P-lh];
  return[ch.sx*P,(ch.sy+3)*P]}
function syncButtons(){if(!L)return;const P=L.P;
  for(const ch of L.chars){if(!ch.btn)continue;const r=hitBox(ch),k=r.join(",");
    const away=ch.rt&&ch.rt.mode!=="seat",vis=ch.labOK&&!away?"visible":"hidden";
    if(k!==ch.bk){ch.bk=k;const s=ch.btn.style;s.left=r[0]*P+"px";s.top=r[1]*P+"px";s.width=(r[2]-r[0])*P+"px";s.height=(r[3]-r[1])*P+"px";
      s.zIndex=String(ch.l.state==="down"?1+ch.down.y:400+r[3]);   // 前面的人蓋後面的人；倒地範圍較大，讓給活人
      const a=labAnchor(ch,P);ch.lab.style.left=(a[0]-r[0]*P)+"px";ch.lab.style.top=(a[1]-r[1]*P)+"px"}
    if(ch.lab.style.visibility!==vis)ch.lab.style.visibility=vis}}
function buildButtons(chars,P){const focus=document.activeElement&&box.contains(document.activeElement)?document.activeElement.dataset.nm:null,e=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  layer.innerHTML=chars.map(ch=>{const l=ch.l;
    return`<button type="button" class="sc-c st-${l.state}${l.master?" master":""}" data-nm="${e(lineKey(l))}" aria-label="${e(projectLabel(l.project_id)+l.name)}，${WORD[l.state]}，${l.pct==null?"脈絡無資料":"脈絡 "+Math.round(l.pct)+"%"}。${e(l.reason)}"><span class="sc-n"${P?` style="visibility:hidden;width:auto;max-width:${activeProject==="*"?80:96}px;padding:1px 5px 2px"`:""}><u title="${e(projectLabel(l.project_id)+l.name)}">${e(sceneLabel(l))}</u><s><em style="width:${Math.min(100,l.pct||0)}%"></em></s><span class="sc-w">${l.pct==null?"":Math.round(l.pct)+"%　"}${WORD[l.state]}</span></span></button>`}).join("");
  if(P){const btns=[...layer.children];chars.forEach((ch,i)=>{ch.btn=btns[i];ch.lab=btns[i].firstElementChild;ch.bk=null;ch.lw=ch.lab.offsetWidth;ch.lh=ch.lab.offsetHeight;ch.labOK=false});
    // 名牌不互相重疊、不蓋臉、不壓圖例；放不下就只在滑過時看提示
    const rank=ch=>ch.master?0:ch.l.state==="down"?1:ch.l.state==="tired"?2:3,placed=[],faces=chars.map(c=>c.l.state==="down"?[(c.down.x-10)*P,(c.down.y-21)*P,(c.down.x+10)*P,c.down.y*P,c]:[(c.sx-5)*P,(c.sy-21)*P,(c.sx+5)*P,(c.sy-12)*P,c]);
    for(const ch of [...chars].sort((a,b)=>rank(a)-rank(b))){const a=labAnchor(ch,P),r=[a[0]-ch.lw/2,a[1],a[0]+ch.lw/2,a[1]+ch.lh];
      if(r[0]<1||r[1]<1||r[2]>box.clientWidth-1||r[3]>box.clientHeight-1)continue;
      if(L.lgc&&ov(r,L.lgc,2))continue;if(placed.some(q=>ov(r,q,2)))continue;if(faces.some(q=>q[4]!==ch&&ov(r,q,-1)))continue;
      placed.push(r);ch.labOK=true}
    syncButtons()}
  if(focus){const b=[...layer.children].find(n=>n.dataset.nm===focus);b&&b.focus({preventScroll:true})}
  const cur=pinned||hoverNm;if(cur){const b=[...layer.children].find(n=>n.dataset.nm===cur);if(b)showTip(b);else{pinned=null;hoverNm=null;tip.hidden=true}}}
layer.addEventListener("mouseover",e=>{const b=e.target.closest(".sc-c");if(b){hoverNm=b.dataset.nm;if(!pinned)showTip(b)}});
layer.addEventListener("mouseleave",()=>{hoverNm=null;hideTip()});
layer.addEventListener("focusin",e=>{const b=e.target.closest(".sc-c");if(b){hoverNm=b.dataset.nm;if(!pinned)showTip(b)}});
layer.addEventListener("focusout",e=>{if(!box.contains(e.relatedTarget)){hoverNm=null;hideTip()}});
layer.addEventListener("click",e=>{const b=e.target.closest(".sc-c");if(!b)return;e.stopPropagation();const nm=b.dataset.nm;if(pinned===nm){pinned=null;hideTip()}else{pinned=nm;showTip(b)}});
document.addEventListener("click",e=>{if(pinned&&!box.contains(e.target)){pinned=null;hideTip()}});

/* ── 資料 ── */
function demoLines(){const names=["總控2","簡報修改","廠區動畫","3d互動","滑軌3d","滑軌互動","FBC腳本","手拿板說明","光雕D-1","展板排版","知識查證","導覽腳本","影片審閱","施工圖對照","多餘的線一","多餘的線二"];
  const n=Math.max(1,parseInt(Q.get("n")||"14",10)||14),all=Q.get("all");
  const plan=[["busy","normal",38],["busy","normal",52],["idle","normal",12],["busy","tired",74],["idle","tired",82],["idle","down",null],["shell","normal",21],["idle","normal",9],["busy","down",93],["busy","normal",44],["idle","normal",31],["busy","tired",71],["idle","down",12],["idle","normal",27],["idle","normal",5],["idle","normal",6]];
  const out=[];for(let i=0;i<n;i++){let [status,state,pct]=plan[i%plan.length];
    if(all==="busy"){status="busy";state="normal";pct=40}if(all==="idle"){status="idle";state="normal";pct=20}if(all==="tired"){state="tired";pct=75;status=i%2?"busy":"idle"}if(all==="down"){state="down";pct=92}
    const reason=state==="down"?(pct==null?"行程已不存在，這條要重開":pct>=90?`脈絡 ${pct}% 逼近上限，要立刻壓縮或重開`:"最後一筆紀錄是 API 拒絕，這條已無法繼續，要重開"):state==="tired"?`脈絡 ${pct}%，接近自動壓縮，建議現在壓縮`:`脈絡 ${pct}%`;
    out.push({line_id:"demo-"+i,project_id:i<10?"demo-south":"demo-study",name:names[i%names.length]+(i>=names.length?i:""),status,model:i%3===2?"claude-sonnet-5-5":"claude-opus-5-5",used_tokens:pct==null?null:pct*10000,limit_tokens:1000000,pct,state,reason,project:i<10?"南科再生水廠":"3Dstudy",updated:new Date(Date.now()-new Date().getTimezoneOffset()*60000).toISOString().slice(0,19)})}
  return out}
function prepare(raw){const rank={down:0,tired:1,normal:2};let arr=raw.filter(l=>DEMO||activeProject==="*"||l.project_id===activeProject);hidden=0;
  if(arr.length>MAX){const keep=arr.map((l,i)=>[l,i]).sort((a,b)=>(/總控/.test(b[0].name)-/總控/.test(a[0].name))||(rank[a[0].state]-rank[b[0].state])||(a[1]-b[1])).slice(0,MAX).map(x=>x[1]).sort((a,b)=>a-b);hidden=arr.length-MAX;arr=keep.map(i=>arr[i])}
  const mi=arr.findIndex(l=>/總控/.test(l.name));
  return arr.map((l,i)=>Object.assign({},l,{master:i===mi}))}
function legend(){const list=lines||[],c=s=>list.filter(l=>l.state===s).length;
  lg.innerHTML=(DEMO?`<span class="sc-demo">示範假資料</span>`:"")+`<span class="l-n"><i></i>正常 <b>${failed?"—":c("normal")}</b></span><span class="l-t"><i></i>需要壓縮 <b>${failed?"—":c("tired")}</b></span><span class="l-d"><i></i>需要重啟 <b>${failed?"—":c("down")}</b></span>`+(hidden?`<span class="sc-more">另 ${hidden} 條</span>`:"")}
function apply(force){legend();const s=rosterSig();if(!force&&s===sig){kick();return}sig=s;
  msg.hidden=!(failed||(lines&&!lines.length));msg.className="sc-msg"+(failed?"":" calm");msg.textContent=failed?"讀不到對話資料":"目前沒有對話";
  const list=failed?[]:(lines||[]),old=L;
  L=place(list);
  if(!L){ // 放不下：改名單
    box.classList.add("list");listChars=list.map(l=>({l}));bg=null;buildButtons(listChars,0);stop();return}
  box.classList.remove("list");
  cv.width=L.W;cv.height=L.H;cv.style.width=L.W*L.P+"px";cv.style.height=L.H*L.P+"px";
  if(sprites.size>3000)sprites.clear();
  const r=paintRoom(L);bg=r.c;glow=r.gc;buildGrid(L);
  // 同一版面（名單與尺寸不變）時延續走動狀態，不會每次資料更新就瞬移回座
  for(const ch of L.chars){const o=old&&old.key===L.key?old.chars.find(c=>lineKey(c.l)===lineKey(ch.l)):null;
    ch.rt=o&&o.rt&&o.l.state==="normal"&&ch.l.state==="normal"?o.rt:{mode:"seat",u:ch.su,v:ch.sv,face:ch.face,dist:0,target:null,cool:ch.l.state==="normal"?Math.random()*5000:1e12};
    if(ch.l.state!=="normal")ch.rt.cool=1e12}
  buildButtons(L.chars,L.P);
  draw();kick()}
async function pull(){if(pulling)return;lastPull=Date.now();
  if(DEMO){rawLines=demoLines();lines=prepare(rawLines);failed=false;apply();return}
  pulling=true;
  try{const r=await fetch("/api/lines",{cache:"no-store"});if(!r.ok)throw new Error("http");const j=await r.json();if(!j||j.ok!==true||!Array.isArray(j.lines))throw new Error("shape");rawLines=j.lines;lines=prepare(rawLines);failed=false}
  catch(e){failed=true;lines=null;hidden=0;pinned=null;tip.hidden=true}
  finally{pulling=false}
  apply()}
function visible(){return!document.hidden&&!qb.hidden&&box.offsetParent!==null}
function running(){return visible()&&!calm.matches&&!!L&&!!bg}
function loop(ts){raf=0;if(!running())return;const dt=lastTs?Math.min(100,ts-lastTs):16;lastTs=ts;
  const moving=step(dt);let tick=false;if(ts-last>=STEP){last=ts;frame=(frame+1)%1000000;tick=true}
  if(moving||tick){draw();syncButtons()}
  raf=requestAnimationFrame(loop)}
function kick(){if(!raf&&running()){lastTs=0;raf=requestAnimationFrame(loop)}}
function stop(){if(raf){cancelAnimationFrame(raf);raf=0}}
function days(){try{const p=deadlineProject();window.__sceneDays=p&&p.deadline?Math.ceil((new Date(p.deadline)-new Date())/86400000):null}catch(e){window.__sceneDays=null}}
function wake(){days();if(!visible()){stop();return}if(Date.now()-lastPull>=POLL||(!lines&&!failed))pull();else{if(L&&bg)draw();kick()}}
document.addEventListener("projectchange",()=>{pinned=null;hoverNm=null;tip.hidden=true;lines=prepare(rawLines||[]);days();apply(true);wake()});
document.addEventListener("visibilitychange",wake);
new MutationObserver(wake).observe(qb,{attributes:true,attributeFilter:["hidden"]});
new ResizeObserver(()=>{if(visible()&&(lines||failed))apply()}).observe(box);
if(calm.addEventListener)calm.addEventListener("change",()=>{if(L&&bg)draw();kick()});
setInterval(()=>{days();if(visible())pull()},POLL);
window.__scene={frame:()=>frame,running,walkers:()=>L?L.chars.filter(c=>c.rt&&c.rt.mode!=="seat").map(c=>({name:c.l.name,mode:c.rt.mode,pos:posOf(c),face:c.rt.face})):[],chars:()=>L?L.chars.map(c=>({line_id:c.l.line_id,project_id:c.l.project_id,name:c.l.name,state:c.l.state,face:c.face,seat:[c.sx,c.sy],down:c.l.state==="down"?[c.down.x,c.down.y]:null,box:hitBox(c),lab:!!c.labOK})):[],P:()=>L&&L.P,tables:()=>L?{f:L.f,t:L.tables.map(t=>({p:t.p,L:t.L,W:t.W,u0:t.u0,v0:t.v0}))}:null};
setTimeout(wake,0);
})();
/*SCENE-JS-END*/
