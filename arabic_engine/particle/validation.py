"""Particle validation — التحقق من اكتمال الحرف الفراكتالي.

Implements:

1. **Minimal completeness** check — the 8 conditions
   (ثبوت، حد، امتداد، مقوّم، علاقة بنائية، انتظام، وحدة، قابلية التعيين).

2. **Fractal score** computation — the 6-stage law
   (تعيين → حفظ → ربط → حكم → انتقال → رد).

3. **Full validation** — combines both checks.
"""

from __future__ import annotations

from typing import Optional

from arabic_engine.core.types import (
    ParticleFractalScore,
    ParticleMinimalCompleteness,
    ParticleRecord,
)
from arabic_engine.particle.registry import lookup

# ── Minimal Completeness ────────────────────────────────────────────

# Default fractal score threshold (θ₂)
FRACTAL_THRESHOLD: float = 0.5


def check_minimal_completeness(
    record: ParticleRecord,
) -> ParticleMinimalCompleteness:
    """Verify the 8 conditions of minimal completeness for a particle.

    Parameters
    ----------
    record : ParticleRecord
        The particle record to verify.

    Returns
    -------
    ParticleMinimalCompleteness
        Each of the 8 conditions evaluated.
    """
    return ParticleMinimalCompleteness(
        existence=bool(record.form),
        boundary=bool(record.particle_type is not None),
        extension=len(record.form) >= 1,
        constituent=(
            bool(record.form)
            and bool(record.relation_type)
            and bool(record.scope)
        ),
        structural_relation=bool(record.relation_type),
        regularity=bool(record.direction),
        unity=bool(record.particle_type),
        assignability=bool(record.particle_type),
    )


# ── Fractal Score ───────────────────────────────────────────────────


def compute_fractal_score(
    record: ParticleRecord,
) -> ParticleFractalScore:
    """Compute the 6-stage fractal completeness score FH(H).

    The six stages of the fractal law:

    1. **Identification (تعيين)** — particle type determinable?
    2. **Preservation (حفظ)** — identity retained across contexts?
    3. **Binding (ربط)** — does it bind/direct/restrict?
    4. **Judgment (حكم)** — can type, scope, conditions be judged?
    5. **Transition (انتقال)** — does it open/restrict/redirect?
    6. **Return (رد)** — can the syntactic effect be traced back?

    Parameters
    ----------
    record : ParticleRecord
        The particle record to score.

    Returns
    -------
    ParticleFractalScore
        The computed score for each stage plus the aggregate.
    """
    # 1. Identification — can the particle type be determined?
    identification = 1.0 if record.particle_type is not None else 0.0

    # 2. Preservation — does it retain identity across contexts?
    #    A cataloged particle with a stable form preserves identity.
    preservation = 1.0 if record.form else 0.0

    # 3. Binding — does it bind/direct/restrict?
    binding = 1.0 if record.relation_type is not None else 0.0

    # 4. Judgment — can we judge its type, scope, conditions?
    jd_score = 0.0
    if record.particle_type is not None:
        jd_score += 0.34
    if record.scope:
        jd_score += 0.33
    if record.effect:
        jd_score += 0.33
    judgment = min(jd_score, 1.0)

    # 5. Transition — does it open/restrict/redirect structure?
    transition = 1.0 if record.effect else 0.0

    # 6. Return — can its syntactic effect be traced back?
    return_trace = 1.0 if record.direction else 0.0

    return ParticleFractalScore(
        identification=identification,
        preservation=preservation,
        binding=binding,
        judgment=judgment,
        transition=transition,
        return_trace=return_trace,
    )


# ── Full Validation ─────────────────────────────────────────────────


def validate_particle(
    form: str,
    *,
    theta: float = FRACTAL_THRESHOLD,
) -> bool:
    """Full validation: is *form* a valid particle per the constitution?

    Checks:
    1. The form is in the particle catalog.
    2. Minimal completeness holds (all 8 conditions).
    3. Fractal score ≥ *theta*.

    Parameters
    ----------
    form : str
        The surface form to validate.
    theta : float
        Minimum fractal score threshold (default 0.5).

    Returns
    -------
    bool
        ``True`` if the form is a valid fractal particle.
    """
    record = lookup(form)
    if record is None:
        return False
    mc = check_minimal_completeness(record)
    if not mc.is_complete:
        return False
    fs = compute_fractal_score(record)
    return fs.fractal_score >= theta


def validate_record(
    record: ParticleRecord,
    *,
    theta: float = FRACTAL_THRESHOLD,
) -> bool:
    """Validate a pre-built :class:`ParticleRecord`.

    Parameters
    ----------
    record : ParticleRecord
        The record to validate.
    theta : float
        Minimum fractal score threshold.

    Returns
    -------
    bool
        ``True`` if both minimal completeness and fractal score pass.
    """
    mc = check_minimal_completeness(record)
    if not mc.is_complete:
        return False
    fs = compute_fractal_score(record)
    return fs.fractal_score >= theta
