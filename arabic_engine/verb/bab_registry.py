"""Bāb registry — سجل أبواب التصريف.

Provides the canonical registry of trilateral conjugation gates
(أبواب الثلاثي المجرد) and augmented verb patterns (أوزان المزيد).

Each gate is the *minimum structural bridge* that connects a bare
root to the morphological, temporal, and semantic systems — making
it a condition of epistemic possibility for the verb's existence.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from arabic_engine.core.enums import (
    MazidPattern,
    ThulathiBab,
    VerbAugmentation,
    VerbBaseType,
)
from arabic_engine.core.types import VerbBab

# ── Trilateral gates (أبواب الثلاثي المجرد) ─────────────────────────

_THULATHI_BABS: Dict[ThulathiBab, VerbBab] = {
    ThulathiBab.FA3ALA_YAF3ULU: VerbBab(
        bab_id=1,
        base_type=VerbBaseType.THULATHI,
        augmentation=VerbAugmentation.MUJARRAD,
        past_pattern="فَعَلَ",
        present_pattern="يَفْعُلُ",
        masdar_pattern="فَعْل",
        bab_label="باب نَصَرَ",
        semantic_tendency="عمل متعدٍّ غالبًا",
    ),
    ThulathiBab.FA3ALA_YAF3ILU: VerbBab(
        bab_id=2,
        base_type=VerbBaseType.THULATHI,
        augmentation=VerbAugmentation.MUJARRAD,
        past_pattern="فَعَلَ",
        present_pattern="يَفْعِلُ",
        masdar_pattern="فَعْل",
        bab_label="باب ضَرَبَ",
        semantic_tendency="عمل متعدٍّ غالبًا",
    ),
    ThulathiBab.FA3ALA_YAF3ALU: VerbBab(
        bab_id=3,
        base_type=VerbBaseType.THULATHI,
        augmentation=VerbAugmentation.MUJARRAD,
        past_pattern="فَعَلَ",
        present_pattern="يَفْعَلُ",
        masdar_pattern="فَعْل",
        bab_label="باب فَتَحَ",
        semantic_tendency="عمل متعدٍّ غالبًا",
    ),
    ThulathiBab.FA3ILA_YAF3ALU: VerbBab(
        bab_id=4,
        base_type=VerbBaseType.THULATHI,
        augmentation=VerbAugmentation.MUJARRAD,
        past_pattern="فَعِلَ",
        present_pattern="يَفْعَلُ",
        masdar_pattern="فَعَل",
        bab_label="باب عَلِمَ",
        semantic_tendency="حالة أو انفعال",
    ),
    ThulathiBab.FA3ULA_YAF3ULU: VerbBab(
        bab_id=5,
        base_type=VerbBaseType.THULATHI,
        augmentation=VerbAugmentation.MUJARRAD,
        past_pattern="فَعُلَ",
        present_pattern="يَفْعُلُ",
        masdar_pattern="فَعَالَة",
        bab_label="باب كَرُمَ",
        semantic_tendency="صفة لازمة / طبيعة",
    ),
    ThulathiBab.FA3ILA_YAF3ILU: VerbBab(
        bab_id=6,
        base_type=VerbBaseType.THULATHI,
        augmentation=VerbAugmentation.MUJARRAD,
        past_pattern="فَعِلَ",
        present_pattern="يَفْعِلُ",
        masdar_pattern="فَعَل",
        bab_label="باب حَسِبَ",
        semantic_tendency="حالة أو انفعال",
    ),
}

# ── Augmented patterns (أوزان المزيد) ───────────────────────────────

_MAZID_BABS: Dict[MazidPattern, VerbBab] = {
    MazidPattern.AF3ALA: VerbBab(
        bab_id=11,
        base_type=VerbBaseType.THULATHI,
        augmentation=VerbAugmentation.MAZID,
        past_pattern="أَفْعَلَ",
        present_pattern="يُفْعِلُ",
        masdar_pattern="إِفْعَال",
        bab_label="أَفْعَلَ",
        semantic_tendency="تعدية / سببية",
    ),
    MazidPattern.FA33ALA: VerbBab(
        bab_id=12,
        base_type=VerbBaseType.THULATHI,
        augmentation=VerbAugmentation.MAZID,
        past_pattern="فَعَّلَ",
        present_pattern="يُفَعِّلُ",
        masdar_pattern="تَفْعِيل",
        bab_label="فَعَّلَ",
        semantic_tendency="تكثير / تعدية",
    ),
    MazidPattern.FA3ALA_III: VerbBab(
        bab_id=13,
        base_type=VerbBaseType.THULATHI,
        augmentation=VerbAugmentation.MAZID,
        past_pattern="فَاعَلَ",
        present_pattern="يُفَاعِلُ",
        masdar_pattern="مُفَاعَلَة",
        bab_label="فَاعَلَ",
        semantic_tendency="مشاركة",
    ),
    MazidPattern.TAFA33ALA: VerbBab(
        bab_id=14,
        base_type=VerbBaseType.THULATHI,
        augmentation=VerbAugmentation.MAZID,
        past_pattern="تَفَعَّلَ",
        present_pattern="يَتَفَعَّلُ",
        masdar_pattern="تَفَعُّل",
        bab_label="تَفَعَّلَ",
        semantic_tendency="تكلُّف / مطاوعة فَعَّلَ",
    ),
    MazidPattern.TAFA3ALA: VerbBab(
        bab_id=15,
        base_type=VerbBaseType.THULATHI,
        augmentation=VerbAugmentation.MAZID,
        past_pattern="تَفَاعَلَ",
        present_pattern="يَتَفَاعَلُ",
        masdar_pattern="تَفَاعُل",
        bab_label="تَفَاعَلَ",
        semantic_tendency="تشارك / تظاهر",
    ),
    MazidPattern.INFA3ALA: VerbBab(
        bab_id=16,
        base_type=VerbBaseType.THULATHI,
        augmentation=VerbAugmentation.MAZID,
        past_pattern="اِنْفَعَلَ",
        present_pattern="يَنْفَعِلُ",
        masdar_pattern="اِنْفِعَال",
        bab_label="اِنْفَعَلَ",
        semantic_tendency="مطاوعة فَعَلَ",
    ),
    MazidPattern.IFTA3ALA: VerbBab(
        bab_id=17,
        base_type=VerbBaseType.THULATHI,
        augmentation=VerbAugmentation.MAZID,
        past_pattern="اِفْتَعَلَ",
        present_pattern="يَفْتَعِلُ",
        masdar_pattern="اِفْتِعَال",
        bab_label="اِفْتَعَلَ",
        semantic_tendency="مطاوعة / اتخاذ",
    ),
    MazidPattern.IF3ALLA: VerbBab(
        bab_id=18,
        base_type=VerbBaseType.THULATHI,
        augmentation=VerbAugmentation.MAZID,
        past_pattern="اِفْعَلَّ",
        present_pattern="يَفْعَلُّ",
        masdar_pattern="اِفْعِلَال",
        bab_label="اِفْعَلَّ",
        semantic_tendency="لون أو عيب",
    ),
    MazidPattern.ISTAF3ALA: VerbBab(
        bab_id=19,
        base_type=VerbBaseType.THULATHI,
        augmentation=VerbAugmentation.MAZID,
        past_pattern="اِسْتَفْعَلَ",
        present_pattern="يَسْتَفْعِلُ",
        masdar_pattern="اِسْتِفْعَال",
        bab_label="اِسْتَفْعَلَ",
        semantic_tendency="طلب / صيرورة",
    ),
    MazidPattern.TAFA3LALA: VerbBab(
        bab_id=20,
        base_type=VerbBaseType.RUBAI,
        augmentation=VerbAugmentation.MAZID,
        past_pattern="تَفَعْلَلَ",
        present_pattern="يَتَفَعْلَلُ",
        masdar_pattern="تَفَعْلُل",
        bab_label="تَفَعْلَلَ",
        semantic_tendency="مطاوعة فَعْلَلَ",
    ),
}


# ── Public query functions ──────────────────────────────────────────


def get_thulathi_bab(bab: ThulathiBab) -> VerbBab:
    """Return the :class:`VerbBab` for a trilateral gate."""
    return _THULATHI_BABS[bab]


def get_mazid_bab(pattern: MazidPattern) -> VerbBab:
    """Return the :class:`VerbBab` for an augmented pattern."""
    return _MAZID_BABS[pattern]


def all_thulathi_babs() -> List[VerbBab]:
    """Return all six trilateral gates in canonical order."""
    return list(_THULATHI_BABS.values())


def all_mazid_babs() -> List[VerbBab]:
    """Return all augmented patterns in canonical order."""
    return list(_MAZID_BABS.values())


def find_bab_by_id(bab_id: int) -> Optional[VerbBab]:
    """Look up a bāb by its numeric identifier."""
    for bab in _THULATHI_BABS.values():
        if bab.bab_id == bab_id:
            return bab
    for bab in _MAZID_BABS.values():
        if bab.bab_id == bab_id:
            return bab
    return None


def match_pattern(past_pat: str, present_pat: str) -> Optional[VerbBab]:
    """Find the bāb whose past/present patterns match the given pair."""
    for bab in _THULATHI_BABS.values():
        if bab.past_pattern == past_pat and bab.present_pattern == present_pat:
            return bab
    for bab in _MAZID_BABS.values():
        if bab.past_pattern == past_pat and bab.present_pattern == present_pat:
            return bab
    return None


# ── Demo verb-to-bāb mapping ───────────────────────────────────────

_VERB_BAB_MAP: Dict[str, Tuple[Tuple[str, ...], ThulathiBab]] = {
    "كَتَبَ": (("ك", "ت", "ب"), ThulathiBab.FA3ALA_YAF3ULU),
    "كتب": (("ك", "ت", "ب"), ThulathiBab.FA3ALA_YAF3ULU),
    "نَصَرَ": (("ن", "ص", "ر"), ThulathiBab.FA3ALA_YAF3ULU),
    "ضَرَبَ": (("ض", "ر", "ب"), ThulathiBab.FA3ALA_YAF3ILU),
    "فَتَحَ": (("ف", "ت", "ح"), ThulathiBab.FA3ALA_YAF3ALU),
    "عَلِمَ": (("ع", "ل", "م"), ThulathiBab.FA3ILA_YAF3ALU),
    "كَرُمَ": (("ك", "ر", "م"), ThulathiBab.FA3ULA_YAF3ULU),
    "حَسِبَ": (("ح", "س", "ب"), ThulathiBab.FA3ILA_YAF3ILU),
    "جَلَسَ": (("ج", "ل", "س"), ThulathiBab.FA3ALA_YAF3ILU),
    "ذَهَبَ": (("ذ", "ه", "ب"), ThulathiBab.FA3ALA_YAF3ALU),
    "خَرَجَ": (("خ", "ر", "ج"), ThulathiBab.FA3ALA_YAF3ULU),
    "دَخَلَ": (("د", "خ", "ل"), ThulathiBab.FA3ALA_YAF3ULU),
    "شَرِبَ": (("ش", "ر", "ب"), ThulathiBab.FA3ILA_YAF3ALU),
    "سَمِعَ": (("س", "م", "ع"), ThulathiBab.FA3ILA_YAF3ALU),
    "قَرَأَ": (("ق", "ر", "أ"), ThulathiBab.FA3ALA_YAF3ALU),
    "أَكَلَ": (("أ", "ك", "ل"), ThulathiBab.FA3ALA_YAF3ULU),
}


def lookup_verb(surface: str) -> Optional[Tuple[Tuple[str, ...], VerbBab]]:
    """Look up a known verb form and return its root + bāb.

    Returns ``None`` for unknown verbs.
    """
    entry = _VERB_BAB_MAP.get(surface)
    if entry is None:
        return None
    root, bab_key = entry
    return root, _THULATHI_BABS[bab_key]
