from app.domain.measurement import Measurement
from app.services.rate_service import calcular_rate


def test_loc_sem_medicao_nao_e_reprovado_sem_marcacao_visual():
    pontos = [f"LOC{i}" for i in range(1, 113) if i != 78]
    medicoes = []
    for loc in pontos:
        if loc in {"LOC4", "LOC5"}:
            continue
        medicoes.append(Measurement(loc, "OUTROS", None, "T", 0, 1, 1, 0, 0, 0))

    for medicao in medicoes[:46]:
        medicao.medicao = 2

    resultado = calcular_rate(
        medicoes,
        pontos_detectados=pontos,
        pontos_forcados_fora={"LOC5"},
    )

    assert resultado.calculated_points == 111
    assert resultado.rejected == 47
    assert resultado.approved == 64
    assert resultado.calculated_percentage == 57.66
    assert sum(p["status"] == "FORA" for p in resultado.points_audit) == 47
    assert next(p for p in resultado.points_audit if p["elemento"] == "LOC4")["status"] == "SEM_MEDICAO"
    assert next(p for p in resultado.points_audit if p["elemento"] == "LOC5")["status"] == "FORA"
