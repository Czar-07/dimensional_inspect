"""
Parser robusto de medições dimensionais do DIMENSION-RATE.

O texto extraído de PDFs varia bastante conforme o gerador do relatório.

Alguns PDFs entregam cada campo em uma linha, enquanto outros entregam
toda a linha de medição de uma vez.

Este módulo suporta os dois formatos sem assumir uma quantidade fixa
de pontos.
"""

from __future__ import annotations

import re
from typing import Optional

from app.domain.measurement import Measurement


# ============================================================
# ELEMENTOS DOS RELATÓRIOS HEXAGON / DIMENSIONAIS
# ============================================================

# Exemplos:
#
# LOC10 - DATUM C
# LOC16 - MTC6
# PLANO1 - PLN1
#
PADRAO_ELEMENTO = re.compile(
    r"^(?P<elemento>LOC\d+)\s*-\s*(?P<referencia>.+?)\s*$",
    re.IGNORECASE,
)

# Características do relatório que possuem a mesma estrutura de
# uma medição LOC, mas não são LOCs. Ex.: PLANO1 e DIST1.
PADRAO_CARACTERISTICA = re.compile(
    r"^\s*(?:[^A-Za-z0-9]*\s*MM\s*)?(?P<elemento>(?:LOC|PLANO|DIST)\d+)\s*-\s*(?P<referencia>.+?)\s*$",
    re.IGNORECASE,
)


# ============================================================
# TIPOS DE MEDIÇÃO
# ============================================================

TIPOS_MEDICAO = {
    "X",
    "Y",
    "Z",
    "M",
    "D",
    "T",
    # Características dimensionais que o Hexagon exporta como
    # "eixos" próprios em pontos especiais (slot/círculo).
    "CDF",
    "LE",
    "DE",
}


# ============================================================
# NÚMERO
# ============================================================

# Aceita:
#
# 10
# 10.50
# 10,50
# -10.50
# +10.50
# −10.50
# –10.50
#
NUMERO = r"[-+−–]?\d+(?:[.,]\d+)?"


# ============================================================
# MEDIÇÃO COMPACTA
# ============================================================

# Exemplo:
#
# X 4776.40 0.50 0.50 4776.40 0.00 0.00
#
PADRAO_MEDICAO_COMPACTA = re.compile(
    rf"^(?P<eixo>[XYZMDT]|CDF|LE|DE)\s+"
    rf"(?P<nominal>{NUMERO})\s+"
    rf"(?P<tol_mais>{NUMERO})\s+"
    rf"(?P<tol_menos>{NUMERO})\s+"
    rf"(?P<medicao>{NUMERO})\s+"
    rf"(?P<desvio>{NUMERO})\s+"
    rf"(?P<fora>{NUMERO})\s*$",
    re.IGNORECASE,
)


# ============================================================
# CABEÇALHOS
# ============================================================

CABECALHOS = {
    "RELATÓRIO DIMENSIONAL",
    "RELATORIO DIMENSIONAL",
    "AX",
    "NOMINAL TOL+ TOL-",
    "NOMINAL TOL+ TOL- MED DESV",
    "FORATOL",
    "MED DESV",
    "MM",
}


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def _normalizar_linha(linha: str) -> str:
    """
    Normaliza espaços sem alterar os números ou sinais.
    """

    linha = str(linha or "")

    linha = linha.replace(
        "\u00a0",
        " "
    )

    return re.sub(
        r"\s+",
        " ",
        linha.strip()
    ).strip()


# ============================================================
# CONVERSÃO NUMÉRICA
# ============================================================

def _numero(valor: str) -> Optional[float]:
    """
    Converte números com ponto/vírgula decimal e sinais Unicode.
    """

    if valor is None:
        return None

    valor = str(valor).strip()

    valor = valor.replace(
        "−",
        "-"
    )

    valor = valor.replace(
        "–",
        "-"
    )

    valor = valor.replace(
        ",",
        "."
    )

    try:
        return float(valor)

    except (TypeError, ValueError):
        return None


# ============================================================
# IDENTIFICAÇÃO DE CATEGORIA
# ============================================================

