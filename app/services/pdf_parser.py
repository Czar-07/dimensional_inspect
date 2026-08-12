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
