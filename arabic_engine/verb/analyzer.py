"""Verb analyzer — المحلل الفعلي.

Takes a surface form and produces a :class:`VerbProfile` combining
root, bāb, tense, transitivity, completeness, person, number,
gender, voice, and optional nāsikh classification.
"""

from __future__ import annotations

from typing import Optional

from arabic_engine.core.enums import (
    POS,
    NasikhCategory,
    VerbCompleteness,
    VerbGender,
    VerbNumber,
    VerbPerson,
    VerbTense,
    VerbTransitivity,
    VerbVoice,
)
from arabic_engine.core.types import VerbProfile

from . import bab_registry, nasikh

# ── Tense detection from morphological pattern ─────────────────────

_PAST_PATTERNS = frozenset({
    "فَعَلَ", "فَعِلَ", "فَعُلَ",
    "أَفْعَلَ", "فَعَّلَ", "فَاعَلَ",
    "تَفَعَّلَ", "تَفَاعَلَ",
    "اِنْفَعَلَ", "اِفْتَعَلَ", "اِفْعَلَّ", "اِسْتَفْعَلَ",
    "تَفَعْلَلَ",
})

_PRESENT_PATTERNS = frozenset({
    "يَفْعُلُ", "يَفْعِلُ", "يَفْعَلُ",
    "يُفْعِلُ", "يُفَعِّلُ", "يُفَاعِلُ",
    "يَتَفَعَّلُ", "يَتَفَاعَلُ",
    "يَنْفَعِلُ", "يَفْتَعِلُ", "يَفْعَلُّ", "يَسْتَفْعِلُ",
    "يَتَفَعْلَلُ",
})


def _detect_tense(pattern: str) -> Optional[VerbTense]:
    """Detect tense from a morphological pattern string."""
    if pattern in _PAST_PATTERNS:
        return VerbTense.MADI
    if pattern in _PRESENT_PATTERNS:
        return VerbTense.MUDARI
    # Imperative patterns typically start with اُ or اِ and lack prefix يَ
    if pattern and not pattern.startswith("يَ") and pattern.endswith("ْ"):
        return VerbTense.AMR
    return None


# ── Transitivity heuristic ──────────────────────────────────────────

_KNOWN_LAZIM = frozenset({
    "جَلَسَ", "ذَهَبَ", "خَرَجَ", "دَخَلَ", "كَرُمَ",
})

_KNOWN_MUTA3ADDI_2 = frozenset({
    "ظنّ", "حسب", "خال", "زعم", "رأى", "علم",
    "وجد", "درى", "أعطى",
})

_KNOWN_MUTA3ADDI_3 = frozenset({
    "أرى", "أعلم", "أنبأ",
})


def _detect_transitivity(
    surface: str,
    nasikh_cat: Optional[NasikhCategory],
) -> VerbTransitivity:
    """Heuristic transitivity detection."""
    if surface in _KNOWN_MUTA3ADDI_3:
        return VerbTransitivity.MUTA3ADDI_LI_THALATHA
    if surface in _KNOWN_MUTA3ADDI_2:
        return VerbTransitivity.MUTA3ADDI_LI_ITHNAYN
    if nasikh_cat == NasikhCategory.ZANNA_WA_AKHAWAT:
        return VerbTransitivity.MUTA3ADDI_LI_ITHNAYN
    if surface in _KNOWN_LAZIM:
        return VerbTransitivity.LAZIM
    # Default: single-object transitive
    return VerbTransitivity.MUTA3ADDI


# ── Voice detection ─────────────────────────────────────────────────

def _detect_voice(pattern: str) -> VerbVoice:
    """Detect voice from pattern vowelling."""
    # Passive past: فُعِلَ  (damma + kasra on R1/R2)
    if pattern and "ُ" in pattern[:3] and "ِ" in pattern[2:5]:
        return VerbVoice.MAJHUL
    return VerbVoice.MA3LUM


# ── Main entry point ────────────────────────────────────────────────


def analyze(surface: str, pattern: str = "", pos: POS = POS.FI3L) -> Optional[VerbProfile]:
    """Analyse *surface* and return a :class:`VerbProfile`, or ``None``.

    Parameters
    ----------
    surface : str
        The surface form of the verb (e.g. "كَتَبَ").
    pattern : str
        Morphological pattern (e.g. "فَعَلَ").  If empty, the
        analyser attempts lookup from the bāb registry.
    pos : POS
        Part-of-speech tag — must be ``POS.FI3L`` for analysis to
        proceed.

    Returns
    -------
    VerbProfile | None
        ``None`` when the surface form cannot be analysed as a verb.
    """
    if pos != POS.FI3L:
        return None

    # 1. Look up root + bāb
    lookup = bab_registry.lookup_verb(surface)
    if lookup is not None:
        root, bab = lookup
    else:
        # Fallback: try to match pattern
        root = ()
        bab_match = None
        if pattern:
            for b in bab_registry.all_thulathi_babs():
                if b.past_pattern == pattern or b.present_pattern == pattern:
                    bab_match = b
                    break
            if bab_match is None:
                for b in bab_registry.all_mazid_babs():
                    if b.past_pattern == pattern or b.present_pattern == pattern:
                        bab_match = b
                        break
        if bab_match is None:
            return None
        bab = bab_match

    # 2. Tense
    tense = _detect_tense(pattern) if pattern else _detect_tense(bab.past_pattern)
    if tense is None:
        tense = VerbTense.MADI  # default assumption

    # 3. Nāsikh check
    nasikh_profile = nasikh.classify(surface)
    nasikh_cat = nasikh_profile.category if nasikh_profile else None

    # 4. Completeness
    completeness = (
        VerbCompleteness.NAQIS if nasikh_cat is not None
        else VerbCompleteness.KAMIL
    )

    # 5. Transitivity
    transitivity = _detect_transitivity(surface, nasikh_cat)

    # 6. Voice
    voice = _detect_voice(pattern)

    # 7. Person / number / gender — default to 3rd person masc. sg.
    person = VerbPerson.GHAIB
    number = VerbNumber.MUFRAD
    gender = VerbGender.MUDHAKKAR

    return VerbProfile(
        root=root,
        bab=bab,
        tense=tense,
        transitivity=transitivity,
        completeness=completeness,
        voice=voice,
        person=person,
        number=number,
        gender=gender,
        nasikh_category=nasikh_cat,
        surface=surface,
    )