def identificar_categoria(
    referencia: str | None,
    elemento: str | None = None,
) -> str:
    """
    Classifica a medição usando a referência e, quando necessário,
    o elemento.

    O fallback é OUTROS.
    """

    referencia = str(
        referencia or ""
    ).upper().strip()

    elemento = str(
        elemento or ""
    ).upper().strip()

    texto = f"{referencia} {elemento}"


    # --------------------------------------------------------
    # DATUM
    # --------------------------------------------------------

    if (
        "DATUM" in texto
        or re.search(
            r"\bDAT\b",
            texto
        )
    ):
        return "DATUM"


    # --------------------------------------------------------
    # MATCHING
    # --------------------------------------------------------

    if (
        referencia.startswith(
            (
                "MTC",
                "MATCH",
                "MATCHING",
            )
        )
        or "MATCHING" in texto
    ):
        return "MATCHING"


    # --------------------------------------------------------
    # PLANOS
    # --------------------------------------------------------

    if (
        referencia.startswith(
            (
                "PLN",
                "PLAN",
            )
        )
        or "PLANO" in texto
        or "PLANICIDADE" in texto
    ):
        return "PLANOS"


    # --------------------------------------------------------
    # SUPERFÍCIES
    # --------------------------------------------------------

    if (
        referencia.startswith(
            (
                "SUP",
                "SURF",
                "SFC",
            )
        )
        or "SUPERFICIE" in texto
        or "SUPERFÍCIE" in texto
    ):
        return "SUPERFÍCIES"


    # --------------------------------------------------------
    # BORDAS
    # --------------------------------------------------------

    if (
        referencia.startswith(
            (
                "BRD",
                "EDGE",
                "BORD",
            )
        )
        or "BORDA" in texto
        or "BORDAS" in texto
    ):
        return "BORDAS"


    # --------------------------------------------------------
    # FUROS
    # --------------------------------------------------------

    if (
        referencia.startswith(
            (
                "FUR",
                "FURO",
                "HOLE",
                "CIR",
                "CIRC",
                "DIAM",
            )
        )
        or any(
            termo in texto
            for termo in (
                "FURAÇÃO",
                "FURACAO",
                "FURO",
                "CÍRCULO",
                "CIRCULO",
                "HOLE",
            )
        )
    ):
        return "FURAÇÃO"


    # --------------------------------------------------------
    # PARAFUSOS
    # --------------------------------------------------------

    if (
        referencia.startswith(
            (
                "PARAF",
                "BOLT",
                "SCREW",
            )
        )
        or any(
            termo in texto
            for termo in (
                "PARAFUSO",
                "PARAFUSOS",
                "BOLT",
                "SCREW",
            )
        )
    ):
        return "PARAFUSOS"


    # --------------------------------------------------------
    # OBLONGOS
    # --------------------------------------------------------

    if (
        referencia.startswith(
            (
                "OBL",
                "OBLONG",
            )
        )
        or "OBLONGO" in texto
        or "OBLONG" in texto
    ):
        return "FURAÇÃO"


    # --------------------------------------------------------
    # POSICIONAMENTO
    # --------------------------------------------------------

    if (
        referencia.startswith(
            (
                "POS",
                "LOC",
                "POSITION",
            )
        )
        or any(
            termo in texto
            for termo in (
                "POSIÇÃO",
                "POSICAO",
                "POSITION",
            )
        )
    ):
        return "POSICIONAMENTO"


    # --------------------------------------------------------
    # DIMENSÕES
    # --------------------------------------------------------

    if (
        referencia.startswith(
            (
                "DIM",
                "ANG",
                "LEN",
                "DIST",
                "SIZE",
            )
        )
        or any(
            termo in texto
            for termo in (
                "DIMENSÃO",
                "DIMENSAO",
                "DISTÂNCIA",
                "DISTANCIA",
                "ÂNGULO",
                "ANGULO",
            )
        )
    ):
        return "DIMENSÕES"


    return "OUTROS"


# ============================================================
# CATEGORIA POR SEÇÃO
# ============================================================

