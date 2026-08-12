import io

import pymupdf

from app.services.pdf_parser import extrair_texto_pdf
from app.services.measurement_service import extrair_medicoes
from app.services.rate_service import calcular_rate


# ============================================================
# AUXILIAR
# ============================================================

def criar_pdf(texto):
    documento = pymupdf.open()

    pagina = documento.new_page()

    pagina.insert_textbox(
        (40, 40, 550, 750),
        texto,
    )

    dados = documento.tobytes()

    documento.close()

    return dados


# ============================================================
# PIPELINE COMPLETO
# PDF → TEXTO → MEDIÇÕES → RATE
# ============================================================

def test_pipeline_completo():
    pdf = criar_pdf(
        """
        RELATÓRIO DIMENSIONAL

        LOC01 - DIM001
        X 100.00 1.00 1.00 100.20 0.20 0.00

        LOC02 - DIM002
        X 200.00 1.00 1.00 199.80 -0.20 0.00

        LOC03 - DIM003
        X 300.00 1.00 1.00 302.00 2.00 1.00

        LOC04 - DIM004
        X 400.00 1.00 1.00 400.00 0.00 0.00
        """
    )

    # ========================================================
    # 1. PDF
    # ========================================================

    texto = extrair_texto_pdf(
        io.BytesIO(pdf)
    )

    assert texto

    assert "LOC01" in texto
    assert "LOC04" in texto

    # ========================================================
    # 2. MEDIÇÕES
    # ========================================================

    medicoes = extrair_medicoes(
        texto
    )

    assert len(medicoes) == 4

    # ========================================================
    # 3. RATE
    # ========================================================

    resultado = calcular_rate(
        medicoes
    )

    # ========================================================
    # 4. RESULTADO
    # ========================================================

    assert resultado.calculated_points == 4

    assert resultado.approved == 3

    assert resultado.rejected == 1

    assert resultado.calculated_percentage == 75.0

    assert resultado.measurements_count == 4

    # ========================================================
    # 5. NÃO CONFORMIDADE
    # ========================================================

    assert len(
        resultado.out_of_tolerance
    ) == 1

    ponto = resultado.out_of_tolerance[0]

    assert ponto["elemento"] == "LOC03"

    assert ponto["eixo"] == "X"

    assert ponto["nominal"] == 300.0

    assert ponto["medicao"] == 302.0


# ============================================================
# RATE DECLARADO
# ============================================================

def test_pipeline_com_rate_declarado():
    pdf = criar_pdf(
        """
        RELATÓRIO DIMENSIONAL

        LOC01 - DIM001
        X 100.00 1.00 1.00 100.00 0.00 0.00

        LOC02 - DIM002
        X 200.00 1.00 1.00 202.00 2.00 1.00

        LOC03 - DIM003
        X 300.00 1.00 1.00 300.00 0.00 0.00

        LOC04 - DIM004
        X 400.00 1.00 1.00 400.00 0.00 0.00
        """
    )

    texto = extrair_texto_pdf(
        io.BytesIO(pdf)
    )

    medicoes = extrair_medicoes(
        texto
    )

    resultado = calcular_rate(
        medicoes,
        rate_declarado=(
            4,
            75.0,
        ),
    )

    assert resultado.calculated_points == 4

    assert resultado.approved == 3

    assert resultado.rejected == 1

    assert resultado.calculated_percentage == 75.0

    assert resultado.declared_points == 4

    assert resultado.declared_percentage == 75.0

    assert resultado.difference == 0.0

    assert resultado.consistent is True

    assert resultado.status == "CONSISTENTE"


# ============================================================
# VÁRIOS EIXOS NO MESMO LOC
# ============================================================

def test_pipeline_multiplos_eixos():
    pdf = criar_pdf(
        """
        RELATÓRIO DIMENSIONAL

        LOC01 - DIM001
        X 100.00 1.00 1.00 100.00 0.00 0.00
        Y 200.00 1.00 1.00 200.00 0.00 0.00
        Z 300.00 1.00 1.00 300.00 0.00 0.00

        LOC02 - DIM002
        X 400.00 1.00 1.00 402.00 2.00 1.00
        Y 500.00 1.00 1.00 500.00 0.00 0.00
        """
    )

    texto = extrair_texto_pdf(
        io.BytesIO(pdf)
    )

    medicoes = extrair_medicoes(
        texto
    )

    assert len(medicoes) == 5

    resultado = calcular_rate(
        medicoes
    )

    # LOC01 = aprovado
    # LOC02 = reprovado porque X falhou

    assert resultado.calculated_points == 2

    assert resultado.approved == 1

    assert resultado.rejected == 1

    assert resultado.calculated_percentage == 50.0