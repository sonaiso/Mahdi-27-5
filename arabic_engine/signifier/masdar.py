"""Masdar extraction and derivation engine — محرك المصدر.

Provides the core masdar (verbal noun) operations:

* **extract_masdar** — extract a masdar from root + verb pattern + bab
* **derive_from_masdar** — derive participles, time/place/manner/instrument nouns
* **build_fractal_node** — build a complete fractal masdar node
* **interpret_masdar** — interpret an interpreted masdar (مصدر مؤوّل) from أن + verb
* **validate_completeness** — verify the 8 conditions of the minimal complete threshold
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from arabic_engine.core.enums import (
    POS,
    DerivationTarget,
    KawnType,
    MasdarBab,
    MasdarType,
)
from arabic_engine.core.types import (
    FractalMasdarNode,
    LexicalClosure,
    MasdarDerivation,
    MasdarRecord,
)

# ── Masdar pattern tables ───────────────────────────────────────────
# Maps (MasdarBab) → (masdar_pattern, verb_pattern)

_BAB_TO_PATTERN: Dict[MasdarBab, Tuple[str, str]] = {
    # Tri-literal base (الثلاثي المجرد)
    MasdarBab.FA3L: ("فَعْل", "فَعَلَ"),
    MasdarBab.FI3ALA: ("فِعالة", "فَعَلَ"),
    MasdarBab.FU3UL: ("فُعول", "فَعَلَ"),
    MasdarBab.FA3AL: ("فَعَل", "فَعِلَ"),
    MasdarBab.FA3IL: ("فَعيل", "فَعَلَ"),
    MasdarBab.FU3AL: ("فُعال", "فَعُلَ"),
    # Augmented forms (المزيد)
    MasdarBab.IF3AL: ("إفعال", "أَفْعَلَ"),
    MasdarBab.TAF3IL: ("تفعيل", "فَعَّلَ"),
    MasdarBab.MUFA3ALA: ("مُفاعلة", "فاعَلَ"),
    MasdarBab.INFI3AL: ("انفعال", "انفَعَلَ"),
    MasdarBab.IFTI3AL: ("افتعال", "افتَعَلَ"),
    MasdarBab.TAFA33UL: ("تَفَعُّل", "تَفَعَّلَ"),
    MasdarBab.TAFA3UL: ("تَفاعُل", "تَفاعَلَ"),
    MasdarBab.IF3I3AL: ("افعِلال", "افعَلَّ"),
    MasdarBab.ISTIF3AL: ("استفعال", "استَفعَلَ"),
}

# ── Derivation pattern tables ───────────────────────────────────────
# Maps DerivationTarget → pattern string

_DERIVATION_PATTERNS: Dict[DerivationTarget, str] = {
    DerivationTarget.FI3L: "فَعَلَ",
    DerivationTarget.ISM_FA3IL: "فاعِل",
    DerivationTarget.ISM_MAF3UL: "مَفْعول",
    DerivationTarget.ISM_ZAMAN: "مَفْعَل",
    DerivationTarget.ISM_MAKAN: "مَفْعَل",
    DerivationTarget.ISM_HAY2A: "فِعْلة",
    DerivationTarget.ISM_ALA: "مِفْعَل",
    DerivationTarget.SIFA_MUSHABBAHA: "فَعِيل",
    DerivationTarget.ISM_TAFDIL: "أَفْعَل",
}

# ── Known masdar lookup ─────────────────────────────────────────────
# Surface-form → (root, bab, masdar_type, verb_form)

_MASDAR_LEXICON: Dict[str, Dict] = {
    "كِتابة": {
        "root": ("ك", "ت", "ب"),
        "bab": MasdarBab.FI3ALA,
        "masdar_type": MasdarType.ORIGINAL,
        "verb_form": "كَتَبَ",
        "event_core": "كتب",
    },
    "كتابة": {
        "root": ("ك", "ت", "ب"),
        "bab": MasdarBab.FI3ALA,
        "masdar_type": MasdarType.ORIGINAL,
        "verb_form": "كَتَبَ",
        "event_core": "كتب",
    },
    "خُروج": {
        "root": ("خ", "ر", "ج"),
        "bab": MasdarBab.FU3UL,
        "masdar_type": MasdarType.ORIGINAL,
        "verb_form": "خَرَجَ",
        "event_core": "خرج",
    },
    "خروج": {
        "root": ("خ", "ر", "ج"),
        "bab": MasdarBab.FU3UL,
        "masdar_type": MasdarType.ORIGINAL,
        "verb_form": "خَرَجَ",
        "event_core": "خرج",
    },
    "تَعليم": {
        "root": ("ع", "ل", "م"),
        "bab": MasdarBab.TAF3IL,
        "masdar_type": MasdarType.ORIGINAL,
        "verb_form": "عَلَّمَ",
        "event_core": "علم",
    },
    "تعليم": {
        "root": ("ع", "ل", "م"),
        "bab": MasdarBab.TAF3IL,
        "masdar_type": MasdarType.ORIGINAL,
        "verb_form": "عَلَّمَ",
        "event_core": "علم",
    },
    "استغفار": {
        "root": ("غ", "ف", "ر"),
        "bab": MasdarBab.ISTIF3AL,
        "masdar_type": MasdarType.ORIGINAL,
        "verb_form": "استَغفَرَ",
        "event_core": "غفر",
    },
    "ضَرْب": {
        "root": ("ض", "ر", "ب"),
        "bab": MasdarBab.FA3L,
        "masdar_type": MasdarType.ORIGINAL,
        "verb_form": "ضَرَبَ",
        "event_core": "ضرب",
    },
    "ضرب": {
        "root": ("ض", "ر", "ب"),
        "bab": MasdarBab.FA3L,
        "masdar_type": MasdarType.ORIGINAL,
        "verb_form": "ضَرَبَ",
        "event_core": "ضرب",
    },
    "إكرام": {
        "root": ("ك", "ر", "م"),
        "bab": MasdarBab.IF3AL,
        "masdar_type": MasdarType.ORIGINAL,
        "verb_form": "أَكْرَمَ",
        "event_core": "كرم",
    },
    "انكسار": {
        "root": ("ك", "س", "ر"),
        "bab": MasdarBab.INFI3AL,
        "masdar_type": MasdarType.ORIGINAL,
        "verb_form": "انكَسَرَ",
        "event_core": "كسر",
    },
    "اجتماع": {
        "root": ("ج", "م", "ع"),
        "bab": MasdarBab.IFTI3AL,
        "masdar_type": MasdarType.ORIGINAL,
        "verb_form": "اجتَمَعَ",
        "event_core": "جمع",
    },
    "تَعَلُّم": {
        "root": ("ع", "ل", "م"),
        "bab": MasdarBab.TAFA33UL,
        "masdar_type": MasdarType.ORIGINAL,
        "verb_form": "تَعَلَّمَ",
        "event_core": "علم",
    },
    "تَعاوُن": {
        "root": ("ع", "و", "ن"),
        "bab": MasdarBab.TAFA3UL,
        "masdar_type": MasdarType.ORIGINAL,
        "verb_form": "تَعاوَنَ",
        "event_core": "عون",
    },
}

# ── All full derivation targets for a standard masdar ───────────────

_FULL_DERIVATION_CAPACITY: List[DerivationTarget] = [
    DerivationTarget.FI3L,
    DerivationTarget.ISM_FA3IL,
    DerivationTarget.ISM_MAF3UL,
    DerivationTarget.ISM_ZAMAN,
    DerivationTarget.ISM_MAKAN,
    DerivationTarget.ISM_HAY2A,
    DerivationTarget.ISM_ALA,
]


# ── Public API ──────────────────────────────────────────────────────


def extract_masdar(
    root: Tuple[str, ...],
    verb_pattern: str,
    bab: MasdarBab,
    *,
    surface: str = "",
    masdar_type: MasdarType = MasdarType.ORIGINAL,
) -> MasdarRecord:
    """Extract a masdar record from root + verb pattern + bab.

    Parameters
    ----------
    root : tuple of str
        Tri-literal root radicals, e.g. ``("ك", "ت", "ب")``.
    verb_pattern : str
        The morphological pattern of the source verb, e.g. ``"فَعَلَ"``.
    bab : MasdarBab
        The masdar bab (morphological class).
    surface : str, optional
        The surface form of the masdar if known.
    masdar_type : MasdarType, optional
        Type of masdar (default ``ORIGINAL``).

    Returns
    -------
    MasdarRecord
    """
    pattern_info = _BAB_TO_PATTERN.get(bab, ("", ""))
    masdar_pattern = pattern_info[0]
    event_core = "".join(root)

    masdar_id = f"MSDR_{'_'.join(root)}_{bab.name}"

    return MasdarRecord(
        masdar_id=masdar_id,
        surface=surface or masdar_pattern,
        root=root,
        pattern=masdar_pattern,
        masdar_type=masdar_type,
        masdar_bab=bab,
        verb_form=verb_pattern,
        kawn_type=KawnType.MASDAR_BRIDGE,
        event_core=event_core,
        derivation_capacity=list(_FULL_DERIVATION_CAPACITY),
        confidence=1.0,
    )


def extract_masdar_from_surface(surface: str) -> Optional[MasdarRecord]:
    """Look up a masdar by its surface form in the lexicon.

    Parameters
    ----------
    surface : str
        Surface form of the masdar (with or without tashkīl).

    Returns
    -------
    MasdarRecord or None
        A masdar record if found, ``None`` otherwise.
    """
    entry = _MASDAR_LEXICON.get(surface)
    if entry is None:
        return None
    return extract_masdar(
        root=entry["root"],
        verb_pattern=entry.get("verb_form", ""),
        bab=entry["bab"],
        surface=surface,
        masdar_type=entry.get("masdar_type", MasdarType.ORIGINAL),
    )


def derive_from_masdar(
    masdar: MasdarRecord,
    target: DerivationTarget,
) -> MasdarDerivation:
    """Derive a target form from a masdar.

    Parameters
    ----------
    masdar : MasdarRecord
        The source masdar.
    target : DerivationTarget
        The derivation target type.

    Returns
    -------
    MasdarDerivation
    """
    target_pattern = _DERIVATION_PATTERNS.get(target, "")
    rule_id = f"DR_{masdar.masdar_bab.name}_{target.name}"

    return MasdarDerivation(
        source_masdar_id=masdar.masdar_id,
        target_type=target,
        target_surface=target_pattern,
        target_pattern=target_pattern,
        derivation_rule_id=rule_id,
        confidence=0.9,
    )


def interpret_masdar(
    closures: List[LexicalClosure],
) -> Optional[MasdarRecord]:
    """Interpret an interpreted masdar (مصدر مؤوّل) from 'أن + verb'.

    Scans the closure list for the pattern ``أَنْ`` (or ``أن``) followed
    by a verb and returns a masdar record of type ``MUAWWAL``.

    Parameters
    ----------
    closures : list of LexicalClosure
        The lexical closures for the sentence.

    Returns
    -------
    MasdarRecord or None
        An interpreted masdar record, or ``None`` if pattern not found.
    """
    for i, cl in enumerate(closures):
        if cl.surface in ("أَنْ", "أن") and i + 1 < len(closures):
            verb_cl = closures[i + 1]
            if verb_cl.pos == POS.FI3L:
                masdar_id = f"MSDR_MUAWWAL_{'_'.join(verb_cl.root)}"
                return MasdarRecord(
                    masdar_id=masdar_id,
                    surface=f"أن {verb_cl.surface}",
                    root=verb_cl.root,
                    pattern="مصدر مؤوّل",
                    masdar_type=MasdarType.MUAWWAL,
                    masdar_bab=MasdarBab.FA3L,
                    verb_form=verb_cl.pattern,
                    kawn_type=KawnType.MASDAR_BRIDGE,
                    event_core="".join(verb_cl.root),
                    derivation_capacity=list(_FULL_DERIVATION_CAPACITY),
                    confidence=0.85,
                )
    return None


def validate_completeness(node: FractalMasdarNode) -> float:
    """Validate the 8 conditions of the minimal complete threshold.

    The eight conditions (الحد الأدنى المكتمل):

    1. **Thubūt**  (الثبوت)    — has a lexical or interpretive form
    2. **Ḥadd**    (الحد)      — distinguished from verb, noun, adjective
    3. **Imtidād** (الامتداد)  — event, derivational, conceptual extension
    4. **Muqawwim**(المقوِّم)   — event core + nominal abstraction + derivability
    5. **ʿAlāqa**  (العلاقة)   — links root, pattern, verb, derivatives
    6. **Intiẓām** (الانتظام)  — ordered in morpho-semantic network
    7. **Waḥda**   (الوحدة)    — forms one event essence
    8. **Taʿyīn**  (التعيين)   — assignable as explicit/interpreted masdar

    Parameters
    ----------
    node : FractalMasdarNode
        The fractal masdar node to validate.

    Returns
    -------
    float
        Completeness score in [0.0, 1.0] where 1.0 = all 8 conditions met.
    """
    score = 0.0
    m = node.masdar

    # 1. Thubūt — has surface form
    if m.surface:
        score += 1.0

    # 2. Ḥadd — has a masdar type distinct from verb/noun/adjective
    if m.masdar_type in (
        MasdarType.ORIGINAL,
        MasdarType.MIMI,
        MasdarType.INDUSTRIAL,
        MasdarType.MARRAH,
        MasdarType.HAY2A,
        MasdarType.MUAWWAL,
    ):
        score += 1.0

    # 3. Imtidād — has event core and derivation capacity
    if m.event_core and m.derivation_capacity:
        score += 1.0

    # 4. Muqawwim — has event core + pattern + root
    if m.event_core and m.pattern and m.root:
        score += 1.0

    # 5. ʿAlāqa — links root, pattern, verb
    if m.root and m.pattern and m.verb_form:
        score += 1.0

    # 6. Intiẓām — has bab assignment
    if m.masdar_bab is not None:
        score += 1.0

    # 7. Waḥda — kawn_type is MASDAR_BRIDGE (one event essence)
    if m.kawn_type == KawnType.MASDAR_BRIDGE:
        score += 1.0

    # 8. Taʿyīn — can be judged as explicit or interpreted
    if m.masdar_type != MasdarType.MUAWWAL or m.surface:
        score += 1.0

    return score / 8.0


def build_fractal_node(
    masdar: MasdarRecord,
    existential_link: str = "",
) -> FractalMasdarNode:
    """Build a complete fractal masdar node with all derivations.

    Creates derivations for all targets in the masdar's derivation
    capacity and computes the completeness score.

    Parameters
    ----------
    masdar : MasdarRecord
        The masdar record to build the node for.
    existential_link : str, optional
        An identifier linking to the existential being (الكينونة الوجودية).

    Returns
    -------
    FractalMasdarNode
    """
    derivations = [
        derive_from_masdar(masdar, target) for target in masdar.derivation_capacity
    ]
    children = [d.derivation_rule_id for d in derivations]

    node = FractalMasdarNode(
        node_id=f"FN_{masdar.masdar_id}",
        masdar=masdar,
        existential_link=existential_link,
        transformational_links=derivations,
        fractal_children=children,
        fractal_depth=1,
        completeness_score=0.0,
    )

    node.completeness_score = validate_completeness(node)
    return node
