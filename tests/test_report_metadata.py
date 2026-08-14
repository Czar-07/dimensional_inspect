from app.services.pdf_parser import extrair_metadados_relatorio

def test_extrai_part_number_do_cabecalho():
    texto = "Nº Desenho : 2FC 864 103 Nome da Peça Revisão : 001\nNº Peça : 2FC 864 103 : LOWER BRACKET PEÇA : 01"
    meta = extrair_metadados_relatorio(texto)
    assert meta["part_number"] == "2FC 864 103"


def test_fallback_part_number_pelo_nome_do_arquivo():
    meta = extrair_metadados_relatorio(
        "RELATORIO SEM PART NUMBER NO CABECALHO",
        "7162_752D48642R_PC01_RENAULT.pdf",
    )
    assert meta["report_number"] == "7162"
    assert meta["part_number"] == "752D48642R"
    assert meta["piece"] == "PC01"
    assert meta["client"] == "RENAULT"


def test_part_number_do_pdf_tem_prioridade_sobre_nome_do_arquivo():
    meta = extrair_metadados_relatorio(
        "Nº Peça : PDF-123",
        "7162_752D48642R_PC01_RENAULT.pdf",
    )
    assert meta["part_number"] == "PDF-123"
    assert meta["report_number"] == "7162"
