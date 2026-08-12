from pathlib import Path

from app.services.pdf_parser import extrair_texto_pdf


CAMINHO_PDF = "uploads/relatorio_teste.pdf"
CAMINHO_SAIDA = "texto_extraido.txt"


texto = extrair_texto_pdf(CAMINHO_PDF)

conteudo = []

conteudo.append("=" * 80)
conteudo.append("TEXTO EXTRAÍDO DO PDF")
conteudo.append("=" * 80)

for numero, linha in enumerate(texto.splitlines(), start=1):
    conteudo.append(f"{numero:04d}: {linha!r}")

conteudo.append("=" * 80)
conteudo.append(f"TOTAL DE LINHAS: {len(texto.splitlines())}")
conteudo.append("=" * 80)


Path(CAMINHO_SAIDA).write_text(
    "\n".join(conteudo),
    encoding="utf-8"
)

print(f"Arquivo gerado: {CAMINHO_SAIDA}")