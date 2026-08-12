"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const raw = sessionStorage.getItem("dimensionRateReport");
    if (!raw) { mostrarSemDados(); return; }

    let rateChart = null;
    let categoryChart = null;

    try {
        const data = JSON.parse(raw);
        renderizarRelatorio(data);
    } catch (erro) {
        console.error("[DIMENSION-RATE] Erro ao carregar relatório:", erro);
        mostrarSemDados();
    }

    function renderizarRelatorio(data) {
        const doc = data.document || {};
        const rate = data.rate || {};
        const declared = rate.declared || {};
        const calculated = rate.calculated || {};
        const measurements = Array.isArray(data.measurements) ? data.measurements : [];
        const rejected = Array.isArray(data.out_of_tolerance) ? data.out_of_tolerance : [];
        const categories = Array.isArray(data.summary?.categories) ? data.summary.categories : [];
        const audit = Array.isArray(data.points_audit) ? data.points_audit : [];

        setText("reportRate", percentual(calculated.percentage));
        setText("reportFilename", doc.filename || "—");
        setText("reportMeasurements", doc.measurements_extracted ?? measurements.length);
        setText("reportPoints", calculated.points ?? 0);
        setText("reportExcluded", rate.excluded?.points ?? doc.measurements_excluded ?? 0);

        const paginasTotal = Number(doc.pages_total) || 0;
        const paginasAnalisadas = Number(doc.pages_analyzed) || 0;
        const paginasIgnoradas = Number(doc.pages_ignored) || 0;
        if (paginasTotal) {
            setText("reportPages", `${paginasAnalisadas}/${paginasTotal}`);
        } else {
            setText("reportPages", "—");
        }
        renderizarPaginasIgnoradas(doc);

        setText("reportApproved", calculated.approved ?? 0);
        setText("reportRejected", calculated.rejected ?? rejected.length);
        setText("reportRejectedBadge", rejected.length);
        setText("reportAllCount", measurements.length);
        setText("reportCategoryCount", categories.length);

        const status = rate.status || "NAO_DECLARADO";
        if (status === "NAO_DECLARADO") {
            setText("reportDeclared", "Não declarado");
            setText("reportConsistency", "NÃO DECLARADO");
            setText("reportStatus", "O relatório não informa um RATE declarado; o resultado é calculado diretamente pelas medições.");
            setStatusBadge("warning", "RATE não declarado", "fa-circle-info");
        } else if (status === "CONSISTENTE") {
            setText("reportDeclared", percentual(declared.percentage));
            setText("reportConsistency", "CONSISTENTE");
            setText("reportStatus", "RATE declarado e RATE calculado são consistentes.");
            setStatusBadge("success", "RATE consistente", "fa-circle-check");
        } else {
            setText("reportDeclared", percentual(declared.percentage));
            setText("reportConsistency", "DIVERGENTE");
            setText("reportStatus", "Foi encontrada divergência entre o RATE declarado e o calculado.");
            setStatusBadge("danger", "RATE divergente", "fa-triangle-exclamation");
        }

        setText("reportCalculated", percentual(calculated.percentage));
        renderizarCategorias(categories);
        renderizarTodas(measurements);
        renderizarReprovadas(rejected);
        renderizarAuditoria(audit);
        renderizarGraficos(calculated, categories);
    }

    function renderizarPaginasIgnoradas(doc) {
        const box = document.getElementById("reportPagesNote");
        const text = document.getElementById("reportPagesNoteText");
        if (!box || !text) return;

        const paginas = Array.isArray(doc.ignored_pages) ? doc.ignored_pages : [];
        if (!paginas.length) {
            box.hidden = true;
            return;
        }

        const mapa = {
            MAPA_DE_COR: "mapa de cor",
            SEM_PONTOS_DIMENSIONAIS: "sem pontos dimensionais",
        };

        const resumo = paginas.map(item => {
            const numero = Number(item.pagina) || 0;
            const motivo = mapa[item.motivo] || "sem dados dimensionais";
            return `página ${numero} (${motivo})`;
        });

        text.textContent = `${paginas.length} página(s) foram ignoradas da análise: ${resumo.join(", ")}.`;
        box.hidden = false;
    }

    function renderizarCategorias(items) {
        const tbody = document.getElementById("reportCategoryBody");
        if (!tbody) return;
        if (!items.length) { tbody.innerHTML = '<tr><td colspan="5" class="dr-empty">Nenhuma categoria encontrada.</td></tr>'; return; }
        tbody.innerHTML = items.map(item => {
            const total = Number(item.total) || 0;
            const aprovados = Number(item.aprovados) || 0;
            const reprovados = Number(item.reprovados) || 0;
            const conf = total ? (aprovados / total * 100) : 0;
            return `<tr><td><span class="${categoriaClasse(item.categoria)}">${escapeHtml(categoriaLabel(item.categoria))}</span></td><td>${total}</td><td class="dr-positive">${aprovados}</td><td class="dr-negative">${reprovados}</td><td>${percentual(conf)}</td></tr>`;
        }).join("");
    }

    function renderizarTodas(items) {
        const tbody = document.getElementById("reportAllBody");
        if (!tbody) return;
        if (!items.length) { tbody.innerHTML = '<tr><td colspan="12" class="dr-empty">Nenhuma medição foi retornada pela API.</td></tr>'; return; }
        tbody.innerHTML = items.map((ponto, i) => {
            const reprovado = Number(ponto.fora_tolerancia) > 0;
            return `<tr class="${reprovado ? 'dr-row-rejected' : ''}"><td>${i + 1}</td><td><strong>${escapeHtml(ponto.elemento)}</strong></td><td><span class="${categoriaClasse(ponto.categoria)}">${escapeHtml(categoriaLabel(ponto.categoria))}</span></td><td>${escapeHtml(ponto.referencia)}</td><td>${escapeHtml(ponto.eixo)}</td><td>${numero(ponto.nominal)}</td><td>${numero(ponto.tolerancia_mais)}</td><td>${numero(ponto.tolerancia_menos)}</td><td>${numero(ponto.medicao)}</td><td>${numero(ponto.desvio)}</td><td class="${reprovado ? 'dr-negative' : ''}">${numero(ponto.fora_tolerancia)}</td><td><span class="dr-measure-status ${reprovado ? 'rejected' : 'approved'}">${reprovado ? 'REPROVADO' : 'APROVADO'}</span></td></tr>`;
        }).join("");
    }

    function renderizarReprovadas(items) {
        const tbody = document.getElementById("reportRejectedBody");
        if (!tbody) return;
        if (!items.length) { tbody.innerHTML = '<tr><td colspan="8" class="dr-empty"><i class="fa-solid fa-circle-check"></i> Nenhum ponto fora da tolerância.</td></tr>'; return; }
        tbody.innerHTML = items.map(p => `<tr class="dr-row-rejected"><td><strong>${escapeHtml(p.elemento)}</strong></td><td><span class="${categoriaClasse(p.categoria)}">${escapeHtml(categoriaLabel(p.categoria))}</span></td><td>${escapeHtml(p.referencia)}</td><td>${escapeHtml(p.eixo)}</td><td>${numero(p.nominal)}</td><td>${numero(p.medicao)}</td><td>${numero(p.desvio)}</td><td class="dr-negative">${numero(p.fora_tolerancia)}</td></tr>`).join("");
    }


    function renderizarAuditoria(items) {
        const tbody = document.getElementById("reportAuditBody");
        if (!tbody) return;

        const detected = items.length;
        const measured = items.filter(p => p.status !== "SEM_MEDICAO").length;
        const out = items.filter(p => p.status === "FORA").length;
        const missing = items.filter(p => p.status === "SEM_MEDICAO").length;

        setText("reportAuditCount", detected);
        setText("auditDetected", detected);
        setText("auditMeasured", measured);
        setText("auditOut", out);
        setText("auditMissing", missing);

        if (!items.length) {
            tbody.innerHTML = '<tr><td colspan="6" class="dr-empty">Nenhum LOC foi detectado.</td></tr>';
            return;
        }

        tbody.innerHTML = items.map((ponto, i) => {
            const status = ponto.status || "SEM_MEDICAO";
            const classe =
                status === "FORA" ? "audit-out" :
                status === "OK" ? "audit-ok" : "audit-missing";
            const label =
                status === "FORA" ? "FORA" :
                status === "OK" ? "OK" : "SEM MEDIÇÃO";
            const eixos = Array.isArray(ponto.eixos) ? ponto.eixos.join(", ") : "—";
            return `<tr class="${status === "FORA" ? "dr-row-rejected" : ""}">
                <td>${i + 1}</td>
                <td><strong>${escapeHtml(ponto.elemento || "—")}</strong></td>
                <td class="${classe}">${label}</td>
                <td>${Number(ponto.medicoes) || 0}</td>
                <td>${escapeHtml(eixos)}</td>
                <td>${Array.isArray(ponto.fora_tolerancia) ? ponto.fora_tolerancia.length : 0}</td>
            </tr>`;
        }).join("");
    }

    function renderizarGraficos(calculated, categories) {
        if (typeof Chart === "undefined") return;
        const rateCanvas = document.getElementById("reportRateChart");
        if (rateCanvas) {
            rateChart?.destroy();
            rateChart = new Chart(rateCanvas, { type: "doughnut", data: { labels: ["Aprovados", "Reprovados"], datasets: [{ data: [Number(calculated.approved)||0, Number(calculated.rejected)||0], backgroundColor: ["#16a34a", "#dc2626"], borderWidth: 0 }] }, options: { responsive: true, maintainAspectRatio: false, cutout: "70%", plugins: { legend: { position: "bottom", labels: { usePointStyle: true, padding: 18, font: { size: 10 } } } } } });
        }
        const categoryCanvas = document.getElementById("reportCategoryChart");
        if (categoryCanvas) {
            categoryChart?.destroy();
            const palette = ["#2563eb", "#7c3aed", "#0891b2", "#0f766e", "#ea580c", "#4f46e5", "#475569", "#64748b", "#94a3b8"];
            categoryChart = new Chart(categoryCanvas, { type: "bar", data: { labels: categories.map(x => categoriaLabel(x.categoria)), datasets: [{ label: "Medições", data: categories.map(x => Number(x.total)||0), backgroundColor: categories.map((_,i) => palette[i % palette.length]), borderRadius: 7, borderSkipped: false }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } }, x: { grid: { display: false } } } } });
        }
    }

    function mostrarSemDados() {
        setText("reportRate", "—"); setText("reportStatus", "Nenhuma análise disponível"); setText("reportConsistency", "SEM DADOS"); setText("reportDeclared", "—"); setText("reportCalculated", "—"); setText("reportApproved", "—"); setText("reportRejected", "—");
        setStatusBadge("neutral", "Sem dados", "fa-circle-info");
    }

    function setStatusBadge(tipo, texto, icone) { const badge = document.getElementById("reportStatusBadge"); const hero = document.getElementById("reportHero"); if (!badge) return; badge.innerHTML = `<i class="fa-solid ${icone}"></i> ${escapeHtml(texto)}`; badge.dataset.status = tipo; if (hero) hero.dataset.status = tipo; }
    function setText(id, valor) { const el = document.getElementById(id); if (el) el.textContent = valor; }
    function percentual(valor) { if (valor === null || valor === undefined || valor === "") return "—"; const n=Number(valor); return Number.isFinite(n) ? n.toLocaleString("pt-BR", {minimumFractionDigits:2, maximumFractionDigits:2})+"%" : "—"; }
    function numero(valor) { if (valor === null || valor === undefined || valor === "") return "—"; const n=Number(valor); return Number.isFinite(n) ? n.toLocaleString("pt-BR", {minimumFractionDigits:2, maximumFractionDigits:2}) : "—"; }
    function categoriaLabel(categoria) { const mapa={DATUM:"Datum",PLANOS:"Planos",MATCHING:"Matching","SUPERFÍCIES":"Superfícies",BORDAS:"Bordas","FURAÇÃO":"Furação",PARAFUSOS:"Parafusos",POSICIONAMENTO:"Posicionamento","DIMENSÕES":"Dimensões",OUTROS:"Outros"}; return mapa[String(categoria||"OUTROS").toUpperCase()] || "Outros"; }
    function categoriaClasse(categoria) { const chave=String(categoria||"OUTROS").toUpperCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"").replace(/[^A-Z0-9]+/g,"-"); return `dr-category dr-category-${chave.toLowerCase()}`; }
    function escapeHtml(valor) { return String(valor ?? "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#039;"); }
});
