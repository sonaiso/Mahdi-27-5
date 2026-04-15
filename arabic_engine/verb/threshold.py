"""Minimal threshold validator — الحد الأدنى المكتمل.

Validates that a candidate verb satisfies the eight conditions
for verb-hood.  Each condition is a *pillar* of the proof that
the verb is a legitimate epistemic node.
"""

from __future__ import annotations

from typing import Optional, Tuple

from arabic_engine.core.enums import POS, VerbTense
from arabic_engine.core.types import VerbBab, VerbMinimalThreshold


def validate(
    *,
    surface: str,
    pos: POS,
    root: Tuple[str, ...],
    pattern: str,
    tense: Optional[VerbTense],
    bab: Optional[VerbBab],
) -> VerbMinimalThreshold:
    """Check the eight pillars and return a threshold record.

    Parameters
    ----------
    surface : str
        The surface form of the candidate verb.
    pos : POS
        Part-of-speech tag assigned to the token.
    root : tuple[str, ...]
        Extracted root letters.
    pattern : str
        Morphological pattern string.
    tense : VerbTense | None
        Detected tense (``None`` if unknown).
    bab : VerbBab | None
        Matched conjugation gate (``None`` if unknown).

    Returns
    -------
    VerbMinimalThreshold
        Record with all eight boolean fields populated.
    """
    # 1. ثبوت — has a realised phonological form
    has_thubut = bool(surface) and tense is not None

    # 2. حد — distinctly identifiable as a verb
    has_hadd = pos == POS.FI3L

    # 3. امتداد — phonological, pattern, temporal, predicative extension
    has_imtidad = bool(pattern) and tense is not None and len(root) >= 3

    # 4. مقوِّم — root + pattern + temporal direction + event capacity
    has_muqawwim = (
        len(root) >= 3
        and bool(pattern)
        and tense is not None
    )

    # 5. علاقة بنائية — root→pattern→event→time→predication chain
    has_3alaqa_binaya = (
        len(root) >= 3
        and bool(pattern)
        and tense is not None
        and pos == POS.FI3L
    )

    # 6. انتظام — follows a known bāb / morphological system
    has_intizam = bab is not None

    # 7. وحدة — functions as a single verbal unit
    has_wahda = bool(surface) and " " not in surface

    # 8. قابلية تعيين — classifiable
    has_qabiliyyat_ta3yin = (
        pos == POS.FI3L
        and tense is not None
        and bab is not None
    )

    return VerbMinimalThreshold(
        has_thubut=has_thubut,
        has_hadd=has_hadd,
        has_imtidad=has_imtidad,
        has_muqawwim=has_muqawwim,
        has_3alaqa_binaya=has_3alaqa_binaya,
        has_intizam=has_intizam,
        has_wahda=has_wahda,
        has_qabiliyyat_ta3yin=has_qabiliyyat_ta3yin,
    )
