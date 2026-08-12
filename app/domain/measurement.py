# ============================================================
# DIMENSION-RATE
# MODELO DE MEDIÇÃO
# ============================================================

from dataclasses import dataclass
from typing import Optional


# ============================================================
# CONFIGURAÇÃO
# ============================================================

TOLERANCIA_ARREDONDAMENTO = 1e-9


# ============================================================
# MEDIÇÃO
# ============================================================

@dataclass
class Measurement:

    # ========================================================
    # IDENTIFICAÇÃO
    # ========================================================

    elemento: str

    categoria: str

    referencia: Optional[str]

    eixo: Optional[str]

    # ========================================================
    # ESPECIFICAÇÃO
    # ========================================================

    nominal: float

    tol_mais: float

    tol_menos: float

    # ========================================================
    # RESULTADO DA MEDIÇÃO
    # ========================================================

    medicao: float

    desvio: float

    fora_tolerancia: float

    # True quando o próprio PDF Hexagon marcou visualmente a
    # característica em vermelho (FORA). Isso é necessário porque
    # alguns relatórios arredondam o valor exibido até o limite, mas
    # ainda assim classificam a característica como fora.
    forcado_fora: bool = False

    # ========================================================
    # LIMITE SUPERIOR
    # ========================================================

    @property
    def limite_superior(self) -> float:
        """
        Retorna o limite máximo permitido para a medição.

        Fórmula:

            limite superior =
                nominal + tolerância positiva
        """

        return (
            self.nominal +
            self.tol_mais
        )

    # ========================================================
    # LIMITE INFERIOR
    # ========================================================

    @property
    def limite_inferior(self) -> float:
        """
        Retorna o limite mínimo permitido para a medição.

        Fórmula:

            limite inferior =
                nominal - tolerância negativa
        """

        return (
            self.nominal -
            self.tol_menos
        )

    # ========================================================
    # APROVAÇÃO
    # ========================================================

    @property
    def aprovado(self) -> bool:
        """
        Determina se a medição está dentro da tolerância.

        A comparação utiliza uma pequena tolerância numérica
        para evitar erros de ponto flutuante.
        """

        if self.forcado_fora:
            return False

        # A tolerância numérica continua inclusiva quando o PDF não
        # fornece uma indicação visual de reprovação.
        return (
            self.medicao >= (
                self.limite_inferior -
                TOLERANCIA_ARREDONDAMENTO
            )
            and
            self.medicao <= (
                self.limite_superior +
                TOLERANCIA_ARREDONDAMENTO
            )
        )

    # ========================================================
    # REPROVAÇÃO
    # ========================================================

    @property
    def reprovado(self) -> bool:
        """
        Retorna True quando a medição está fora da tolerância.
        """

        return not self.aprovado