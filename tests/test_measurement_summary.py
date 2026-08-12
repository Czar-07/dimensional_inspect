from collections import Counter

from app.services.pdf_parser import extrair_texto_pdf
from app.services.measurement_service import extrair_medicoes


CAMINHO_PDF = "uploads/relatorio_teste.pdf"


texto = extrair_texto_pdf(CAMINHO_PDF)

medicoes = extrair_medicoes(texto)


print("=" * 80)
print("DIMENSION-RATE")
print("RESUMO DAS MEDIÇÕES")
print("=" * 80)

print()

print(
    f"Total de medições: {len(medicoes)}"
)

print()

categorias = Counter(
    medicao.categoria
    for medicao in medicoes
)

print("POR CATEGORIA")
print("-" * 80)

for categoria, quantidade in categorias.items():

    print(
        f"{categoria:20} {quantidade:>5}"
    )

print()

tipos = Counter(
    medicao.eixo
    for medicao in medicoes
)

print("POR TIPO")
print("-" * 80)

for tipo, quantidade in tipos.items():

    print(
        f"{tipo:20} {quantidade:>5}"
    )

print()

print("=" * 80)