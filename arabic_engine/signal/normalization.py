"""Normalization actions — تطبيع مع تبرير.

Wraps the existing :func:`arabic_engine.signifier.unicode_norm.normalize`
but adds atom-level tracking: every normalization decision (tatweel
removal, whitespace collapse, optional tashkīl strip) is recorded
as a :class:`~arabic_engine.core.types.DecisionTrace`.

The key architectural rule: **no normalization without justification**.
"""

from __future__ import annotations

from typing import List, Tuple

from arabic_engine.core.enums import ActivationStage, SignalType
from arabic_engine.core.types import DecisionTrace, SignalUnit, UnicodeAtom
from arabic_engine.signifier.unicode_norm import normalize

# ── Tatweel code-point ──────────────────────────────────────────────
_TATWEEL_CP = 0x0640


def normalize_atoms(
    atoms: List[UnicodeAtom],
    *,
    strip_tashkil: bool = False,
) -> Tuple[List[SignalUnit], List[DecisionTrace]]:
    """Normalize a list of atoms into signal units with trace.

    Steps
    -----
    1. Group atoms into whitespace-delimited token spans.
    2. For each span, apply :func:`normalize` and record which atoms
       were dropped or modified.
    3. Return the resulting :class:`SignalUnit` list and a trace entry
       per normalization action taken.

    Parameters
    ----------
    atoms : list[UnicodeAtom]
        Output of :func:`~arabic_engine.signal.unicode_atoms.decompose`.
    strip_tashkil : bool
        When ``True``, diacritics are removed (forwarded to
        :func:`normalize`).

    Returns
    -------
    tuple[list[SignalUnit], list[DecisionTrace]]
        Normalised signal units and their justification traces.
    """
    if not atoms:
        return [], []

    # Reconstruct raw text from atoms
    raw = "".join(a.char for a in atoms)
    normed = normalize(raw, strip_tashkil=strip_tashkil)

    # Build token-level signal units from normalised text
    tokens = normed.split() if normed.strip() else []
    units: List[SignalUnit] = []
    traces: List[DecisionTrace] = []

    # Walk the original atoms to find spans for each normalised token
    atom_idx = 0
    for tok_idx, token in enumerate(tokens):
        # Skip whitespace atoms
        while atom_idx < len(atoms) and atoms[atom_idx].signal_type == SignalType.WHITESPACE:
            atom_idx += 1

        start = atom_idx
        matched_chars = 0
        dropped: List[str] = []

        # Consume atoms until we've matched all chars in the token
        while atom_idx < len(atoms) and matched_chars < len(token):
            a = atoms[atom_idx]
            if a.signal_type == SignalType.WHITESPACE:
                break
            if a.codepoint == _TATWEEL_CP:
                dropped.append(a.atom_id)
                atom_idx += 1
                continue
            if strip_tashkil and a.signal_type == SignalType.DIACRITIC:
                dropped.append(a.atom_id)
                atom_idx += 1
                continue
            matched_chars += 1
            atom_idx += 1

        end = atom_idx
        surface = "".join(atoms[i].char for i in range(start, end) if i < len(atoms))

        units.append(
            SignalUnit(
                unit_id=f"SU_{tok_idx}",
                surface_text=surface,
                normalized_text=token,
                source_span=(start, end),
                signal_type=SignalType.BASE_LETTER,
            )
        )

        if dropped:
            traces.append(
                DecisionTrace(
                    trace_id=f"NT_{tok_idx}",
                    stage=ActivationStage.SIGNAL,
                    decision_type="normalization",
                    input_refs=tuple(dropped),
                    output_refs=(f"SU_{tok_idx}",),
                    applied_rules=_classify_dropped_rules(atoms, dropped),
                    justification="Removed tatweel or diacritics during normalization",
                )
            )

    return units, traces


def _classify_dropped_rules(
    atoms: List[UnicodeAtom], dropped: List[str]
) -> tuple[str, ...]:
    """Determine which normalization rule was applied to dropped atoms."""
    has_tatweel = False
    for d in dropped:
        parts = d.split("_", 1)
        if len(parts) == 2 and parts[0] == "A":
            try:
                idx = int(parts[1])
            except ValueError:
                continue
            if 0 <= idx < len(atoms) and atoms[idx].codepoint == _TATWEEL_CP:
                has_tatweel = True
                break
    return ("tatweel_removal",) if has_tatweel else ("tashkil_strip",)
