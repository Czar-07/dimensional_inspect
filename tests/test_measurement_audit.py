
from app.services.measurement_service import extrair_medicoes, extrair_pontos
from app.services.rate_service import calcular_rate


def test_cdf_le_de_sao_medições_validas():
    texto = """
    POSIÇÃO DO FURO E SLOT
    LOC8 - SLTQ_1
    AX NOMINAL TOL+ TOL- MED DESV FORATOL BÔNUS
    X 3020.00 0.00 0.00 3019.83 -0.17 0.00
    Y 375.00 0.00 0.00 375.24 0.24 0.00
    CDF 8.50 0.20 0.00 7.53 -0.97 0.97
    LE 8.50 0.20 0.00 7.44 -1.06 1.06
    PR CMAXMAT 1.00 0.59 0.59 0.00 0.00
    LOC7 - CÍR_1
    DE 12.00 0.20 0.00 11.85 -0.15 0.15 0.00
    """
    pontos = extrair_pontos(texto)
    medicoes = extrair_medicoes(texto)

    assert pontos == ["LOC8", "LOC7"]
    assert any(m.eixo == "CDF" for m in medicoes)
    assert any(m.eixo == "LE" for m in medicoes)
    assert any(m.eixo == "DE" for m in medicoes)

    resultado = calcular_rate(medicoes, pontos_detectados=pontos)

    assert resultado.calculated_points == 2
    assert resultado.rejected == 2
    assert len(resultado.out_of_tolerance) >= 2
    assert [p["status"] for p in resultado.points_audit] == ["FORA", "FORA"]


def test_loc_sem_medicao_nao_e_aprovado_silenciosamente():
    texto = """
    LOC1 - DATUM A
    X 10.00 0.50 0.50 10.00 0.00 0.00
    LOC2 - REFERENCIA_ESPECIAL
    """
    pontos = extrair_pontos(texto)
    medicoes = extrair_medicoes(texto)

    resultado = calcular_rate(medicoes, pontos_detectados=pontos)

    assert resultado.calculated_points == 2
    assert resultado.approved == 1
    assert resultado.rejected == 1
    assert any(p["status"] == "SEM_MEDICAO" for p in resultado.points_audit)
