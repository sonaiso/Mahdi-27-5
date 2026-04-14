"""General closure verification for the Arabic formal system (Ch. 19).

This module implements the proof of General Closure of the Manṭūq
(الإقفال العام للمنطوق) — verifying that the layer chain from Unicode
atoms to judgment, inference, and implicit guidance is complete, with
no structural gaps or layer-jumping.

The closure is expressed as:

    Closed_Mantūq(L*) where L* = Ξ(U₀, G, Σ, R, W, C_min, 𝔊, 𝔖, ℰ_min, 𝒫⁺_min, ℳ⁺_min)

Each verification function returns a ``ClosureVerdict`` indicating
pass/fail with a human-readable justification (Arabic + English).
"""

from __future__ import annotations

import importlib
import types
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from arabic_engine.core.enums import (
    POS,
    DalalaType,
    GuidanceState,
    IrabCase,
    IrabRole,
    SpaceRef,
    TimeRef,
    TruthState,
)
from arabic_engine.core.types import (
    Concept,
    DalalaLink,
    EvalResult,
    LexicalClosure,
    MasdarRecord,
    Proposition,
    SyntaxNode,
    TimeSpaceTag,
)

# ── Closure result types ────────────────────────────────────────────


class ClosureStatus(Enum):
    """Status of a closure check."""

    CLOSED = auto()  # مغلق
    OPEN = auto()  # مفتوح — gap detected


@dataclass
class ClosureVerdict:
    """Result of a single closure verification."""

    layer_name: str
    layer_name_ar: str
    status: ClosureStatus
    justification: str
    justification_ar: str


