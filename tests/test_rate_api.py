import io

import pymupdf

from app import app


def criar_pdf_teste() -> bytes:
    documento = pymupdf.open()

    pagina = documento.new_page()

    pagina.insert_text(
        (50, 50),
        """
        RELATÓRIO DIMENSIONAL

        LOC10 - DIM10

        X 100.00 1.00 1.00 100.00 0.00 0.00
        Y 50.00 0.50 0.50 50.20 0.20 0.00

        LOC20 - DIM20

        X 200.00 1.00 1.00 202.00 2.00 1.00
        """,
    )

    dados = documento.tobytes()

    documento.close()

    return dados


def test_api_rate_analyze():

    cliente = app.test_client()

    pdf = criar_pdf_teste()

    resposta = cliente.post(
        "/api/rate/analyze",
        data={
            "file": (
                io.BytesIO(pdf),
                "teste.pdf",
            )
        },
        content_type="multipart/form-data",
    )

    assert resposta.status_code == 200

    dados = resposta.get_json()

    assert dados is not None

    assert dados["success"] is True

    assert dados["document"]["filename"] == "teste.pdf"

    assert (
        dados["document"]["measurements_extracted"]
        == 3
    )

    assert "rate" in dados

    assert "calculated" in dados["rate"]

    assert "declared" in dados["rate"]

    assert "summary" in dados

    assert "categories" in dados["summary"]

    assert "out_of_tolerance" in dados