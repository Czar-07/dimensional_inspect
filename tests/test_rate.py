from app.services.pdf_parser import extrair_texto_pdf
from app.services.measurement_service import extrair_medicoes
from app.services.rate_service import calcular_rate


CAMINHO_PDF = "uploads/relatorio_teste.pdf"


texto = extrair_texto_pdf(
    CAMINHO_PDF
)

medicoes = extrair_medicoes(
    texto
)


resultado = calcular_rate(
    pontos=medicoes,
)


print("=" * 80)
print("DIMENSION-RATE")
print("FASE 3 - MOTOR DE RATE")
print("=" * 80)

print()

print(
    f"Total de medições extraídas : "
    f"{len(medicoes)}"
)

print(
    f"Pontos considerados no RATE : "
    f"{resultado.total_pontos}"
)

print(
    f"Pontos aprovados             : "
    f"{resultado.pontos_aprovados}"
)

print(
    f"Pontos reprovados            : "
    f"{resultado.pontos_reprovados}"
)

print(
    f"RATE                         : "
    f"{resultado.percentual:.2f}%"
)

print()

print("PONTOS FORA DA TOLERÂNCIA")
print("-" * 80)

for ponto in resultado.pontos_fora:

    print(
        f"{ponto.elemento:8} | "
        f"{ponto.categoria:12} | "
        f"{ponto.eixo:1} | "
        f"DESV={ponto.desvio:7.2f} | "
        f"FORATOL={ponto.fora_tolerancia:5.2f}"
    )

print()

print("=" * 80)