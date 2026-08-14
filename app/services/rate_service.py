# ============================================================
# DIMENSION-RATE
# SERVIÇO DE CÁLCULO DO RATE
# ============================================================

from __future__ import annotations

from collections import OrderedDict
import re
from typing import Iterable

from app.domain.measurement import Measurement
from app.domain.rate_result import RateResult


# ============================================================
# CONFIGURAÇÃO
# ============================================================

TOLERANCIA_ARREDONDAMENTO = 1e-9


@property
def aprovado(self) -> bool:

    return (
        self.medicao >=
        self.limite_inferior -
        TOLERANCIA_ARREDONDAMENTO
        and
        self.medicao <=
        self.limite_superior +
        TOLERANCIA_ARREDONDAMENTO
    )



# ============================================================
# NORMALIZAÇÃO
# ============================================================

def _texto(valor) -> str:

    if valor is None:
        return ""

    return str(valor).strip()


def _numero(valor) -> float:

    if valor is None:
        return 0.0

    if isinstance(valor, (int, float)):
        return float(valor)

    texto = str(valor).strip()

    if not texto:
        return 0.0

    texto = (
        texto
        .replace("−", "-")
        .replace("–", "-")
        .replace(",", ".")
    )

    try:
        return float(texto)

    except (TypeError, ValueError):
        return 0.0


# ============================================================
# IDENTIDADE DO PONTO / LOC
# ============================================================

def _chave_ponto(medicao: Measurement) -> tuple:

    elemento = _texto(
        getattr(
            medicao,
            "elemento",
            ""
        )
    ).upper()

    if elemento:

        return (
            "ELEMENTO",
            elemento
        )

    categoria = _texto(
        getattr(
            medicao,
            "categoria",
            ""
        )
    ).upper()

    referencia = _texto(
        getattr(
            medicao,
            "referencia",
            ""
        )
    ).upper()

    return (
        "FALLBACK",
        categoria,
        referencia
    )


# ============================================================
# IDENTIDADE DA MEDIÇÃO
# ============================================================

def _chave_medicao(medicao: Measurement) -> tuple:

    return (
        _chave_ponto(medicao),

        _texto(
            getattr(
                medicao,
                "eixo",
                ""
            )
        ).upper(),

        round(
            _numero(
                getattr(
                    medicao,
                    "nominal",
                    0
                )
            ),
            9
        ),

        round(
            _numero(
                getattr(
                    medicao,
                    "tol_mais",
                    0
                )
            ),
            9
        ),

        round(
            _numero(
                getattr(
                    medicao,
                    "tol_menos",
                    0
                )
            ),
            9
        ),

        round(
            _numero(
                getattr(
                    medicao,
                    "medicao",
                    0
                )
            ),
            9
        ),

        round(
            _numero(
                getattr(
                    medicao,
                    "desvio",
                    0
                )
            ),
            9
        ),

        round(
            _numero(
                getattr(
                    medicao,
                    "fora_tolerancia",
                    0
                )
            ),
            9
        ),
    )


# ============================================================
# REMOVER DUPLICAÇÕES
# ============================================================

def _remover_medicoes_duplicadas(
    medicoes: Iterable[Measurement]
) -> list[Measurement]:

    unicas = OrderedDict()

    for medicao in medicoes:

        if medicao is None:
            continue

        chave = _chave_medicao(
            medicao
        )

        if chave not in unicas:

            unicas[chave] = medicao

    return list(
        unicas.values()
    )


# ============================================================
# AGRUPAR POR PONTO
# ============================================================

def _agrupar_por_ponto(
    medicoes: Iterable[Measurement]
) -> OrderedDict:

    grupos = OrderedDict()

    for medicao in medicoes:

        chave = _chave_ponto(
            medicao
        )

        if chave not in grupos:

            grupos[chave] = []

        grupos[chave].append(
            medicao
        )

    return grupos


# ============================================================
# STATUS DA MEDIÇÃO
# ============================================================

# ============================================================
# STATUS DA MEDIÇÃO
# ============================================================

def _medicao_aprovada(
    medicao: Measurement
) -> bool:
    """
    Classifica a medição usando o resultado dimensional do próprio
    relatório. O campo FORATOL é tratado como indicador explícito de
    fora de tolerância quando presente; a comparação pelos limites
    continua como segunda validação.
    """

    if medicao is None:
        return False

    try:
        fora = float(
            getattr(medicao, "fora_tolerancia", 0.0) or 0.0
        )
    except (TypeError, ValueError):
        fora = 0.0

    if fora > TOLERANCIA_ARREDONDAMENTO:
        return False

    if bool(getattr(medicao, "forcado_fora", False)):
        return False

    return bool(medicao.aprovado)