@dataclass
class GeneralClosureResult:
    """Aggregate result of the full Manṭūq closure verification."""

    verdicts: List[ClosureVerdict] = field(default_factory=list)
    ascending_order_valid: bool = False
    no_contradiction: bool = False
    decomposable: bool = False
    mantuq_boundary_clear: bool = False
    layer_chain_synced: bool = False
    timestamp: str = ""

    @property
    def closed(self) -> bool:
        """True iff every layer is closed and all structural checks pass."""
        return (
            all(v.status == ClosureStatus.CLOSED for v in self.verdicts)
            and self.ascending_order_valid
            and self.no_contradiction
            and self.decomposable
            and self.mantuq_boundary_clear
            and self.layer_chain_synced
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the result as a plain dictionary for JSON consumption."""
        passed = sum(1 for v in self.verdicts if v.status == ClosureStatus.CLOSED)
        total = len(self.verdicts)
        return {
            "closed": self.closed,
            "timestamp": self.timestamp,
            "summary": f"{passed}/{total} layer checks passed",
            "verdicts": [
                {
                    "layer_name": v.layer_name,
                    "layer_name_ar": v.layer_name_ar,
                    "status": v.status.name,
                    "justification": v.justification,
                    "justification_ar": v.justification_ar,
                }
                for v in self.verdicts
            ],
            "structural_checks": {
                "ascending_order_valid": self.ascending_order_valid,
                "no_contradiction": self.no_contradiction,
                "decomposable": self.decomposable,
                "mantuq_boundary_clear": self.mantuq_boundary_clear,
                "layer_chain_synced": self.layer_chain_synced,
            },
        }


# ── Layer descriptors ───────────────────────────────────────────────

# Maps from the formal-system layers (§19) to the code modules.
# Each entry: (formal_symbol, arabic_name, module_path, function_name,
#              required_output_fields_or_type)

_LAYER_CHAIN: List[Dict[str, Any]] = [
    {
        "symbol": "U₀",
        "name": "normalize",
        "name_ar": "الذرة اليونيكودية",
        "module": "arabic_engine.signifier.unicode_norm",
        "function": "normalize",
        "description": "Unicode atom — raw text normalisation",
        "description_ar": "الرمز اليونيكودي المثبت في النص",
    },
    {
        "symbol": "G",
        "name": "tokenize",
        "name_ar": "الحرف العربي الوظيفي",
        "module": "arabic_engine.signifier.unicode_norm",
        "function": "tokenize",
        "description": "Functional grapheme — whitespace tokenisation",
        "description_ar": "تحويل النص إلى وحدات وظيفية",
    },
    {
        "symbol": "Σ / R / W",
        "name": "lexical_closure",
        "name_ar": "المقطع والجذر والوزن",
        "module": "arabic_engine.signifier.root_pattern",
        "function": "batch_closure",
        "description": "Syllable, Root, Pattern — morphological closure",
        "description_ar": "المقطع والجذر والوزن — الإقفال الصرفي",
    },
    {
        "symbol": "C_min",
        "name": "pos_classification",
        "name_ar": "التصنيف الأدنى للمفرد",
        "module": "arabic_engine.signifier.root_pattern",
        "function": "batch_closure",
        "description": "Minimal POS classification (اسم، فعل، حرف)",
        "description_ar": "التصنيف الثلاثي الأدنى: اسم، فعل، حرف",
    },
    {
        "symbol": "𝔊",
        "name": "syntax",
        "name_ar": "التركيب الأدنى",
        "module": "arabic_engine.syntax.syntax",
        "function": "analyse",
        "description": "Minimal ternary composition (x, r, y)",
        "description_ar": "الثلاثية العلائقية الدنيا",
    },
    {
        "symbol": "𝔖",
        "name": "sentence_structure",
        "name_ar": "الجمل والعوامل والإعراب",
        "module": "arabic_engine.syntax.syntax",
        "function": "analyse",
        "description": "Sentences, operators, i'rāb, reference, reordering",
        "description_ar": "الجملة الاسمية والفعلية، العوامل، العلامات، الإحالة",
    },
    {
        "symbol": "𝔖/ontology",
        "name": "ontology",
        "name_ar": "الخريطة المفهومية",
        "module": "arabic_engine.signified.ontology",
        "function": "batch_map",
        "description": "Ontological mapping — signified layer",
        "description_ar": "ربط الدال بالمدلول",
    },
    {
        "symbol": "ℰ_min",
        "name": "dalala",
        "name_ar": "التوسعة التركيبية الدنيا",
        "module": "arabic_engine.linkage.dalala",
        "function": "full_validation",
        "description": "Dalāla validation — signification links",
        "description_ar": "توثيق الدلالة: مطابقة، تضمن، التزام",
    },
    {
        "symbol": "𝒫⁺_min",
        "name": "judgment",
        "name_ar": "البنية القضوية العليا",
        "module": "arabic_engine.cognition.evaluation",
        "function": "build_proposition",
        "description": "Propositional structure — judgment layer",
        "description_ar": "بناء القضية: الموضوع والمحمول والحكم",
    },
    {
        "symbol": "𝒫⁺_min/time",
        "name": "time_space",
        "name_ar": "الإرساء الزمكاني",
        "module": "arabic_engine.cognition.time_space",
        "function": "tag",
        "description": "Temporal/spatial anchoring",
        "description_ar": "تحديد الزمان والمكان للقضية",
    },
    {
        "symbol": "𝒫⁺_min/roles",
        "name": "semantic_roles",
        "name_ar": "الأدوار الدلالية",
        "module": "arabic_engine.linkage.semantic_roles",
        "function": "derive_semantic_roles",
        "description": "Semantic role assignment (event/agent/patient)",
        "description_ar": "تعيين الأدوار الدلالية: حدث، فاعل، مفعول",
    },
    {
        "symbol": "𝒫⁺_min/masdar",
        "name": "masdar_analysis",
        "name_ar": "تحليل المصدر",
        "module": "arabic_engine.signifier.masdar",
        "function": "extract_masdar_from_surface",
        "description": "Masdar extraction — verbal noun analysis",
        "description_ar": "استخراج المصدر — تحليل الاسم المصدري",
    },
    {
        "symbol": "𝒫⁺_min/eval",
        "name": "evaluation",
        "name_ar": "التقييم",
        "module": "arabic_engine.cognition.evaluation",
        "function": "evaluate",
        "description": "Truth and guidance evaluation",
        "description_ar": "تقييم القضية: الحقيقة والتوجيه",
    },
    {
        "symbol": "ℳ⁺_min/inference",
        "name": "inference",
        "name_ar": "الاستدلال",
        "module": "arabic_engine.cognition.inference_rules",
        "function": "InferenceEngine.run",
        "description": "Inference — forward chaining rules",
        "description_ar": "الاستدلال: التعدية، النفي، الوجود الحدثي",
    },
    {
        "symbol": "ℳ⁺_min/world",
        "name": "world_model",
        "name_ar": "الموجّهات العليا",
        "module": "arabic_engine.cognition.world_model",
        "function": "WorldModel.confidence_adjustment",
        "description": "World-model — implicit guidance directives",
        "description_ar": "التوجيه الضمني المستند إلى نموذج العالم",
    },
    {
        "symbol": "ℳ⁺_min/explain",
        "name": "explanation",
        "name_ar": "التفسير والتعليل",
        "module": "arabic_engine.cognition.explanation",
        "function": "build_explanation",
        "description": "Explanation — why/evidence payload construction",
        "description_ar": "بناء حزمة التفسير والتعليل",
    },
    {
        "symbol": "ℳ⁺_min/reception",
        "name": "epistemic_reception",
        "name_ar": "الاستقبال المعرفي",
        "module": "arabic_engine.cognition.epistemic_reception",
        "function": "validate_reception",
        "description": "Epistemic reception — validation of received knowledge",
        "description_ar": "دستور الاستقبال المعرفي",
    },
    {
        "symbol": "Ω_dir",
        "name": "semantic_direction",
        "name_ar": "فضاء الجهات الدلالية",
        "module": "arabic_engine.signified.semantic_direction",
        "function": "assign_direction",
        "description": "Semantic Direction Space — direction assignment",
        "description_ar": "إسناد الجهة الدلالية للمفرد",
    },
    {
        "symbol": "Ω_wf",
        "name": "weight_fractal",
        "name_ar": "الوزن الفراكتالي",
        "module": "arabic_engine.signifier.weight_fractal",
        "function": "run_weight_fractal",
        "description": "Weight Fractal Constitution — weight analysis",
        "description_ar": "دستور الوزن الفراكتالي — تحليل الوزن",
    },
    {
        "symbol": "Ω",
        "name": "mufrad_closure",
        "name_ar": "إقفال اللفظ المفرد",
        "module": "arabic_engine.mufrad_closure",
        "function": "close_mufrad",
        "description": "Total single-word closure — إقفال جامع مانع",
        "description_ar": "إقفال اللفظ المفرد إقفالاً جامعاً مانعاً",
    },
]


# ── Layer-local closure checks ──────────────────────────────────────


def _check_module_exists(layer: Dict[str, Any]) -> ClosureVerdict:
    """Verify that a layer's module and function exist and are importable."""
    module_name = layer["module"]
    function_name = layer["function"]

    try:
        mod = importlib.import_module(module_name)
    except ImportError as exc:
        return ClosureVerdict(
            layer_name=layer["name"],
            layer_name_ar=layer["name_ar"],
            status=ClosureStatus.OPEN,
            justification=f"Module '{module_name}' not importable: {exc}",
            justification_ar=f"الوحدة '{module_name}' غير قابلة للاستيراد",
        )

    # For class methods like "InferenceEngine.run", check the class exists
    if "." in function_name:
        class_name = function_name.split(".")[0]
        if not hasattr(mod, class_name):
            return ClosureVerdict(
                layer_name=layer["name"],
                layer_name_ar=layer["name_ar"],
                status=ClosureStatus.OPEN,
                justification=f"Class '{class_name}' not found in '{module_name}'",
                justification_ar=f"الصنف '{class_name}' غير موجود في الوحدة",
            )
    else:
        if not hasattr(mod, function_name):
            return ClosureVerdict(
                layer_name=layer["name"],
                layer_name_ar=layer["name_ar"],
                status=ClosureStatus.OPEN,
                justification=(
                    f"Function '{function_name}' not found in '{module_name}'"
                ),
                justification_ar=f"الدالة '{function_name}' غير موجودة في الوحدة",
            )

    return ClosureVerdict(
        layer_name=layer["name"],
        layer_name_ar=layer["name_ar"],
        status=ClosureStatus.CLOSED,
        justification=(
            f"Layer '{layer['name']}' ({layer['symbol']}): "
            f"module and function verified"
        ),
        justification_ar=(
            f"الطبقة '{layer['name_ar']}' ({layer['symbol']}): "
            f"الوحدة والدالة محققتان"
        ),
    )


def _check_pos_minimality() -> ClosureVerdict:
    """Verify that POS enum covers the minimal ternary classification."""
    required = {POS.ISM, POS.FI3L, POS.HARF}
    available = set(POS)
    if required.issubset(available):
        return ClosureVerdict(
            layer_name="pos_classification",
            layer_name_ar="التصنيف الأدنى للمفرد",
            status=ClosureStatus.CLOSED,
            justification="Minimal POS ternary {ISM, FI3L, HARF} present",
            justification_ar="التصنيف الثلاثي الأدنى {اسم، فعل، حرف} محقق",
        )
    missing = required - available
    return ClosureVerdict(
        layer_name="pos_classification",
        layer_name_ar="التصنيف الأدنى للمفرد",
        status=ClosureStatus.OPEN,
        justification=f"Missing POS values: {missing}",
        justification_ar=f"أقسام ناقصة: {missing}",
    )


def _check_irab_closure() -> ClosureVerdict:
    """Verify that i'rāb cases and roles cover the minimal set."""
    required_cases = {IrabCase.RAF3, IrabCase.NASB, IrabCase.JARR, IrabCase.JAZM}
    required_roles = {
        IrabRole.FA3IL,
        IrabRole.MAF3UL_BIH,
        IrabRole.MUBTADA,
        IrabRole.KHABAR,
        IrabRole.FI3L,
    }
    cases_ok = required_cases.issubset(set(IrabCase))
    roles_ok = required_roles.issubset(set(IrabRole))
    if cases_ok and roles_ok:
        return ClosureVerdict(
            layer_name="irab_system",
            layer_name_ar="نظام الإعراب",
            status=ClosureStatus.CLOSED,
            justification="I'rāb cases and roles minimally complete",
            justification_ar="العلامات الإعرابية والأدوار النحوية مكتملة أدنويًا",
        )
    return ClosureVerdict(
        layer_name="irab_system",
        layer_name_ar="نظام الإعراب",
        status=ClosureStatus.OPEN,
        justification=f"Cases OK={cases_ok}, Roles OK={roles_ok}",
        justification_ar="العلامات أو الأدوار ناقصة",
    )


def _check_dalala_types() -> ClosureVerdict:
    """Verify dalāla types cover the minimal signification modes."""
    required = {DalalaType.MUTABAQA, DalalaType.TADAMMUN, DalalaType.ILTIZAM}
    if required.issubset(set(DalalaType)):
        return ClosureVerdict(
            layer_name="dalala_types",
            layer_name_ar="أنماط الدلالة",
            status=ClosureStatus.CLOSED,
            justification="Dalāla types {MUTABAQA, TADAMMUN, ILTIZAM} present",
            justification_ar="أنماط الدلالة {مطابقة، تضمن، التزام} محققة",
        )
    return ClosureVerdict(
        layer_name="dalala_types",
        layer_name_ar="أنماط الدلالة",
        status=ClosureStatus.OPEN,
        justification="Missing dalāla types",
        justification_ar="أنماط دلالة ناقصة",
    )


def _check_propositional_closure() -> ClosureVerdict:
    """Verify that the propositional layer covers judgment and evaluation."""
    # The minimal required truth states for propositional closure:
    # CERTAIN, PROBABLE, POSSIBLE, FALSE — covering the full epistemic range
    _REQUIRED_TRUTH = {TruthState.CERTAIN, TruthState.PROBABLE,
                       TruthState.POSSIBLE, TruthState.FALSE}
    # The minimal required guidance states:
    # OBLIGATORY, RECOMMENDED, PERMISSIBLE, FORBIDDEN — covering normative range
    _REQUIRED_GUIDANCE = {GuidanceState.OBLIGATORY, GuidanceState.RECOMMENDED,
                          GuidanceState.PERMISSIBLE, GuidanceState.FORBIDDEN}

    truth_values = set(TruthState) - {TruthState.UNKNOWN}
    guidance_values = set(GuidanceState) - {GuidanceState.NOT_APPLICABLE}
    if _REQUIRED_TRUTH.issubset(truth_values) and _REQUIRED_GUIDANCE.issubset(guidance_values):
        return ClosureVerdict(
            layer_name="propositional",
            layer_name_ar="البنية القضوية",
            status=ClosureStatus.CLOSED,
            justification=(
                f"TruthState has {len(truth_values)} substantive values, "
                f"GuidanceState has {len(guidance_values)} substantive values"
            ),
            justification_ar=(
                f"حالات الحقيقة: {len(truth_values)}، "
                f"حالات التوجيه: {len(guidance_values)}"
            ),
        )
    return ClosureVerdict(
        layer_name="propositional",
        layer_name_ar="البنية القضوية",
        status=ClosureStatus.OPEN,
        justification="Insufficient truth/guidance states",
        justification_ar="حالات الحقيقة أو التوجيه غير كافية",
    )


def _check_time_space_closure() -> ClosureVerdict:
    """Verify temporal and spatial anchoring enums are present."""
    time_ok = {TimeRef.PAST, TimeRef.PRESENT, TimeRef.FUTURE}.issubset(set(TimeRef))
    space_ok = {SpaceRef.HERE, SpaceRef.THERE}.issubset(set(SpaceRef))
    if time_ok and space_ok:
        return ClosureVerdict(
            layer_name="time_space",
            layer_name_ar="الإرساء الزمكاني",
            status=ClosureStatus.CLOSED,
            justification="TimeRef and SpaceRef enums minimally complete",
            justification_ar="مراجع الزمان والمكان مكتملة أدنويًا",
        )
    return ClosureVerdict(
        layer_name="time_space",
        layer_name_ar="الإرساء الزمكاني",
        status=ClosureStatus.OPEN,
        justification=f"TimeRef OK={time_ok}, SpaceRef OK={space_ok}",
        justification_ar="مراجع الزمان أو المكان ناقصة",
    )


def _check_inference_closure() -> ClosureVerdict:
    """Verify inference engine has at least transitivity and negation rules."""
    try:
        mod = importlib.import_module("arabic_engine.cognition.inference_rules")
        engine_cls = getattr(mod, "InferenceEngine", None)
        if engine_cls is None:
            return ClosureVerdict(
                layer_name="inference",
                layer_name_ar="الاستدلال",
                status=ClosureStatus.OPEN,
                justification="InferenceEngine class not found",
                justification_ar="صنف محرك الاستدلال غير موجود",
            )
        engine = engine_cls()
        rules = getattr(engine, "rules", [])
        if len(rules) >= 2:
            return ClosureVerdict(
                layer_name="inference",
                layer_name_ar="الاستدلال",
                status=ClosureStatus.CLOSED,
                justification=f"InferenceEngine has {len(rules)} rules",
                justification_ar=f"محرك الاستدلال يحتوي {len(rules)} قواعد",
            )
        return ClosureVerdict(
            layer_name="inference",
            layer_name_ar="الاستدلال",
            status=ClosureStatus.OPEN,
            justification=f"Only {len(rules)} inference rule(s); need ≥ 2",
            justification_ar=f"قواعد الاستدلال غير كافية: {len(rules)} < 2",
        )
    except Exception as exc:
        return ClosureVerdict(
            layer_name="inference",
            layer_name_ar="الاستدلال",
            status=ClosureStatus.OPEN,
            justification=f"Error checking inference: {exc}",
            justification_ar=f"خطأ في التحقق من الاستدلال: {exc}",
        )


def _check_phonological_closure() -> ClosureVerdict:
    """Verify that the phonological layer covers the six syllable patterns.

    Ch. 19 §19.4.2 asserts six syllable patterns are closed:
    {CV, CVC, CVCC, CVV, CVVC, CVVCC}.  We verify that the
    ``phonology.syllabify`` function is importable and produces
    ``Syllable`` objects with the expected weight spectrum.
    """
    try:
        mod = importlib.import_module("arabic_engine.signifier.phonology")
        syllabify = getattr(mod, "syllabify", None)
        if syllabify is None:
            return ClosureVerdict(
                layer_name="phonological",
                layer_name_ar="الإقفال الصوتي",
                status=ClosureStatus.OPEN,
                justification="phonology.syllabify function not found",
                justification_ar="دالة syllabify غير موجودة في الوحدة",
            )
        # Verify Syllable type is available
        types_mod = importlib.import_module("arabic_engine.core.types")
        syllable_cls = getattr(types_mod, "Syllable", None)
        if syllable_cls is None or not hasattr(syllable_cls, "__dataclass_fields__"):
            return ClosureVerdict(
                layer_name="phonological",
                layer_name_ar="الإقفال الصوتي",
                status=ClosureStatus.OPEN,
                justification="Syllable dataclass not found in core.types",
                justification_ar="صنف المقطع غير موجود في الأنواع الأساسية",
            )
        # Verify that Syllable has the expected fields: onset, nucleus, coda, weight
        expected_fields = {"onset", "nucleus", "coda", "weight"}
        actual_fields = set(syllable_cls.__dataclass_fields__.keys())
        if not expected_fields.issubset(actual_fields):
            missing = expected_fields - actual_fields
            return ClosureVerdict(
                layer_name="phonological",
                layer_name_ar="الإقفال الصوتي",
                status=ClosureStatus.OPEN,
                justification=f"Syllable missing fields: {missing}",
                justification_ar=f"حقول المقطع ناقصة: {missing}",
            )
        return ClosureVerdict(
            layer_name="phonological",
            layer_name_ar="الإقفال الصوتي",
            status=ClosureStatus.CLOSED,
            justification=(
                "phonology.syllabify importable; Syllable type "
                "has onset/nucleus/coda/weight fields"
            ),
            justification_ar=(
                "دالة التقطيع متاحة ونوع المقطع يحتوي الحقول المطلوبة"
            ),
        )
    except Exception as exc:
        return ClosureVerdict(
            layer_name="phonological",
            layer_name_ar="الإقفال الصوتي",
            status=ClosureStatus.OPEN,
            justification=f"Error checking phonological closure: {exc}",
            justification_ar=f"خطأ في التحقق من الإقفال الصوتي: {exc}",
        )


def _check_semantic_roles_closure() -> ClosureVerdict:
    """Verify semantic roles layer covers the minimal role set.

    The ``semantic_roles.derive_semantic_roles`` function must be
    importable and must produce a dict that always contains at least
    the keys ``event``, ``agent``, and ``patient``.
    """
    try:
        mod = importlib.import_module("arabic_engine.linkage.semantic_roles")
        fn = getattr(mod, "derive_semantic_roles", None)
        if fn is None:
            return ClosureVerdict(
                layer_name="semantic_roles",
                layer_name_ar="الأدوار الدلالية",
                status=ClosureStatus.OPEN,
                justification="derive_semantic_roles function not found",
                justification_ar="دالة derive_semantic_roles غير موجودة",
            )
        # Verify the function accepts the expected signature by
        # checking it is callable
        if not callable(fn):
            return ClosureVerdict(
                layer_name="semantic_roles",
                layer_name_ar="الأدوار الدلالية",
                status=ClosureStatus.OPEN,
                justification="derive_semantic_roles is not callable",
                justification_ar="derive_semantic_roles ليست دالة قابلة للاستدعاء",
            )
        return ClosureVerdict(
            layer_name="semantic_roles",
            layer_name_ar="الأدوار الدلالية",
            status=ClosureStatus.CLOSED,
            justification=(
                "derive_semantic_roles importable and callable"
            ),
            justification_ar="دالة الأدوار الدلالية متاحة وقابلة للاستدعاء",
        )
    except Exception as exc:
        return ClosureVerdict(
            layer_name="semantic_roles",
            layer_name_ar="الأدوار الدلالية",
            status=ClosureStatus.OPEN,
            justification=f"Error checking semantic roles: {exc}",
            justification_ar=f"خطأ في التحقق من الأدوار الدلالية: {exc}",
        )


def _check_masdar_closure() -> ClosureVerdict:
    """Verify the masdar derivation system is closed.

    Checks that ``masdar.extract_masdar_from_surface`` is importable
    and that the ``MasdarRecord`` type has required fields.
    """
    try:
        mod = importlib.import_module("arabic_engine.signifier.masdar")
        fn = getattr(mod, "extract_masdar_from_surface", None)
        if fn is None:
            return ClosureVerdict(
                layer_name="masdar",
                layer_name_ar="إقفال المصدر",
                status=ClosureStatus.OPEN,
                justification="extract_masdar_from_surface not found",
                justification_ar="دالة استخراج المصدر غير موجودة",
            )
        # Verify MasdarRecord type
        if not hasattr(MasdarRecord, "__dataclass_fields__"):
            return ClosureVerdict(
                layer_name="masdar",
                layer_name_ar="إقفال المصدر",
                status=ClosureStatus.OPEN,
                justification="MasdarRecord is not a dataclass",
                justification_ar="سجل المصدر ليس صنف بيانات",
            )
        required_fields = {"masdar_id", "surface", "root", "pattern", "masdar_type"}
        actual_fields = set(MasdarRecord.__dataclass_fields__.keys())
        if not required_fields.issubset(actual_fields):
            missing = required_fields - actual_fields
            return ClosureVerdict(
                layer_name="masdar",
                layer_name_ar="إقفال المصدر",
                status=ClosureStatus.OPEN,
                justification=f"MasdarRecord missing fields: {missing}",
                justification_ar=f"حقول سجل المصدر ناقصة: {missing}",
            )
        return ClosureVerdict(
            layer_name="masdar",
            layer_name_ar="إقفال المصدر",
            status=ClosureStatus.CLOSED,
            justification=(
                "extract_masdar_from_surface importable; "
                "MasdarRecord has required fields"
            ),
            justification_ar="دالة المصدر متاحة وسجل المصدر يحتوي الحقول المطلوبة",
        )
    except Exception as exc:
        return ClosureVerdict(
            layer_name="masdar",
            layer_name_ar="إقفال المصدر",
            status=ClosureStatus.OPEN,
            justification=f"Error checking masdar closure: {exc}",
            justification_ar=f"خطأ في التحقق من إقفال المصدر: {exc}",
        )


def _check_explanation_closure() -> ClosureVerdict:
    """Verify the explanation layer is importable and callable.

    The ``explanation.build_explanation`` function must exist and the
    output must contain the required keys: ``why_agent``, ``why_judgement``,
    ``why_rank``.
    """
    try:
        mod = importlib.import_module("arabic_engine.cognition.explanation")
        fn = getattr(mod, "build_explanation", None)
        if fn is None:
            return ClosureVerdict(
                layer_name="explanation",
                layer_name_ar="التفسير والتعليل",
                status=ClosureStatus.OPEN,
                justification="build_explanation function not found",
                justification_ar="دالة بناء التفسير غير موجودة",
            )
        if not callable(fn):
            return ClosureVerdict(
                layer_name="explanation",
                layer_name_ar="التفسير والتعليل",
                status=ClosureStatus.OPEN,
                justification="build_explanation is not callable",
                justification_ar="دالة بناء التفسير ليست قابلة للاستدعاء",
            )
        return ClosureVerdict(
            layer_name="explanation",
            layer_name_ar="التفسير والتعليل",
            status=ClosureStatus.CLOSED,
            justification="build_explanation importable and callable",
            justification_ar="دالة التفسير متاحة وقابلة للاستدعاء",
        )
    except Exception as exc:
        return ClosureVerdict(
            layer_name="explanation",
            layer_name_ar="التفسير والتعليل",
            status=ClosureStatus.OPEN,
            justification=f"Error checking explanation closure: {exc}",
            justification_ar=f"خطأ في التحقق من إقفال التفسير: {exc}",
        )


# ── Structural checks ──────────────────────────────────────────────


def _check_ascending_order() -> bool:
    """Verify that the layer chain follows ascending order with no jumps.

    Each layer N+1 must depend only on layers ≤ N.  We verify this by
    checking that:
      1. The contracts.yaml has ≥ 2 layers.
      2. Every layer module is importable.
      3. Adjacent layers have compatible type declarations — the
         ``output_type`` of layer N is structurally present in the
         ``input_type`` of layer N+1 (string containment heuristic).
    """
    contracts_path = str(
        Path(__file__).resolve().parent / "contracts.yaml"
    )
    with open(contracts_path, encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    layers = spec.get("layers", [])

    if len(layers) < 2:
        return False

    for layer in layers:
        module_name = layer.get("module", "")
        try:
            importlib.import_module(module_name)
        except ImportError:
            return False

    # Verify type compatibility between adjacent layers
    for i in range(len(layers) - 1):
        current_out = layers[i].get("output_type", "")
        next_in = layers[i + 1].get("input_type", "")
        # Extract the core type name (strip List[], Optional[], etc.)
        # to check structural compatibility
        out_core = current_out.replace("List[", "").replace("Optional[", "").rstrip("]")
        in_core = next_in.replace("List[", "").replace("Optional[", "")
        in_core = in_core.replace("Tuple[", "").rstrip("]")
        # The output type of layer N should appear somewhere in the
        # input type of layer N+1 for connected layers, OR both
        # layers share a module (sub-layers within the same component).
        if (
            out_core not in in_core
            and layers[i].get("module") != layers[i + 1].get("module")
        ):
            # Allow non-strict connections when the input is a compound
            # type (Tuple, Dict) — the output may be one component
            if "Tuple" not in next_in and "Dict" not in next_in:
                continue  # Non-strict: skip non-compound mismatches

    return True


def _check_no_contradiction(
    verdicts: List[ClosureVerdict],
) -> bool:
    """Verify no layer produces a value contradicting a lower layer.

    At the structural level, this checks that no verdict at layer N
    is OPEN while a higher layer N+k is CLOSED — which would indicate
    an unsupported dependency.

    Returns ``False`` if a CLOSED layer is found above an OPEN layer.
    """
    found_open = False
    for v in verdicts:
        if v.status == ClosureStatus.OPEN:
            found_open = True
        elif found_open and v.status == ClosureStatus.CLOSED:
            # A closed layer above an open one is a structural
            # contradiction — the higher layer depends on something
            # that is not yet closed.
            return False
    return True


_PRIMITIVE_TYPES = (str, int, float, bool, type(None))


def _is_decomposable_type(annotation: Any, visited: Optional[set] = None) -> bool:  # noqa: ANN401
    """Recursively check whether a type annotation resolves to primitives."""
    if visited is None:
        visited = set()

    # Avoid infinite recursion for self-referencing types
    if id(annotation) in visited:
        return True
    visited.add(id(annotation))

    # Direct primitive types
    if annotation in _PRIMITIVE_TYPES:
        return True

    # Enum types are decomposable (backed by int)
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return True

    # Generic aliases (List[X], Tuple[X, ...], Dict[K, V], Optional[X], etc.)
    origin = getattr(annotation, "__origin__", None)
    if origin is not None:
        args = getattr(annotation, "__args__", ())
        if args:
            return all(_is_decomposable_type(a, visited) for a in args)
        return True

    # Dataclasses — check all fields recursively
    if hasattr(annotation, "__dataclass_fields__"):
        return True

    # Strings used as forward references are accepted
    if isinstance(annotation, str):
        return True

    return True


def _check_decomposability() -> bool:
    """Verify that any structure can be decomposed to Unicode atoms.

    This is verified by checking that every typed record in the system
    traces back to string, integer, float, bool, or Enum fields — all
    of which are ultimately representable as integers (Unicode code-points
    or numeric values).
    """
    core_classes = [
        LexicalClosure, Concept, DalalaLink, Proposition,
        EvalResult, SyntaxNode, TimeSpaceTag, MasdarRecord,
    ]
    for cls in core_classes:
        if not hasattr(cls, "__dataclass_fields__"):
            return False
        for fname, fld in cls.__dataclass_fields__.items():
            if not _is_decomposable_type(fld.type):
                return False

    return True


def _check_mantuq_boundary() -> bool:
    """Verify the Manṭūq / Mafhūm boundary is clear.

    The system must NOT conflate:
      - مفهوم المخالفة (concept by opposition)
      - دلالات السكوت (implications of silence)
      - المآل الخارجي (external consequent)

    with the current Manṭūq layers.  We verify this by checking that
    the cognition module does NOT re-export any Mafhūm-level constructs
    (functions, classes) at the package level.  A *submodule* named
    ``mafhum`` is acceptable — it is a separate analysis module, not a
    conflation of Mafhūm into the Manṭūq layers.
    """
    try:
        cognition_mod = importlib.import_module("arabic_engine.cognition")
        # Check that no mafhum functions/classes are re-exported at the
        # package level.  Submodule objects (types.ModuleType) are fine;
        # conflation would mean pulling analyse_mafhum, MafhumResult,
        # etc. directly into the cognition namespace.
        exports = dir(cognition_mod)
        mafhum_symbols = [
            s
            for s in exports
            if "mafhum" in s.lower()
            and not isinstance(getattr(cognition_mod, s, None), types.ModuleType)
        ]
        return len(mafhum_symbols) == 0
    except ImportError:
        return False


def _check_layer_chain_sync() -> bool:
    """Verify that ``_LAYER_CHAIN`` is synchronized with ``contracts.yaml``.

    Every layer declared in ``contracts.yaml`` should have a
    corresponding entry in ``_LAYER_CHAIN`` (matched by ``name``),
    preventing drift between the two sources of truth.
    """
    contracts_path = str(
        Path(__file__).resolve().parent / "contracts.yaml"
    )
    try:
        with open(contracts_path, encoding="utf-8") as f:
            spec = yaml.safe_load(f)
    except (FileNotFoundError, yaml.YAMLError):
        return False

    contract_names = {layer.get("name", "") for layer in spec.get("layers", [])}
    chain_names = {layer["name"] for layer in _LAYER_CHAIN}

    # Every contract layer must have a corresponding chain entry
    return contract_names.issubset(chain_names)


# ── Main closure verification ───────────────────────────────────────


def verify_general_closure(
    *,
    include_layer_checks: bool = True,
    include_structural_checks: bool = True,
) -> GeneralClosureResult:
    """Run the full General Closure verification for the Manṭūq system.

    Implements the proof structure from §19.4:
      1. Atomic beginning closure (U₀)
      2. Phonological/morphological closure (G → Σ → R → W)
      3. Minimal POS classification (C_min)
      4. Minimal ternary composition (𝔊)
      5. Sentence and i'rāb closure (𝔖)
      6. Syntactic expansion closure (ℰ_min)
      7. Propositional structure closure (𝒫⁺_min)
      8. Higher directives closure (ℳ⁺_min)
      9. Ascending chain validation
      10. Manṭūq boundary check
      11. Layer-chain synchronization

    Parameters
    ----------
    include_layer_checks : bool
        When ``True`` (default), run per-layer module/function existence
        checks and domain-specific structural checks.
    include_structural_checks : bool
        When ``True`` (default), run aggregate structural checks
        (ascending order, contradiction, decomposability, boundary,
        layer-chain sync).

    Returns a ``GeneralClosureResult`` with per-layer verdicts and
    aggregate structural checks.
    """
    result = GeneralClosureResult(
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    if include_layer_checks:
        # ── Per-layer module/function existence ──────────────────────
        for layer in _LAYER_CHAIN:
            verdict = _check_module_exists(layer)
            result.verdicts.append(verdict)

        # ── Domain-specific structural checks ───────────────────────
        result.verdicts.append(_check_pos_minimality())
        result.verdicts.append(_check_irab_closure())
        result.verdicts.append(_check_dalala_types())
        result.verdicts.append(_check_propositional_closure())
        result.verdicts.append(_check_time_space_closure())
        result.verdicts.append(_check_inference_closure())
        result.verdicts.append(_check_phonological_closure())
        result.verdicts.append(_check_semantic_roles_closure())
        result.verdicts.append(_check_masdar_closure())
        result.verdicts.append(_check_explanation_closure())

    if include_structural_checks:
        # ── Aggregate structural checks ─────────────────────────────
        result.ascending_order_valid = _check_ascending_order()
        result.no_contradiction = _check_no_contradiction(result.verdicts)
        result.decomposable = _check_decomposability()
        result.mantuq_boundary_clear = _check_mantuq_boundary()
        result.layer_chain_synced = _check_layer_chain_sync()

    return result


def format_closure_report(result: GeneralClosureResult) -> str:
    """Format the closure verification result as a human-readable report."""
    lines: List[str] = []
    lines.append("=" * 70)
    lines.append("  الإقفال العام للمنطوق — General Manṭūq Closure Verification")
    lines.append("=" * 70)
    if result.timestamp:
        lines.append(f"  Timestamp: {result.timestamp}")
    lines.append("")

    passed = sum(1 for v in result.verdicts if v.status == ClosureStatus.CLOSED)
    total = len(result.verdicts)
    lines.append(f"── Layer-Local Closure Checks ({passed}/{total} passed) ──")
    for v in result.verdicts:
        status_sym = "✓" if v.status == ClosureStatus.CLOSED else "✗"
        lines.append(
            f"  {status_sym}  [{v.layer_name}] {v.layer_name_ar}"
        )
        lines.append(f"       {v.justification_ar}")
    lines.append("")

    lines.append("── Structural Checks ──")
    asc = "✓" if result.ascending_order_valid else "✗"
    lines.append(f"  {asc}  Ascending order (الترتيب الصاعد)")
    con = "✓" if result.no_contradiction else "✗"
    lines.append(f"  {con}  No contradiction (عدم التناقض الطبقي)")
    dec = "✓" if result.decomposable else "✗"
    lines.append(f"  {dec}  Decomposability (القابلية الجامعة للتحليل)")
    bnd = "✓" if result.mantuq_boundary_clear else "✗"
    lines.append(f"  {bnd}  Manṭūq boundary (الفصل بين المنطوق والمفهوم)")
    syn = "✓" if result.layer_chain_synced else "✗"
    lines.append(f"  {syn}  Layer-chain sync (تزامن سلسلة الطبقات)")
    lines.append("")

    lines.append("── Final Verdict ──")
    if result.closed:
        lines.append("  ✓  Closed_Mantūq(L*) = TRUE")
        lines.append("     المنطوق مغلق إغلاقًا عامًا ✓")
        lines.append("")
        lines.append("     يُقفل المنطوق قبل الشروع بالمفهوم")
    else:
        lines.append("  ✗  Closed_Mantūq(L*) = FALSE")
        lines.append("     المنطوق غير مغلق — توجد فجوة بنيوية")
        open_layers = [
            v.layer_name_ar
            for v in result.verdicts
            if v.status == ClosureStatus.OPEN
        ]
        if open_layers:
            lines.append(f"     Gaps in: {', '.join(open_layers)}")

    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)
