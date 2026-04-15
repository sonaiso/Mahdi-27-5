"""Morphological hypotheses — فرضيات صرفية.

Generates morphological hypothesis nodes from segmentation hypotheses.
Wraps the existing :mod:`arabic_engine.morphology.root_pattern` module
to produce multiple candidates per token (when available).
"""

from __future__ import annotations

from typing import List

from arabic_engine.core.enums import POS, ActivationStage, HypothesisStatus
from arabic_engine.core.types import HypothesisNode
from arabic_engine.morphology.masdar import extract_masdar_from_surface
from arabic_engine.morphology.root_pattern import extract_root_pattern, lexical_closure


def generate(segments: List[HypothesisNode]) -> List[HypothesisNode]:
    """Generate morphological hypotheses for each segmentation hypothesis.

    For each segment, attempts root/pattern extraction via the lexicon.
    If found, produces a high-confidence hypothesis.  Otherwise produces
    a fallback hypothesis with lower confidence.

    Additionally generates masdar-specific hypotheses when a segment
    matches a known masdar pattern.

    Parameters
    ----------
    segments : list[HypothesisNode]
        Segmentation hypotheses (``hypothesis_type == "segmentation"``).

    Returns
    -------
    list[HypothesisNode]
        Morphological hypotheses, one or more per segment.
    """
    hypotheses: List[HypothesisNode] = []
    for seg in segments:
        token = seg.get("token_text", "")
        rp = extract_root_pattern(str(token))

        if rp is not None:
            hypotheses.append(
                HypothesisNode(
                    node_id=f"MORPH_{seg.node_id}",
                    hypothesis_type="morphology",
                    stage=ActivationStage.MORPHOLOGY,
                    source_refs=(seg.node_id,),
                    payload=(
                        ("lemma", str(token)),
                        ("root", rp.root),
                        ("pattern", rp.pattern),
                        ("root_id", rp.root_id),
                        ("pattern_id", rp.pattern_id),
                    ),
                    confidence=0.95,
                    status=HypothesisStatus.ACTIVE,
                )
            )

            # Check if this is also a masdar
            closure = lexical_closure(str(token))
            if closure.pos in (POS.MASDAR_SARIH, POS.MASDAR_MUAWWAL):
                masdar = extract_masdar_from_surface(str(token))
                if masdar is not None:
                    hypotheses.append(
                        HypothesisNode(
                            node_id=f"MORPH_MASDAR_{seg.node_id}",
                            hypothesis_type="morphology_masdar",
                            stage=ActivationStage.MORPHOLOGY,
                            source_refs=(seg.node_id,),
                            payload=(
                                ("lemma", str(token)),
                                ("root", masdar.root),
                                ("pattern", masdar.pattern),
                                ("masdar_type", masdar.masdar_type.name),
                                ("masdar_bab", masdar.masdar_bab.name),
                                ("event_core", masdar.event_core),
                            ),
                            confidence=0.92,
                            status=HypothesisStatus.ACTIVE,
                        )
                    )
        else:
            # Still check masdar lexicon for unknown tokens
            masdar = extract_masdar_from_surface(str(token))
            if masdar is not None:
                hypotheses.append(
                    HypothesisNode(
                        node_id=f"MORPH_MASDAR_{seg.node_id}",
                        hypothesis_type="morphology_masdar",
                        stage=ActivationStage.MORPHOLOGY,
                        source_refs=(seg.node_id,),
                        payload=(
                            ("lemma", str(token)),
                            ("root", masdar.root),
                            ("pattern", masdar.pattern),
                            ("masdar_type", masdar.masdar_type.name),
                            ("masdar_bab", masdar.masdar_bab.name),
                            ("event_core", masdar.event_core),
                        ),
                        confidence=0.90,
                        status=HypothesisStatus.ACTIVE,
                    )
                )
            else:
                # Fallback: unknown morphology
                hypotheses.append(
                    HypothesisNode(
                        node_id=f"MORPH_{seg.node_id}",
                        hypothesis_type="morphology",
                        stage=ActivationStage.MORPHOLOGY,
                        source_refs=(seg.node_id,),
                        payload=(
                            ("lemma", str(token)),
                            ("root", ()),
                            ("pattern", ""),
                        ),
                        confidence=0.3,
                        status=HypothesisStatus.ACTIVE,
                    )
                )
    return hypotheses
