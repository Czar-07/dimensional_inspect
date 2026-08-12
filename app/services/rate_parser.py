"""Extração do RATE declarado no relatório."""

from __future__ import annotations

import re


# Formatos conhecidos:
#   61_PNTS_RATE = 88.52%
#   61 PNTS RATE = 88,52%
#   61_PNTS_RATE=88.52%
PADRAO_RATE_COM_PONTOS = re.compile(
    r"(?P<pontos>\d+)\s*_?\s*PNTS\s*_?\s*RATE\s*=\s*"
    r"(?P<rate>\d+(?:[.,]\d+)?)\s*%",
    re.IGNORECASE,
)

# Fallback para relatórios que informam o RATE mas não a quantidade de pontos.
PADRAO_RATE_SEM_PONTOS = re.compile(
    r"\bRATE\s*=\s*(?P<rate>\d+(?:[.,]\d+)?)\s*%",
    re.IGNORECASE,
)


def extrair_rate_declarado(texto: str) -> tuple[int | None, float] | None:
    """Retorna ``(pontos, percentual)`` ou ``None`` quando não declarado."""
    if not texto:
        return None

    resultado = PADRAO_RATE_COM_PONTOS.search(texto)
    if resultado:
        return (
            int(resultado.group("pontos")),
            float(resultado.group("rate").replace(",", ".")),
        )

    resultado = PADRAO_RATE_SEM_PONTOS.search(texto)
    if resultado:
        return (
            None,
            float(resultado.group("rate").replace(",", ".")),
        )

    return None
