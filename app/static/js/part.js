(() => {
  "use strict";
  const KEY="dimensionRateHistory", MERGE_KEY="dimensionRatePartGroups";
  const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));
  const pct=v=>Number.isFinite(Number(v))?Number(v).toLocaleString("pt-BR",{minimumFractionDigits:2,maximumFractionDigits:2})+"%":"—";
  const read=k=>{try{return JSON.parse(localStorage.getItem(k)||"[]")}catch{return[]}};
  const merges=()=>{try{return JSON.parse(localStorage.getItem(MERGE_KEY)||"{}")}catch{return{}}};
  const key=x=>`${x.filename||""}|${x.reportNumber||""}|${x.date||""}`;
  const params=new URLSearchParams(location.search), id=params.get("group")||"";
  const history=read(KEY).map(x=>{const d=x.data?.document||{};return {...x,client:x.client||d.client||"—",metrologist:x.metrologist||d.metrologist||"—",partNumber:x.partNumber||d.part_number||"SEM PART NUMBER",reportNumber:x.reportNumber||d.report_number||"—"};}); const allMerges=merges();
  let group;
  if(id.startsWith("merge:")) group=allMerges[id.slice(6)] ? {label:allMerges[id.slice(6)].label,parts:allMerges[id.slice(6)].parts} : null;
  else { const part=decodeURIComponent(id.replace(/^part:/,"")); group={label:part,parts:[part]}; }
  const items=history.filter(x=>group?.parts?.includes(String(x.partNumber||"SEM PART NUMBER").trim().toUpperCase()));
  const title=document.getElementById("partTitle"), subtitle=document.getElementById("partSubtitle"), overview=document.getElementById("partOverview"), list=document.getElementById("partReportsList"), search=document.getElementById("partSearch");
  title.textContent=group?.label||"Família não encontrada";
  subtitle.textContent=group?`${group.parts.join(" · ")} · ${items.length} relatório(s)`:"O grupo solicitado não existe mais.";
  const rates=items.map(x=>Number(x.rate)).filter(Number.isFinite), avg=rates.length?rates.reduce((a,b)=>a+b,0)/rates.length:null;
  overview.innerHTML=group?`<article><span>PART NUMBERS</span><b>${group.parts.length}</b></article><article><span>RELATÓRIOS</span><b>${items.length}</b></article><article><span>RATE MÉDIO</span><b>${pct(avg)}</b></article><article><span>REPROVAÇÕES</span><b>${items.reduce((n,x)=>n+(Number(x.rejected)||0),0)}</b></article>`:"";
  function render(){const q=(search.value||"").toLowerCase();const rows=items.filter(x=>[x.reportNumber,x.filename,x.client,x.metrologist,x.revision,x.piece].some(v=>String(v||"").toLowerCase().includes(q)));list.innerHTML=rows.length?rows.map((x,i)=>`<article class="part-report-row"><div class="part-report-number">${String(i+1).padStart(2,"0")}</div><div class="part-report-info"><span>${esc(x.partNumber||"SEM PART NUMBER")}</span><h3>${esc(x.reportNumber||x.filename||"Relatório")}</h3><p>${esc(x.date||"")} · ${esc(x.client||"Cliente não informado")} · ${esc(x.metrologist||"Metrologista não informado")}</p></div><div class="part-report-metric"><small>RATE</small><b>${pct(x.rate)}</b></div><div class="part-report-metric"><small>REPROVAÇÕES</small><b>${Number(x.rejected)||0}</b></div><button class="btn btn-primary part-open" data-key="${esc(key(x))}" type="button"><i class="fa-solid fa-arrow-right"></i> Abrir</button></article>`).join(""): `<div class="part-empty"><i class="fa-solid fa-file-circle-xmark"></i><b>Nenhum relatório encontrado</b></div>`;list.querySelectorAll(".part-open").forEach(b=>b.addEventListener("click",()=>{const x=items.find(x=>key(x)===b.dataset.key);if(x?.data){sessionStorage.setItem("dimensionRateReport",JSON.stringify(x.data));location.href="/report";}}));}
  search.addEventListener("input",render); render();
})();
