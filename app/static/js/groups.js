(() => {
  "use strict";
  const KEY = "dimensionRateHistory";
  const MERGE_KEY = "dimensionRatePartGroups";
  const esc = v => String(v ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));
  const pct = v => Number.isFinite(Number(v)) ? Number(v).toLocaleString("pt-BR", {minimumFractionDigits:2, maximumFractionDigits:2}) + "%" : "—";
  const read = () => { try { return JSON.parse(localStorage.getItem(KEY) || "[]").map(x => { const d=x.data?.document||{}; return {...x, client:x.client||d.client||"—", metrologist:x.metrologist||d.metrologist||"—", piece:x.piece||d.piece||"—", partNumber:x.partNumber||d.part_number||"SEM PART NUMBER", reportNumber:x.reportNumber||d.report_number||"—"}; }); } catch { return []; } };
  const save = items => localStorage.setItem(KEY, JSON.stringify(items));
  const readMerges = () => { try { return JSON.parse(localStorage.getItem(MERGE_KEY) || "{}"); } catch { return {}; } };
  const saveMerges = x => localStorage.setItem(MERGE_KEY, JSON.stringify(x));
  const normalize = v => String(v || "SEM PART NUMBER").trim().toUpperCase();
  const itemKey = x => `${x.filename || ""}|${x.reportNumber || ""}|${x.date || ""}`;

  const search = document.getElementById("groupSearch");
  const grid = document.getElementById("groupsGrid");
  const searchResults = document.getElementById("searchResults");
  const empty = document.getElementById("groupsEmpty");
  const analyze = document.getElementById("analyzeSelectedGroups");
  const filterButton = document.getElementById("filterButton");
  const filterPanel = document.getElementById("filterPanel");
  const filterClient = document.getElementById("filterClient");
  const filterMetrologist = document.getElementById("filterMetrologist");
  const sortReports = document.getElementById("sortReports");
  const filterCount = document.getElementById("filterCount");
  const catalogActions = document.getElementById("catalogActions");
  const selectedPartCount = document.getElementById("selectedPartCount");
  const mergeModal = document.getElementById("mergeModal");
  const mergeSelection = document.getElementById("mergeSelection");
  const mergeName = document.getElementById("mergeName");
  let visibleItems = [];
  let currentGroups = [];

  const dateScore = x => {
    const d = Date.parse(String(x?.date || "").replace(/(\d{2})\/(\d{2})\/(\d{4})/, "$2/$1/$3"));
    return Number.isFinite(d) ? d : 0;
  };
  const partBase = x => normalize(x.partNumber);

  function getGroups(all) {
    const merges = readMerges();
    const map = new Map();
    all.forEach(item => {
      const part = partBase(item);
      const merge = Object.entries(merges).find(([,v]) => Array.isArray(v.parts) && v.parts.includes(part));
      const id = merge ? `merge:${merge[0]}` : `part:${part}`;
      if (!map.has(id)) map.set(id, {id, label: merge?.[1]?.label || part, parts: merge?.[1]?.parts || [part], items: []});
      map.get(id).items.push(item);
    });
    return [...map.values()];
  }

  function fillFilters(all) {
    const clients = [...new Set(all.map(x => x.client).filter(v => v && v !== "—"))].sort((a,b)=>a.localeCompare(b,"pt-BR"));
    const metrologists = [...new Set(all.map(x => x.metrologist).filter(v => v && v !== "—"))].sort((a,b)=>a.localeCompare(b,"pt-BR"));
    const fill = (el, values) => { const current = el.value; el.innerHTML = '<option value="">Todos</option>' + values.map(v => `<option value="${esc(v)}">${esc(v)}</option>`).join(""); if(values.includes(current)) el.value=current; };
    fill(filterClient, clients); fill(filterMetrologist, metrologists);
  }

  function activeFilterCount() {
    return [filterClient?.value, filterMetrologist?.value, sortReports?.value && sortReports.value !== "recent" ? sortReports.value : ""].filter(Boolean).length;
  }

  function applyFilters(items) {
    const q = (search?.value || "").trim().toLowerCase();
    let out = items.filter(x => {
      const hay = [x.filename,x.partNumber,x.drawingNumber,x.revision,x.reportNumber,x.client,x.metrologist,x.piece].map(v=>String(v||"").toLowerCase());
      return !q || hay.some(v=>v.includes(q));
    });
    if (filterClient?.value) out = out.filter(x => String(x.client||"") === filterClient.value);
    if (filterMetrologist?.value) out = out.filter(x => String(x.metrologist||"") === filterMetrologist.value);
    const sort = sortReports?.value || "recent";
    out.sort((a,b) => sort === "oldest" ? dateScore(a)-dateScore(b) : sort === "rate_desc" ? (Number(b.rate)||0)-(Number(a.rate)||0) : sort === "rate_asc" ? (Number(a.rate)||0)-(Number(b.rate)||0) : sort === "part_asc" ? partBase(a).localeCompare(partBase(b)) : sort === "report_asc" ? String(a.reportNumber||a.filename).localeCompare(String(b.reportNumber||b.filename)) : dateScore(b)-dateScore(a));
    return out;
  }

  function reportOpen(item) {
    if (!item?.data) return;
    sessionStorage.setItem("dimensionRateReport", JSON.stringify(item.data));
    location.href = "/report";
  }

  function deleteReport(item) {
    if (!confirm(`Excluir o relatório "${item.reportNumber || item.filename || "sem identificação"}"?\n\nEssa ação remove apenas o registro do histórico local.`)) return;
    const key = itemKey(item);
    save(read().filter(x => itemKey(x) !== key));
    render();
  }

  function renderSearchResults(items) {
    visibleItems = items;
    grid.innerHTML = "";
    if (!items.length) { searchResults.hidden = true; empty.hidden = false; return; }
    empty.hidden = true;
    searchResults.hidden = false;
    searchResults.innerHTML = `<div class="search-results-head"><div><span class="section-kicker">RESULTADOS</span><h2>${items.length} relatório(s) encontrado(s)</h2><p>A pesquisa mostra os relatórios individualmente, sem agrupar por Part Number.</p></div><span class="results-chip"><i class="fa-solid fa-file-lines"></i> ${items.length}</span></div><div class="report-results-grid">${items.map((item,i)=>`<article class="report-result-card"><label class="result-select"><input class="group-report-check" type="checkbox" data-key="${esc(itemKey(item))}"><span></span></label><div class="report-result-icon"><i class="fa-solid fa-file-lines"></i></div><div class="report-result-main"><span class="report-result-kicker">${esc(partBase(item))}</span><h3>${esc(item.reportNumber || item.filename || `Relatório ${i+1}`)}</h3><p>${esc(item.client || "Cliente não informado")} · ${esc(item.metrologist || "Metrologista não informado")} · ${esc(item.date || "")}</p><div class="report-result-meta"><span>RATE <b>${pct(item.rate)}</b></span><span>REPROVAÇÕES <b>${Number(item.rejected)||0}</b></span><span>${Number(item.characteristics || item.points || 0)} características</span></div></div><div class="report-result-actions"><button class="btn btn-primary result-open" data-key="${esc(itemKey(item))}" type="button"><i class="fa-solid fa-arrow-right"></i> Abrir</button><button class="icon-button danger result-delete" data-key="${esc(itemKey(item))}" type="button" title="Excluir relatório" aria-label="Excluir relatório"><i class="fa-solid fa-trash"></i></button></div></article>`).join("")}</div>`;
    searchResults.querySelectorAll(".result-open").forEach(b=>b.addEventListener("click",()=>reportOpen(items.find(x=>itemKey(x)===b.dataset.key))));
    searchResults.querySelectorAll(".result-delete").forEach(b=>b.addEventListener("click",()=>deleteReport(items.find(x=>itemKey(x)===b.dataset.key))));
    searchResults.querySelectorAll(".group-report-check").forEach(c=>c.addEventListener("change",updateReportSelection));
    updateReportSelection();
  }

  function renderGroups(groups) {
    searchResults.hidden = true;
    grid.innerHTML = groups.map(group => {
      const rates=group.items.map(x=>Number(x.rate)).filter(Number.isFinite), avg=rates.length?rates.reduce((a,b)=>a+b,0)/rates.length:null;
      const latest=[...group.items].sort((a,b)=>dateScore(b)-dateScore(a))[0];
      return `<article class="part-card" data-group-id="${esc(group.id)}"><label class="part-family-select"><input class="part-group-check" type="checkbox" data-group-id="${esc(group.id)}"><span></span><b>Selecionar família</b></label><button class="part-card-main" type="button" data-group-id="${esc(group.id)}"><div class="part-card-top"><div class="part-emblem"><i class="fa-solid fa-cube"></i></div><div class="part-title"><span>FAMÍLIA</span><h3>${esc(group.label)}</h3><small>${group.parts.map(esc).join(" · ")} · ${group.items.length} relatório(s)</small></div><strong class="part-rate">${pct(avg)}</strong></div><div class="part-ornament"></div><div class="part-meta"><div><span>CLIENTES</span><b>${new Set(group.items.map(x=>x.client).filter(Boolean)).size || "—"}</b></div><div><span>ÚLTIMO RELATÓRIO</span><b>${esc(latest?.reportNumber||"—")}</b></div><div><span>REPROVAÇÕES</span><b>${group.items.reduce((n,x)=>n+(Number(x.rejected)||0),0)}</b></div></div><div class="part-card-footer"><span><i class="fa-solid fa-file-lines"></i> Ver ${group.items.length} relatório(s)</span><i class="fa-solid fa-arrow-right"></i></div></button></article>`;
    }).join("");
    grid.querySelectorAll(".part-card-main").forEach(b=>b.addEventListener("click",()=>location.href=`/groups/part?group=${encodeURIComponent(b.dataset.groupId)}`));
    grid.querySelectorAll(".part-group-check").forEach(c=>c.addEventListener("change",updatePartSelection));
  }

  function updatePartSelection() {
    const selected=[...document.querySelectorAll(".part-group-check:checked")];
    selectedPartCount.textContent=selected.length;
    catalogActions.hidden=selected.length<2;
  }

  function updateReportSelection() {
    const n=document.querySelectorAll(".group-report-check:checked").length;
    if(analyze) analyze.disabled=n<2;
    document.getElementById("selectedReportCount").textContent=n?`(${n})`:"";
  }

  function render() {
    const all=read(); fillFilters(all);
    const filtered=applyFilters(all);
    document.getElementById("reportCount").textContent=all.length;
    document.getElementById("rejectedCount").textContent=all.reduce((n,x)=>n+(Number(x.rejected)||0),0);
    const rates=all.map(x=>Number(x.rate)).filter(Number.isFinite);
    document.getElementById("averageRate").textContent=rates.length?pct(rates.reduce((a,b)=>a+b,0)/rates.length):"—";
    filterCount.textContent=activeFilterCount(); filterCount.hidden=activeFilterCount()===0;
    const q=(search?.value||"").trim();
    if(q || filterClient?.value || filterMetrologist?.value || (sortReports?.value && sortReports.value!=="recent")) {
      renderSearchResults(filtered); document.getElementById("groupCount").textContent=getGroups(all).length; return;
    }
    const groups=getGroups(all); currentGroups=groups; document.getElementById("groupCount").textContent=groups.length;
    if(!groups.length){grid.innerHTML="";empty.hidden=false;searchResults.hidden=true;catalogActions.hidden=true;return;}
    empty.hidden=true; renderGroups(groups); updatePartSelection(); updateReportSelection();
  }

  filterButton?.addEventListener("click",()=>{filterPanel.hidden=!filterPanel.hidden;filterButton.setAttribute("aria-expanded",String(!filterPanel.hidden));});
  [filterClient,filterMetrologist,sortReports].forEach(el=>el?.addEventListener("change",render));
  document.getElementById("clearFilters")?.addEventListener("click",()=>{filterClient.value="";filterMetrologist.value="";sortReports.value="recent";search.value="";render();});
  search?.addEventListener("input",render);

  analyze?.addEventListener("click",()=>{const selected=[...document.querySelectorAll(".group-report-check:checked")].map(c=>visibleItems.find(x=>itemKey(x)===c.dataset.key)).filter(x=>x?.data);if(selected.length<2)return;sessionStorage.setItem("dimensionRateComparison",JSON.stringify(selected.map(x=>x.data)));location.href="/report";});

  document.getElementById("mergePartsButton")?.addEventListener("click",()=>{
    const ids=[...document.querySelectorAll(".part-group-check:checked")].map(x=>x.dataset.groupId);
    const groups=currentGroups.filter(g=>ids.includes(g.id));
    if(groups.length<2)return;
    mergeSelection.innerHTML=groups.map(g=>`<div class="merge-selection-item"><i class="fa-solid fa-cube"></i><div><b>${esc(g.label)}</b><small>${g.parts.map(esc).join(" · ")} · ${g.items.length} relatório(s)</small></div></div>`).join("");
    mergeName.value=`${groups.map(g=>g.label).join(" + ")}`.slice(0,80);
    mergeModal.hidden=false; mergeModal.classList.add("is-open");
  });
  const closeMerge=()=>{mergeModal.hidden=true;mergeModal.classList.remove("is-open");};
  document.getElementById("mergeClose")?.addEventListener("click",closeMerge);document.getElementById("mergeCancel")?.addEventListener("click",closeMerge);
  mergeModal?.addEventListener("click",e=>{if(e.target===mergeModal)closeMerge();});
  document.getElementById("mergeConfirm")?.addEventListener("click",()=>{
    const ids=[...document.querySelectorAll(".part-group-check:checked")].map(x=>x.dataset.groupId); const groups=currentGroups.filter(g=>ids.includes(g.id)); if(groups.length<2)return;
    const merges=readMerges(); const parts=[...new Set(groups.flatMap(g=>g.parts))]; const base=groups.map(g=>g.id.replace(/^merge:/,"" )).join("__");
    Object.keys(merges).forEach(k=>{if(parts.some(p=>merges[k]?.parts?.includes(p)))delete merges[k];});
    merges[base]={label:(mergeName.value||parts.join(" + ")).trim().slice(0,80),parts,createdAt:new Date().toISOString()}; saveMerges(merges); closeMerge(); render();
  });

  document.addEventListener("keydown",e=>{if(e.key==="Escape"&&!mergeModal.hidden)closeMerge();});
  render();
})();
