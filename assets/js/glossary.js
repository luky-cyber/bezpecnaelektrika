document.addEventListener("DOMContentLoaded",()=>{
  const input=document.querySelector("#glossary-search");
  const buttons=[...document.querySelectorAll("[data-glossary-filter]")];
  const entries=[...document.querySelectorAll(".dictionary-entry")];
  const empty=document.querySelector("#glossary-empty");
  if(!input||!entries.length)return;
  let filter="all";
  const apply=()=>{
    const q=input.value.trim().toLocaleLowerCase("sk");let shown=0;
    entries.forEach(e=>{const okCat=filter==="all"||e.dataset.category===filter;const hay=(e.dataset.search||e.textContent).toLocaleLowerCase("sk");const okQ=!q||hay.includes(q);const show=okCat&&okQ;e.hidden=!show;if(show)shown++;});
    if(empty)empty.hidden=shown!==0;
  };
  const openHash=()=>{
    const key=decodeURIComponent(location.hash.replace(/^#/,"")); if(!key)return;
    let target=document.getElementById(key);
    if(!target) target=entries.find(e=>e.dataset.oldId===key);
    if(target&&target.matches("details")){
      target.hidden=false; target.open=true;
      target.querySelector("summary")?.setAttribute("aria-current","location");
    }
  };
  input.addEventListener("input",apply);
  buttons.forEach(b=>b.addEventListener("click",()=>{filter=b.dataset.glossaryFilter;buttons.forEach(x=>x.classList.toggle("active",x===b));apply();}));
  window.addEventListener("hashchange",openHash);
  openHash();
});
