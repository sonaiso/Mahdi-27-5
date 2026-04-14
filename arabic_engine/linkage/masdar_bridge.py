"""Masdar bridge — الجسر المصدري.

Implements the ontological bridge between:
  * **Existential being** (الكينونة الوجودية) — static nouns / rigid designators
  * **Transformational being** (الكينونة التحولية) — verbs / events / change

The masdar serves as the central linking node in the constitutional
architecture, connecting the static world of nouns with the dynamic
world of verbs through the abstract event concept.
"""

from __future__ import annotations

from typing import List, Optional

from arabic_engine.core.enums import (
    DalalaType,
    KawnType,
)
from arabic_engine.core.types import (
    Concept,
    DalalaLink,
    FractalMasdarNode,
    MasdarDerivation,
    MasdarRecord,
)


class KawnBridge:
    """الجسر الكينوني — bridge between existential and transformational being.

    The bridge tracks:
    - The rigid noun (جامد) that anchors the existential side
    - The masdar that serves as the bridge node
    - The verb/event concept that anchors the transformational side
    """

    def __init__(
        self,
        masdar: MasdarRecord,
        jamid_concept: Optional[Concept] = None,
        fi3l_concept: Optional[Concept] = None,
    ) -> None:
        self.masdar = masdar
        self.jamid_concept = jamid_concept
        self.fi3l_concept = fi3l_concept
        self._links: List[DalalaLink] = []

    @property
    def is_complete(self) -> bool:
        """Return ``True`` if both sides of the bridge are connected."""
        return self.jamid_concept is not None and self.fi3l_concept is not None

    @property
    def bridge_kawn_type(self) -> KawnType:
        """The being-mode of the bridge — always MASDAR_BRIDGE."""
        return KawnType.MASDAR_BRIDGE

    @property
    def links(self) -> List[DalalaLink]:
        """All dalāla links produced by the bridge."""
        return list(self._links)


def build_bridge(
    jamid_concept: Concept,
    masdar: MasdarRecord,
    fi3l_concept: Concept,
) -> KawnBridge:
    """Build a complete masdar bridge between existential and transformational.

    Creates a :class:`KawnBridge` and populates it with the dalāla links
    that represent the masdar's bridging role.

    Parameters
    ----------
    jamid_concept : Concept
        The existential-side concept (rigid noun / entity).
    masdar : MasdarRecord
        The masdar serving as bridge.
    fi3l_concept : Concept
        The transformational-side concept (verb / event).

    Returns
    -------
    KawnBridge
        A fully populated bridge instance.
    """
    bridge = KawnBridge(
        masdar=masdar,
        jamid_concept=jamid_concept,
        fi3l_concept=fi3l_concept,
    )

    # Link masdar → existential (jamid)
    bridge._links.append(
        DalalaLink(
            source_lemma=masdar.surface,
            target_concept_id=jamid_concept.concept_id,
            dalala_type=DalalaType.MASDAR_BRIDGE,
            accepted=True,
            confidence=0.9,
        )
    )

    # Link masdar → transformational (fi3l)
    bridge._links.append(
        DalalaLink(
            source_lemma=masdar.surface,
            target_concept_id=fi3l_concept.concept_id,
            dalala_type=DalalaType.MASDAR_BRIDGE,
            accepted=True,
            confidence=0.95,
        )
    )

    return bridge


def trace_fractal_path(
    node: FractalMasdarNode,
    target_type: str,
) -> List[MasdarDerivation]:
    """Trace the fractal derivation path from masdar to a target type.

    Parameters
    ----------
    node : FractalMasdarNode
        The fractal masdar node.
    target_type : str
        The name of the derivation target to trace (e.g. ``"ISM_FA3IL"``).

    Returns
    -------
    list of MasdarDerivation
        All derivations matching the target type.
    """
    return [
        d for d in node.transformational_links if d.target_type.name == target_type
    ]


def validate_masdar_link(
    masdar: MasdarRecord,
    concept: Concept,
) -> DalalaLink:
    """Validate a masdar-bridge dalāla link.

    Tests whether the masdar's root overlaps with the concept label,
    and produces a MASDAR_BRIDGE link with appropriate confidence.

    Parameters
    ----------
    masdar : MasdarRecord
        The masdar record.
    concept : Concept
        The target concept.

    Returns
    -------
    DalalaLink
    """
    # Root-based matching
    if masdar.root and any(r in concept.label for r in masdar.root):
        confidence = 0.85
    else:
        confidence = 0.5

    return DalalaLink(
        source_lemma=masdar.surface,
        target_concept_id=concept.concept_id,
        dalala_type=DalalaType.MASDAR_BRIDGE,
        accepted=True,
        confidence=confidence,
    )
