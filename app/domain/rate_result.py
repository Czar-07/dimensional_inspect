# ============================================================
# DIMENSION-RATE
# RESULTADO DO RATE
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RateResult:

    # ========================================================
    # PONTOS / LOC
    # ========================================================

    calculated_points: int

    approved: int

    rejected: int

    calculated_percentage: float

    # ========================================================
    # MEDIÇÕES
    # ========================================================

    measurements_count: int

    # ========================================================
    # RATE DECLARADO
    # ========================================================

    declared_points: Optional[int]

    declared_percentage: Optional[float]

    # ========================================================
    # COMPARAÇÃO
    # ========================================================

    difference: Optional[float]

    consistent: Optional[bool]

    status: str

    # ========================================================
    # DETALHES
    # ========================================================

    out_of_tolerance: list

    categories: list

    # Auditoria de todos os LOCs detectados no PDF.
    points_audit: list = field(default_factory=list)

    measurements_details: list = field(default_factory=list)

    # ========================================================
    # SERIALIZAÇÃO
    # ========================================================

    def to_dict(self) -> dict:

        return {
            "calculated": {
                "points": self.calculated_points,
                "approved": self.approved,
                "rejected": self.rejected,
                "percentage": self.calculated_percentage,
            },

            "declared": {
                "points": self.declared_points,
                "percentage": self.declared_percentage,
            },

            "difference": self.difference,

            "consistent": self.consistent,

            "status": self.status,

            "measurements": self.measurements_count,

            "categories": self.categories,

            "out_of_tolerance": self.out_of_tolerance,
        }