"""Fractal Representation Spec v1 (FRS-v1).

This module is the primary implementation of the first derived specification
of the Fractal Core Constitution (FCC-v1 §7).

Specification reference: ``docs/fractal_representation_spec_v1.md``
Constitution reference:  ``docs/fractal_core_constitution_v1.md``

Overview
--------
The Fractal Representation encodes the **entire analysis trace** of a
linguistic element as a single, immutable, hashable Python object.  It:

1. Records the fractal origin tuple `(E, K, F, C)` for the input element.
2. Captures the layer-by-layer trace `L0 → L9`.
3. Assigns a canonical representation format and mode.
4. Provides a deterministic integer encoding (`to_int_vector`) making the
   full representation a member of ℕⁿ, consistent with FCC-v1 §2.

Public types
------------
* :class:`FractalOrigin`    — the `(E, K, F, C)` origin tuple.
* :class:`LayerTrace`       — ordered sequence of layer identifiers reached.
* :class:`RepresentationMode` — output mode (text / numeric / graph).
* :class:`RepresentationFormat` — serialisation format.
* :class:`FractalRepresentation` — complete, immutable representation record.

Public functions
----------------
* :func:`validate_fractal_origin`   — verify an origin satisfies FCC-v1 §2.
* :func:`build_fractal_representation` — construct a :class:`FractalRepresentation`.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum, auto
from typing import Sequence


# ── FRS-v1 §1 — Fractal origin ──────────────────────────────────────


@dataclass(frozen=True)
class FractalOrigin:
    """الأصل الفراكتالي — origin tuple `(E, K, F, C)` (FCC-v1 §2 / FRS-v1 §1).

    Parameters
    ----------
    existence:
        `E(u)` — Unicode code-point integer proving existence of the element.
    prior_knowledge_key:
        `K(u)` — opaque key into prior-knowledge registry (e.g. DMIN_REGISTRY).
    function_mask:
        `F(u)` — integer bitmask of phonological features and transforms.
    initial_class:
        `C(u)` — initial classification string (e.g. ``"consonant"``,
        ``"short_vowel"``).
    """

    existence: int          # E(u) — codepoint ∈ ℕ
    prior_knowledge_key: str  # K(u) — registry key
    function_mask: int      # F(u) — feature/transform bitmask ∈ ℕ
    initial_class: str      # C(u) — discrete classification label


# ── FRS-v1 §2 — Layer trace ─────────────────────────────────────────


@dataclass(frozen=True)
class LayerTrace:
    """أثر الطبقات — ordered record of pipeline layers completed (FRS-v1 §2).

    Parameters
    ----------
    layers:
        Tuple of layer names in ascending order, e.g.
        ``("SIGNAL", "MORPHOLOGY", "SYNTAX")``.
    final_layer:
        Name of the highest layer reached.
    gate_passed:
        ``True`` when every inter-layer gate was passed without blocking.
    """

    layers: tuple[str, ...]
    final_layer: str
    gate_passed: bool

    @classmethod
    def from_sequence(
        cls, layers: Sequence[str], *, gate_passed: bool = True
    ) -> "LayerTrace":
        """Construct from a plain sequence of layer-name strings."""
        t = tuple(layers)
        return cls(
            layers=t,
            final_layer=t[-1] if t else "",
            gate_passed=gate_passed,
        )


# ── FRS-v1 §3 — Representation modes and formats ────────────────────


class RepresentationMode(Enum):
    """نمط التمثيل — output encoding mode (FRS-v1 §3).

    TEXT
        Human-readable Arabic-script representation.
    NUMERIC
        Integer-vector representation `(u, c, g, f, t) ∈ ℕⁿ`.
    GRAPH
        Node-edge graph representation compatible with Kernel-14.
    HYBRID
        Combined text + numeric encoding.
    """

    TEXT = auto()
    NUMERIC = auto()
    GRAPH = auto()
    HYBRID = auto()


class RepresentationFormat(Enum):
    """صيغة التمثيل — serialisation format for exchange (FRS-v1 §3).

    TUPLE
        Python frozen tuple — default in-memory format.
    JSON
        JSON-serialisable dict (integers, strings, lists only).
    YAML
        YAML-compatible mapping.
    CYPHER
        Neo4j Cypher ``CREATE`` statement for graph import.
    """

    TUPLE = auto()
    JSON = auto()
    YAML = auto()
    CYPHER = auto()


# ── FRS-v1 §4 — Fractal representation record ───────────────────────


@dataclass(frozen=True)
class FractalRepresentation:
    """سجل التمثيل الفراكتالي — complete, immutable representation (FRS-v1 §4).

    This is the canonical output type of the Fractal Representation Spec.
    Every field traces back to the fractal origin `(E, K, F, C)`.

    Parameters
    ----------
    element_id:
        Unique identifier for the element, e.g. ``"U+0643"``.
    origin:
        The fractal origin tuple for this element.
    layer_trace:
        Ordered record of pipeline layers completed.
    mode:
        Representation mode used when building this record.
    format:
        Serialisation format tag for this record.
    confidence_vector:
        Layer-by-layer confidence scores `(c_0, c_1, …, c_n) ∈ [0, 1]ⁿ`.
    sha256:
        Deterministic SHA-256 digest of the origin + trace combination,
        providing a stable content-hash for deduplication.
    """

    element_id: str
    origin: FractalOrigin
    layer_trace: LayerTrace
    mode: RepresentationMode = RepresentationMode.NUMERIC
    format: RepresentationFormat = RepresentationFormat.TUPLE
    confidence_vector: tuple[float, ...] = ()
    sha256: str = ""

    def to_int_vector(self) -> tuple[int, ...]:
        """تحويل إلى متجه عددي — convert to an integer vector ∈ ℕⁿ (FCC-v1 §2).

        Returns a deterministic tuple of non-negative integers encoding the
        full representation.  The components are:

        ``(existence, function_mask, mode_value, format_value,
           layer_count, sha256_prefix_int)``
        """
        sha_prefix = int(self.sha256[:8], 16) if self.sha256 else 0
        return (
            self.origin.existence,
            self.origin.function_mask,
            self.mode.value,
            self.format.value,
            len(self.layer_trace.layers),
            sha_prefix,
        )


# ── FRS-v1 §5 — Validation ──────────────────────────────────────────


@dataclass(frozen=True)
class OriginValidationResult:
    """نتيجة التحقق من الأصل — result of validating a :class:`FractalOrigin`.

    Parameters
    ----------
    valid:
        ``True`` when all FCC-v1 §2 invariants hold for the origin.
    errors:
        Tuple of error descriptions (empty when valid).
    """

    valid: bool
    errors: tuple[str, ...] = ()


def validate_fractal_origin(origin: FractalOrigin) -> OriginValidationResult:
    """تحقق من صحة الأصل الفراكتالي — validate a :class:`FractalOrigin` (FRS-v1 §5).

    Invariants checked (FCC-v1 §2):

    1. ``existence`` is a non-negative integer (`E ∈ ℕ`).
    2. ``prior_knowledge_key`` is a non-empty string (`K ≠ ∅`).
    3. ``function_mask`` is a non-negative integer (`F ∈ ℕ`).
    4. ``initial_class`` is a non-empty string (`C ≠ ∅`).

    Parameters
    ----------
    origin:
        The origin tuple to validate.

    Returns
    -------
    OriginValidationResult
        ``valid=True`` when all invariants hold.
    """
    errors: list[str] = []

    if not isinstance(origin.existence, int) or origin.existence < 0:
        errors.append(
            f"E(u) must be a non-negative integer, got {origin.existence!r}"
        )
    if not isinstance(origin.prior_knowledge_key, str) or not origin.prior_knowledge_key:
        errors.append("K(u) must be a non-empty string")
    if not isinstance(origin.function_mask, int) or origin.function_mask < 0:
        errors.append(
            f"F(u) must be a non-negative integer, got {origin.function_mask!r}"
        )
    if not isinstance(origin.initial_class, str) or not origin.initial_class:
        errors.append("C(u) must be a non-empty string")

    return OriginValidationResult(valid=len(errors) == 0, errors=tuple(errors))


# ── FRS-v1 §6 — Builder ─────────────────────────────────────────────


def _compute_sha256(origin: FractalOrigin, layer_trace: LayerTrace) -> str:
    """Deterministic SHA-256 digest for (origin, layer_trace) (FRS-v1 §4)."""
    parts = [
        str(origin.existence),
        origin.prior_knowledge_key,
        str(origin.function_mask),
        origin.initial_class,
        "|".join(layer_trace.layers),
        layer_trace.final_layer,
        str(int(layer_trace.gate_passed)),
    ]
    raw = ":".join(parts).encode()
    return hashlib.sha256(raw).hexdigest()


def build_fractal_representation(
    element_id: str,
    origin: FractalOrigin,
    layer_trace: LayerTrace,
    *,
    mode: RepresentationMode = RepresentationMode.NUMERIC,
    format: RepresentationFormat = RepresentationFormat.TUPLE,
    confidence_vector: Sequence[float] = (),
) -> FractalRepresentation:
    """بناء سجل التمثيل الفراكتالي — construct a :class:`FractalRepresentation`.

    This is the primary factory function for the Fractal Representation Spec.
    It validates the origin, computes the SHA-256 digest, and returns an
    immutable :class:`FractalRepresentation`.

    Parameters
    ----------
    element_id:
        Unique identifier for the element (e.g. ``"U+0643"``).
    origin:
        The fractal origin `(E, K, F, C)` for this element.
    layer_trace:
        Ordered record of pipeline layers completed.
    mode:
        Representation mode; defaults to :attr:`RepresentationMode.NUMERIC`.
    format:
        Serialisation format; defaults to :attr:`RepresentationFormat.TUPLE`.
    confidence_vector:
        Optional sequence of per-layer confidence scores.

    Returns
    -------
    FractalRepresentation
        Complete, immutable representation record.

    Raises
    ------
    ValueError
        When the supplied ``origin`` fails FCC-v1 §2 invariant checks.
    """
    validation = validate_fractal_origin(origin)
    if not validation.valid:
        raise ValueError(
            "Invalid FractalOrigin (FCC-v1 §2): "
            + "; ".join(validation.errors)
        )

    sha = _compute_sha256(origin, layer_trace)

    return FractalRepresentation(
        element_id=element_id,
        origin=origin,
        layer_trace=layer_trace,
        mode=mode,
        format=format,
        confidence_vector=tuple(confidence_vector),
        sha256=sha,
    )
