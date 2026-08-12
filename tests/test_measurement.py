from app.domain.measurement import Measurement


def criar_medicao(
    *,
    nominal=100.0,
    tol_mais=1.0,
    tol_menos=1.0,
    medicao=100.0,
):
    return Measurement(
        elemento="LOC01",
        categoria="DIMENSÕES",
        referencia="DIM01",
        eixo="X",
        nominal=nominal,
        tol_mais=tol_mais,
        tol_menos=tol_menos,
        medicao=medicao,
        desvio=medicao - nominal,
        fora_tolerancia=0.0,
    )


def test_limite_superior():
    medicao = criar_medicao(
        nominal=100.0,
        tol_mais=1.5,
        tol_menos=1.0,
    )

    assert medicao.limite_superior == 101.5


def test_limite_inferior():
    medicao = criar_medicao(
        nominal=100.0,
        tol_mais=1.5,
        tol_menos=1.0,
    )

    assert medicao.limite_inferior == 99.0


def test_medicao_aprovada_no_nominal():
    medicao = criar_medicao(
        medicao=100.0
    )

    assert medicao.aprovado is True


def test_medicao_no_limite_inferior_e_aprovada_sem_marca_visual():
    medicao = criar_medicao(
        medicao=99.0
    )

    assert medicao.aprovado is True


def test_medicao_no_limite_superior_e_aprovada_sem_marca_visual():
    medicao = criar_medicao(
        medicao=101.0
    )

    assert medicao.aprovado is True


def test_medicao_marcada_pelo_hexagon_como_fora():
    medicao = criar_medicao(
        medicao=101.0
    )
    medicao.forcado_fora = True

    assert medicao.aprovado is False


def test_medicao_reprovada_acima_do_limite():
    medicao = criar_medicao(
        medicao=101.01
    )

    assert medicao.aprovado is False


def test_medicao_reprovada_abaixo_do_limite():
    medicao = criar_medicao(
        medicao=98.99
    )

    assert medicao.aprovado is False