# ============================================================
# STATUS DO PONTO
# ============================================================

def _ponto_aprovado(
    medicoes_do_ponto: list[Measurement]
) -> bool:

    if not medicoes_do_ponto:

        return False

    return all(
        _medicao_aprovada(
            medicao
        )
        for medicao in medicoes_do_ponto
    )


# ============================================================
# SERIALIZAÇÃO DA MEDIÇÃO
# ============================================================

def _medicao_para_dict(
    medicao: Measurement
) -> dict:

    return {

        "elemento":
            _texto(
                getattr(
                    medicao,
                    "elemento",
                    ""
                )
            ),

        "categoria":
            _texto(
                getattr(
                    medicao,
                    "categoria",
                    ""
                )
            )
            or
            "OUTROS",

        "referencia":
            getattr(
                medicao,
                "referencia",
                None
            ),

        "eixo":
            getattr(
                medicao,
                "eixo",
                None
            ),

        "nominal":
            _numero(
                getattr(
                    medicao,
                    "nominal",
                    0
                )
            ),

        "medicao":
            _numero(
                getattr(
                    medicao,
                    "medicao",
                    0
                )
            ),

        "desvio":
            _numero(
                getattr(
                    medicao,
                    "desvio",
                    0
                )
            ),

        "fora_tolerancia":
            _numero(
                getattr(
                    medicao,
                    "fora_tolerancia",
                    0
                )
            ),

        "tolerancia_mais":
            _numero(
                getattr(
                    medicao,
                    "tol_mais",
                    0
                )
            ),

        "tolerancia_menos":
            _numero(
                getattr(
                    medicao,
                    "tol_menos",
                    0
                )
            ),
    }


# ============================================================
# RESUMO POR CATEGORIA
# ============================================================

def _resumo_categorias(
    medicoes: Iterable[Measurement]
) -> list[dict]:

    grupos = OrderedDict()

    for medicao in medicoes:

        categoria = _texto(
            getattr(
                medicao,
                "categoria",
                ""
            )
        ).upper()

        if not categoria:
            categoria = "OUTROS"

        if categoria not in grupos:

            grupos[categoria] = {
                "categoria": categoria,
                "total": 0,
                "aprovadas": 0,
                "reprovadas": 0,
            }

        grupos[categoria]["total"] += 1

        if _medicao_aprovada(
            medicao
        ):

            grupos[categoria]["aprovadas"] += 1

        else:

            grupos[categoria]["reprovadas"] += 1

    return list(
        grupos.values()
    )


# ============================================================
# CALCULAR RATE
# ============================================================


# ============================================================
# AUDITORIA DOS PONTOS
# ============================================================

def _auditoria_pontos(
    todos_os_pontos: set[str],
    grupos: OrderedDict,
    pontos_forcados_fora: set[str] | None = None,
) -> list[dict]:
    """Audita todas as características consideradas no RATE.

    LOCs são agrupados por elemento. Características sem LOC (por
    exemplo PLANO/DIST) são agrupadas pela chave de categoria/referência.
    """

    auditoria = []
    pontos_forcados_fora = {
        str(p).strip().upper()
        for p in (pontos_forcados_fora or set())
    }

    def ordem_chave(chave):
        if chave and chave[0] == "ELEMENTO":
            valor = chave[1]
            match = re.search(r"\d+", valor or "")
            return (0, int(match.group()) if match else 10**9, valor)
        return (1, str(chave[1] if len(chave) > 1 else ""), str(chave[2] if len(chave) > 2 else ""))

    # Características com medição: LOC e não-LOC.
    for chave, medicoes in sorted(grupos.items(), key=lambda item: ordem_chave(item[0])):
        if not medicoes:
            continue

        aprovado = _ponto_aprovado(medicoes)
        primeira = medicoes[0]
        eh_loc = chave[0] == "ELEMENTO"

        if eh_loc:
            identificador = chave[1]
            elemento = identificador
            referencia = _texto(getattr(primeira, "referencia", ""))
        else:
            categoria = _texto(getattr(primeira, "categoria", "")) or "OUTROS"
            referencia = _texto(getattr(primeira, "referencia", "")) or chave[-1]
            identificador = referencia or categoria
            elemento = identificador

        auditoria.append({
            "elemento": elemento,
            "categoria": _texto(getattr(primeira, "categoria", "")) or "OUTROS",
            "referencia": referencia,
            "status": "OK" if aprovado else "FORA",
            "conforme": aprovado,
            "medicoes": len(medicoes),
            "eixos": [
                _texto(getattr(m, "eixo", ""))
                for m in medicoes
            ],
            "fora_tolerancia": [
                _medicao_para_dict(m)
                for m in medicoes
                if not _medicao_aprovada(m)
            ],
        })

    # LOCs detectados no PDF mas que não produziram Measurement.
    for elemento in sorted(
        todos_os_pontos - {
            chave[1]
            for chave in grupos
            if chave and chave[0] == "ELEMENTO"
        },
        key=lambda valor: (
            int(re.search(r"\d+", valor).group())
            if re.search(r"\d+", valor)
            else 10**9,
            valor,
        ),
    ):
        if elemento in pontos_forcados_fora:
            status = "FORA"
            conforme = False
        else:
            status = "SEM_MEDICAO"
            conforme = None

        auditoria.append({
            "elemento": elemento,
            "categoria": "OUTROS",
            "referencia": "FORA VISUAL HEXAGON" if status == "FORA" else None,
            "status": status,
            "conforme": conforme,
            "medicoes": 0,
            "eixos": [],
            "fora_tolerancia": [],
        })

    return auditoria


