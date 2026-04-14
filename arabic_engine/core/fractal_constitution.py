"""Fractal Core Constitution v1 — الدستور الفراكتالي الأصلي.

This module encodes the sovereignty invariants of the Fractal Core
Constitution (FCC-v1) as computable Python objects.  It provides:

* :class:`ConstitutionLayer` — the ten canonical pipeline layers.
* :class:`ConstitutionConstraint` — the six sovereignty constraints.
* :class:`DerivedSpec` — catalogue of derived specifications.
* :func:`validate_constitution` — runtime validation of the constitution.
* :class:`ConstitutionReport` — validation result.
* :class:`ConstitutionValidator` — callable validator.

The document this module implements is ``docs/fractal_core_constitution_v1.md``.

Reference
---------
FCC-v1 §6 states::

    ConstitutionValidator().validate()  # must return ConstitutionReport(valid=True)
"""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Sequence


# ── §4 — Layer registry ──────────────────────────────────────────────


class ConstitutionLayer(Enum):
    """الطبقات العشر الرسمية — ten canonical pipeline layers (FCC-v1 §4).

    Each layer name mirrors its :class:`~arabic_engine.core.enums.ActivationStage`
    counterpart.  The integer value encodes the strict ascending order.
    """

    SIGNAL = 0      # L0 — UnicodeAtom
    MORPHOLOGY = 1  # L1 — RootPattern
    PHONOLOGY = 2   # L2 — DMin ∈ ℕ⁵
    SYNTAX = 3      # L3 — SyntaxNode
    CONCEPT = 4     # L4 — Concept
    DALALA = 5      # L5 — DalalaLink
    JUDGEMENT = 6   # L6 — Proposition
    ANCHORING = 7   # L7 — TimeSpaceTag
    EVALUATION = 8  # L8 — EvalResult
    INFERENCE = 9   # L9 — InferenceResult


# ── §8 — Sovereignty constraints ────────────────────────────────────


class ConstitutionConstraint(Enum):
    """القيود السيادية الستة — six sovereignty constraints (FCC-v1 §8)."""

    SINGLE_FRACTAL_ORIGIN = auto()       # القيد 1 — وحدة الأصل
    KERNEL_14_CLOSED = auto()            # القيد 2 — انغلاق الكيرنل-14
    STRICT_LAYER_SEQUENCE = auto()       # القيد 3 — تسلسل الطبقات
    COMPUTATIONAL_DETERMINISM = auto()   # القيد 4 — الحتمية الحاسوبية
    NO_DUPLICATE_CONTENT = auto()        # القيد 5 — عدم التكرار
    SINGLE_REFERENCE_AUTHORITY = auto()  # القيد 6 — المرجعية الوحيدة


# ── §7 — Derived specification catalogue ────────────────────────────


@dataclass(frozen=True)
class DerivedSpec:
    """مواصفة مشتقة — a specification derived from FCC-v1 (§7).

    Parameters
    ----------
    code:
        Machine-readable identifier, e.g. ``"FRS-v1"``.
    title:
        Human-readable title.
    doc_path:
        Path to the documentation file relative to the project root.
    module:
        Importable Python module name implementing the spec.
    """

    code: str
    title: str
    doc_path: str
    module: str


DERIVED_SPECS: tuple[DerivedSpec, ...] = (
    DerivedSpec(
        code="FRS-v1",
        title="Fractal Representation Spec v1",
        doc_path="docs/fractal_representation_spec_v1.md",
        module="arabic_engine.representation.fractal_rep_spec",
    ),
    DerivedSpec(
        code="KS-v1",
        title="Kernel Schema v1 — Kernel-14",
        doc_path="docs/kernel_schema.md",
        module="arabic_engine.core.kernel",
    ),
    DerivedSpec(
        code="ABL-v1",
        title="Atomic Beginning Law v1",
        doc_path="docs/atomic_beginning_law.md",
        module="arabic_engine.core.laws",
    ),
    DerivedSpec(
        code="GCL-v1",
        title="General Closure — Chapter 19",
        doc_path="docs/chapter_19_general_closure.md",
        module="arabic_engine.closure",
    ),
    DerivedSpec(
        code="MFH-v1",
        title="Mafhum Types — Chapter 21",
        doc_path="docs/chapter_21_mafhum_types.md",
        module="arabic_engine.cognition.mafhum",
    ),
)


# ── Constitution validation ──────────────────────────────────────────


