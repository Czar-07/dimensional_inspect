(() => {
  "use strict";
  const list = document.getElementById("historyList");
  const count = document.getElementById("historyCount");
  const clear = document.getElementById("clearHistory");
  const key = "dimensionRateHistory";
  const read = () => { try { return JSON.parse(localStorage.getItem(key) || "[]"); } catch { return []; } };
  const esc = (v) => String(v ?? "").replace(/[&<>'"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;","\"":"&quot;"}[c]));
  const pct = (v) => Number.isFinite(Number(v)) ? Number(v).toLocaleString("pt-BR", {minimumFractionDigits:2,maximumFractionDigits:2}) + "%" : "—";
  const render = () => {
    const items = read();
    count.textContent = `${items.length} ${items.length === 1 ? "análise" : "análises"}`;
    if (!items.length) {
      list.innerHTML = '<div class="history-empty"><i class="fa-regular fa-folder-open"></i><strong>Nenhuma análise registrada</strong><span>Depois de analisar um PDF, o resultado aparecerá aqui.</span><a class="btn btn-primary" href="/rate">Analisar primeiro relatório</a></div>';
      return;
    }
    list.innerHTML = items.map((item, index) => `
      <div class="history-item">
        <div class="file-icon"><i class="fa-solid fa-file-pdf"></i></div>
        <div class="history-info"><strong title="${esc(item.filename)}">${esc(item.filename)}</strong><span>${esc(item.date)} • ${item.points ?? 0} pontos • ${item.rejected ?? 0} reprovados</span></div>
        <strong class="history-rate">${pct(item.rate)}</strong>
        <span class="history-status">${esc(item.status || "ANALISADO")}</span>
        <button class="btn btn-secondary history-open" type="button" data-index="${index}"><i class="fa-solid fa-eye"></i> Abrir</button>
      </div>`).join("");
    list.querySelectorAll(".history-open").forEach(btn => btn.addEventListener("click", () => {
      const item = items[Number(btn.dataset.index)];
      if (!item?.data) return;
      sessionStorage.setItem("dimensionRateReport", JSON.stringify(item.data));
      location.href = "/report";
    }));
  };
  clear?.addEventListener("click", () => { if (read().length && confirm("Limpar todo o histórico deste navegador?")) { localStorage.removeItem(key); render(); } });
  render();
})();
