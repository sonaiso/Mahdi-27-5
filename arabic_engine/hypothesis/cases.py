"""Case hypotheses — فرضيات الحالة الإعرابية.

Generates case (i'rāb) hypotheses from role + factor hypotheses.
Case is treated as a *stabilisation decision* — not a direct lookup.

Expanded role-case mapping covering:
- Standard verbal sentence roles (فاعل, مفعول)
- Nominal sentence roles (مبتدأ, خبر)
- إنّ وأخواتها (اسم إنّ, خبر إنّ)
- كان وأخواتها (اسم كان, خبر كان)
- Preposition-governed (مجرور)
- Vocative (منادى)
- Particles and tools (أداة)
"""

from __future__ import annotations

from typing import List

from arabic_engine.core.enums import ActivationStage, HypothesisStatus
from arabic_engine.core.types import HypothesisNode

_ROLE_CASE_MAP: dict[str, str] = {
    # Standard verbal roles
    "فاعل": "رفع",
    "مفعول": "نصب",
    "فعل": "مبني",
    # Nominal sentence
    "مبتدأ": "رفع",
    "خبر": "رفع",
    # إنّ وأخواتها
    "اسم_إن": "نصب",
    "خبر_إن": "رفع",
    # كان وأخواتها
    "اسم_كان": "رفع",
    "خبر_كان": "نصب",
    # Preposition-governed
    "حرف_جر": "مبني",
    "مجرور": "جر",
    "مضاف_إليه": "جر",
    # Vocative
    "منادى": "بناء",
    # Adverbial
    "حال": "نصب",
    "تمييز": "نصب",
    # Tools and particles
    "أداة": "مبني",
    "أداة_نداء": "مبني",
    "أداة_استفهام": "مبني",
    "أداة_نفي": "مبني",
    "فعل_ناقص": "مبني",
}


def generate(
    role_hypotheses: List[HypothesisNode],
    factor_hypotheses: List[HypothesisNode],
) -> List[HypothesisNode]:
    """Generate case hypotheses from paired role + factor hypotheses.

    Parameters
    ----------
    role_hypotheses : list[HypothesisNode]
        Role hypotheses in sentence order.
    factor_hypotheses : list[HypothesisNode]
        Factor hypotheses (parallel to role hypotheses).

    Returns
    -------
    list[HypothesisNode]
        Case hypotheses, one per role/factor pair.
    """
    hypotheses: List[HypothesisNode] = []
    for role_h, factor_h in zip(role_hypotheses, factor_hypotheses):
        role = str(role_h.get("role", ""))
        factor = str(factor_h.get("factor", ""))
        case_state = _ROLE_CASE_MAP.get(role, "غير_محدد")
        justification = f"{role} + {factor} → {case_state}"

        hypotheses.append(
            HypothesisNode(
                node_id=f"CASE_{role_h.node_id}",
                hypothesis_type="case",
                stage=ActivationStage.CASE,
                source_refs=(role_h.node_id, factor_h.node_id),
                payload=(
                    ("case_state", case_state),
                    ("role", role),
                    ("factor", factor),
                    ("justification", justification),
                ),
                confidence=min(role_h.confidence, factor_h.confidence),
                status=HypothesisStatus.ACTIVE,
            )
        )
    return hypotheses