@dataclass(frozen=True)
class ConstitutionReport:
    """تقرير التحقق من الدستور — validation result for the constitution.

    Parameters
    ----------
    valid:
        ``True`` when all invariants hold.
    errors:
        Tuple of human-readable error descriptions (empty when valid).
    checked_layers:
        Tuple of layer names verified in ascending order.
    checked_specs:
        Tuple of derived-spec codes whose modules were importable.
    missing_specs:
        Tuple of derived-spec codes whose modules could not be imported.
    """

    valid: bool
    errors: tuple[str, ...] = ()
    checked_layers: tuple[str, ...] = ()
    checked_specs: tuple[str, ...] = ()
    missing_specs: tuple[str, ...] = ()


def _check_layer_order(layers: Sequence[ConstitutionLayer]) -> list[str]:
    """Verify layers are strictly ascending by value (FCC-v1 §8 constraint 3)."""
    errors: list[str] = []
    for i in range(1, len(layers)):
        if layers[i].value <= layers[i - 1].value:
            errors.append(
                f"Layer order violation: {layers[i - 1].name} "
                f"(={layers[i - 1].value}) must precede "
                f"{layers[i].name} (={layers[i].value})"
            )
    return errors


def _check_kernel_count() -> list[str]:
    """Verify the Kernel-14 label set is exactly 14 (FCC-v1 §8 constraint 2)."""
    errors: list[str] = []
    try:
        from arabic_engine.core.kernel import KernelLabel  # noqa: PLC0415
        count = len(KernelLabel)
        if count != 14:
            errors.append(
                f"Kernel label count must be exactly 14, got {count} "
                "(FCC-v1 §8 constraint 2)"
            )
    except ImportError as exc:
        errors.append(f"Cannot import KernelLabel: {exc}")
    return errors


def _check_derived_specs(
    specs: Sequence[DerivedSpec],
) -> tuple[list[str], list[str], list[str]]:
    """Return (errors, checked_codes, missing_codes) for each derived spec.

    Uses :func:`importlib.util.find_spec` to locate each module *without*
    importing it, so that no side-effects (e.g. submodule attribute
    registration on parent packages) are triggered.
    """
    errors: list[str] = []
    checked: list[str] = []
    missing: list[str] = []
    for spec in specs:
        try:
            found = importlib.util.find_spec(spec.module)
        except (ModuleNotFoundError, ValueError):
            found = None
        if found is not None:
            checked.append(spec.code)
        else:
            errors.append(
                f"Derived spec {spec.code!r} module {spec.module!r} "
                "could not be located"
            )
            missing.append(spec.code)
    return errors, checked, missing


def validate_constitution(
    *,
    specs: Sequence[DerivedSpec] = DERIVED_SPECS,
) -> ConstitutionReport:
    """التحقق من صحة الدستور الفراكتالي — validate the Fractal Core Constitution.

    Checks performed (FCC-v1 §12):

    1. Layer ordering is strictly ascending (§8 constraint 3).
    2. Kernel-14 label count is exactly 14 (§8 constraint 2).
    3. All derived-spec modules are importable (§12 acceptance criterion).

    Parameters
    ----------
    specs:
        Derived specifications to check; defaults to :data:`DERIVED_SPECS`.

    Returns
    -------
    ConstitutionReport
        ``valid=True`` when every check passes.
    """
    errors: list[str] = []
    all_layers = list(ConstitutionLayer)

    # Check 1: layer order
    errors.extend(_check_layer_order(all_layers))

    # Check 2: kernel-14 count
    errors.extend(_check_kernel_count())

    # Check 3: derived specs importable
    spec_errors, checked_codes, missing_codes = _check_derived_specs(specs)
    errors.extend(spec_errors)

    return ConstitutionReport(
        valid=len(errors) == 0,
        errors=tuple(errors),
        checked_layers=tuple(layer.name for layer in all_layers),
        checked_specs=tuple(checked_codes),
        missing_specs=tuple(missing_codes),
    )


class ConstitutionValidator:
    """Callable validator for the Fractal Core Constitution (FCC-v1 §6).

    Usage::

        from arabic_engine.core.fractal_constitution import ConstitutionValidator
        report = ConstitutionValidator().validate()
        assert report.valid

    Parameters
    ----------
    specs:
        Override the list of derived specifications to check.
        Defaults to :data:`DERIVED_SPECS`.
    """

    def __init__(
        self,
        specs: Sequence[DerivedSpec] | None = None,
    ) -> None:
        self._specs: Sequence[DerivedSpec] = specs if specs is not None else DERIVED_SPECS

    def validate(self) -> ConstitutionReport:
        """Run all constitution invariant checks and return a report."""
        return validate_constitution(specs=self._specs)
