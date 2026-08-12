from app.services.pdf_parser import extrair_texto_pdf
from app.services.rate_parser import extrair_rate_declarado


CAMINHO_PDF = "uploads/relatorio_teste.pdf"


texto = extrair_texto_pdf(
    CAMINHO_PDF
)


resultado = extrair_rate_declarado(
    texto
)


print("=" * 80)
print("DIMENSION-RATE")
print("FASE 3.2 - PARSER DO RATE DECLARADO")
print("=" * 80)

print()

if resultado is None:

    print(
        "ERRO: RATE não encontrado no PDF."
    )

else:

    pontos, rate = resultado

    print(
        f"Pontos declarados : {pontos}"
    )

    print(
        f"RATE declarado    : {rate:.2f}%"
    )

print()

print("=" * 80)