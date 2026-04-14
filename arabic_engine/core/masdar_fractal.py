"""Masdar fractal law engine — القانون الفراكتالي المصدري.

Implements the six-phase fractal law cycle for the masdar:

    تعيين → حفظ → ربط → حكم → انتقال → ردّ
    assign → preserve → link → judge → transition → return_to_source

Also provides the D_min masdar validation (8-condition completeness check).
"""

from __future__ import annotations

from typing import Dict, List, Optional

from arabic_engine.core.enums import DerivationTarget, KawnType, MasdarBab
from arabic_engine.core.types import (
    FractalMasdarNode,
    MasdarDerivation,
    MasdarRecord,
)
from arabic_engine.signifier.masdar import (
    build_fractal_node,
    derive_from_masdar,
    validate_completeness,
)


# ── Phase 1: Assign (تعيين) ─────────────────────────────────────────


def assign(masdar: MasdarRecord) -> Dict[str, object]:
    """Assign — تعيين: this is a masdar for verb X.

    Produces an assignment record declaring the masdar's identity:
    its bab, type, root, and generating verb.

    Parameters
    ----------
    masdar : MasdarRecord

    Returns
    -------
    dict
        Assignment record with keys: masdar_id, bab, masdar_type,
        root, verb_form, event_core.
    """
    return {
        "masdar_id": masdar.masdar_id,
        "bab": masdar.masdar_bab.name,
        "masdar_type": masdar.masdar_type.name,
        "root": masdar.root,
        "verb_form": masdar.verb_form,
        "event_core": masdar.event_core,
    }


# ── Phase 2: Preserve (حفظ) ─────────────────────────────────────────


def preserve(masdar: MasdarRecord) -> Dict[str, object]:
    """Preserve — حفظ: preserves the event essence.

    Extracts and returns the core event content that the masdar
    preserves abstractly, independent of time and person.

    Parameters
    ----------
    masdar : MasdarRecord

    Returns
    -------
    dict
        Preservation record with event_core, surface, pattern.
    """
    return {
        "event_core": masdar.event_core,
        "surface": masdar.surface,
        "pattern": masdar.pattern,
        "kawn_type": masdar.kawn_type.name,
        "preserved": True,
    }


# ── Phase 3: Link (ربط) ─────────────────────────────────────────────


def link(
    masdar: MasdarRecord,
    jamid_id: str = "",
    fi3l_id: str = "",
    mushtaqqat_ids: Optional[List[str]] = None,
) -> Dict[str, object]:
    """Link — ربط: links the masdar to rigid noun, verb, and derivatives.

    Creates a linking record showing how the masdar connects
    existential being (jamid) to transformational being (fi3l)
    and the derived forms (mushtaqqat).

    Parameters
    ----------
    masdar : MasdarRecord
    jamid_id : str
        Identifier of the rigid noun (existential side).
    fi3l_id : str
        Identifier of the verb (transformational side).
    mushtaqqat_ids : list of str, optional
        Identifiers of derived forms.

    Returns
    -------
    dict
        Linking record.
    """
    return {
        "masdar_id": masdar.masdar_id,
        "existential_link": jamid_id,
        "transformational_link": fi3l_id,
        "derivative_links": mushtaqqat_ids or [],
        "bridge_type": KawnType.MASDAR_BRIDGE.name,
    }


# ── Phase 4: Judge (حكم) ────────────────────────────────────────────


def judge(masdar: MasdarRecord) -> Dict[str, object]:
    """Judge — حكم: judges the masdar by bab, type, direction, productivity.

    Parameters
    ----------
    masdar : MasdarRecord

    Returns
    -------
    dict
        Judgment record with bab, type, derivation capacity, confidence.
    """
    return {
        "masdar_id": masdar.masdar_id,
        "bab": masdar.masdar_bab.name,
        "masdar_type": masdar.masdar_type.name,
        "derivation_capacity": [t.name for t in masdar.derivation_capacity],
        "productivity": len(masdar.derivation_capacity),
        "confidence": masdar.confidence,
    }


# ── Phase 5: Transition (انتقال) ────────────────────────────────────


def transition(
    masdar: MasdarRecord,
    targets: Optional[List[DerivationTarget]] = None,
) -> List[MasdarDerivation]:
    """Transition — انتقال: derives verb/participles/time/place/manner/instrument.

    Parameters
    ----------
    masdar : MasdarRecord
    targets : list of DerivationTarget, optional
        Specific targets; defaults to the masdar's full derivation capacity.

    Returns
    -------
    list of MasdarDerivation
    """
    if targets is None:
        targets = masdar.derivation_capacity
    return [derive_from_masdar(masdar, t) for t in targets]


