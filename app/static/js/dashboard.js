"use strict";

(() => {
  const input = document.getElementById("pdfInput");
  const dropzone = document.getElementById("dropzone");
  const selectBtn = document.getElementById("fileSelectButton");
  const analyzeBtn = document.getElementById("btnAnalyze");
  const selectedFilesEl = document.getElementById("selectedFiles");
  const uploadCard = document.getElementById("uploadCard");
  const loading = document.getElementById("loadingState");
  const loadingTitle = document.getElementById("loadingTitle");
  const loadingText = document.getElementById("loadingText");
  const errorState = document.getElementById("errorState");
  const errorMessage = document.getElementById("errorMessage");
  const closeError = document.getElementById("closeError");
  const batchResults = document.getElementById("batchResults");
  const batchList = document.getElementById("batchList");
  const batchCount = document.getElementById("batchCount");
  const batchProcessed = document.getElementById("batchProcessed");
  const batchSuccess = document.getElementById("batchSuccess");
  const batchFailed = document.getElementById("batchFailed");
  const batchParts = document.getElementById("batchParts");
  const clearBatch = document.getElementById("btnClearBatch");
  const HISTORY_KEY = "dimensionRateHistory";
  let files = [];

  const esc = v => String(v ?? "").replace(/[&<>\"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[c]));
  const pct = v => Number.isFinite(Number(v)) ? Number(v).toLocaleString("pt-BR", {minimumFractionDigits:2, maximumFractionDigits:2}) + "%" : "—";
  const readHistory = () => { try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]"); } catch { return []; } };
  const saveHistory = item => {
    try {
      const history = readHistory();
      const key = `${item.filename}|${item.reportNumber}|${item.date}`;
      const filtered = history.filter(x => `${x.filename}|${x.reportNumber}|${x.date}` !== key);
      filtered.unshift(item);
      localStorage.setItem(HISTORY_KEY, JSON.stringify(filtered.slice(0, 50)));
    } catch (e) { console.warn("[DIMENSION-RATE] Histórico local indisponível", e); }
  };

  function showError(message) { if (errorMessage) errorMessage.textContent = message; if (errorState) errorState.hidden = false; }
  function hideError() { if (errorState) errorState.hidden = true; }
  function size(bytes) { const mb = bytes / 1024 / 1024; return mb >= 1 ? `${mb.toFixed(2)} MB` : `${(bytes / 1024).toFixed(1)} KB`; }

  function addFiles(incoming) {
    const valid = [];
    for (const file of incoming) {
      const isPdf = file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
      if (!isPdf) { showError(`"${file.name}" não é um PDF.`); continue; }
      if (file.size > 50 * 1024 * 1024) { showError(`"${file.name}" excede o limite de 50 MB.`); continue; }
      valid.push(file);
    }
    const map = new Map(files.map(f => [`${f.name}|${f.size}|${f.lastModified}`, f]));
    valid.forEach(f => map.set(`${f.name}|${f.size}|${f.lastModified}`, f));
    files = [...map.values()];
    renderFiles();
    hideError();
  }

  function renderFiles() {
    if (!selectedFilesEl) return;
    selectedFilesEl.hidden = files.length === 0;
    analyzeBtn.disabled = files.length === 0;
    selectedFilesEl.innerHTML = files.map((file, i) => `<div class="selected-file-row"><div class="file-icon"><i class="fa-solid fa-file-pdf"></i></div><div class="file-details"><strong title="${esc(file.name)}">${esc(file.name)}</strong><span>${size(file.size)}</span></div><button class="icon-button remove-selected" type="button" data-index="${i}" aria-label="Remover"><i class="fa-solid fa-xmark"></i></button></div>`).join("");
    selectedFilesEl.querySelectorAll(".remove-selected").forEach(btn => btn.addEventListener("click", () => { files.splice(Number(btn.dataset.index), 1); renderFiles(); }));
  }

  selectBtn?.addEventListener("click", () => input?.click());
  input?.addEventListener("change", () => { addFiles([...input.files]); input.value = ""; });
  ["dragenter", "dragover"].forEach(e => document.addEventListener(e, ev => { ev.preventDefault(); dropzone?.classList.add("dragover"); }));
  ["dragleave", "drop"].forEach(e => document.addEventListener(e, ev => { ev.preventDefault(); dropzone?.classList.remove("dragover"); }));
  document.addEventListener("drop", ev => { if (ev.dataTransfer?.files?.length) addFiles([...ev.dataTransfer.files]); });
  closeError?.addEventListener("click", hideError);

  function renderBatch(items) {
    const successful = items.filter(x => x.success);
    const failed = items.filter(x => !x.success);
    const parts = new Set(successful.map(x => String(x.data?.document?.part_number || "SEM PART NUMBER").trim().toUpperCase()));
    batchCount.textContent = items.length;
    batchProcessed.textContent = items.length;
    batchSuccess.textContent = successful.length;
    batchFailed.textContent = failed.length;
    batchParts.textContent = parts.size;
    batchList.innerHTML = items.map((item, index) => {
      if (!item.success) return `<article class="batch-item batch-failed"><div class="batch-file-icon"><i class="fa-solid fa-triangle-exclamation"></i></div><div class="batch-info"><strong>${esc(item.filename)}</strong><span>${esc(item.error || "Falha na análise")}</span></div><span class="batch-status">Falha</span></article>`;
      const d = item.data.document || {}, r = item.data.rate || {}, c = r.calculated || {};
      const part = d.part_number || "SEM PART NUMBER";
      return `<article class="batch-item"><div class="batch-file-icon"><i class="fa-solid fa-file-circle-check"></i></div><div class="batch-info"><strong>${esc(d.report_number || d.filename || item.filename)}</strong><span>${esc(part)} • ${esc(d.client || "Cliente não informado")} • ${c.points ?? 0} características${d.locs_detected != null ? ` • ${d.locs_detected} LOCs` : ""}</span></div><div class="batch-metric"><small>RATE</small><b>${pct(c.percentage)}</b></div><div class="batch-metric"><small>REPROVADOS</small><b>${c.rejected ?? 0}</b></div><button class="btn btn-primary batch-open" type="button" data-index="${index}"><i class="fa-solid fa-file-lines"></i> Abrir relatório</button></article>`;
    }).join("");
    batchList.querySelectorAll(".batch-open").forEach(btn => btn.addEventListener("click", () => {
      const item = items[Number(btn.dataset.index)];
      if (!item?.data) return;
      sessionStorage.setItem("dimensionRateReport", JSON.stringify(item.data));
      location.href = "/report";
    }));
  }

  async function analyzeOne(file) {
    const form = new FormData(); form.append("file", file);
    const response = await fetch("/api/rate/analyze", {method:"POST", body:form});
    let data;
    try { data = await response.json(); } catch { throw new Error("O servidor retornou uma resposta inválida."); }
    if (!response.ok || !data.success) throw new Error(data.error || "Falha ao analisar o relatório.");
    return data;
  }

  async function analyzeAll() {
    if (!files.length) return showError("Selecione pelo menos um PDF.");
    hideError(); uploadCard.hidden = true; batchResults.hidden = true; loading.hidden = false;
    const current = [...files]; const results = [];
    for (let i = 0; i < current.length; i++) {
      loadingTitle.textContent = `Analisando ${i + 1} de ${current.length}`;
      loadingText.textContent = current[i].name;
      try {
        const data = await analyzeOne(current[i]);
        results.push({success:true, filename:current[i].name, data});
        const d = data.document || {}, r = data.rate || {}, c = r.calculated || {};
        saveHistory({filename:d.filename || current[i].name, partNumber:d.part_number || "SEM PART NUMBER", drawingNumber:d.drawing_number || "—", revision:d.revision || "—", reportNumber:d.report_number || "—", client:d.client || "—", metrologist:d.metrologist || "—", piece:d.piece || "—", rate:Number(c.percentage)||0, points:Number(c.points)||0, locs:Number(d.locs_detected)||0, characteristics:Number(d.characteristics_calculated ?? c.points)||0, rejected:Number(c.rejected)||0, status:r.status || "ANALISADO", date:new Date().toLocaleString("pt-BR"), data});
      } catch (e) { results.push({success:false, filename:current[i].name, error:e.message || "Erro inesperado"}); }
    }
    loading.hidden = true; batchResults.hidden = false; renderBatch(results); files = []; renderFiles();
  }

  analyzeBtn?.addEventListener("click", analyzeAll);
  clearBatch?.addEventListener("click", () => { batchResults.hidden = true; uploadCard.hidden = false; files = []; renderFiles(); window.scrollTo({top:0, behavior:"smooth"}); });
})();
