# ============================================================
# DIMENSION-RATE
# PARSER DE PDF
# ============================================================

from __future__ import annotations

import pymupdf


# ============================================================
# CONFIGURAÇÃO HEXAGON
# ============================================================

# Vermelho utilizado pelo relatório Hexagon para indicar
# características fora de tolerância.
COR_HEXAGON_FORA = 0xFF0000

# Marcador interno preservado no texto para os parsers.
MARCADOR_FORA = "__HEXAGON_FORA__"


def _extrair_pagina_preservando_status(pagina) -> str:
    """
    Extrai uma página preservando a informação visual de FORA.

    O processamento é feito página a página para evitar manter
    estruturas de várias páginas simultaneamente na memória.
    """

    linhas: list[str] = []

    # "dict" é necessário porque precisamos da cor de cada span.
    dados = pagina.get_text("dict")

    for bloco in dados.get("blocks", ()):
        linhas_bloco = bloco.get("lines")

        if not linhas_bloco:
            continue

        for linha in linhas_bloco:
            textos: list[str] = []
            linha_tem_vermelho = False

            for span in linha.get("spans", ()):
                texto = span.get("text", "")

                if not texto or not texto.strip():
                    continue

                textos.append(texto.strip())

                if span.get("color", 0) == COR_HEXAGON_FORA:
                    linha_tem_vermelho = True

            if not textos:
                continue

            texto_linha = " ".join(textos)

            if linha_tem_vermelho:
                texto_linha = (
                    f"{MARCADOR_FORA} {texto_linha}"
                )

            linhas.append(texto_linha)

    return "\n".join(linhas)


def extrair_texto_pdf(arquivo) -> str:
    """
    Extrai texto do PDF preservando as marcações de FORA.

    Limite de tamanho:
        50 MB

    O documento PyMuPDF é sempre fechado no bloco finally.
    """

    if arquivo is None:
        raise ValueError("Nenhum arquivo PDF foi recebido.")

    if hasattr(arquivo, "read"):
        dados = arquivo.read()
    elif isinstance(arquivo, bytes):
        dados = arquivo
    else:
        raise TypeError(
            "Formato de arquivo PDF não suportado."
        )

    if not dados:
        raise ValueError("O arquivo PDF está vazio.")

    tamanho_maximo = 50 * 1024 * 1024

    if len(dados) > tamanho_maximo:
        tamanho_mb = len(dados) / (1024 * 1024)
        raise ValueError(
            f"O PDF possui {tamanho_mb:.1f} MB. "
            "O limite permitido é 50 MB."
        )

    documento = None

    try:
        documento = pymupdf.open(
            stream=dados,
            filetype="pdf",
        )

        if documento.page_count == 0:
            raise ValueError(
                "O PDF não possui páginas."
            )

        paginas: list[str] = []

        for pagina in documento:
            texto_pagina = (
                _extrair_pagina_preservando_status(
                    pagina
                )
            )

            if texto_pagina:
                paginas.append(texto_pagina)

        return "\n".join(paginas)

    finally:
        if documento is not None:
            documento.close()

        dados = None


def extrair_metadados_relatorio(texto: str, nome_arquivo: str | None = None) -> dict[str, str | None]:
    """Extrai identificadores do cabeçalho Hexagon, com fallback pelo nome do arquivo.

    Formato de fallback suportado:
        7162_752D48642R_PC01_RENAULT.pdf

    Nesse formato:
        relatório = 7162
        part number = 752D48642R
        peça = PC01
        cliente = RENAULT

    Informações encontradas no PDF sempre têm prioridade sobre o nome do arquivo.
    """
    import re

    texto = texto or ""
    nome_arquivo = nome_arquivo or ""

    def buscar(padroes):
        for padrao in padroes:
            m = re.search(padrao, texto, flags=re.IGNORECASE | re.MULTILINE)
            if m:
                valor = re.sub(r"\s+", " ", m.group(1)).strip(" :")
                if valor:
                    return valor
        return None

    def fallback_nome_arquivo():
        base = re.sub(r"\.pdf$", "", nome_arquivo.strip(), flags=re.IGNORECASE)
        partes = [p.strip() for p in base.split("_") if p.strip()]
        if len(partes) < 4:
            return {}

        # O padrão oficial esperado é Nº_RELATÓRIO_PART_NUMBER_PEÇA_CLIENTE.
        # O cliente pode conter underscores; por isso o restante é preservado.
        relatorio = partes[0]
        part_number = partes[1]
        peca = partes[2]
        cliente = "_".join(partes[3:])

        if not re.fullmatch(r"\d+", relatorio):
            return {}
        if not part_number or not re.fullmatch(r"[A-Za-z0-9.\-]+", part_number):
            return {}

        return {
            "report_number": relatorio,
            "part_number": part_number,
            "piece": peca,
            "client": cliente or None,
        }

    fallback = fallback_nome_arquivo()

    def buscar(padroes):
        for padrao in padroes:
            m = re.search(padrao, texto, flags=re.IGNORECASE | re.MULTILINE)
            if m:
                valor = re.sub(r"\s+", " ", m.group(1)).strip(" :")
                if valor:
                    return valor
        return None

    return {
        "part_number": buscar([
            r"N[º°]?\s*Peça\s*:\s*([^:\n]+)",
            r"N[º°]?\s*PEÇA\s*[:\-]?\s*([^:\n]+)",
        ]) or fallback.get("part_number"),
        "drawing_number": buscar([
            r"N[º°]?\s*Desenho\s*:\s*([^\n]+?)(?=\s+Nome da Peça|\s+Revisão|$)",
        ]),
        "revision": buscar([
            r"Revisão\s*:\s*([^\n]+)",
        ]),
        "report_number": buscar([
            r"RELATÓRIO DIMENSIONAL Nº\s*:\s*([^\n]+)",
        ]) or fallback.get("report_number"),
        "client": buscar([
            r"Cliente\s+Motivo da Medição\s+Metrologista\s*\n\s*:\s*([^:]+?)\s*:",
            r"Cliente\s*[:\-]\s*([^\n]+)",
        ]) or fallback.get("client"),
        "metrologist": buscar([
            r"Metrologista\s*[:\-]\s*([^\n]+)",
            r"Cliente\s+Motivo da Medição\s+Metrologista\s*\n\s*:[^:]+:\s*([^\n]+)",
        ]),
        "piece": fallback.get("piece"),
    }
