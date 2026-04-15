"""Morphological engine — محرك التحليل الصرفي.

Provides advanced morphological analysis building on the existing
signifier layer (root_pattern.py). Combines root extraction, pattern
matching, and affix stripping into a unified analysis.
"""

from __future__ import annotations

from typing import List, Optional

from arabic_engine.core.enums import AffixType, MorphemeType, POS
from arabic_engine.core.types import (
    AffixSet,
    LexicalClosure,
    MorphemeRecord,
    PatternTemplate,
    RootEntry,
)
from arabic_engine.morphology.affixes import strip_affixes
from arabic_engine.morphology.lexicon import lookup_root
from arabic_engine.signifier.root_pattern import extract_root_pattern


def analyze(token: str) -> dict[str, object]:
    """Perform full morphological analysis on *token*.

    Parameters
    ----------
    token : str
        A single Arabic token (with or without diacritics).

    Returns
    -------
    dict
        Analysis result with keys: root, pattern, morphemes, affix_set,
        features, root_entry, pos.
    """
    # Step 1: Extract root and pattern via signifier layer
    rp = extract_root_pattern(token)

    # Step 2: Strip affixes
    affix_set = strip_affixes(token)

    # Step 3: Look up root in lexicon
    root_entry: Optional[RootEntry] = None
    if rp:
        root_entry = lookup_root(rp.root)

    # Step 4: Build morpheme records
    morphemes: List[MorphemeRecord] = []

    # Root morpheme
    if rp and rp.root:
        morphemes.append(MorphemeRecord(
            text="".join(rp.root),
            morpheme_type=MorphemeType.ROOT,
            features=rp.root,
            position=0,
        ))

    # Pattern morpheme
    if rp and rp.pattern:
        morphemes.append(MorphemeRecord(
            text=rp.pattern,
            morpheme_type=MorphemeType.PATTERN,
            features=(rp.pattern,),
            position=0,
        ))

    # Affix morphemes
    for prefix in affix_set.prefixes:
        morphemes.append(MorphemeRecord(
            text=prefix,
            morpheme_type=MorphemeType.AFFIX,
            features=(prefix,),
            position=0,
        ))
    for suffix in affix_set.suffixes:
        morphemes.append(MorphemeRecord(
            text=suffix,
            morpheme_type=MorphemeType.AFFIX,
            features=(suffix,),
            position=len(token) - len(suffix),
        ))

    # Step 5: Determine POS from pattern if available
    pos = POS.UNKNOWN
    if rp:
        pos = rp.pos

    # Step 6: Build pattern template
    pattern_template: Optional[PatternTemplate] = None
    if rp and rp.pattern:
        pattern_template = PatternTemplate(
            pattern=rp.pattern,
            skeletal=rp.pattern,
            pos=pos,
            features=(),
        )

    return {
        "token": token,
        "root": rp.root if rp else (),
        "pattern": rp.pattern if rp else "",
        "morphemes": morphemes,
        "affix_set": affix_set,
        "root_entry": root_entry,
        "pattern_template": pattern_template,
        "pos": pos,
    }
