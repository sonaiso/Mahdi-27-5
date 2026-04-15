"""Pre-U₀ admissibility — Unicode possibility and cognitive admissibility.

Implements the six-dimension admissibility check that must pass before
any input enters the main pipeline chain.  This is the first gate in
the system, preceding even L0 (normalisation).

See ``docs/unicode_possibility_and_cognitive_admissibility_constitution_v1.md``
for the formal specification.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone

from arabic_engine.core.enums import AdmissibilityDecision, AdmissibilityDimension
from arabic_engine.core.types import AdmissibilityCheck, AdmissibilityResult

# ── Arabic Unicode ranges ───────────────────────────────────────────

# Compiled pattern matching at least one Arabic-script character.
_ARABIC_RE = re.compile(
    "["
    "\u0600-\u06FF"   # Arabic
    "\u0750-\u077F"   # Arabic Supplement
    "\u0870-\u089F"   # Arabic Extended-B
    "\u08A0-\u08FF"   # Arabic Extended-A
    "\uFB50-\uFDFF"   # Arabic Presentation Forms-A
    "\uFE70-\uFEFF"   # Arabic Presentation Forms-B
    "]"
)

# Diacritical marks and tatweel that do not carry content on their own.
_DIACRITICS_RE = re.compile(
    "["
    "\u064B-\u065F"   # Arabic combining marks
    "\u0670"          # Superscript alef
    "\u0640"          # Tatweel
    "]"
)


# ── Dimension checks ───────────────────────────────────────────────


def _check_presence(text: str) -> AdmissibilityCheck:
    """Dimension 1 — الحضور: input exists and is non-empty."""
    if text is None or len(text.strip()) == 0:
        return AdmissibilityCheck(
            dimension=AdmissibilityDimension.PRESENCE,
            passed=False,
            reason="Input is empty or whitespace-only",
        )
    return AdmissibilityCheck(
        dimension=AdmissibilityDimension.PRESENCE,
        passed=True,
        reason="Input is present",
        evidence=(f"length={len(text)}",),
    )


def _check_distinguishability(text: str) -> AdmissibilityCheck:
    """Dimension 2 — القابلية للتمييز: at least one visible character."""
    for ch in text:
        cat = unicodedata.category(ch)
        # Letters, numbers, punctuation, symbols are visible
        if cat[0] in ("L", "N", "P", "S"):
            return AdmissibilityCheck(
                dimension=AdmissibilityDimension.DISTINGUISHABILITY,
                passed=True,
                reason="At least one visible character found",
                evidence=(f"char={ch!r} category={cat}",),
            )
    return AdmissibilityCheck(
        dimension=AdmissibilityDimension.DISTINGUISHABILITY,
        passed=False,
        reason="No visible characters found (whitespace/control only)",
    )


def _check_initial_admissibility(text: str) -> AdmissibilityCheck:
    """Dimension 3 — القبول الأولي: contains at least one Arabic character."""
    m = _ARABIC_RE.search(text)
    if m:
        return AdmissibilityCheck(
            dimension=AdmissibilityDimension.INITIAL_ADMISSIBILITY,
            passed=True,
            reason="Arabic character found",
            evidence=(f"char={m.group()!r}",),
        )
    return AdmissibilityCheck(
        dimension=AdmissibilityDimension.INITIAL_ADMISSIBILITY,
        passed=False,
        reason="No Arabic characters found in input",
    )


def _check_prior_knowledge_binding(text: str) -> AdmissibilityCheck:
    """Dimension 4 — الربط بالمعرفة المسبقة: characters belong to known scripts."""
    arabic_count = 0
    non_arabic_letter_count = 0
    for ch in text:
        if _ARABIC_RE.match(ch):
            arabic_count += 1
        elif unicodedata.category(ch).startswith("L"):
            non_arabic_letter_count += 1

    total_letters = arabic_count + non_arabic_letter_count
    if total_letters == 0:
        return AdmissibilityCheck(
            dimension=AdmissibilityDimension.PRIOR_KNOWLEDGE_BINDING,
            passed=True,
            reason="No letter characters to classify",
        )

    arabic_ratio = arabic_count / total_letters
    if arabic_ratio >= 0.5:
        return AdmissibilityCheck(
            dimension=AdmissibilityDimension.PRIOR_KNOWLEDGE_BINDING,
            passed=True,
            reason=f"Arabic ratio {arabic_ratio:.0%} — predominantly Arabic",
            evidence=(f"arabic={arabic_count}", f"non_arabic={non_arabic_letter_count}"),
        )
    return AdmissibilityCheck(
        dimension=AdmissibilityDimension.PRIOR_KNOWLEDGE_BINDING,
        passed=False,
        reason=f"Arabic ratio {arabic_ratio:.0%} — predominantly non-Arabic",
        evidence=(f"arabic={arabic_count}", f"non_arabic={non_arabic_letter_count}"),
    )


def _check_preliminary_interpretation(text: str) -> AdmissibilityCheck:
    """Dimension 5 — التأويل الأولي: content remains after stripping diacritics/tatweel."""
    stripped = _DIACRITICS_RE.sub("", text).strip()
    if stripped:
        return AdmissibilityCheck(
            dimension=AdmissibilityDimension.PRELIMINARY_INTERPRETATION,
            passed=True,
            reason="Content remains after diacritic/tatweel removal",
            evidence=(f"stripped_length={len(stripped)}",),
        )
    return AdmissibilityCheck(
        dimension=AdmissibilityDimension.PRELIMINARY_INTERPRETATION,
        passed=False,
        reason="Input is diacritics/tatweel only — no interpretable content",
    )


def _check_pre_designation_conception(text: str) -> AdmissibilityCheck:
    """Dimension 6 — التصور قبل التعيين: input can be split into tokens."""
    stripped = _DIACRITICS_RE.sub("", text).strip()
    tokens = stripped.split()
    if tokens:
        return AdmissibilityCheck(
            dimension=AdmissibilityDimension.PRE_DESIGNATION_CONCEPTION,
            passed=True,
            reason=f"Input splits into {len(tokens)} token(s)",
            evidence=(f"tokens={len(tokens)}",),
        )
    return AdmissibilityCheck(
        dimension=AdmissibilityDimension.PRE_DESIGNATION_CONCEPTION,
        passed=False,
        reason="Input cannot be split into tokens",
    )


# ── Main entry point ────────────────────────────────────────────────


_CHECKS = [
    _check_presence,
    _check_distinguishability,
    _check_initial_admissibility,
    _check_prior_knowledge_binding,
    _check_preliminary_interpretation,
    _check_pre_designation_conception,
]

# Dimensions that trigger REJECT on failure (critical dimensions).
_CRITICAL_DIMENSIONS = frozenset({
    AdmissibilityDimension.PRESENCE,
    AdmissibilityDimension.DISTINGUISHABILITY,
    AdmissibilityDimension.INITIAL_ADMISSIBILITY,
    AdmissibilityDimension.PRELIMINARY_INTERPRETATION,
    AdmissibilityDimension.PRE_DESIGNATION_CONCEPTION,
})


def check_admissibility(text: str) -> AdmissibilityResult:
    """Run the six-dimension pre-U₀ admissibility check.

    Parameters
    ----------
    text : str
        Raw input text to evaluate.

    Returns
    -------
    AdmissibilityResult
        Overall decision (ACCEPT / SUSPEND / REJECT) with per-dimension
        check results.
    """
    checks = []
    has_critical_failure = False
    has_non_critical_failure = False

    for check_fn in _CHECKS:
        result = check_fn(text if text is not None else "")
        checks.append(result)
        if not result.passed:
            if result.dimension in _CRITICAL_DIMENSIONS:
                has_critical_failure = True
            else:
                has_non_critical_failure = True

    if has_critical_failure:
        decision = AdmissibilityDecision.REJECT
    elif has_non_critical_failure:
        decision = AdmissibilityDecision.SUSPEND
    else:
        decision = AdmissibilityDecision.ACCEPT

    return AdmissibilityResult(
        input_text=text if text is not None else "",
        decision=decision,
        checks=tuple(checks),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
