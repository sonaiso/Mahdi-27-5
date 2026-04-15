"""Morphological lexicon — واجهة المعجم.

Provides root lookup and pattern registry for Arabic morphological
analysis. Currently uses an in-memory seed lexicon; designed for
future extension to a persistent database backend.
"""

from __future__ import annotations

from typing import Optional, Tuple

from arabic_engine.core.types import RootEntry

# ── Seed lexicon ────────────────────────────────────────────────────
# In-memory root entries for common Arabic roots.

_LEXICON: dict[Tuple[str, ...], RootEntry] = {
    ("ك", "ت", "ب"): RootEntry(
        root=("ك", "ت", "ب"),
        patterns=("فَعَلَ", "كِتَاب", "مَكْتُوب", "كَاتِب", "كُتُب"),
        base_meaning="writing",
        frequency=100,
    ),
    ("ق", "ر", "أ"): RootEntry(
        root=("ق", "ر", "أ"),
        patterns=("فَعَلَ", "قِرَاءَة", "قَارِئ", "مَقْرُوء"),
        base_meaning="reading",
        frequency=90,
    ),
    ("ع", "ل", "م"): RootEntry(
        root=("ع", "ل", "م"),
        patterns=("فَعِلَ", "عِلْم", "عَالِم", "مَعْلُوم", "تَعَلَّمَ"),
        base_meaning="knowing",
        frequency=95,
    ),
    ("ذ", "ه", "ب"): RootEntry(
        root=("ذ", "ه", "ب"),
        patterns=("فَعَلَ", "ذَهَاب", "ذَاهِب"),
        base_meaning="going",
        frequency=80,
    ),
    ("ج", "ل", "س"): RootEntry(
        root=("ج", "ل", "س"),
        patterns=("فَعَلَ", "جُلُوس", "جَالِس", "مَجْلِس"),
        base_meaning="sitting",
        frequency=75,
    ),
    ("ف", "ع", "ل"): RootEntry(
        root=("ف", "ع", "ل"),
        patterns=("فَعَلَ", "فِعْل", "فَاعِل", "مَفْعُول"),
        base_meaning="doing",
        frequency=85,
    ),
    ("ح", "ك", "م"): RootEntry(
        root=("ح", "ك", "م"),
        patterns=("فَعَلَ", "حُكْم", "حَاكِم", "مَحْكُوم", "حِكْمَة"),
        base_meaning="judging / ruling",
        frequency=85,
    ),
    ("ن", "ص", "ر"): RootEntry(
        root=("ن", "ص", "ر"),
        patterns=("فَعَلَ", "نَصْر", "نَاصِر", "مَنْصُور"),
        base_meaning="helping / victory",
        frequency=70,
    ),
    ("ف", "ت", "ح"): RootEntry(
        root=("ف", "ت", "ح"),
        patterns=("فَعَلَ", "فَتْح", "فَاتِح", "مَفْتُوح", "مِفْتَاح"),
        base_meaning="opening",
        frequency=75,
    ),
    ("س", "م", "ع"): RootEntry(
        root=("س", "م", "ع"),
        patterns=("فَعِلَ", "سَمْع", "سَامِع", "مَسْمُوع"),
        base_meaning="hearing",
        frequency=70,
    ),
    ("ج", "م", "ع"): RootEntry(
        root=("ج", "م", "ع"),
        patterns=("فَعَلَ", "جَمْع", "جَامِع", "مَجْمُوع", "جَمِيع"),
        base_meaning="gathering / collecting",
        frequency=80,
    ),
    ("ح", "م", "د"): RootEntry(
        root=("ح", "م", "د"),
        patterns=("فَعِلَ", "حَمْد", "حَامِد", "مَحْمُود", "أَحْمَد"),
        base_meaning="praising",
        frequency=85,
    ),
    ("ر", "ح", "م"): RootEntry(
        root=("ر", "ح", "م"),
        patterns=("فَعِلَ", "رَحْمَة", "رَحِيم", "رَحْمَن"),
        base_meaning="mercy",
        frequency=90,
    ),
    ("ص", "ل", "ح"): RootEntry(
        root=("ص", "ل", "ح"),
        patterns=("فَعُلَ", "صَلَاح", "صَالِح", "إِصْلَاح"),
        base_meaning="goodness / reform",
        frequency=65,
    ),
    ("خ", "ر", "ج"): RootEntry(
        root=("خ", "ر", "ج"),
        patterns=("فَعَلَ", "خُرُوج", "خَارِج", "مَخْرَج"),
        base_meaning="exiting",
        frequency=75,
    ),
    ("د", "خ", "ل"): RootEntry(
        root=("د", "خ", "ل"),
        patterns=("فَعَلَ", "دُخُول", "دَاخِل", "مَدْخَل"),
        base_meaning="entering",
        frequency=75,
    ),
    ("ش", "ر", "ب"): RootEntry(
        root=("ش", "ر", "ب"),
        patterns=("فَعِلَ", "شُرْب", "شَارِب", "مَشْرُوب"),
        base_meaning="drinking",
        frequency=60,
    ),
    ("أ", "ك", "ل"): RootEntry(
        root=("أ", "ك", "ل"),
        patterns=("فَعَلَ", "أَكْل", "آكِل", "مَأْكُول"),
        base_meaning="eating",
        frequency=65,
    ),
    ("ن", "ز", "ل"): RootEntry(
        root=("ن", "ز", "ل"),
        patterns=("فَعَلَ", "نُزُول", "نَازِل", "مَنْزِل"),
        base_meaning="descending",
        frequency=70,
    ),
    ("ق", "و", "ل"): RootEntry(
        root=("ق", "و", "ل"),
        patterns=("فَعَلَ", "قَوْل", "قَائِل", "مَقُول"),
        base_meaning="saying",
        frequency=95,
    ),
}


def lookup_root(root: tuple[str, ...]) -> Optional[RootEntry]:
    """Look up a root in the lexicon.

    Parameters
    ----------
    root : tuple[str, ...]
        Consonantal root (e.g. ("ك", "ت", "ب")).

    Returns
    -------
    RootEntry | None
        The lexicon entry if found, else None.
    """
    return _LEXICON.get(root)


def list_roots() -> list[tuple[str, ...]]:
    """Return all roots in the lexicon."""
    return list(_LEXICON.keys())


def root_count() -> int:
    """Return the number of roots in the lexicon."""
    return len(_LEXICON)
