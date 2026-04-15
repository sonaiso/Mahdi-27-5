"""Derivative chain builder — بناء سلسلة المشتقات.

Given a root and bāb, generates the complete derivational network:
maṣdar, active/passive participle, nouns of time/place/manner/instrument.

Each derivative is a *condition of epistemic possibility* for a
particular facet of event-knowledge.
"""

from __future__ import annotations

from typing import Tuple

from arabic_engine.core.enums import VerbAugmentation
from arabic_engine.core.types import VerbBab, VerbDerivativeChain

# ── Pattern-based derivative generation ─────────────────────────────
# For trilateral mujarrad, the derivatives follow well-known rules.
# For mazid patterns, derivatives are predictable from the augmented
# pattern (مُ prefix for active/passive participles, etc.).


def _apply_pattern(root: Tuple[str, ...], pattern: str) -> str:
    """Substitute root letters into a pattern template.

    The pattern uses ف for R1, ع for R2, ل for R3 (and optionally
    a fourth root letter for quadrilateral).  Characters that are
    not ف/ع/ل are kept as-is (prefix مُ, suffix ة, etc.).
    """
    result: list[str] = []
    root_slots = "فعل"
    for ch in pattern:
        if ch in root_slots:
            slot_pos = root_slots.index(ch)
            if slot_pos < len(root):
                result.append(root[slot_pos])
            else:
                result.append(ch)
        else:
            result.append(ch)
    return "".join(result)


def build(root: Tuple[str, ...], bab: VerbBab) -> VerbDerivativeChain:
    """Build the full derivative chain for *root* in *bab*.

    Parameters
    ----------
    root : tuple[str, ...]
        Root consonants (minimum 3).
    bab : VerbBab
        The conjugation gate that governs derivation.

    Returns
    -------
    VerbDerivativeChain
        All derivative slots filled with generated forms.
    """
    if bab.augmentation == VerbAugmentation.MUJARRAD:
        return _build_mujarrad(root, bab)
    return _build_mazid(root, bab)


def _build_mujarrad(
    root: Tuple[str, ...], bab: VerbBab,
) -> VerbDerivativeChain:
    """Derivatives for a trilateral bare (مجرد) verb."""
    r1, r2, r3 = root[0], root[1], root[2]

    masdar = _apply_pattern(root, bab.masdar_pattern)
    ism_fa3il = f"{r1}َا{r2}ِ{r3}"        # فَاعِل
    ism_maf3ul = f"مَ{r1}ْ{r2}ُو{r3}"     # مَفْعُول
    ism_zaman = f"مَ{r1}ْ{r2}َ{r3}"       # مَفْعَل
    ism_makan = f"مَ{r1}ْ{r2}َ{r3}"       # مَفْعَل (same pattern)
    ism_haya = f"{r1}ِ{r2}ْ{r3}َة"        # فِعْلَة
    ism_ala = f"مِ{r1}ْ{r2}َ{r3}"         # مِفْعَل

    return VerbDerivativeChain(
        root=root,
        bab_id=bab.bab_id,
        masdar=masdar,
        ism_fa3il=ism_fa3il,
        ism_maf3ul=ism_maf3ul,
        ism_zaman=ism_zaman,
        ism_makan=ism_makan,
        ism_haya=ism_haya,
        ism_ala=ism_ala,
    )


def _build_mazid(
    root: Tuple[str, ...], bab: VerbBab,
) -> VerbDerivativeChain:
    """Derivatives for an augmented (مزيد) verb.

    Augmented active participles use مُ prefix; passive participles
    change the penultimate vowel to fatḥa.
    """
    r1 = root[0] if len(root) > 0 else ""
    r2 = root[1] if len(root) > 1 else ""
    r3 = root[2] if len(root) > 2 else ""

    masdar = _apply_pattern(root, bab.masdar_pattern)

    # Active participle: replace initial vowel with مُ
    past = bab.past_pattern
    if past.startswith("أَ"):
        ism_fa3il = f"مُ{r1}ْ{r2}ِ{r3}"        # مُفْعِل
        ism_maf3ul = f"مُ{r1}ْ{r2}َ{r3}"        # مُفْعَل
    elif past.startswith("تَفَعَّ"):
        ism_fa3il = f"مُتَ{r1}َ{r2}ِّ{r3}"      # مُتَفَعِّل
        ism_maf3ul = f"مُتَ{r1}َ{r2}َّ{r3}"      # مُتَفَعَّل
    elif past.startswith("تَفَا"):
        ism_fa3il = f"مُتَ{r1}َا{r2}ِ{r3}"      # مُتَفَاعِل
        ism_maf3ul = f"مُتَ{r1}َا{r2}َ{r3}"      # مُتَفَاعَل
    elif past.startswith("اِنْ"):
        ism_fa3il = f"مُنْ{r1}َ{r2}ِ{r3}"       # مُنْفَعِل
        ism_maf3ul = f"مُنْ{r1}َ{r2}َ{r3}"       # مُنْفَعَل
    elif past.startswith("اِفْتَ"):
        ism_fa3il = f"مُ{r1}ْتَ{r2}ِ{r3}"       # مُفْتَعِل
        ism_maf3ul = f"مُ{r1}ْتَ{r2}َ{r3}"       # مُفْتَعَل
    elif past.startswith("اِسْتَ"):
        ism_fa3il = f"مُسْتَ{r1}ْ{r2}ِ{r3}"     # مُسْتَفْعِل
        ism_maf3ul = f"مُسْتَ{r1}ْ{r2}َ{r3}"     # مُسْتَفْعَل
    elif past.startswith("فَعَّ"):
        ism_fa3il = f"مُ{r1}َ{r2}ِّ{r3}"         # مُفَعِّل
        ism_maf3ul = f"مُ{r1}َ{r2}َّ{r3}"         # مُفَعَّل
    elif past.startswith("فَاعَ"):
        ism_fa3il = f"مُ{r1}َا{r2}ِ{r3}"         # مُفَاعِل
        ism_maf3ul = f"مُ{r1}َا{r2}َ{r3}"         # مُفَاعَل
    else:
        ism_fa3il = f"مُ{r1}َ{r2}ِ{r3}"
        ism_maf3ul = f"مُ{r1}َ{r2}َ{r3}"

    ism_zaman = f"مَ{r1}ْ{r2}َ{r3}"
    ism_makan = f"مَ{r1}ْ{r2}َ{r3}"

    return VerbDerivativeChain(
        root=root,
        bab_id=bab.bab_id,
        masdar=masdar,
        ism_fa3il=ism_fa3il,
        ism_maf3ul=ism_maf3ul,
        ism_zaman=ism_zaman,
        ism_makan=ism_makan,
        ism_haya="",
        ism_ala="",
    )
