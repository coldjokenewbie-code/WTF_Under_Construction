"""One-item behavior stays within the review document; sandbox also applies to new tabs."""
ONE_ITEM_JS = r'''<script id="__oi">(function(){
function hide(c){c.style.display='none';c.setAttribute('data-oi','1');}
function overlay(c){var s=getComputedStyle(c);return s.position==='fixed'||/lightbox|modal|^lb$|overlay/i.test((c.id||'')+' '+(c.className||''));}
function hideOthers(x){var a=x;while(a&&a.parentElement&&a!==document.body){var p=a.parentElement;
 [].slice.call(p.children).forEach(function(c){if(c===a||c.contains(x)||/^(SCRIPT|STYLE|LINK|META)$/.test(c.tagName)||overlay(c))return;
 if((c.id&&c.tagName===x.tagName)||c.querySelector('img,figure,table,section,article')||/^(SECTION|ARTICLE|FIGURE|TABLE|NAV|ASIDE)$/.test(c.tagName))hide(c);});a=p;}}
function apply(){[].slice.call(document.querySelectorAll('[data-oi]')).forEach(function(e){e.style.display='';e.removeAttribute('data-oi');});
 var bar=document.getElementById('__oi_bar');if(bar)bar.remove();var h=decodeURIComponent(location.hash.slice(1));if(!h)return;
 var t=document.getElementById(h);if(!t)return;var x=t;while(x&&x.parentElement&&x.parentElement!==document.body.parentElement){
 var p=x.parentElement,s=[].slice.call(p.children).filter(function(c){return c!==x&&c.id&&c.tagName===x.tagName;});if(x.id&&s.length)break;x=x.parentElement;}
 if(!x||!x.id||!x.parentElement)return;hideOthers(x);
 [].slice.call(document.querySelectorAll('nav,.toc,#toc,[class*="toc"],[class*="index"]')).forEach(function(n){if(!n.contains(x))hide(n);});
 bar=document.createElement('div');bar.id='__oi_bar';bar.style.cssText='position:fixed;top:8px;right:8px;z-index:99999;background:#0b6fa4;color:#fff;padding:6px 12px;border-radius:6px;font:14px/1.4 sans-serif;cursor:pointer';
 bar.textContent='只顯示這一項｜看全部';bar.onclick=function(){history.replaceState(null,'',location.pathname+location.search);apply();window.scrollTo(0,0);};document.body.appendChild(bar);x.scrollIntoView();}
window.addEventListener('hashchange',apply);if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',apply);else apply();})();</script>'''

REVIEW_CSP = "sandbox allow-scripts; default-src 'self' data: blob: https:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; style-src 'self' 'unsafe-inline' https:; frame-ancestors 'self'; base-uri 'none'; form-action 'none'"


def inject_one_item(body):
    if b'id="__oi"' in body:
        return body
    script = ONE_ITEM_JS.encode()
    index = body.lower().rfind(b"</body>")
    return body[:index] + script + body[index:] if index >= 0 else body + script