def categoria_por_secao(
    secao: str | None,
) -> str | None:
    """
    Converte o título de uma seção do relatório em categoria.
    """

    secao = str(
        secao or ""
    ).upper().strip()

    mapa = {
        "DATUM": "DATUM",
        "FURAÇÃO": "FURAÇÃO",
        "FURACAO": "FURAÇÃO",
        "MATCHING": "MATCHING",
        "SUPERFICIE": "SUPERFÍCIES",
        "SUPERFÍCIE": "SUPERFÍCIES",
        "BORDAS": "BORDAS",
        "PARAFUSOS": "PARAFUSOS",
        "PARAFUSO": "PARAFUSOS",
        "PLANOS": "PLANOS",
        "PLANO": "PLANOS",
        "POSICIONAMENTO": "POSICIONAMENTO",
        "DIMENSÕES": "DIMENSÕES",
        "DIMENSOES": "DIMENSÕES",
    }

    return mapa.get(secao)


# ============================================================
# EXTRAÇÃO — LINHA COMPACTA
# ============================================================

def _extrair_linha_compacta(
    linha: str,
) -> tuple[str, list[float]] | None:
    """
    Reconhece uma medição inteira em uma única linha.
    """

    resultado = PADRAO_MEDICAO_COMPACTA.match(
        linha
    )

    if not resultado:
        return None


    valores = [
        _numero(
            resultado.group(nome)
        )
        for nome in (
            "nominal",
            "tol_mais",
            "tol_menos",
            "medicao",
            "desvio",
            "fora",
        )
    ]


    if any(
        valor is None
        for valor in valores
    ):
        return None


    return (
        resultado.group(
            "eixo"
        ).upper(),

        [
            float(valor)
            for valor in valores
        ],
    )


# ============================================================
# EXTRAÇÃO — SEIS NÚMEROS
# ============================================================

def _extrair_seis_numeros(
    linhas: list[str],
    inicio: int,
) -> tuple[list[float], int] | None:
    """
    Lê seis números consecutivos depois de um eixo isolado.

    Exemplo:

        X
        3144.00
        0.70 0.70 3143.51 -0.49
        0.63
    """

    valores: list[float] = []

    indice = inicio

    saltos = 0


    while (
        indice < len(linhas)
        and len(valores) < 6
    ):

        linha = linhas[indice]

        maiuscula = linha.upper()


        if not linha:

            indice += 1

            saltos += 1

            if saltos > 3:
                return None

            continue


        # ----------------------------------------------------
        # Não atravessar novo eixo
        # ----------------------------------------------------

        if maiuscula in TIPOS_MEDICAO:
            return None


        # ----------------------------------------------------
        # Não atravessar novo elemento
        # ----------------------------------------------------

        if PADRAO_CARACTERISTICA.match(
            linha
        ):
            return None


        # ----------------------------------------------------
        # Cabeçalhos
        # ----------------------------------------------------

        if maiuscula in CABECALHOS:

            indice += 1

            saltos += 1

            if saltos > 5:
                return None

            continue


        # ----------------------------------------------------
        # Tokens numéricos
        # ----------------------------------------------------

        tokens = re.findall(
            NUMERO,
            linha
        )


        if not tokens:
            return None


        for token in tokens:

            numero = _numero(
                token
            )

            if numero is None:
                return None

            valores.append(
                numero
            )

            if len(valores) == 6:
                break


        indice += 1


    if len(valores) != 6:
        return None


    return (
        valores,
        indice,
    )


# ============================================================
# CRIAR MEDIÇÃO
# ============================================================

def _nova_medicao(
    *,
    elemento: str,
    referencia: Optional[str],
    categoria: str,
    eixo: str,
    valores: list[float],
    forcado_fora: bool = False,
) -> Measurement:

    return Measurement(
        elemento=elemento,
        categoria=categoria,
        referencia=referencia,
        eixo=eixo,

        nominal=valores[0],

        tol_mais=valores[1],

        tol_menos=valores[2],

        medicao=valores[3],

        desvio=valores[4],

        fora_tolerancia=max(
            0.0,
            valores[5],
        ),

        forcado_fora=forcado_fora,
    )


# ============================================================
# EXTRAIR MEDIÇÕES
# ============================================================

