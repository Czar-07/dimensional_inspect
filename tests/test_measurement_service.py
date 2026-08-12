from app.services.measurement_service import (
    extrair_medicoes,
    identificar_categoria,
    categoria_por_secao,
)


# ============================================================
# CATEGORIAS
# ============================================================

def test_identificar_categoria_datum():
    assert identificar_categoria(
        "DATUM C",
        "LOC10",
    ) == "DATUM"


def test_identificar_categoria_matching():
    assert identificar_categoria(
        "MTC6",
        "LOC16",
    ) == "MATCHING"


def test_identificar_categoria_planos():
    assert identificar_categoria(
        "PLN1",
        "PLANO1",
    ) == "PLANOS"


def test_identificar_categoria_furacao():
    assert identificar_categoria(
        "FUR01",
        "FURO1",
    ) == "FURAÇÃO"


def test_identificar_categoria_posicionamento():
    assert identificar_categoria(
        "POS01",
        "LOC01",
    ) == "POSICIONAMENTO"


def test_identificar_categoria_dimensoes():
    assert identificar_categoria(
        "DIM01",
        "DIM01",
    ) == "DIMENSÕES"


def test_identificar_categoria_outros():
    assert identificar_categoria(
        "ABC01",
        "ELEMENTO1",
    ) == "OUTROS"


# ============================================================
# CATEGORIA POR SEÇÃO
# ============================================================

def test_categoria_por_secao():
    assert categoria_por_secao("DATUM") == "DATUM"
    assert categoria_por_secao("FURAÇÃO") == "FURAÇÃO"
    assert categoria_por_secao("MATCHING") == "MATCHING"
    assert categoria_por_secao("PLANOS") == "PLANOS"
    assert categoria_por_secao("BORDAS") == "BORDAS"


def test_categoria_por_secao_desconhecida():
    assert categoria_por_secao("SEÇÃO DESCONHECIDA") is None


# ============================================================
# MEDIÇÃO COMPACTA
# ============================================================

def test_extrair_medicao_compacta():
    texto = """
    LOC10 - DATUM C
    X 100.00 0.50 0.50 100.20 0.20 0.00
    """

    medicoes = extrair_medicoes(texto)

    assert len(medicoes) == 1

    medicao = medicoes[0]

    assert medicao.elemento == "LOC10"
    assert medicao.referencia == "DATUM C"
    assert medicao.categoria == "DATUM"
    assert medicao.eixo == "X"

    assert medicao.nominal == 100.00
    assert medicao.tol_mais == 0.50
    assert medicao.tol_menos == 0.50
    assert medicao.medicao == 100.20
    assert medicao.desvio == 0.20
    assert medicao.fora_tolerancia == 0.00


# ============================================================
# MEDIÇÃO REPROVADA
# ============================================================

def test_extrair_medicao_reprovada():
    texto = """
    LOC20 - DIM001
    X 100.00 0.50 0.50 101.00 1.00 0.50
    """

    medicoes = extrair_medicoes(texto)

    assert len(medicoes) == 1

    medicao = medicoes[0]

    assert medicao.medicao == 101.00
    assert medicao.aprovado is False
    assert medicao.fora_tolerancia == 0.50


# ============================================================
# VÁRIOS EIXOS
# ============================================================

def test_extrair_varios_eixos():
    texto = """
    LOC30 - DIM001
    X 100.00 1.00 1.00 100.10 0.10 0.00
    Y 200.00 1.00 1.00 199.90 -0.10 0.00
    Z 300.00 1.00 1.00 300.20 0.20 0.00
    """

    medicoes = extrair_medicoes(texto)

    assert len(medicoes) == 3

    assert medicoes[0].eixo == "X"
    assert medicoes[1].eixo == "Y"
    assert medicoes[2].eixo == "Z"

    assert all(
        medicao.aprovado
        for medicao in medicoes
    )


# ============================================================
# VÁRIOS ELEMENTOS
# ============================================================

def test_extrair_varios_elementos():
    texto = """
    LOC01 - DIM001
    X 100.00 1.00 1.00 100.00 0.00 0.00

    LOC02 - DIM002
    X 200.00 1.00 1.00 200.00 0.00 0.00

    LOC03 - DIM003
    X 300.00 1.00 1.00 300.00 0.00 0.00
    """

    medicoes = extrair_medicoes(texto)

    assert len(medicoes) == 3

    assert medicoes[0].elemento == "LOC01"
    assert medicoes[1].elemento == "LOC02"
    assert medicoes[2].elemento == "LOC03"


# ============================================================
# NÚMEROS COM VÍRGULA
# ============================================================

def test_extrair_numeros_com_virgula():
    texto = """
    LOC40 - DIM001
    X 100,00 0,50 0,50 100,25 0,25 0,00
    """

    medicoes = extrair_medicoes(texto)

    assert len(medicoes) == 1

    medicao = medicoes[0]

    assert medicao.nominal == 100.00
    assert medicao.tol_mais == 0.50
    assert medicao.tol_menos == 0.50
    assert medicao.medicao == 100.25
    assert medicao.desvio == 0.25


# ============================================================
# NÚMEROS COM SINAL UNICODE
# ============================================================

def test_extrair_numero_com_sinal_unicode():
    texto = """
    LOC50 - DIM001
    X 100.00 1.00 1.00 99.50 −0.50 0.00
    """

    medicoes = extrair_medicoes(texto)

    assert len(medicoes) == 1

    medicao = medicoes[0]

    assert medicao.medicao == 99.50
    assert medicao.desvio == -0.50
    assert medicao.aprovado is True


# ============================================================
# TEXTO VAZIO
# ============================================================

def test_texto_vazio():
    assert extrair_medicoes("") == []


def test_texto_none():
    assert extrair_medicoes(None) == []


# ============================================================
# FORMATO VERTICAL
# ============================================================

def test_extrair_medicao_vertical():
    texto = """
    LOC60 - DIM001
    X
    100.00
    0.50 0.50 100.20 0.20
    0.00
    """

    medicoes = extrair_medicoes(texto)

    assert len(medicoes) == 1

    medicao = medicoes[0]

    assert medicao.elemento == "LOC60"
    assert medicao.eixo == "X"
    assert medicao.nominal == 100.00
    assert medicao.tol_mais == 0.50
    assert medicao.tol_menos == 0.50
    assert medicao.medicao == 100.20
    assert medicao.desvio == 0.20
    assert medicao.fora_tolerancia == 0.00