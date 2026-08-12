from app.services.pdf_parser import extrair_texto_pdf
from app.services.measurement_service import extrair_medicoes, extrair_pontos
from app.services.rate_service import calcular_rate


def _analisar(caminho):
    with open(caminho, "rb") as arquivo:
        texto = extrair_texto_pdf(arquivo.read())
    medicoes = extrair_medicoes(texto)
    pontos = extrair_pontos(texto)
    return calcular_rate(medicoes, pontos_detectados=pontos)


def test_7004_tem_117_pontos_e_15_fora():
    resultado = _analisar("/mnt/data/7004_69100BP400_CALIBRADA_PC04_HYUNDAI.PDF")

    assert resultado.calculated_points == 117
    assert resultado.rejected == 15
    assert resultado.approved == 102
    assert resultado.calculated_percentage == 87.18

    fora = {item["elemento"] for item in resultado.points_audit if item["status"] == "FORA"}
    assert fora == {
        "LOC3", "LOC88", "LOC99", "LOC102", "LOC111",
        "LOC145", "LOC146", "LOC147", "LOC148", "LOC149",
        "LOC165", "LOC171", "LOC178", "LOC190", "LOC199",
    }


def test_7013_tem_117_pontos():
    resultado = _analisar("/mnt/data/7013_69100BP400_CALIBRADA_PC06_HYUNDAI.PDF")
    assert resultado.calculated_points == 117


def test_7028_tem_111_pontos_mesmo_com_loc_especial_sem_medicao():
    resultado = _analisar("/mnt/data/7028_69148BP000_PC01_HYUNDAI.PDF")
    assert resultado.calculated_points == 111
