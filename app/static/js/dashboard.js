"use strict";


/* ============================================================
   DIMENSION-RATE
   DASHBOARD
   ============================================================ */


document.addEventListener(
    "DOMContentLoaded",
    () => {


        /* ====================================================
           ELEMENTOS
           ==================================================== */


        const input =
            document.getElementById(
                "pdfInput"
            );


        const dropzone =
            document.getElementById(
                "dropzone"
            );


        const btnAnalyze =
            document.getElementById(
                "btnAnalyze"
            );


        const btnNewAnalysis =
            document.getElementById(
                "btnNewAnalysis"
            );


        const fileSelectButton =
            document.getElementById(
                "fileSelectButton"
            );


        const removeFile =
            document.getElementById(
                "removeFile"
            );


        const selectedFile =
            document.getElementById(
                "selectedFile"
            );


        const fileName =
            document.getElementById(
                "fileName"
            );


        const fileSize =
            document.getElementById(
                "fileSize"
            );


        const uploadCard =
            document.getElementById(
                "uploadCard"
            );


        const loadingState =
            document.getElementById(
                "loadingState"
            );


        const results =
            document.getElementById(
                "results"
            );


        const errorState =
            document.getElementById(
                "errorState"
            );


        const errorMessage =
            document.getElementById(
                "errorMessage"
            );


        const closeError =
            document.getElementById(
                "closeError"
            );


        fileSelectButton?.addEventListener(
            "click",
            () => input?.click()
        );


        let arquivoSelecionado = null;


        let rateChart = null;


        let categoryChart = null;


        /* ====================================================
           RESTAURAR ÚLTIMA ANÁLISE
           ==================================================== */


        function restaurarUltimaAnalise() {

            if (!results) {
                return;
            }


            const raw =
                sessionStorage.getItem(
                    "dimensionRateReport"
                );


            if (!raw) {
                return;
            }


            try {

                const data =
                    JSON.parse(raw);


                if (
                    !data ||
                    !data.success
                ) {
                    return;
                }


                console.log(
                    "[DIMENSION-RATE] Restaurando última análise."
                );


                renderizarResultado(
                    data
                );


            } catch (erro) {

                console.warn(
                    "[DIMENSION-RATE] "
                    + "Não foi possível restaurar a análise:",
                    erro
                );

            }

        }


        /* ====================================================
           FORMATAÇÃO
           ==================================================== */


        function formatarNumero(
            valor,
            casas = 2
        ) {

            const numero =
                Number(valor);


            if (
                !Number.isFinite(
                    numero
                )
            ) {

                return (
                    0
                ).toLocaleString(
                    "pt-BR",
                    {
                        minimumFractionDigits:
                            casas,

                        maximumFractionDigits:
                            casas
                    }
                );

            }


            return numero.toLocaleString(
                "pt-BR",
                {
                    minimumFractionDigits:
                        casas,

                    maximumFractionDigits:
                        casas
                }
            );

        }


        function formatarPercentual(
            valor
        ) {

            const numero =
                Number(valor);


            if (
                !Number.isFinite(
                    numero
                )
            ) {

                return "0,00%";

            }


            return (
                formatarNumero(
                    numero,
                    2
                )
                + "%"
            );

        }


        function formatarTamanho(
            bytes
        ) {

            if (!bytes) {
                return "0 KB";
            }


            const mb =
                bytes
                / 1024
                / 1024;


            if (mb >= 1) {

                return (
                    mb.toFixed(2)
                    + " MB"
                );

            }


            return (
                (
                    bytes / 1024
                ).toFixed(1)
                + " KB"
            );

        }


        /* ====================================================
           ELEMENTOS SEGUROS
           ==================================================== */


        function definirTexto(
            id,
            valor
        ) {

            const elemento =
                document.getElementById(
                    id
                );


            if (!elemento) {

                console.warn(
                    `[DIMENSION-RATE] `
                    + `Elemento #${id} não encontrado.`
                );

                return;
            }


            elemento.textContent =
                valor;

        }


        /* ====================================================
           SEGURANÇA HTML
           ==================================================== */


        function escapeHtml(
            valor
        ) {

            return String(
                valor ?? ""
            )
                .replace(
                    /&/g,
                    "&amp;"
                )
                .replace(
                    /</g,
                    "&lt;"
                )
                .replace(
                    />/g,
                    "&gt;"
                )
                .replace(
                    /"/g,
                    "&quot;"
                )
                .replace(
                    /'/g,
                    "&#039;"
                );

        }


        /* ====================================================
           ARQUIVO
           ==================================================== */


        function selecionarArquivo(
            arquivo
        ) {

            if (!arquivo) {
                return;
            }


            const nome =
                String(
                    arquivo.name || ""
                ).toLowerCase();


            const ehPdf =
                arquivo.type ===
                    "application/pdf"
                ||
                nome.endsWith(
                    ".pdf"
                );


            if (!ehPdf) {

                mostrarErro(
                    "O arquivo selecionado não é um PDF."
                );


                limparArquivo();

                return;
            }


            arquivoSelecionado =
                arquivo;


            if (fileName) {

                fileName.textContent =
                    arquivo.name;

            }


            if (fileSize) {

                fileSize.textContent =
                    formatarTamanho(
                        arquivo.size
                    );

            }


            if (selectedFile) {

                selectedFile.hidden =
                    false;

            }


            if (btnAnalyze) {

                btnAnalyze.disabled =
                    false;

            }


            esconderErro();

        }


        function limparArquivo() {

            arquivoSelecionado =
                null;


            if (input) {

                input.value =
                    "";

            }


            if (selectedFile) {

                selectedFile.hidden =
                    true;

            }


            if (btnAnalyze) {

                btnAnalyze.disabled =
                    true;

            }

        }


        if (input) {

            input.addEventListener(
                "change",
                () => {

                    const arquivo =
                        input.files &&
                        input.files[0];


                    selecionarArquivo(
                        arquivo
                    );

                }
            );

        }


        if (removeFile) {

            removeFile.addEventListener(
                "click",
                limparArquivo
            );

        }


        /* ====================================================
           DRAG & DROP
           ==================================================== */


        function ativarDragDrop() {

            if (!dropzone) {
                return;
            }


            [
                "dragenter",
                "dragover",
                "dragleave",
                "drop"
            ].forEach(
                evento => {

                    document.addEventListener(
                        evento,
                        event => {

                            event.preventDefault();
                            event.stopPropagation();

                        },
                        false
                    );

                }
            );


            [
                "dragenter",
                "dragover"
            ].forEach(
                evento => {

                    dropzone.addEventListener(
                        evento,
                        event => {

                            event.preventDefault();
                            event.stopPropagation();


                            dropzone.classList.add(
                                "dragover"
                            );

                        }
                    );

                }
            );


            [
                "dragleave",
                "drop"
            ].forEach(
                evento => {

                    dropzone.addEventListener(
                        evento,
                        event => {

                            event.preventDefault();
                            event.stopPropagation();


                            dropzone.classList.remove(
                                "dragover"
                            );

                        }
                    );

                }
            );


            dropzone.addEventListener(
                "drop",
                event => {

                    const arquivos =
                        event.dataTransfer.files;


                    if (
                        !arquivos ||
                        !arquivos.length
                    ) {
                        return;
                    }


                    selecionarArquivo(
                        arquivos[0]
                    );

                }
            );


            const dashboard =
                document.querySelector(
                    ".dr-dashboard"
                );


            if (!dashboard) {
                return;
            }


            dashboard.addEventListener(
                "dragover",
                event => {

                    event.preventDefault();


                    dashboard.classList.add(
                        "dr-file-dragging"
                    );

                }
            );


            dashboard.addEventListener(
                "dragleave",
                event => {

                    if (
                        event.target ===
                        dashboard
                    ) {

                        dashboard.classList.remove(
                            "dr-file-dragging"
                        );

                    }

                }
            );


            dashboard.addEventListener(
                "drop",
                event => {

                    event.preventDefault();


                    dashboard.classList.remove(
                        "dr-file-dragging"
                    );


                    if (
                        event.target.closest(
                            "#dropzone"
                        )
                    ) {
                        return;
                    }


                    const arquivos =
                        event.dataTransfer.files;


                    if (
                        !arquivos ||
                        !arquivos.length
                    ) {
                        return;
                    }


                    selecionarArquivo(
                        arquivos[0]
                    );

                }
            );

        }


        ativarDragDrop();


        /* ====================================================
           ANALISAR
           ==================================================== */


        if (btnAnalyze) {

            btnAnalyze.addEventListener(
                "click",
                analisar
            );

        }


        async function analisar() {

            if (!arquivoSelecionado) {

                mostrarErro(
                    "Selecione um relatório PDF."
                );

                return;
            }


            esconderErro();


            if (uploadCard) {

                uploadCard.hidden =
                    true;

            }


            if (results) {

                results.hidden =
                    true;

            }


            if (loadingState) {

                loadingState.hidden =
                    false;

            }


            const formData =
                new FormData();


            formData.append(
                "file",
                arquivoSelecionado
            );


            try {

                const response =
                    await fetch(
                        "/api/rate/analyze",
                        {
                            method:
                                "POST",

                            body:
                                formData
                        }
                    );


                let data;


                try {

                    data =
                        await response.json();

                } catch {

                    throw new Error(
                        "O servidor retornou uma resposta inválida."
                    );

                }


                console.log(
                    "[DIMENSION-RATE] "
                    + "Resposta da API:",
                    data
                );


                if (
                    !response.ok ||
                    !data.success
                ) {

                    throw new Error(
                        data.error ||
                        "Falha ao analisar o relatório."
                    );

                }


                renderizarResultado(
                    data
                );


            } catch (erro) {

                console.error(
                    "[DIMENSION-RATE] Erro:",
                    erro
                );


                if (loadingState) {

                    loadingState.hidden =
                        true;

                }


                if (uploadCard) {

                    uploadCard.hidden =
                        false;

                }


                mostrarErro(
                    erro.message ||
                    "Erro inesperado ao analisar o relatório."
                );

            }

        }


        /* ====================================================
           RESULTADO
           ==================================================== */


        function renderizarResultado(
            data
        ) {

            console.log(
                "[DIMENSION-RATE] "
                + "Renderizando resultado:",
                data
            );


            if (loadingState) {

                loadingState.hidden =
                    true;

            }


            if (results) {

                results.hidden =
                    false;

            }


            const documentData =
                data.document || {};


            const rate =
                data.rate || {};


            const declared =
                rate.declared || {};


            const calculated =
                rate.calculated || {};


            /* =================================================
               DOCUMENTO
               ================================================= */


            definirTexto(
                "resultFilename",
                documentData.filename ||
                "-"
            );


            /* =================================================
               VALORES
               ================================================= */


            const total =
                Number(
                    calculated.points
                ) || 0;


            const approved =
                Number(
                    calculated.approved
                ) || 0;


            const rejected =
                Number(
                    calculated.rejected
                ) || 0;


            const calculatedPercentage =
                Number(
                    calculated.percentage
                ) || 0;


            const extracted =
                Number(
                    documentData
                        .measurements_extracted
                ) || 0;


            /* =================================================
               KPIs
               ================================================= */


            definirTexto(
                "rateCalculated",
                formatarPercentual(
                    calculatedPercentage
                )
            );


            definirTexto(
                "pointsTotal",
                total
            );


            definirTexto(
                "pointsApproved",
                approved
            );


            definirTexto(
                "pointsRejected",
                rejected
            );


            /* =================================================
               RATE DECLARADO
               ================================================= */


            const rateDeclarado =
                rate.status ===
                "NAO_DECLARADO"
                    ? null
                    : declared.percentage;


            if (
                rateDeclarado === null ||
                rateDeclarado === undefined
            ) {

                definirTexto(
                    "rateDeclared",
                    "Não declarado"
                );

            } else {

                definirTexto(
                    "rateDeclared",
                    formatarPercentual(
                        rateDeclarado
                    )
                );

            }


            /* =================================================
               RATE SECUNDÁRIO
               ================================================= */


            definirTexto(
                "rateCalculatedSecondary",
                formatarPercentual(
                    calculatedPercentage
                )
            );


            /* =================================================
               DIFERENÇA
               ================================================= */


            if (
                rate.status ===
                "NAO_DECLARADO"
            ) {

                definirTexto(
                    "rateDifference",
                    "Não aplicável"
                );

            } else {

                definirTexto(
                    "rateDifference",
                    formatarNumero(
                        rate.difference
                    )
                    + " p.p."
                );

            }


            /* =================================================
               MEDIÇÕES
               ================================================= */


            definirTexto(
                "measurementsExtracted",
                extracted
            );


            definirTexto(
                "measurementsRate",
                total
            );


            definirTexto(
                "measurementsExcluded",
                Math.max(
                    0,
                    extracted - total
                )
            );


            /* =================================================
               STATUS
               ================================================= */


            atualizarStatusRate(
                rate
            );


            /* =================================================
               FORA DA TOLERÂNCIA
               ================================================= */


            renderizarPontosFora(
                data.out_of_tolerance || []
            );


            /* =================================================
               GRÁFICO RATE
               ================================================= */


            try {

                renderizarRateChart(
                    calculated
                );

            } catch (erro) {

                console.error(
                    "[DIMENSION-RATE] "
                    + "Erro no gráfico RATE:",
                    erro
                );

            }


            /* =================================================
               GRÁFICO CATEGORIAS
               ================================================= */


            try {

                const categorias =
                    data.summary &&
                    Array.isArray(
                        data.summary.categories
                    )
                        ? data.summary.categories
                        : [];

                console.log(
                    "[DIMENSION-RATE] Resumo de categorias:",
                    categorias
                );

                renderizarCategoryChart(
                    categorias
                );

            } catch (erro) {

                console.error(
                    "[DIMENSION-RATE] Erro no gráfico de categorias:",
                    erro
                );
            }


            /* =================================================
               SALVAR
               ================================================= */


            sessionStorage.setItem(
                "dimensionRateReport",
                JSON.stringify(
                    data
                )
            );

            try {
                const historico = JSON.parse(localStorage.getItem("dimensionRateHistory") || "[]");
                const item = {
                    filename: documentData.filename || "Relatório sem nome",
                    rate: calculatedPercentage,
                    points: total,
                    rejected: rejected,
                    status: rate.status || "ANALISADO",
                    date: new Date().toLocaleString("pt-BR"),
                    data
                };
                historico.unshift(item);
                localStorage.setItem("dimensionRateHistory", JSON.stringify(historico.slice(0, 10)));
            } catch (erro) {
                console.warn("[DIMENSION-RATE] Não foi possível salvar o histórico local:", erro);
            }


            console.log(
                "[DIMENSION-RATE] "
                + "Dashboard atualizado com sucesso."
            );

        }


        /* ====================================================
           STATUS
           ==================================================== */


        function atualizarStatusRate(
            rate
        ) {

            const badge =
                document.getElementById(
                    "consistencyBadge"
                );


            if (!badge) {
                return;
            }


            const status =
                rate.status ||
                (
                    rate.consistent
                        ? "CONSISTENTE"
                        : "DIVERGENTE"
                );


            badge.className =
                "dr-consistency";


            if (
                status ===
                "NAO_DECLARADO"
            ) {

                badge.innerHTML = `
                    <i class="fa-solid fa-circle-info"></i>
                    RATE não declarado
                `;


                badge.style.color =
                    "var(--dr-warning)";


                badge.style.background =
                    "var(--dr-warning-soft)";


                badge.style.borderColor =
                    "#fde68a";


                return;
            }


            if (
                status ===
                "CONSISTENTE"
            ) {

                badge.innerHTML = `
                    <i class="fa-solid fa-circle-check"></i>
                    RATE consistente
                `;


                badge.style.color =
                    "var(--dr-success)";


                badge.style.background =
                    "var(--dr-success-soft)";


                badge.style.borderColor =
                    "#bbf7d0";


                return;
            }


            if (
                status ===
                "DIVERGENTE"
            ) {

                badge.innerHTML = `
                    <i class="fa-solid fa-triangle-exclamation"></i>
                    RATE divergente
                `;


                badge.style.color =
                    "var(--dr-danger)";


                badge.style.background =
                    "var(--dr-danger-soft)";


                badge.style.borderColor =
                    "#fecaca";


                return;
            }


            badge.innerHTML = `
                <i class="fa-solid fa-circle-question"></i>
                Status desconhecido
            `;

        }


        /* ====================================================
           CATEGORIAS
           ==================================================== */


        function normalizarCategoria(categoria) {

            const mapa = {

                "DATUM":
                    "Datum",

                "PLANOS":
                    "Planos",

                "MATCHING":
                    "Matching",

                "SUPERFÍCIES":
                    "Superfícies",

                "BORDAS":
                    "Bordas",

                "FURAÇÃO":
                    "Furação",

                "PARAFUSOS":
                    "Parafusos",

                "POSICIONAMENTO":
                    "Posicionamento",

                "DIMENSÕES":
                    "Dimensões",

                "OUTROS":
                    "Outros"
            };

            const chave = String(
                categoria || "OUTROS"
            ).toUpperCase();

            return mapa[chave] || "Outros";
        }


        function classeCategoria(
            categoria
        ) {

            const chave =
                String(
                    categoria ||
                    "OUTROS"
                )
                    .toUpperCase()
                    .normalize("NFD")
                    .replace(
                        /[\u0300-\u036f]/g,
                        ""
                    )
                    .replace(
                        /[^A-Z0-9]+/g,
                        "-"
                    );


            return (
                "dr-category "
                + "dr-category-"
                + chave.toLowerCase()
            );

        }


        /* ====================================================
           TABELA FORA DA TOLERÂNCIA
           ==================================================== */


        function renderizarPontosFora(
            pontos
        ) {

            const tbody =
                document.getElementById(
                    "outOfToleranceBody"
                );


            const counter =
                document.getElementById(
                    "outOfToleranceCount"
                );


            if (!tbody) {
                return;
            }


            pontos =
                Array.isArray(pontos)
                    ? pontos
                    : [];


            if (counter) {

                counter.textContent =
                    pontos.length;

            }


            if (!pontos.length) {

                tbody.innerHTML = `
                    <tr>
                        <td
                            colspan="8"
                            class="dr-empty"
                        >
                            <i class="fa-solid fa-circle-check"></i>
                            Nenhum ponto fora da tolerância.
                        </td>
                    </tr>
                `;


                return;
            }


            tbody.innerHTML =
                pontos
                    .map(
                        ponto => `

                            <tr>

                                <td>
                                    ${escapeHtml(
                                        ponto.elemento
                                    )}
                                </td>

                                <td>
                                    <span
                                        class="${classeCategoria(
                                            ponto.categoria
                                        )}"
                                    >
                                        ${escapeHtml(
                                            normalizarCategoria(
                                                ponto.categoria
                                            )
                                        )}
                                    </span>
                                </td>

                                <td>
                                    ${escapeHtml(
                                        ponto.referencia
                                    )}
                                </td>

                                <td>
                                    ${escapeHtml(
                                        ponto.eixo
                                    )}
                                </td>

                                <td>
                                    ${formatarNumero(
                                        ponto.nominal
                                    )}
                                </td>

                                <td>
                                    ${formatarNumero(
                                        ponto.medicao
                                    )}
                                </td>

                                <td>
                                    ${formatarNumero(
                                        ponto.desvio
                                    )}
                                </td>

                                <td>
                                    ${formatarNumero(
                                        ponto.fora_tolerancia
                                    )}
                                </td>

                            </tr>

                        `
                    )
                    .join("");

        }


        /* ====================================================
           GRÁFICO RATE
           ==================================================== */


        function renderizarRateChart(
            calculated
        ) {

            const canvas =
                document.getElementById(
                    "rateChart"
                );


            if (!canvas) {
                return;
            }


            if (
                typeof Chart ===
                "undefined"
            ) {

                console.warn(
                    "[DIMENSION-RATE] "
                    + "Chart.js não carregado."
                );

                return;
            }


            if (rateChart) {

                rateChart.destroy();

            }


            rateChart =
                new Chart(
                    canvas,
                    {

                        type:
                            "doughnut",


                        data: {

                            labels: [
                                "Aprovados",
                                "Reprovados"
                            ],


                            datasets: [

                                {

                                    data: [

                                        Number(
                                            calculated.approved
                                        ) || 0,

                                        Number(
                                            calculated.rejected
                                        ) || 0

                                    ],


                                    backgroundColor: [
                                        "#16a34a",
                                        "#dc2626"
                                    ],


                                    borderWidth:
                                        0

                                }

                            ]

                        },


                        options: {

                            responsive:
                                true,

                            maintainAspectRatio:
                                false,

                            cutout:
                                "72%",


                            plugins: {

                                legend: {

                                    position:
                                        "bottom",

                                    labels: {

                                        usePointStyle:
                                            true,

                                        padding:
                                            18,

                                        font: {

                                            size:
                                                10

                                        }

                                    }

                                }

                            }

                        }

                    }
                );

        }


        /* ====================================================
           GRÁFICO DE CATEGORIAS
           ==================================================== */


        function renderizarCategoryChart(categoriasResumo) {

            const canvas = document.getElementById(
                "categoryChart"
            );

            if (!canvas) {
                return;
            }

            if (typeof Chart === "undefined") {

                console.warn(
                    "[DIMENSION-RATE] Chart.js não carregado."
                );

                return;
            }

            if (categoryChart) {

                categoryChart.destroy();

                categoryChart = null;
            }

            const categorias = Array.isArray(
                categoriasResumo
            )
                ? categoriasResumo
                : [];

            if (!categorias.length) {

                console.warn(
                    "[DIMENSION-RATE] Nenhuma categoria recebida."
                );

                return;
            }

            const ordem = [
                "DATUM",
                "PLANOS",
                "MATCHING",
                "SUPERFÍCIES",
                "FURAÇÃO",
                "PARAFUSOS",
                "POSICIONAMENTO",
                "DIMENSÕES",
                "BORDAS",
                "OUTROS"
            ];

            const ordenadas = [
                ...categorias
            ].sort((a, b) => {

                const ia = ordem.indexOf(
                    String(
                        a.categoria || "OUTROS"
                    ).toUpperCase()
                );

                const ib = ordem.indexOf(
                    String(
                        b.categoria || "OUTROS"
                    ).toUpperCase()
                );

                return (
                    (ia < 0 ? 999 : ia) -
                    (ib < 0 ? 999 : ib)
                );
            });

            const labels = ordenadas.map(
                item =>
                    normalizarCategoria(
                        item.categoria
                    )
            );

            const values = ordenadas.map(
                item =>
                    Number(
                        item.total
                    ) || 0
            );

            const palette = [
                "#2563eb",
                "#7c3aed",
                "#0891b2",
                "#0f766e",
                "#ea580c",
                "#4f46e5",
                "#475569",
                "#64748b",
                "#94a3b8",
                "#334155"
            ];

            categoryChart = new Chart(
                canvas,
                {
                    type: "bar",

                    data: {

                        labels,

                        datasets: [
                            {
                                label: "Medições",

                                data: values,

                                backgroundColor:
                                    ordenadas.map(
                                        (_, index) =>
                                            palette[
                                                index %
                                                palette.length
                                            ]
                                    ),

                                borderRadius: 7,

                                borderSkipped: false,

                                barPercentage: 0.68,

                                categoryPercentage: 0.72
                            }
                        ]
                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio: false,

                        animation: {
                            duration: 500
                        },

                        plugins: {

                            legend: {
                                display: false
                            },

                            tooltip: {

                                backgroundColor:
                                    "#0f172a",

                                titleFont: {
                                    size: 12,
                                    weight: "700"
                                },

                                bodyFont: {
                                    size: 11
                                },

                                padding: 12,

                                displayColors: false,

                                callbacks: {

                                    label: context =>
                                        `${context.raw} medições`
                                }
                            }
                        },

                        scales: {

                            y: {

                                beginAtZero: true,

                                ticks: {
                                    precision: 0,
                                    color: "#64748b",
                                    font: {
                                        size: 10
                                    }
                                },

                                grid: {
                                    color: "#e2e8f0"
                                },

                                border: {
                                    display: false
                                }
                            },

                            x: {

                                ticks: {
                                    color: "#475569",
                                    font: {
                                        size: 10,
                                        weight: "600"
                                    }
                                },

                                grid: {
                                    display: false
                                },

                                border: {
                                    display: false
                                }
                            }
                        }
                    }
                }
            );
        }


        /* ====================================================
           NOVA ANÁLISE
           ==================================================== */


        function novaAnalise() {

            sessionStorage.removeItem(
                "dimensionRateReport"
            );


            limparArquivo();


            if (results) {

                results.hidden =
                    true;

            }


            if (loadingState) {

                loadingState.hidden =
                    true;

            }


            if (uploadCard) {

                uploadCard.hidden =
                    false;

            }


            esconderErro();


            window.scrollTo({

                top:
                    0,

                behavior:
                    "smooth"

            });

        }


        if (btnNewAnalysis) {

            btnNewAnalysis.addEventListener(
                "click",
                novaAnalise
            );

        }





        /* ====================================================
           ERROS
           ==================================================== */


        function mostrarErro(
            mensagem
        ) {

            if (
                !errorMessage ||
                !errorState
            ) {
                return;
            }


            errorMessage.textContent =
                mensagem;


            errorState.hidden =
                false;

        }


        function esconderErro() {

            if (!errorState) {
                return;
            }


            errorState.hidden =
                true;

        }


        if (closeError) {

            closeError.addEventListener(
                "click",
                esconderErro
            );

        }


        /* ====================================================
           INICIALIZAÇÃO
           ==================================================== */


        restaurarUltimaAnalise();


        console.log(
            "[DIMENSION-RATE] "
            + "Dashboard JS carregado."
        );

    }
);