def extrair_medicoes(
    texto: str,
) -> list[Measurement]:
    """
    Extrai todas as medições dimensionais reconhecidas no texto do PDF.

    A quantidade de pontos é descoberta dinamicamente.
    """

    if not texto:
        return []


    linhas = [
        _normalizar_linha(linha)
        for linha in str(texto).splitlines()
    ]


    linhas = [
        linha
        for linha in linhas
        if linha
    ]


    medicoes: list[Measurement] = []


    elemento_atual: str | None = None

    referencia_atual: str | None = None

    categoria_atual = "OUTROS"

    secao_atual: str | None = None


    i = 0


    while i < len(linhas):

        linha_original = linhas[i]

        forcado_fora = linha_original.upper().startswith(MARCADOR_FORA)

        linha = (
            linha_original[len(MARCADOR_FORA):].strip()
            if forcado_fora
            else linha_original
        )

        maiuscula = linha.upper()


        # ====================================================
        # SEÇÃO
        # ====================================================

        categoria_secao = categoria_por_secao(
            maiuscula
        )


        if categoria_secao is not None:

            secao_atual = maiuscula

            i += 1

            continue


        # ====================================================
        # MEDIÇÃO COMPACTA
        # ====================================================

        compacta = _extrair_linha_compacta(
            linha
        )


        if (
            compacta
            and elemento_atual is not None
        ):

            eixo, valores = compacta


            medicoes.append(
                _nova_medicao(
                    elemento=elemento_atual,
                    referencia=referencia_atual,
                    categoria=categoria_atual,
                    eixo=eixo,
                    valores=valores,
                    forcado_fora=forcado_fora,
                )
            )


            i += 1

            continue


        # ====================================================
        # NOVO ELEMENTO
        # ====================================================

        elemento_match = PADRAO_CARACTERISTICA.match(
            linha
        )


        if elemento_match:

            elemento_atual = (
                elemento_match
                .group("elemento")
                .strip()
            )


            referencia_atual = (
                elemento_match
                .group("referencia")
                .strip()
            )


            categoria_atual = identificar_categoria(
                referencia_atual,
                elemento_atual,
            )


            if categoria_atual == "OUTROS":

                categoria_atual = (
                    categoria_por_secao(
                        secao_atual
                    )
                    or "OUTROS"
                )


            i += 1

            continue


        # ====================================================
        # FORMATO VERTICAL
        # ====================================================

        if (
            maiuscula in TIPOS_MEDICAO
            and elemento_atual is not None
        ):

            bloco = _extrair_seis_numeros(
                linhas,
                i + 1,
            )


            if bloco is not None:

                valores, proximo = bloco


                medicoes.append(
                    _nova_medicao(
                        elemento=elemento_atual,
                        referencia=referencia_atual,
                        categoria=categoria_atual,
                        eixo=maiuscula,
                        valores=valores,
                        forcado_fora=forcado_fora,
                    )
                )


                i = proximo

                continue


        i += 1


    return medicoes


# ============================================================
# MARCADOR VISUAL DE FORA DO HEXAGON
# ============================================================

MARCADOR_FORA = "__HEXAGON_FORA__"


# ============================================================
# ELEMENTOS / PONTOS DETECTADOS
# ============================================================

def extrair_pontos(texto: str) -> list[str]:
    """Retorna todos os LOCs presentes no relatório, na ordem original."""

    if not texto:
        return []

    pontos: list[str] = []
    vistos: set[str] = set()

    for linha_bruta in str(texto).splitlines():
        linha = _normalizar_linha(linha_bruta)
        match = PADRAO_ELEMENTO.match(linha)

        if not match:
            continue

        elemento = match.group("elemento").upper().strip()

        if elemento not in vistos:
            vistos.add(elemento)
            pontos.append(elemento)

    return pontos


def extrair_caracteristicas(texto: str) -> list[str]:
    """Retorna todas as características numeradas do relatório.

    Inclui LOCs e características independentes como PLANO e DIST.
    """
    if not texto:
        return []

    caracteristicas: list[str] = []
    vistos: set[str] = set()

    for linha_bruta in str(texto).splitlines():
        linha = _normalizar_linha(linha_bruta)
        match = PADRAO_CARACTERISTICA.match(linha)
        if not match:
            continue

        elemento = match.group("elemento").upper().strip()
        if elemento not in vistos:
            vistos.add(elemento)
            caracteristicas.append(elemento)

    return caracteristicas


# ============================================================
# LOCs MARCADOS VISUALMENTE COMO FORA
# ============================================================

