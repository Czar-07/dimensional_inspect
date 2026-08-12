import io

import pymupdf
import pytest

from app.services.pdf_parser import extrair_texto_pdf


# ============================================================
# AUXILIAR
# ============================================================

def criar_pdf(*paginas):
    documento = pymupdf.open()

    for texto in paginas:
        pagina = documento.new_page()
        pagina.insert_text(
            (72, 72),
            texto,
        )

    dados = documento.tobytes()

    documento.close()

    return dados


# ============================================================
# PDF BÁSICO
# ============================================================

def test_extrair_texto_pdf():
    pdf = criar_pdf(
        "RELATÓRIO DIMENSIONAL"
    )

    arquivo = io.BytesIO(pdf)

    texto = extrair_texto_pdf(
        arquivo
    )

    assert "RELATÓRIO DIMENSIONAL" in texto


# ============================================================
# MÚLTIPLAS PÁGINAS
# ============================================================

def test_extrair_texto_multiplas_paginas():
    pdf = criar_pdf(
        "Página 1",
        "Página 2",
        "Página 3",
    )

    texto = extrair_texto_pdf(
        io.BytesIO(pdf)
    )

    assert "Página 1" in texto
    assert "Página 2" in texto
    assert "Página 3" in texto


# ============================================================
# BYTES
# ============================================================

def test_extrair_texto_recebe_bytes():
    pdf = criar_pdf(
        "DIMENSIONAL-RATE"
    )

    texto = extrair_texto_pdf(
        pdf
    )

    assert "DIMENSIONAL-RATE" in texto


# ============================================================
# FILE-LIKE
# ============================================================

def test_extrair_texto_recebe_bytesio():
    pdf = criar_pdf(
        "Teste BytesIO"
    )

    arquivo = io.BytesIO(pdf)

    texto = extrair_texto_pdf(
        arquivo
    )

    assert "Teste BytesIO" in texto


# ============================================================
# ARQUIVO NONE
# ============================================================

def test_arquivo_none():
    with pytest.raises(
        ValueError,
        match="Nenhum arquivo PDF foi recebido",
    ):
        extrair_texto_pdf(None)


# ============================================================
# ARQUIVO VAZIO
# ============================================================

def test_arquivo_vazio():
    arquivo = io.BytesIO(
        b""
    )

    with pytest.raises(
        ValueError,
        match="O arquivo PDF está vazio",
    ):
        extrair_texto_pdf(arquivo)


# ============================================================
# TIPO INVÁLIDO
# ============================================================

def test_tipo_invalido():
    with pytest.raises(
        TypeError,
        match="Formato de arquivo PDF não suportado",
    ):
        extrair_texto_pdf(
            12345
        )


# ============================================================
# PDF COM TEXTO DIMENSIONAL
# ============================================================

def test_extrair_texto_relatorio_dimensional():
    pdf = criar_pdf(
        """
        RELATÓRIO DIMENSIONAL

        LOC10 - DATUM C

        X 100.00 0.50 0.50 100.20 0.20 0.00
        """
    )

    texto = extrair_texto_pdf(
        io.BytesIO(pdf)
    )

    assert "LOC10" in texto
    assert "DATUM C" in texto
    assert "100.00" in texto