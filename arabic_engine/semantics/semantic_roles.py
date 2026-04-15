"""Semantic role assignment from syntax nodes."""

from __future__ import annotations

from typing import Dict, List

from arabic_engine.core.enums import POS, IrabRole
from arabic_engine.core.types import LexicalClosure, SyntaxNode


def derive_semantic_roles(
    closures: List[LexicalClosure],
    syntax_nodes: List[SyntaxNode],
) -> Dict[str, str]:
    """Derive minimal semantic roles for proposition construction/explanation."""
    roles: Dict[str, str] = {
        "event": "",
        "agent": "",
        "patient": "",
        "time": "",
        "place": "",
    }

    lemma_by_surface = {cl.surface: cl.lemma for cl in closures}

    for node in syntax_nodes:
        lemma = lemma_by_surface.get(node.token, node.lemma)
        if node.role == IrabRole.FI3L and not roles["event"]:
            roles["event"] = lemma
        elif node.role == IrabRole.FA3IL and not roles["agent"]:
            roles["agent"] = lemma
        elif node.role == IrabRole.MAF3UL_BIH and not roles["patient"]:
            roles["patient"] = lemma

    for cl in closures:
        if cl.pos == POS.ZARF:
            temporal_name = (
                cl.temporal.name if cl.temporal is not None else "UNSPECIFIED"
            )
            spatial_name = (
                cl.spatial.name if cl.spatial is not None else "UNSPECIFIED"
            )
            if temporal_name != "UNSPECIFIED" and not roles["time"]:
                roles["time"] = cl.surface
            if spatial_name != "UNSPECIFIED" and not roles["place"]:
                roles["place"] = cl.surface

    return roles