# ── Phase 6: Return to Source (ردّ) ──────────────────────────────────


def return_to_source(
    derivations: List[MasdarDerivation],
    masdar: MasdarRecord,
) -> Dict[str, object]:
    """Return to source — ردّ: traces all derivations back to the masdar.

    Verifies that every derivation in the list points back to the
    same masdar, confirming the fractal cycle.

    Parameters
    ----------
    derivations : list of MasdarDerivation
    masdar : MasdarRecord

    Returns
    -------
    dict
        Return record with source_masdar_id, all_return flag, count.
    """
    all_return = all(d.source_masdar_id == masdar.masdar_id for d in derivations)
    return {
        "source_masdar_id": masdar.masdar_id,
        "all_return": all_return,
        "derivation_count": len(derivations),
        "event_core": masdar.event_core,
    }


# ── Full Fractal Cycle ──────────────────────────────────────────────


def run_fractal_cycle(
    masdar: MasdarRecord,
    jamid_id: str = "",
    fi3l_id: str = "",
) -> Dict[str, object]:
    """Run the full six-phase fractal cycle on a masdar.

    Parameters
    ----------
    masdar : MasdarRecord
    jamid_id : str
        Existential-side identifier.
    fi3l_id : str
        Transformational-side identifier.

    Returns
    -------
    dict
        A record containing results from all six phases and
        the final completeness score.
    """
    # Phase 1: تعيين
    assignment = assign(masdar)

    # Phase 2: حفظ
    preservation = preserve(masdar)

    # Phase 3: ربط
    derivations = transition(masdar)
    mushtaqqat_ids = [d.derivation_rule_id for d in derivations]
    linking = link(masdar, jamid_id, fi3l_id, mushtaqqat_ids)

    # Phase 4: حكم
    judgment = judge(masdar)

    # Phase 5: انتقال (already computed above)

    # Phase 6: ردّ
    return_record = return_to_source(derivations, masdar)

    # Build fractal node and validate
    fractal_node = build_fractal_node(masdar, existential_link=jamid_id)
    completeness = validate_completeness(fractal_node)

    return {
        "assignment": assignment,
        "preservation": preservation,
        "linking": linking,
        "judgment": judgment,
        "derivations": [
            {
                "target": d.target_type.name,
                "pattern": d.target_pattern,
                "rule_id": d.derivation_rule_id,
            }
            for d in derivations
        ],
        "return_record": return_record,
        "completeness_score": completeness,
        "fractal_node_id": fractal_node.node_id,
    }


# ── D_min Masdar Validation ─────────────────────────────────────────


def validate_dmin_masdar(node: FractalMasdarNode) -> Dict[str, object]:
    """Validate the 8 conditions of the masdar D_min.

    Returns a per-condition breakdown alongside the aggregate score.

    Parameters
    ----------
    node : FractalMasdarNode

    Returns
    -------
    dict
        Keys: conditions (list of dicts), score (float).
    """
    m = node.masdar
    conditions = [
        {"name": "thubut", "label": "الثبوت", "met": bool(m.surface)},
        {
            "name": "hadd",
            "label": "الحد",
            "met": m.masdar_type is not None,
        },
        {
            "name": "imtidad",
            "label": "الامتداد",
            "met": bool(m.event_core and m.derivation_capacity),
        },
        {
            "name": "muqawwim",
            "label": "المقوِّم",
            "met": bool(m.event_core and m.pattern and m.root),
        },
        {
            "name": "alaqa",
            "label": "العلاقة",
            "met": bool(m.root and m.pattern and m.verb_form),
        },
        {
            "name": "intizam",
            "label": "الانتظام",
            "met": m.masdar_bab is not None,
        },
        {
            "name": "wahda",
            "label": "الوحدة",
            "met": m.kawn_type == KawnType.MASDAR_BRIDGE,
        },
        {
            "name": "taayin",
            "label": "التعيين",
            "met": m.masdar_type is not None and bool(m.surface),
        },
    ]

    met_count = sum(1 for c in conditions if c["met"])
    return {
        "conditions": conditions,
        "score": met_count / 8.0,
        "met_count": met_count,
        "total": 8,
    }
