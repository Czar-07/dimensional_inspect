from dataclasses import dataclass
from math import isclose


@dataclass
class RateValidationResult:
    consistente: bool
    pontos_declarados: int | None
    pontos_calculados: int
    rate_declarado: float
    rate_calculado: float
    diferenca_rate: float
    pontos_consistentes: bool | None
    mensagens: list[str]


def validar_rate(
    *,
    pontos_declarados: int | None,
    rate_declarado: float,
    pontos_calculados: int,
    rate_calculado: float,
) -> RateValidationResult:
    mensagens: list[str] = []

    if pontos_declarados is None:
        pontos_ok = None
        mensagens.append(
            "O relatório declarou o RATE, mas não informou a quantidade de pontos."
        )
    else:
        pontos_ok = pontos_declarados == pontos_calculados
        mensagens.append(
            "Quantidade de pontos consistente."
            if pontos_ok
            else "Quantidade de pontos divergente."
        )

    diferenca = rate_calculado - rate_declarado
    rate_ok = isclose(rate_calculado, rate_declarado, abs_tol=0.01)
    mensagens.append(
        "RATE consistente." if rate_ok else "RATE divergente."
    )

    consistente = rate_ok if pontos_ok is None else (pontos_ok and rate_ok)

    return RateValidationResult(
        consistente=consistente,
        pontos_declarados=pontos_declarados,
        pontos_calculados=pontos_calculados,
        rate_declarado=rate_declarado,
        rate_calculado=rate_calculado,
        diferenca_rate=round(diferenca, 2),
        pontos_consistentes=pontos_ok,
        mensagens=mensagens,
    )
