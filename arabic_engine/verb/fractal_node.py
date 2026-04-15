"""Verb fractal node builder — بناء العقدة الفراكتالية الفعلية.

Constructs the verb as a complete fractal node following the
six-stage cycle:

    تعيين → حفظ → ربط → حكم → انتقال → رد

Each stage produces evidence that the verb satisfies that
dimension of the fractal structure.
"""

from __future__ import annotations

from typing import Optional

from arabic_engine.core.enums import (
    POS,
    VerbAugmentation,
    VerbCompleteness,
    VerbFractalStage,
)
from arabic_engine.core.types import (
    VerbDerivativeChain,
    VerbFractalNode,
)

from . import analyzer, derivatives, threshold


def build(
    surface: str,
    pattern: str = "",
    pos: POS = POS.FI3L,
) -> Optional[VerbFractalNode]:
    """Build a :class:`VerbFractalNode` for the given surface form.

    Returns ``None`` if the surface cannot be analysed as a verb.
    """
    # ── Stage 1: تعيين (Designation) ─────────────────────────────
    profile = analyzer.analyze(surface, pattern=pattern, pos=pos)
    if profile is None:
        return None

    root = profile.root
    bab = profile.bab

    # ── Stage 2: حفظ (Preservation) ──────────────────────────────
    # Validate the minimal threshold
    thresh = threshold.validate(
        surface=surface,
        pos=pos,
        root=root,
        pattern=pattern or bab.past_pattern,
        tense=profile.tense,
        bab=bab,
    )

    # ── Stage 5: انتقال (Transition) — build derivatives ─────────
    if root and len(root) >= 3:
        deriv_chain = derivatives.build(root, bab)
    else:
        deriv_chain = VerbDerivativeChain(
            root=root,
            bab_id=bab.bab_id,
            masdar="",
            ism_fa3il="",
            ism_maf3ul="",
            ism_zaman="",
            ism_makan="",
        )

    # ── Coherence links (evidence per stage) ─────────────────────
    links: list[tuple[str, str]] = []

    # تعيين evidence
    aug_label = (
        "مجرد" if bab.augmentation == VerbAugmentation.MUJARRAD
        else "مزيد"
    )
    links.append((
        VerbFractalStage.TA3YIN.name,
        f"{aug_label} / {profile.tense.name} / {profile.transitivity.name}",
    ))

    # حفظ evidence
    root_str = "-".join(root) if root else "?"
    links.append((
        VerbFractalStage.HIFDH.name,
        f"جذر={root_str} / وزن={bab.past_pattern}",
    ))

    # ربط evidence
    links.append((
        VerbFractalStage.RABT.name,
        f"حدث↔زمن={profile.tense.name} / حدث↔فاعل=بالقوة",
    ))

    # حكم evidence
    comp_label = (
        "ناقص" if profile.completeness == VerbCompleteness.NAQIS
        else "تام"
    )
    links.append((
        VerbFractalStage.HUKM.name,
        f"{comp_label} / {profile.voice.name}",
    ))

    # انتقال evidence
    links.append((
        VerbFractalStage.INTIQAL.name,
        f"مصدر={deriv_chain.masdar}" if deriv_chain.masdar else "—",
    ))

    # رد evidence
    links.append((
        VerbFractalStage.RADD.name,
        f"باب={bab.bab_label} / جذر={root_str}",
    ))

    # Determine which fractal stage the verb has reached.
    # If threshold is complete, the verb is at the highest stage.
    if thresh.is_complete:
        stage = VerbFractalStage.RADD
    elif thresh.has_intizam:
        stage = VerbFractalStage.INTIQAL
    elif thresh.has_3alaqa_binaya:
        stage = VerbFractalStage.HUKM
    elif thresh.has_muqawwim:
        stage = VerbFractalStage.RABT
    elif thresh.has_hadd:
        stage = VerbFractalStage.HIFDH
    else:
        stage = VerbFractalStage.TA3YIN

    return VerbFractalNode(
        profile=profile,
        threshold=thresh,
        derivatives=deriv_chain,
        fractal_stage=stage,
        coherence_links=tuple(links),
    )
