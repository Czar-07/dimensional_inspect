from app.services.pdf_parser import extrair_texto_pdf
from app.services.measurement_service import extrair_medicoes
from app.services.rate_service import calcular_rate
from app.services.rate_validator import validar_rate


CAMINHO_PDF = "uploads/relatorio_teste.pdf"


# ============================================================
# EXTRAÇÃO
# ============================================================

texto = extrair_texto_pdf(
    CAMINHO_PDF
)

medicoes = extrair_medicoes(
    texto
)


# ============================================================
# CÁLCULO
# ============================================================

resultado_rate = calcular_rate(
    pontos=medicoes
)


# ============================================================
# VALIDAÇÃO
#
# Valores atualmente identificados no relatório:
#
# 61 pontos
# 88.52%
# ============================================================

validacao = validar_rate(

    pontos_declarados=61,

    rate_declarado=88.52,

    pontos_calculados=(
        resultado_rate.total_pontos
    ),

    rate_calculado=(
        resultado_rate.percentual
    ),
)


# ============================================================
# RESULTADO
# ============================================================

print("=" * 80)
print("DIMENSION-RATE")
print("FASE 3.1 - VALIDADOR DO RELATÓRIO")
print("=" * 80)

print()

print(
    f"Pontos declarados : "
    f"{validacao.pontos_declarados}"
)

print(
    f"Pontos calculados : "
    f"{validacao.pontos_calculados}"
)

print()

print(
    f"RATE declarado    : "
    f"{validacao.rate_declarado:.2f}%"
)

print(
    f"RATE calculado    : "
    f"{validacao.rate_calculado:.2f}%"
)

print(
    f"Diferença         : "
    f"{validacao.diferenca_rate:.2f}%"
)

print()

print("VALIDAÇÕES")
print("-" * 80)

for mensagem in validacao.mensagens:

    print(
        f"[{'OK' if 'consistente' in mensagem.lower() else 'ERRO'}] "
        f"{mensagem}"
    )

print()

print(
    "STATUS:",
    "✓ CONSISTENTE"
    if validacao.consistente
    else "✗ DIVERGENTE"
)

print()

print("=" * 80)