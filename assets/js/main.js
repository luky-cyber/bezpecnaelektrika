document.documentElement.classList.add("js-ready");
(()=>{const q=(s,c=document)=>c.querySelector(s),qa=(s,c=document)=>[...c.querySelectorAll(s)];const btn=q('[data-menu-button]'),nav=q('[data-nav]');if(btn&&nav){btn.addEventListener('click',()=>{const open=nav.classList.toggle('open');btn.setAttribute('aria-expanded',String(open))});qa('a',nav).forEach(a=>a.addEventListener('click',()=>{nav.classList.remove('open');btn.setAttribute('aria-expanded','false')}))}
qa('.faq-question').forEach(b=>b.addEventListener('click',()=>{const item=b.closest('.faq-item'),open=item.classList.toggle('open');b.setAttribute('aria-expanded',String(open))}));
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;if(!reduced&&'IntersectionObserver'in window){const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('visible');io.unobserve(e.target)}}),{threshold:.12});qa('.reveal').forEach(el=>io.observe(el))}else qa('.reveal').forEach(el=>el.classList.add('visible'));
const sections=qa('main section[id]'),links=qa('.nav a[href^="#"]');if('IntersectionObserver'in window){const nio=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){links.forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+e.target.id))}}),{rootMargin:'-30% 0px -60% 0px'});sections.forEach(s=>nio.observe(s))}
const top=q('[data-top]');if(top){addEventListener('scroll',()=>top.classList.toggle('show',scrollY>700),{passive:true});top.addEventListener('click',()=>scrollTo({top:0,behavior:reduced?'auto':'smooth'}))}
})();


document.addEventListener("DOMContentLoaded",()=>{
  const b=document.querySelector(".nav-toggle");
  const n=document.querySelector("#main-nav");
  if(!b||!n) return;
  const close=()=>{n.classList.remove("open");b.setAttribute("aria-expanded","false");b.setAttribute("aria-label","Otvoriť menu");};
  b.addEventListener("click",(e)=>{
    e.preventDefault();
    const open=!n.classList.contains("open");
    n.classList.toggle("open",open);
    b.setAttribute("aria-expanded",String(open));
    b.setAttribute("aria-label",open?"Zavrieť menu":"Otvoriť menu");
  });
  n.querySelectorAll("a").forEach(a=>a.addEventListener("click",close));
  document.addEventListener("keydown",e=>{if(e.key==="Escape") close();});
});

document.addEventListener("DOMContentLoaded",()=>{
  const b=document.querySelector(".nav-toggle"), n=document.querySelector("#main-nav");
  if(!b||!n) return;
  document.addEventListener("click",(e)=>{
    if(n.classList.contains("open") && !n.contains(e.target) && !b.contains(e.target)){
      n.classList.remove("open");
      b.setAttribute("aria-expanded","false");
      b.setAttribute("aria-label","Otvoriť menu");
    }
  });
});

/* v0.3.8 */
document.addEventListener("DOMContentLoaded",()=>{
  const html=document.documentElement;
  const themeBtn=document.querySelector(".theme-toggle");
  const stored=localStorage.getItem("be-theme");
  const systemPrefersLight=window.matchMedia&&window.matchMedia("(prefers-color-scheme: light)").matches;
  const apply=(mode)=>{
    const resolved=mode==="light"?"light":"dark";
    html.dataset.theme=resolved;
    if(themeBtn){
      themeBtn.setAttribute("aria-label",resolved==="dark"?"Prepnúť na svetlý režim":"Prepnúť na tmavý režim");
      themeBtn.title=resolved==="dark"?"Svetlý režim":"Tmavý režim";
      const icon=themeBtn.querySelector(".theme-icon");
      if(icon) icon.textContent=resolved==="dark"?"☀":"☾";
    }
  };
  apply(stored==="light"||stored==="dark" ? stored : (systemPrefersLight?"light":"dark"));
  if(themeBtn) themeBtn.addEventListener("click",()=>{
    const next=html.dataset.theme==="dark"?"light":"dark";
    localStorage.setItem("be-theme",next); apply(next);
  });

  const more=document.querySelector(".nav-more");
  const moreBtn=document.querySelector(".more-toggle");
  if(more&&moreBtn){
    moreBtn.addEventListener("click",(e)=>{
      e.stopPropagation();
      const open=more.classList.toggle("open");
      moreBtn.setAttribute("aria-expanded",String(open));
    });
    document.addEventListener("click",(e)=>{
      if(more.classList.contains("open")&&!more.contains(e.target)){more.classList.remove("open");moreBtn.setAttribute("aria-expanded","false");}
    });
    document.addEventListener("keydown",(e)=>{if(e.key==="Escape"){more.classList.remove("open");moreBtn.setAttribute("aria-expanded","false");}});
  }
});
