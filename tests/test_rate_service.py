from app.domain.measurement import Measurement
from app.services.rate_service import calcular_rate


def medicao(
    elemento,
    eixo,
    nominal=100.0,
    tol_mais=1.0,
    tol_menos=1.0,
    valor=100.0,
):
    return Measurement(
        elemento=elemento,
        categoria="DIMENSÕES",
        referencia="DIM001",
        eixo=eixo,
        nominal=nominal,
        tol_mais=tol_mais,
        tol_menos=tol_menos,
        medicao=valor,
        desvio=valor - nominal,
        fora_tolerancia=max(
            0.0,
            abs(valor - nominal) - max(tol_mais, tol_menos),
        ),
    )


# ============================================================
# RATE BÁSICO
# ============================================================

def test_rate_100_porcento():
    medicoes = [
        medicao("LOC1", "X"),
        medicao("LOC2", "X"),
        medicao("LOC3", "X"),
        medicao("LOC4", "X"),
    ]

    resultado = calcular_rate(medicoes)

    assert resultado.calculated_points == 4
    assert resultado.approved == 4
    assert resultado.rejected == 0
    assert resultado.calculated_percentage == 100.0


# ============================================================
# RATE COM REPROVAÇÃO
# ============================================================

def test_rate_com_ponto_reprovado():
    medicoes = [
        medicao("LOC1", "X", valor=100.0),
        medicao("LOC2", "X", valor=100.0),
        medicao("LOC3", "X", valor=102.0),
        medicao("LOC4", "X", valor=100.0),
    ]

    resultado = calcular_rate(medicoes)

    assert resultado.calculated_points == 4
    assert resultado.approved == 3
    assert resultado.rejected == 1
    assert resultado.calculated_percentage == 75.0


# ============================================================
# AGRUPAMENTO POR ELEMENTO / LOC
# ============================================================

def test_varias_medicoes_do_mesmo_ponto_formam_um_unico_ponto():
    medicoes = [
        medicao("LOC1", "X"),
        medicao("LOC1", "Y"),
        medicao("LOC1", "Z"),
    ]

    resultado = calcular_rate(medicoes)

    assert resultado.calculated_points == 1
    assert resultado.approved == 1
    assert resultado.rejected == 0
    assert resultado.calculated_percentage == 100.0


# ============================================================
# UM EIXO REPROVADO REPROVA O PONTO
# ============================================================

def test_eixo_reprovado_reprova_o_ponto():
    medicoes = [
        medicao("LOC1", "X", valor=100.0),
        medicao("LOC1", "Y", valor=102.0),
        medicao("LOC1", "Z", valor=100.0),
    ]

    resultado = calcular_rate(medicoes)

    assert resultado.calculated_points == 1
    assert resultado.approved == 0
    assert resultado.rejected == 1
    assert resultado.calculated_percentage == 0.0


# ============================================================
# DUPLICAÇÃO
# ============================================================

def test_remove_medicoes_duplicadas():
    primeira = medicao("LOC1", "X")

    segunda = medicao("LOC1", "X")

    resultado = calcular_rate([
        primeira,
        segunda,
    ])

    assert resultado.measurements_count == 1
    assert resultado.calculated_points == 1


# ============================================================
# RATE DECLARADO CONSISTENTE
# ============================================================

def test_rate_declarado_consistente():
    medicoes = [
        medicao("LOC1", "X"),
        medicao("LOC2", "X"),
        medicao("LOC3", "X"),
        medicao("LOC4", "X"),
    ]

    resultado = calcular_rate(
        medicoes,
        rate_declarado=(4, 100.0),
    )

    assert resultado.declared_points == 4
    assert resultado.declared_percentage == 100.0
    assert resultado.difference == 0.0
    assert resultado.consistent is True
    assert resultado.status == "CONSISTENTE"


# ============================================================
# RATE DECLARADO DIVERGENTE
# ============================================================

def test_rate_declarado_divergente():
    medicoes = [
        medicao("LOC1", "X"),
        medicao("LOC2", "X"),
        medicao("LOC3", "X"),
        medicao("LOC4", "X"),
    ]

    resultado = calcular_rate(
        medicoes,
        rate_declarado=(4, 95.0),
    )

    assert resultado.declared_percentage == 95.0
    assert resultado.difference == 5.0
    assert resultado.consistent is False
    assert resultado.status == "DIVERGENTE"


# ============================================================
# RATE NÃO DECLARADO
# ============================================================

def test_rate_nao_declarado():
    medicoes = [
        medicao("LOC1", "X"),
        medicao("LOC2", "X"),
    ]

    resultado = calcular_rate(
        medicoes,
        rate_declarado=None,
    )

    assert resultado.declared_points is None
    assert resultado.declared_percentage is None
    assert resultado.difference is None
    assert resultado.consistent is None
    assert resultado.status == "NAO_DECLARADO"


# ============================================================
# PONTO FORA DA TOLERÂNCIA
# ============================================================

def test_ponto_fora_da_tolerancia():
    medicoes = [
        medicao(
            "LOC1",
            "X",
            valor=102.0,
        )
    ]

    resultado = calcular_rate(medicoes)

    assert resultado.rejected == 1
    assert resultado.calculated_percentage == 0.0

    assert len(
        resultado.out_of_tolerance
    ) == 1

    ponto = resultado.out_of_tolerance[0]

    assert ponto["elemento"] == "LOC1"
    assert ponto["eixo"] == "X"
    assert ponto["nominal"] == 100.0
    assert ponto["medicao"] == 102.0


# ============================================================
# CATEGORIAS
# ============================================================

def test_resumo_de_categorias():
    medicoes = [
        medicao("LOC1", "X"),
        medicao("LOC2", "X"),
        medicao("LOC3", "X", valor=102.0),
    ]

    resultado = calcular_rate(medicoes)

    assert len(resultado.categories) == 1

    categoria = resultado.categories[0]

    assert categoria["categoria"] == "DIMENSÕES"
    assert categoria["total"] == 3
    assert categoria["aprovadas"] == 2
    assert categoria["reprovadas"] == 1