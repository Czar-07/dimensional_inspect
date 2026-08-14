from app.domain.measurement import Measurement
from app.services.rate_service import calcular_rate


def _medicao(elemento, categoria, referencia, eixo="M"):
    return Measurement(
        elemento=elemento,
        categoria=categoria,
        referencia=referencia,
        eixo=eixo,
        nominal=0.0,
        tol_mais=1.0,
        tol_menos=1.0,
        medicao=0.0,
        desvio=0.0,
        fora_tolerancia=0.0,
    )


def test_caracteristicas_sem_loc_entram_no_rate():
    """
    Um relatório Hexagon pode ter LOCs e características sem LOC.

    No relatório 7131, a contagem correta é:
        45 LOCs + 4 planos + 1 distância = 50 características.
    """
    locs = [f"LOC{i}" for i in range(1, 32)]
    locs += [f"LOC{i}" for i in range(36, 50)]

    medicoes = [
        _medicao(loc, "SUPERFÍCIES", "SUP")
        for loc in locs
    ]

    medicoes += [
        _medicao("PLANO1", "PLANOS", "PLN1"),
        _medicao("PLANO2", "PLANOS", "PLN2"),
        _medicao("PLANO3", "PLANOS", "PLN3"),
        _medicao("PLANO4", "PLANOS", "PLN4"),
        _medicao("DIST1", "DIMENSÕES", "DATUM B1 PARA DATUM B2_C"),
    ]

    resultado = calcular_rate(
        medicoes,
        pontos_detectados=locs,
    )

    assert resultado.calculated_points == 50
    assert resultado.approved == 50
    assert resultado.rejected == 0
    assert resultado.calculated_percentage == 100.0
    assert len(resultado.points_audit) == 50


def test_varios_eixos_da_mesma_caracteristica_continuam_sendo_um_ponto():
    medicoes = [
        _medicao("LOC1", "DATUM", "DATUM A1", "X"),
        _medicao("LOC1", "DATUM", "DATUM A1", "Y"),
        _medicao("LOC1", "DATUM", "DATUM A1", "Z"),
        _medicao("LOC1", "DATUM", "DATUM A1", "D"),
        _medicao("LOC1", "DATUM", "DATUM A1", "L"),
    ]

    resultado = calcular_rate(medicoes, pontos_detectados=["LOC1"])

    assert resultado.calculated_points == 1
    assert resultado.approved == 1
    assert resultado.rejected == 0