def calcular_rate(
    medicoes: Iterable[Measurement],
    rate_declarado: tuple[int, float] | None = None,
    pontos_detectados: Iterable[str] | None = None,
    pontos_forcados_fora: Iterable[str] | None = None,
) -> RateResult:

    medicoes = list(
        medicoes or []
    )

    # ========================================================
    # 1. REMOVER DUPLICAÇÕES
    # ========================================================

    medicoes = (
        _remover_medicoes_duplicadas(
            medicoes
        )
    )

    # ========================================================
    # 2. AGRUPAR POR LOC
    # ========================================================

    grupos = _agrupar_por_ponto(
        medicoes
    )

    # ========================================================
    # 3. TOTAL REAL DE PONTOS
    # ========================================================
    #
    # Alguns relatórios Hexagon possuem LOCs válidos que não geram
    # uma Measurement convencional (por exemplo, LOC4/LOC5 no 7028,
    # que possuem coordenadas auxiliares/PR). Esses LOCs continuam
    # sendo pontos dimensionais e não podem desaparecer do denominador.
    #
    # A lista de LOCs detectados pelo parser é unida aos LOCs que
    # possuem medições.

    pontos_forcados_fora_normalizados = {
        str(ponto).strip().upper()
        for ponto in (pontos_forcados_fora or [])
        if str(ponto).strip()
    }

    pontos_detectados_normalizados = {
        str(ponto).strip().upper()
        for ponto in (pontos_detectados or [])
        if str(ponto).strip()
    }

    pontos_com_medicao = {
        chave[1]
        for chave in grupos
        if chave and chave[0] == "ELEMENTO"
    }

    todos_os_pontos = (
        pontos_detectados_normalizados
        | pontos_com_medicao
    )

    # ========================================================
    # REGRA DO RATE: CARACTERÍSTICA, NÃO LINHA DE MEDIÇÃO
    # ========================================================
    #
    # Um LOC com X/Y/Z/D/L continua sendo UMA característica.
    # Porém, relatórios Hexagon também possuem características que
    # não são LOCs, como PLANO1..4 e DIST1. Cada grupo
    # (categoria + referência) representa uma característica e
    # também precisa entrar no denominador do RATE.
    #
    # Exemplo do relatório 7131:
    #   45 LOCs + 4 PLANOS + 1 DIST = 50 características.
    #
    # O algoritmo antigo contabilizava somente os LOCs e, por isso,
    # retornava 45.
    caracteristicas_com_medicao = len(grupos)

    # LOCs detectados pelo parser mas sem Measurement continuam no
    # denominador, pois são características existentes no relatório.
    caracteristicas_sem_medicao = (
        todos_os_pontos - pontos_com_medicao
    )

    pontos_total = (
        caracteristicas_com_medicao
        + len(caracteristicas_sem_medicao)
    )

    pontos_aprovados = 0

    pontos_reprovados = 0

    # ========================================================
    # 4. PONTOS FORA DA TOLERÂNCIA
    # ========================================================

    fora_tolerancia = []

    # Cada grupo representa uma característica do relatório.
    # Para LOCs, X/Y/Z/D/L pertencem ao mesmo ponto. Para
    # características sem LOC (PLANO, DIST etc.), cada grupo também
    # representa uma característica única.
    for chave, grupo in grupos.items():

        aprovado = _ponto_aprovado(
            grupo
        )

        if aprovado:
            pontos_aprovados += 1
        else:
            pontos_reprovados += 1

        for medicao in grupo:
            if not _medicao_aprovada(medicao):
                fora_tolerancia.append(
                    _medicao_para_dict(medicao)
                )

    # LOCs válidos sem nenhuma medição avaliável não devem ser
    # eliminados do total. Como não existe uma característica
    # toleranciada reconhecida para reprovar esse LOC, ele entra
    # como ponto aprovado até que o parser reconheça sua medição.
    pontos_sem_medicao = (
        todos_os_pontos
        - pontos_com_medicao
    )

    # LOCs sem Measurement convencional permanecem no denominador,
    # mas NÃO são automaticamente reprovados. Isso é importante para
    # LOCs como LOC4 no 7028, que possuem dados auxiliares sem uma
    # Measurement padrão. Se o próprio PDF marcou alguma linha desse
    # LOC em vermelho, ele é reprovado explicitamente.
    sem_medicao_forados = pontos_sem_medicao & pontos_forcados_fora_normalizados
    sem_medicao_neutros = pontos_sem_medicao - sem_medicao_forados
    pontos_reprovados += len(sem_medicao_forados)
    pontos_aprovados += len(sem_medicao_neutros)

    # Mantém também esses pontos na lista pública de não conformidades,
    # mesmo sem uma Measurement convencional, para que a interface não
    # mostre 46 características enquanto o RATE mostra 47 pontos.
    for elemento in sorted(sem_medicao_forados, key=lambda v: int(re.search(r"\d+", v).group()) if re.search(r"\d+", v) else 10**9):
        fora_tolerancia.append({
            "elemento": elemento,
            "categoria": "OUTROS",
            "referencia": "FORA VISUAL HEXAGON",
            "eixo": None,
            "nominal": None,
            "medicao": None,
            "desvio": None,
            "fora_tolerancia": None,
            "tolerancia_mais": None,
            "tolerancia_menos": None,
        })

    # ========================================================
    # 5. RATE
    #
    # Fórmula:
    #
    # RATE =
    #
    # ((TOTAL - FORA) / TOTAL) * 100
    #
    # Exemplo:
    #
    # TOTAL = 100
    # FORA  = 5
    #
    # RATE = 95%
    # ========================================================

    if pontos_total > 0:

        percentual = (
            (
                pontos_total -
                pontos_reprovados
            )
            /
            pontos_total
        ) * 100.0

    else:

        percentual = 0.0

    percentual = round(
        percentual,
        2
    )

    # ========================================================
    # 6. RATE DECLARADO
    # ========================================================

    declarado_pontos = None

    declarado_percentual = None

    if rate_declarado is not None:

        declarado_pontos = int(
            rate_declarado[0]
        )

        declarado_percentual = round(
            float(
                rate_declarado[1]
            ),
            2
        )

    # ========================================================
    # 7. DIFERENÇA
    # ========================================================

    if declarado_percentual is not None:

        diferenca = round(
            percentual -
            declarado_percentual,
            2
        )

    else:

        diferenca = None

    # ========================================================
    # 8. CONSISTÊNCIA
    # ========================================================

    if declarado_percentual is None:

        consistente = None

        status = "NAO_DECLARADO"

    else:

        consistente = (
            abs(
                diferenca
            ) <= 0.01
        )

        status = (
            "CONSISTENTE"
            if consistente
            else
            "DIVERGENTE"
        )

    # ========================================================
    # 9. CATEGORIAS
    # ========================================================

    categorias = _resumo_categorias(
        medicoes
    )

    # ========================================================
    # 10. AUDITORIA DOS PONTOS
    # ========================================================

    auditoria = _auditoria_pontos(
        todos_os_pontos=todos_os_pontos,
        grupos=grupos,
        pontos_forcados_fora=pontos_forcados_fora_normalizados,
    )

    # ========================================================
    # 11. RESULTADO
    # ========================================================

    return RateResult(

        calculated_points=
            pontos_total,

        approved=
            pontos_aprovados,

        rejected=
            pontos_reprovados,

        calculated_percentage=
            percentual,

        measurements_count=
            len(medicoes),

        declared_points=
            declarado_pontos,

        declared_percentage=
            declarado_percentual,

        difference=
            diferenca,

        consistent=
            consistente,

        status=
            status,

        out_of_tolerance=
            fora_tolerancia,

        categories=
            categorias,

        points_audit=
            auditoria,

        measurements_details=[
            _medicao_para_dict(medicao)
            for medicao in medicoes
        ],
    )