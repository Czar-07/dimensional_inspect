from app.services.pdf_parser import extrair_texto_pdf
from app.services.measurement_service import extrair_medicoes
from app.services.rate_parser import extrair_rate_declarado
from app.services.rate_service import calcular_rate


CAMINHO_PDF = "uploads/relatorio_teste.pdf"


def test_relatorio_teste_completo():
    texto = extrair_texto_pdf(CAMINHO_PDF)
    medicoes = extrair_medicoes(texto)
    resultado = calcular_rate(medicoes)
    declarado = extrair_rate_declarado(texto)

    assert len(medicoes) == 80
    assert resultado.total_pontos == 61
    assert resultado.pontos_aprovados == 54
    assert resultado.pontos_reprovados == 7
    assert resultado.percentual == 88.52
    assert declarado == (61, 88.52)
