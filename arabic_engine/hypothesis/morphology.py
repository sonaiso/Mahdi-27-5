"""Morphological hypotheses — فرضيات صرفية.

Generates morphological hypothesis nodes from segmentation hypotheses.
Wraps the existing :mod:`arabic_engine.signifier.root_pattern` module
to produce multiple candidates per token (when available).
"""

from __future__ import annotations

from typing import List

from arabic_engine.core.enums import ActivationStage, HypothesisStatus
from arabic_engine.core.types import HypothesisNode
from arabic_engine.signifier.root_pattern import extract_root_pattern


def generate(segments: List[HypothesisNode]) -> List[HypothesisNode]:
    """Generate morphological hypotheses for each segmentation hypothesis.

    For each segment, attempts root/pattern extraction via the lexicon.
    If found, produces a high-confidence hypothesis.  Otherwise produces
    a fallback hypothesis with lower confidence.

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
