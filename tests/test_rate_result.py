from app.domain.rate_result import RateResult


def criar_resultado():
    return RateResult(
        calculated_points=100,
        approved=95,
        rejected=5,
        calculated_percentage=95.0,
        measurements_count=120,
        declared_points=100,
        declared_percentage=95.0,
        difference=0.0,
        consistent=True,
        status="CONSISTENTE",
        out_of_tolerance=[],
        categories=[
            {
                "categoria": "DIMENSÕES",
                "total": 50,
                "aprovadas": 48,
                "reprovadas": 2,
            }
        ],
    )


def test_serializacao_calculated():
    resultado = criar_resultado()

    data = resultado.to_dict()

    assert data["calculated"]["points"] == 100
    assert data["calculated"]["approved"] == 95
    assert data["calculated"]["rejected"] == 5
    assert data["calculated"]["percentage"] == 95.0


def test_serializacao_declared():
    resultado = criar_resultado()

    data = resultado.to_dict()

    assert data["declared"]["points"] == 100
    assert data["declared"]["percentage"] == 95.0


def test_serializacao_comparacao():
    resultado = criar_resultado()

    data = resultado.to_dict()

    assert data["difference"] == 0.0
    assert data["consistent"] is True
    assert data["status"] == "CONSISTENTE"


def test_serializacao_detalhes():
    resultado = criar_resultado()

    data = resultado.to_dict()

    assert data["measurements"] == 120
    assert data["categories"][0]["categoria"] == "DIMENSÕES"
    assert data["categories"][0]["total"] == 50
    assert data["out_of_tolerance"] == []


def test_rate_nao_declarado():
    resultado = RateResult(
        calculated_points=80,
        approved=80,
        rejected=0,
        calculated_percentage=100.0,
        measurements_count=80,
        declared_points=None,
        declared_percentage=None,
        difference=None,
        consistent=None,
        status="NAO_DECLARADO",
        out_of_tolerance=[],
        categories=[],
    )

    data = resultado.to_dict()

    assert data["declared"]["points"] is None
    assert data["declared"]["percentage"] is None
    assert data["difference"] is None
    assert data["consistent"] is None
    assert data["status"] == "NAO_DECLARADO"