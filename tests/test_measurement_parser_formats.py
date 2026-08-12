from app.services.measurement_service import extrair_medicoes


def test_parser_vertical():
    texto = """
    LOC10 - DATUM C
    AX
    NOMINAL TOL+ TOL-
    MED DESV
    FORATOL
    X
    10.00
    0.10
    0.10
    10.05
    0.05
    0.00
    Y
    20.00
    0.10
    0.10
    20.20
    0.20
    0.10
    """
    medicoes = extrair_medicoes(texto)
    assert len(medicoes) == 2
    assert medicoes[0].elemento == "LOC10"
    assert medicoes[1].eixo == "Y"
    assert medicoes[1].fora_tolerancia == 0.10


def test_parser_compacto():
    texto = """
    LOC57 - DATUM B'
    D 9.00 0.10 0.00 9.17 0.17 0.07
    LOC16 - MTC6
    T 0.00 0.50 0.00 -0.20 -0.20 0.00
    """
    medicoes = extrair_medicoes(texto)
    assert len(medicoes) == 2
    assert medicoes[0].eixo == "D"
    assert medicoes[0].fora_tolerancia == 0.07
    assert medicoes[1].categoria == "MATCHING"


def test_parser_nao_assume_quantidade_fixa():
    linhas = ["LOC1 - DATUM A1"]
    for numero in range(1, 8):
        linhas.extend([
            f"LOC{numero} - DATUM A{numero}",
            "X 1.00 0.10 0.10 1.00 0.00 0.00",
        ])
    medicoes = extrair_medicoes("\n".join(linhas))
    assert len(medicoes) == 7


def test_parser_hexagon_quebra_linha_pdf():
    texto = """
    DATUMS
    ⌜
    MM
    LOC211 - DATUM C
    AX NOMINAL TOL+ TOL-
    MED DESV
    FORATOL
    Y
    415.00
    0.50 0.50 414.98 -0.02
    0.00
    Z
    178.00
    0.50 0.50 178.00
    0.00
    0.00
    FURAÇÃO
    LOC166 - QUADRADO1
    AX NOMINAL TOL+ TOL- MED DESV FORATOL
    X
    3144.00
    0.70 0.70 3142.67 -1.33
    0.63
    """
    medicoes = extrair_medicoes(texto)
    assert len(medicoes) == 3
    assert medicoes[0].eixo == "Y"
    assert medicoes[1].eixo == "Z"
    assert medicoes[2].fora_tolerancia == 0.63