def extrair_pontos_forcados_fora(texto: str) -> list[str]:
    """Retorna LOCs que possuem ao menos uma linha marcada em vermelho
    pelo relatório Hexagon, mesmo quando essa característica não gera
    uma Measurement convencional (ex.: PR/ITE em LOC5).
    """
    if not texto:
        return []

    fora: list[str] = []
    vistos: set[str] = set()
    elemento_atual: str | None = None

    for linha_bruta in str(texto).splitlines():
        linha = _normalizar_linha(linha_bruta)
        marcada = linha.startswith(MARCADOR_FORA)
        if marcada:
            linha = linha[len(MARCADOR_FORA):].strip()

        match = PADRAO_ELEMENTO.match(linha)
        if match:
            elemento_atual = match.group("elemento").upper().strip()
            continue

        if marcada and elemento_atual and elemento_atual not in vistos:
            vistos.add(elemento_atual)
            fora.append(elemento_atual)

    return fora


# ============================================================
# FILTRO DE PÁGINAS
# ============================================================

_MARCADOR_ELEMENTO = re.compile(
    r"^LOC\d+\s*-\s*.+$"
)

_MARCADOR_EIXO = re.compile(
    r"^(?:XYZMDT|CDF|LE|DE)$",
    re.IGNORECASE,
)


# ============================================================
# PÁGINA TEM MEDIÇÃO
# ============================================================

def pagina_tem_medicao(
    texto: str,
) -> bool:
    """
    Retorna True quando a página contém pelo menos uma
    medição dimensional válida.
    """

    if not texto or not texto.strip():
        return False


    return bool(
        extrair_medicoes(texto)
    )


# ============================================================
# FILTRAR PÁGINAS DIMENSIONAIS
# ============================================================

def filtrar_paginas_dimensionais(
    paginas: list[str],
) -> tuple[list[str], list[dict]]:
    """
    Mantém somente páginas que possuem pontos dimensionais.

    Retorna:

        (
            páginas_mantidas,
            páginas_ignoradas
        )
    """

    mantidas: list[str] = []

    ignoradas: list[dict] = []


    for numero, texto in enumerate(
        paginas,
        start=1,
    ):

        if pagina_tem_medicao(texto):

            mantidas.append(
                texto
            )

            continue


        texto_upper = (
            texto or ""
        ).upper()


        if any(
            termo in texto_upper
            for termo in (
                "MAPA DE COR",
                "COLOR MAP",
                "MAPA COR",
            )
        ):

            motivo = "MAPA_DE_COR"

        else:

            motivo = (
                "SEM_PONTOS_DIMENSIONAIS"
            )


        ignoradas.append(
            {
                "pagina": numero,
                "motivo": motivo,
            }
        )


    return (
        mantidas,
        ignoradas,
    )


# ============================================================
# RESUMO POR CATEGORIA
# ============================================================

def resumir_medicoes_por_categoria(
    medicoes: list[Measurement],
) -> list[dict]:
    """
    Gera o resumo das medições agrupadas por categoria.

    Cada categoria informa:

    - categoria
    - total

    O total representa a quantidade de medições/eixos
    extraídos pelo parser.
    """

    contagem: dict[str, int] = {}

    for medicao in medicoes:

        if medicao is None:
            continue

        categoria = str(
            getattr(
                medicao,
                "categoria",
                ""
            ) or "OUTROS"
        ).strip().upper()

        if not categoria:
            categoria = "OUTROS"

        contagem[categoria] = (
            contagem.get(
                categoria,
                0
            ) + 1
        )

    ordem = [
        "DATUM",
        "PLANOS",
        "MATCHING",
        "SUPERFÍCIES",
        "FURAÇÃO",
        "PARAFUSOS",
        "POSICIONAMENTO",
        "DIMENSÕES",
        "BORDAS",
        "OUTROS",
    ]

    categorias = []

    for categoria in ordem:

        if categoria not in contagem:
            continue

        categorias.append({
            "categoria": categoria,
            "total": contagem[categoria],
        })

    # Categorias que eventualmente não estejam
    # na ordem principal.
    for categoria, total in contagem.items():

        if categoria in ordem:
            continue

        categorias.append({
            "categoria": categoria,
            "total": total,
        })

    return categorias