from app.services.pdf_parser import extrair_texto_pdf
from app.services.measurement_service import extrair_medicoes
from app.services.rate_parser import extrair_rate_declarado
from app.services.rate_service import calcular_rate
from app.services.rate_validator import validar_rate


CAMINHO_PDF = "uploads/relatorio_teste.pdf"


# ============================================================
# 1. EXTRAIR TEXTO
# ============================================================

texto = extrair_texto_pdf(
    CAMINHO_PDF
)


# ============================================================
# 2. EXTRAIR MEDIÇÕES
# ============================================================

medicoes = extrair_medicoes(
    texto
)


# ============================================================
# 3. EXTRAIR RATE DECLARADO
# ============================================================

rate_declarado = extrair_rate_declarado(
    texto
)


if rate_declarado is None:

    raise RuntimeError(
        "Não foi possível encontrar "
        "o RATE declarado no relatório."
    )


pontos_declarados, percentual_declarado = (
    rate_declarado
)


# ============================================================
# 4. CALCULAR RATE
# ============================================================

resultado = calcular_rate(
    pontos=medicoes
)


# ============================================================
# 5. VALIDAR
# ============================================================

validacao = validar_rate(

    pontos_declarados=pontos_declarados,

    rate_declarado=percentual_declarado,

    pontos_calculados=resultado.total_pontos,

    rate_calculado=resultado.percentual,
)


# ============================================================
# 6. RESULTADO
# ============================================================

print("=" * 90)
print("DIMENSION-RATE")
print("VALIDAÇÃO COMPLETA DO RELATÓRIO")
print("=" * 90)

print()

print("DOCUMENTO")
print("-" * 90)

print(
    f"Medições extraídas : "
    f"{len(medicoes)}"
)

print(
    f"Pontos RATE        : "
    f"{pontos_declarados}"
)

print(
    f"RATE declarado     : "
    f"{percentual_declarado:.2f}%"
)

print()

print("CÁLCULO")
print("-" * 90)

print(
    f"Pontos calculados  : "
    f"{resultado.total_pontos}"
)

print(
    f"Aprovados          : "
    f"{resultado.pontos_aprovados}"
)

print(
    f"Reprovados         : "
    f"{resultado.pontos_reprovados}"
)

print(
    f"RATE calculado     : "
    f"{resultado.percentual:.2f}%"
)

print()

print("VALIDAÇÃO")
print("-" * 90)

print(
    f"Diferença          : "
    f"{validacao.diferenca_rate:.2f}%"
)

print()

if validacao.consistente:

    print(
        "✓ RELATÓRIO CONSISTENTE"
    )

else:

    print(
        "✗ RELATÓRIO COM DIVERGÊNCIA"
    )

print()

print("=" * 90)