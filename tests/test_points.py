from collections import defaultdict

from app.services.pdf_parser import extrair_texto_pdf
from app.services.measurement_service import extrair_medicoes


CAMINHO_PDF = "uploads/relatorio_teste.pdf"


texto = extrair_texto_pdf(CAMINHO_PDF)

medicoes = extrair_medicoes(texto)


grupos = defaultdict(list)


for medicao in medicoes:

    chave = (
        medicao.categoria,
        medicao.elemento,
        medicao.referencia,
    )

    grupos[chave].append(medicao)


print("=" * 90)
print("DIMENSION-RATE")
print("AGRUPAMENTO DOS PONTOS DE INSPEÇÃO")
print("=" * 90)

print()

print(f"Total de medições: {len(medicoes)}")
print(f"Total de grupos:    {len(grupos)}")

print()

for numero, (chave, itens) in enumerate(
    grupos.items(),
    start=1
):

    categoria, elemento, referencia = chave

    tipos = ", ".join(
        item.eixo
        for item in itens
    )

    print(
        f"{numero:02d} | "
        f"{categoria:12} | "
        f"{elemento:8} | "
        f"{referencia:12} | "
        f"{len(itens):2} medição(ões) | "
        f"{tipos}"
    )

print()

print("=" * 90)