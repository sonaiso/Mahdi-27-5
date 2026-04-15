"""Data types (named tuples / dataclasses) for the Arabic engine.

Every stage of the pipeline produces and consumes typed records so that
all data flowing through the system is a *discrete, numerically-encoded*
structure — satisfying the computability proof in the README.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, List, Optional, Tuple

from .enums import (
    POS,
    ActivationStage,
    AffectiveDimension,
    AuthorityLevel,
    CarrierClass,
    CarrierType,
    CarryingMode,
    CategorizationMode,
    CausalRole,
    CellType,
    CognitiveLayerID,
    CombinationType,
    ConceptFormationMode,
    ConceptRelationType,
    ConceptualSignifiedClass,
    ConditionToken,
    ConflictState,
    ConstraintStrength,
    ConstraintType,
    ContaminationLevel,
    CouplingRelationType,
    CulturalScope,
    DalaalaKind,
    DalalaType,
    DecisionCode,
    DerivationalDirection,
    DerivationTarget,
    DiachronicStatus,
    DirectionBoundary,
    DirectionRelation,
    DiscourseGapType,
    DiscourseValidationOutcome,
    ElementClass,
    ElementFunction,
    ElementLayer,
    EmbodiedDomain,
    EpistemicRank,
    EpistemicStatus,
    EvidenceType,
    ExchangeStatus,
    ExchangeType,
    ExplicitnessLevel,
    FrameType,
    FunctionRole,
    FuncTransitionClass,
    GapSeverity,
    GuidanceState,
    HypothesisStatus,
    InfoKind,
    InsertionPolicy,
    InstitutionalCategory,
    InterpretiveOutcomeType,
    InterpretiveStability,
    IrabCase,
    IrabRole,
    JudgementType,
    JudgmentCategory,
    KawnType,
    LayerGateDecision,
    LinkKind,
    PipelineLayerID,
    PipelineStatus,
    MafhumType,
    MasdarBab,
    MasdarType,
    MentalIntentionalType,
    MetaConceptualLevel,
    MethodFamily,
    ModalCategory,
    NormativeCategory,
    OntologicalConstraintType,
    OntologicalLayer,
    OntologicalMode,
    OperationalCapacity,
    PathKind,
    PhonCategory,
    PhonFeature,
    PhonGroup,
    PhonTransform,
    ProofPathKind,
    ProofStatus,
    PurposeType,
    RankType,
    RationalSelfKind,
    RealityKind,
    ReceiverExpectedAction,
    ReceiverRoleType,
    ReceiverState,
    ReceptionDecisionCode,
    ReceptionLayer,
    ReceptionMode,
    ReceptionRank,
    ReceptionStateType,
    ReceptionValidationOutcome,
    ReversibleValue,
    RevisionType,
    SalienceLevel,
    ScriptPhase,
    SelfModelAspect,
    SemanticDirectionGenus,
    SemanticType,
    SenderRoleType,
    SenseModality,
    SignalType,
    SignifiedClass,
    SignifierClass,
    SlotState,
    SpaceRef,
    StrictLayerID,
    StyleKind,
    SubjectGenre,
    SyllablePosition,
    ThulathiBab,
    TimeRef,
    TraceMode,
    TraceQuality,
    TransitionCondition,
    TransitionGateStatus,
    TransitionLaw,
    TransitionType,
    TriadType,
    TrustBasis,
    TrustLevel,
    TruthState,
    UnicodeProfileType,
    UtteranceMode,
    UtteranceToConceptConstraint,
    UtteredFormClass,
    ValidationOutcome,
    ValidationState,
    WeightCarryingMode,
    WeightClass,
    WeightFractalPhase,
    WeightKind,
    WeightValidationStatus,
)

# ── Signifier layer ─────────────────────────────────────────────────


@dataclass(frozen=True)
class Grapheme:
    """A single grapheme cluster: base code-point + diacritics."""

    base: int  # Unicode code-point of the consonant/vowel letter
    marks: Tuple[int, ...]  # code-points of combining marks (tashkīl)

    @property
    def char(self) -> str:
        return chr(self.base) + "".join(chr(m) for m in self.marks)


@dataclass(frozen=True)
class Syllable:
    """Phonological syllable: onset, nucleus, coda, weight."""

    onset: Tuple[int, ...]
    nucleus: Tuple[int, ...]
    coda: Tuple[int, ...]
    weight: int  # 1 = light, 2 = heavy, 3 = super-heavy


@dataclass(frozen=True)
class RootPattern:
    """Extracted root and morphological pattern."""

    root: Tuple[str, ...]  # e.g. ('ك','ت','ب')
    pattern: str  # e.g. 'فَعَلَ'
    root_id: int = 0
    pattern_id: int = 0


# ── Lexical Closure ─────────────────────────────────────────────────


@dataclass
class LexicalClosure:
    """Full morphological + lexical record for a token (التعريف 4)."""

    surface: str
    lemma: str
    root: Tuple[str, ...]
    pattern: str
    pos: POS
    lemma_id: int = 0
    root_id: int = 0
    pattern_id: int = 0
    pos_id: int = 0
    features: dict = field(default_factory=dict)
    # ── v2 fields ───────────────────────────────────────────────
    case_mark: IrabCase = IrabCase.UNKNOWN
    syntax_role: IrabRole = IrabRole.UNKNOWN
    temporal: TimeRef = TimeRef.UNSPECIFIED
    spatial: SpaceRef = SpaceRef.UNSPECIFIED
    confidence: float = 1.0


# ── Signified layer ─────────────────────────────────────────────────


@dataclass
class Concept:
    """An ontological node — the *signified* (التعريف 5).

    The v2 expansion adds nineteen optional axes that together cover
    the full range of human conceptual knowledge.  All new fields
    default to ``None`` so that existing callers require no changes.

    Core fields (v1)
    ----------------
    concept_id      unique integer identifier
    label           human-readable Arabic label
    semantic_type   primary ontological type (entity / event / …)
    properties      free-form property dict for ad-hoc extensions

    Descriptive axes (v2)
    ---------------------
    epistemic_status       how knowledge of the concept is held
    normative_category     intrinsic normative / deontic value
    affective_dimension    affective / emotional charge
    mental_intentional_type intentional mental state category
    modal_category         alethic modal standing
    frame_type             encyclopaedic frame membership
    script_phase           phase within a cognitive script
    causal_role            role in a causal-explanatory chain
    institutional_category social / institutional fact category
    categorization_mode    crisp / prototype / fuzzy membership
    cultural_scope         cultural / civilisational reach
    diachronic_status      semantic shift / historical status
    formation_mode         how the concept was formed
    meta_level             meta-conceptual order (1st / 2nd / 3rd)
    interpretive_stability single reading vs. polysemy / contested
    salience               cognitive salience / prominence
    embodied_domain        embodied sensorimotor grounding domain
    self_model_aspect      aspect of the self-model (if any)
    operational_capacity   performative / operational capacity
    """

    # ── v1 core fields ───────────────────────────────────────────────
    concept_id: int
    label: str
    semantic_type: SemanticType
    properties: dict = field(default_factory=dict)

    # ── v2 descriptive axes ──────────────────────────────────────────
    epistemic_status: Optional[EpistemicStatus] = None
    normative_category: Optional[NormativeCategory] = None
    affective_dimension: Optional[AffectiveDimension] = None
    mental_intentional_type: Optional[MentalIntentionalType] = None
    modal_category: Optional[ModalCategory] = None
    frame_type: Optional[FrameType] = None
    script_phase: Optional[ScriptPhase] = None
    causal_role: Optional[CausalRole] = None
    institutional_category: Optional[InstitutionalCategory] = None
    categorization_mode: Optional[CategorizationMode] = None
    cultural_scope: Optional[CulturalScope] = None
    diachronic_status: Optional[DiachronicStatus] = None
    formation_mode: Optional[ConceptFormationMode] = None
    meta_level: Optional[MetaConceptualLevel] = None
    interpretive_stability: Optional[InterpretiveStability] = None
    salience: Optional[SalienceLevel] = None
    embodied_domain: Optional[EmbodiedDomain] = None
    self_model_aspect: Optional[SelfModelAspect] = None
    operational_capacity: Optional[OperationalCapacity] = None


@dataclass
class ConceptRelation:
    """A directed relation between two concept nodes (شبكة المفاهيم).

    Used to wire :class:`Concept` nodes into a knowledge graph via
    :class:`~arabic_engine.signified.signified_v2.ConceptNetwork`.

    Fields
    ------
    source_id       ``concept_id`` of the origin node
    target_id       ``concept_id`` of the destination node
    relation_type   the semantic relation linking source → target
    weight          relation strength ∈ (0, 1] (default 1.0)
    notes           optional free-text annotation
    """

    source_id: int
    target_id: int
    relation_type: ConceptRelationType
    weight: float = 1.0
    notes: str = ""


# ── Linkage layer ───────────────────────────────────────────────────


@dataclass
class DalalaLink:
    """A validated signification link (التعريف 6)."""

    source_lemma: str
    target_concept_id: int
    dalala_type: DalalaType
    accepted: bool
    confidence: float  # ∈ [0, 1]


# ── Cognition layer ─────────────────────────────────────────────────


@dataclass
class Proposition:
    """A structured judgment / proposition (التعريف 7)."""

    subject: str
    predicate: str
    obj: str
    time: TimeRef = TimeRef.UNSPECIFIED
    space: SpaceRef = SpaceRef.UNSPECIFIED
    polarity: bool = True  # True = affirmative


@dataclass
class EvalResult:
    """Final evaluation vector (التعريف 8)."""

    proposition: Proposition
    truth_state: TruthState
    guidance_state: GuidanceState
    confidence: float


@dataclass(frozen=True)
class PerceptTrace:
    """Perception trace for a sentence-level episode."""

    raw_text: str
    normalized_text: str
    tokens: Tuple[str, ...]
    trace_quality: float = 1.0


@dataclass(frozen=True)
class PriorKnowledgeUnit:
    """Prior knowledge unit used during linking and judgement."""

    unit_id: str
    content: str
    source: str = "pipeline"
    weight: float = 0.5


@dataclass(frozen=True)
class LinkOperation:
    """A single linking operation between signifier-side and concept-side data."""

    operation_id: str
    operation_type: DalalaType
    source: str
    target: str
    accepted: bool
    confidence: float


@dataclass(frozen=True)
class ConceptNode:
    """Explicit concept node for v3 explainable episode payloads."""

    concept_id: str
    label: str
    semantic_type: SemanticType
    properties: dict = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluationResult:
    """v3 evaluation payload: truth, rank, confidence, and validity."""

    truth_state: TruthState
    epistemic_rank: Optional[EpistemicRank]
    confidence: float
    validation_state: ValidationState
    consistency: str = ""


# ── Syntax layer (v2) ───────────────────────────────────────────────


@dataclass
class SyntaxNode:
    """A node in the i'rāb (syntactic) tree."""

    token: str
    lemma: str
    pos: POS
    case: IrabCase
    role: IrabRole
    governor: Optional[str] = None  # the word that governs this node
    dependents: List[str] = field(default_factory=list)


# ── Time / Space tag (v2) ───────────────────────────────────────────


@dataclass
class TimeSpaceTag:
    """Temporal and spatial anchoring for a proposition."""

    time_ref: TimeRef
    space_ref: SpaceRef
    time_detail: str = ""  # e.g. "أمس", "غدًا"
    space_detail: str = ""  # e.g. "المدينة"


# ── World model fact (v2) ───────────────────────────────────────────


@dataclass
class WorldFact:
    """A fact held in the world-model knowledge base."""

    fact_id: int
    subject: str
    predicate: str
    obj: str
    truth_state: TruthState = TruthState.CERTAIN
    source: str = "axiom"


# ── Inference result (v2) ───────────────────────────────────────────


@dataclass
class InferenceResult:
    """Result of applying an inference rule."""

    rule_name: str
    premises: List[Proposition]
    conclusion: Proposition
    confidence: float
    valid: bool
    rule_category: str = ""
    conditions: Tuple[str, ...] = ()
    outcome: str = ""
    strength: float = 0.0
    explanation: str = ""


# ── Mafhūm layer (Ch. 21) ──────────────────────────────────────────


@dataclass
class MafhumPillar:
    """The four pillars (أركان) required for a Mafhūm to hold.

    A Mafhūm is valid only when all four pillars are present:
      1. closed_mantuq   — the Manṭūq is closed (منطوق مغلق)
      2. constraint_type — a structural constraint exists (قيد بنيوي)
      3. mental_counterpart — a mental counterpart can be formed (مقابل ذهني)
      4. transition_rule — a transition rule applies (قاعدة انتقال)
    """

    closed_mantuq: bool
    constraint_type: ConstraintType
    mental_counterpart: str
    transition_rule: str


@dataclass
class MafhumResult:
    """Result of Mafhūm (implied meaning) analysis (Ch. 21).

    Captures the derivation of an implied concept from the explicit
    text (Manṭūq) via one of the five minimal Mafhūm types.
    """

    mafhum_type: MafhumType
    constraint_type: ConstraintType
    pillars: MafhumPillar
    source_text: str  # the original Manṭūq fragment
    constraint_value: str  # the specific constraint detected
    counterpart: str  # the mental counterpart (المقابل الذهني)
    derived_meaning: str  # the derived implied meaning
    valid: bool  # whether all four pillars hold
    confidence: float  # confidence in [0, 1]


# ── D_min — Minimal Complete Phonological Representation ────────────


@dataclass(frozen=True)
class DMin:
    """Minimal Complete Representation — الأدنى المكتمل.

    Implements the mathematical function::

        D_min(x) = (u, c, g, f, t)

    where every field maps to a computable integer, making the full
    5-tuple a numeric vector in ℕ⁵:

    =========  ======================  ================================
    Field       Type                    Encoding
    =========  ======================  ================================
    unicode     int                     u — Unicode code-point
    category    PhonCategory            c — enum integer value
    group       PhonGroup               g — enum integer value
    features    FrozenSet[PhonFeature]  f — bitmask (2^(v-1) per bit)
    transforms  FrozenSet[PhonTransform] t — bitmask (2^(v-1) per bit)
    =========  ======================  ================================

    The ``code`` field holds the human-readable MinCode string
    (e.g. ``'C:SHF:SHD:MJH'``) and is not part of the numeric vector.
    """

    unicode: int
    category: PhonCategory
    group: PhonGroup
    features: FrozenSet[PhonFeature]
    transforms: FrozenSet[PhonTransform]
    code: str = ""

    # ── Derived string / numeric properties ─────────────────────────

    @property
    def char(self) -> str:
        """Unicode character for this phonological unit."""
        return chr(self.unicode)

    @property
    def feature_mask(self) -> int:
        """Integer bitmask encoding ``features``.

        Bit ``f.value - 1`` is set for each ``f`` in ``self.features``,
        so the result is a unique integer in ``[0, 2^|PhonFeature| - 1]``.
        """
        mask = 0
        for f in self.features:
            mask |= 1 << (f.value - 1)
        return mask

    @property
    def transform_mask(self) -> int:
        """Integer bitmask encoding ``transforms``."""
        mask = 0
        for t in self.transforms:
            mask |= 1 << (t.value - 1)
        return mask

    @property
    def vector(self) -> Tuple[int, int, int, int, int]:
        """Numeric 5-vector ``(u, c, g, f_mask, t_mask) ∈ ℕ⁵``.

        This is the core numeric encoding of ``D_min(x)``:

        * ``u``      — Unicode code-point (identity)
        * ``c``      — ``PhonCategory`` ordinal
        * ``g``      — ``PhonGroup`` ordinal
        * ``f_mask`` — feature bitmask
        * ``t_mask`` — transform bitmask
        """
        return (
            self.unicode,
            self.category.value,
            self.group.value,
            self.feature_mask,
            self.transform_mask,
        )


# ── Transition Engine — قانون الانتقال بين الخانات ──────────────────


@dataclass(frozen=True)
class TransitionContext:
    """السياق الذي يحكم الانتقال — contextual inputs to the transition function.

    Implements the parameters of::

        T_r(E) = f(P, N, F, W, Ec, M)

    ============  ========================  ===================================
    Parameter      Field                    Description
    ============  ========================  ===================================
    P              position                 syllable position of the element
    N              left_neighbor /          adjacent DMin units (or None)
                   right_neighbor
    F              function_role            morpho-syntactic role
    W              pattern                  prosodic / morphological pattern
    Ec             economy_pressure         phonetic economy demand (0–1)
    M              architecture             macro-architecture type label
    ============  ========================  ===================================
    """

    position: SyllablePosition
    function_role: FunctionRole
    left_neighbor: Optional[DMin] = None
    right_neighbor: Optional[DMin] = None
    pattern: str = ""  # e.g. "فَعَلَ", "اسْتَفْعَلَ"
    economy_pressure: float = 0.0  # 0 = none, 1 = maximum
    architecture: str = ""  # e.g. "مجرد", "مزيد", "مشتق"


@dataclass(frozen=True)
class TransitionRule:
    """قاعدة انتقال واحدة — a single row in the formal transition matrix.

    Represents a directed transition::

        from_category [from_features] → to_category [to_features]
        | law | transition_type | conditions | priority | example

    A rule is *applicable* to an element E in context C when:
      * E.category matches ``from_category`` (None = any)
      * E.features ⊇ ``required_features``
      * the transition law is compatible with C
    """

    law: TransitionLaw
    transition_type: TransitionType
    from_category: Optional[PhonCategory]  # None = any category
    required_features: FrozenSet[PhonFeature]  # features element must have
    to_category: PhonCategory  # target cell category
    resulting_transform: PhonTransform  # transform that fires
    conditions: FrozenSet[TransitionCondition]
    priority: int  # lower = higher precedence
    description_ar: str  # Arabic description
    example: str  # canonical Arabic example


@dataclass
class TransitionResult:
    """نتيجة تطبيق قانون الانتقال — result of the transition engine.

    The optimality criterion applied is::

        E_new = ArgMin(loss_root, loss_pattern, phonetic_burden)
        subject to: E_new ∈ Nearest_Valid_Functional_Cell
    """

    source_unicode: int  # codepoint of the original element
    applied_rule: Optional[TransitionRule]  # the winning rule (None = stable)
    stable: bool  # True if no transition occurred
    target_category: Optional[PhonCategory]  # new cell category (None = deleted)
    surface_form: str  # resulting surface character(s)
    loss_root: float  # cost: root integrity loss ∈ [0, 1]
    loss_pattern: float  # cost: pattern integrity loss ∈ [0, 1]
    phonetic_burden: float  # cost: articulatory burden ∈ [0, 1]
    total_cost: float  # = loss_root + loss_pattern + phonetic_burden
    conditions_met: FrozenSet[TransitionCondition]
    notes: str = ""  # optional diagnostic string


# ── Functional Transition Schema types ──────────────────────────────


@dataclass(frozen=True)
class FunctionalTransitionRecord:
    """سجل الانتقال الوظيفي — a single record in the functional transition dataset.

    This type mirrors the JSON Schema defined in
    ``arabic_engine/data/transition_record.schema.json`` and the seed data
    in ``arabic_engine/data/transitions_seed_v1.json``.

    The ``preconditions`` and ``blocking_conditions`` fields use
    :class:`~arabic_engine.core.enums.ConditionToken` values, giving a
    typed, computable DSL instead of free-form strings.

    Fields
    ------
    transition_id       ``TR_NNN`` identifier (e.g. ``"TR_001"``)
    source_cell         source :class:`~arabic_engine.core.enums.CellType`
    target_cell         target :class:`~arabic_engine.core.enums.CellType`
    transition_class    broad class of the transition
    preconditions       frozenset of activating :class:`ConditionToken` values
    blocking_conditions frozenset of blocking :class:`ConditionToken` values
    priority            1 (critical) … 5 (fallback)
    reversible          reversibility status
    surface_form        human-readable surface description
    deep_form           human-readable deep-structure description
    evidence_type       kind of evidence supporting this record (optional)
    notes               free-text annotation (optional)
    """

    transition_id: str
    source_cell: CellType
    target_cell: CellType
    transition_class: FuncTransitionClass
    preconditions: FrozenSet[ConditionToken]
    blocking_conditions: FrozenSet[ConditionToken]
    priority: int  # 1 = critical … 5 = fallback
    reversible: ReversibleValue
    surface_form: str
    deep_form: str
    evidence_type: Optional[EvidenceType] = None
    notes: str = ""


# ── AEU — Alphabetic Encoding Unit ─────────────────────────────────


@dataclass(frozen=True)
class AEU:
    """وحدة الترميز الأبجدي — a single entry in the AEU periodic table.

    Implements the 16-field record::

        AEU = {ID, Name, Class, Function, Referent, Boundary, Necessity,
               Governing_Role, Layer, Combination_Type, Math_Form,
               Unicode_Codepoint, Unicode_Profile, Depends_On, Unlocks,
               Proof_Status}

    The ``math_form`` is an 8-position binary vector ``{0,1}⁸``.
    """

    element_id: str  # e.g. "AE_001"
    element_name: str  # e.g. "Hamza"
    element_class: ElementClass
    element_function: ElementFunction
    referent: str  # الدلالة الوظيفية
    boundary: str  # الحد الفاصل
    necessity: str  # الضرورة
    governing_role: str  # الدور الحاكم
    layer: ElementLayer
    combination_type: CombinationType
    math_form: Tuple[int, ...]  # 8-bit binary vector
    unicode_codepoint: int
    unicode_profile: UnicodeProfileType
    depends_on: Tuple[str, ...] = ()
    unlocks: Tuple[str, ...] = ()
    proof_status: ProofStatus = ProofStatus.PENDING

    @property
    def char(self) -> str:
        """Unicode character for this element."""
        return chr(self.unicode_codepoint)

    @property
    def math_vector(self) -> Tuple[int, ...]:
        """The 8-position binary math form vector."""
        return self.math_form

    def is_proven(self) -> bool:
        """Return True if the element's proof status is PROVEN."""
        return self.proof_status is ProofStatus.PROVEN

    def to_row(self) -> dict:
        """Serialise to a flat dictionary suitable for tabular display.

        Returns the 16 canonical columns with Pascal_Case keys::

            Element_ID, Name, Class, Function, Referent, Boundary,
            Necessity, Governing_Role, Layer, Combination_Type,
            Math_Form, Unicode_Codepoint, Unicode_Profile,
            Depends_On, Unlocks, Proof_Status
        """
        return {
            "Element_ID": self.element_id,
            "Name": self.element_name,
            "Class": self.element_class.name,
            "Function": self.element_function.name,
            "Referent": self.referent,
            "Boundary": self.boundary,
            "Necessity": self.necessity,
            "Governing_Role": self.governing_role,
            "Layer": self.layer.name,
            "Combination_Type": self.combination_type.name,
            "Math_Form": self.math_form,
            "Unicode_Codepoint": f"U+{self.unicode_codepoint:04X}",
            "Unicode_Profile": self.unicode_profile.name,
            "Depends_On": self.depends_on,
            "Unlocks": self.unlocks,
            "Proof_Status": self.proof_status.name,
        }


# ── Axiom Types — الأصول الخمسة ─────────────────────────────────────

# A1/A2 — أصل الموضع الصفري والتحقق الموجب الأول


@dataclass(frozen=True)
class ZeroSlotRecord:
    """الموضع الصفري البنيوي — a structural zero-slot (A1) that can admit
    a first positive occupancy (A2).

    Implements the axioms::

        A1. ∃z (ZeroSlot(z) ∧ Fillable(z))
        A2. ∀z (ZeroSlot(z) ∧ Fillable(z) → ∃x Occupies(x,z))

    And the consequence::

        C1. ZeroSlot ≠ ∅   (the zero-slot is not absolute nothingness)
        C2. OneBase = FirstPositiveOccupancy(ZeroSlot)

    Fields
    ------
    slot_id             unique identifier (e.g. ``"ZS_001"``)
    label               human-readable name (Arabic or English)
    state               current state — EMPTY, OCCUPIED, or BLOCKED
    layer               ontological layer this slot belongs to
    occupant_id         identifier of the first positive occupancy
                        (``None`` while the slot is empty)
    parent_cell         optional :class:`CellType` this slot is attached to
    constraint_token    the :class:`ConditionToken` that gates filling
                        (``None`` if unconstrained)
    notes               free-text annotation
    """

    slot_id: str
    label: str
    state: SlotState
    layer: OntologicalLayer
    occupant_id: Optional[str] = None
    parent_cell: Optional[CellType] = None
    constraint_token: Optional[ConditionToken] = None
    notes: str = ""

    # ── Derived properties ──────────────────────────────────────────

    @property
    def is_fillable(self) -> bool:
        """A1 — the slot is structurally fillable (not blocked)."""
        return self.state is not SlotState.BLOCKED

    @property
    def is_occupied(self) -> bool:
        """A2 — a first positive occupancy has been realised."""
        return self.state is SlotState.OCCUPIED and self.occupant_id is not None

    @property
    def is_zero(self) -> bool:
        """C1 — the slot is empty-but-fillable (≠ ∅)."""
        return self.state is SlotState.EMPTY


# A3 — أصل التمييز الثلاثي


@dataclass(frozen=True)
class TriadicBlockRecord:
    """كتلة ثلاثية — a triadic distinction block (A3).

    Implements the axiom::

        A3. CompleteDistinction(x, y) → ∃t ≠ x, y
            MinimalCompleteDistinction = 3

    And the consequence::

        C3. PairOnly(x, y) → IncompleteRankJudgment

    A ``TriadicBlockRecord`` sits *above* a binary transition (which has
    only ``source`` and ``target``) and adds a third ``apex`` element
    that completes the minimal distinction.

    Fields
    ------
    block_id            unique identifier (e.g. ``"TB_001"``)
    apex                the third, completing element identifier
    left                first element of the base pair
    right               second element of the base pair
    layer               ontological layer of the block
    complete            whether the triadic distinction is satisfied
    governing_transition
                        optional ``Transition_ID`` that this block extends
    notes               free-text annotation
    """

    block_id: str
    apex: str
    left: str
    right: str
    layer: OntologicalLayer
    complete: bool = True
    governing_transition: Optional[str] = None
    notes: str = ""

    # ── Derived properties ──────────────────────────────────────────

    @property
    def members(self) -> Tuple[str, str, str]:
        """Return the ordered triple ``(apex, left, right)``."""
        return (self.apex, self.left, self.right)

    @property
    def is_degenerate(self) -> bool:
        """True if any two members coincide — violating A3."""
        apex, left, right = self.members
        return apex == left or apex == right or left == right


# A4 — أصل الترقية الطبقية


@dataclass(frozen=True)
class LayerPromotionRule:
    """قاعدة الترقية الطبقية — a layer-promotion rule (A4).

    Implements the axiom::

        A4. L_n ≢ L_{n+1}
            Complete(x ∈ L_n) → RequiresHigherContext(x)

    And the consequence::

        C4. Letter → Requires(SyllabicOrHigherContext)

    A ``LayerPromotionRule`` encodes an explicit promotion path from one
    :class:`OntologicalLayer` to the next, together with a
    :class:`ConditionToken` guard and an optional completeness check.

    Fields
    ------
    rule_id             unique identifier (e.g. ``"LP_001"``)
    source_layer        the starting layer
    target_layer        the promoted layer (must be higher)
    condition           :class:`ConditionToken` that gates promotion
    description         human-readable description (Arabic or English)
    requires_completeness
                        whether the source must be complete before promotion
    notes               free-text annotation
    """

    rule_id: str
    source_layer: OntologicalLayer
    target_layer: OntologicalLayer
    condition: ConditionToken
    description: str
    requires_completeness: bool = True
    notes: str = ""

    # ── Derived properties ──────────────────────────────────────────

    @property
    def layer_gap(self) -> int:
        """Number of ontological layers spanned by this promotion."""
        return self.target_layer.value - self.source_layer.value

    @property
    def is_valid(self) -> bool:
        """A4 — target layer must be strictly higher than source."""
        return self.target_layer.value > self.source_layer.value


# ── Structural Slot — الموضع البنيوي الحقيقي ────────────────────────


@dataclass(frozen=True)
class StructuralSlot:
    """الموضع البنيوي الحقيقي — the true structural zero.

    This is **not** a letter, a vowel mark, or a written sukun.  It is a
    position-that-can-be-filled — the ontological precondition for any
    linguistic value to exist.

    Clarifies the distinction::

        ZeroStruct = EmptySlot       (structural possibility)
        Sukun      = ZeroVocalicMark (a specific realisation)

    Implements::

        A1′. StructuralSlot ≠ letter ∧ StructuralSlot ≠ vowel
        Law 1. Slot ≺ Value   (position precedes content)

    Fields
    ------
    slot_id         unique identifier (e.g. ``"SS_001"``)
    label           human-readable name
    layer           ontological layer the slot belongs to
    mode            always ``OntologicalMode.SLOT``
    fillable        whether the slot can currently accept a value
    occupant_id     id of the element occupying the slot (``None`` if empty)
    constraint      optional :class:`ConditionToken` gating occupancy
    notes           free-text annotation
    """

    slot_id: str
    label: str
    layer: OntologicalLayer
    mode: OntologicalMode = OntologicalMode.SLOT
    fillable: bool = True
    occupant_id: Optional[str] = None
    constraint: Optional[ConditionToken] = None
    notes: str = ""

    @property
    def is_empty(self) -> bool:
        """True when the slot has no occupant."""
        return self.occupant_id is None

    @property
    def is_occupied(self) -> bool:
        """True when the slot holds a value."""
        return self.occupant_id is not None


# ── Vocalic Zero — الصفر الحركي المخصوص ─────────────────────────────


@dataclass(frozen=True)
class VocalicZero:
    """الصفر الحركي المخصوص — sukun as a specific vocalic-zero mark.

    The vocalic zero is a *manifestation* (تمظهر) inside the vowel
    layer, **not** the absolute structural zero.  It records the
    absence-of-vowel on a specific consonant slot.

    Clarifies::

        Sukun ≠ ZeroStruct
        Sukun  = 0_V   (a zero *within* the vocalic domain)

    Fields
    ------
    zero_id         unique identifier (e.g. ``"VZ_001"``)
    host_slot_id    the :class:`StructuralSlot` or consonant this zero
                    is attached to
    layer           always CELL (it lives at the phonological cell level)
    mode            always ``OntologicalMode.MODIFIER``
    explicit        whether the sukun is written on the surface
    notes           free-text annotation
    """

    zero_id: str
    host_slot_id: str
    layer: OntologicalLayer = OntologicalLayer.CELL
    mode: OntologicalMode = OntologicalMode.MODIFIER
    explicit: bool = True
    notes: str = ""

    @property
    def is_structural_zero(self) -> bool:
        """Always False — this is a vocalic zero, not a structural one."""
        return False

    @property
    def is_vocalic_zero(self) -> bool:
        """Always True — this is a zero within the vocalic domain."""
        return True


# ── Triad Record — سجل الثلاثية ──────────────────────────────────────


@dataclass(frozen=True)
class TriadRecord:
    """سجل ثلاثي منضبط — a formally typed triadic record.

    Every triad must declare its :class:`TriadType` before entering
    any computation (Law of Triad Type / قانون نوع المثلث).

    Implements::

        Triad = (Members, Type)
        Type ∈ {Distinctive, Hierarchical, Generative}

    And the Minimum Triad Law::

        MinArabicStructure = (Slot, Value, Constraint)

    Fields
    ------
    triad_id        unique identifier (e.g. ``"TD_001"``)
    triad_type      the formal type of this triad
    node_a          first member (slot / apex / base)
    node_b          second member (value / left-branch / motion)
    node_c          third member (constraint / right-branch / constraint)
    layer           ontological layer
    decision_rule   optional decision function identifier
    notes           free-text annotation
    """

    triad_id: str
    triad_type: TriadType
    node_a: str
    node_b: str
    node_c: str
    layer: OntologicalLayer = OntologicalLayer.CELL
    decision_rule: Optional[str] = None
    notes: str = ""

    @property
    def members(self) -> Tuple[str, str, str]:
        """Return the ordered triple ``(node_a, node_b, node_c)``."""
        return (self.node_a, self.node_b, self.node_c)

    @property
    def is_degenerate(self) -> bool:
        """True if any two members coincide — violating the triad law."""
        a, b, c = self.members
        return a == b or a == c or b == c

    @property
    def has_decision_rule(self) -> bool:
        """True when a decision function is attached (Law 2)."""
        return self.decision_rule is not None


# ── Rank Decision — قرار الرتبة ──────────────────────────────────────


@dataclass(frozen=True)
class RankDecision:
    """قرار الرتبة — the limit/capacity rank decision for an element.

    Implements Law 3 (قانون الحد والسعة)::

        L(x) = LimitScore,  C(x) = CapacityScore
        L ≫ C → LIMITAL
        C ≫ L → CAPACITIVE
        L ≈ C → TRANSITIONAL

    And Law 4 (قانون القيد السابق على التفسير)::

        Ω(x) = 0 → NoInterpretation(x)

    Fields
    ------
    decision_id         unique identifier (e.g. ``"RD_001"``)
    element_id          the element this decision is about
    limit_score         حدّية — how much the element acts as a boundary
    capacity_score      سعة — how much the element acts as a container
    rank_type           derived :class:`RankType`
    omega               constraint weight (Ω) — 0 means no interpretation
    promotion_target    optional next-layer target for promotion (Law 5)
    notes               free-text annotation
    """

    decision_id: str
    element_id: str
    limit_score: float
    capacity_score: float
    rank_type: RankType
    omega: float = 1.0
    promotion_target: Optional[OntologicalLayer] = None
    notes: str = ""

    @property
    def is_limital(self) -> bool:
        """True when limit dominates capacity."""
        return self.rank_type is RankType.LIMITAL

    @property
    def is_capacitive(self) -> bool:
        """True when capacity dominates limit."""
        return self.rank_type is RankType.CAPACITIVE

    @property
    def is_transitional(self) -> bool:
        """True when limit and capacity are balanced."""
        return self.rank_type is RankType.TRANSITIONAL

    @property
    def has_interpretation(self) -> bool:
        """Law 4 — Ω(x) = 0 → no interpretation possible."""
        return self.omega != 0.0

    @property
    def requires_promotion(self) -> bool:
        """Law 5 — whether a promotion target is specified."""
        return self.promotion_target is not None


# ── Axiom & Theorem Records — السجلات البرهانية ──────────────────────


@dataclass(frozen=True)
class AxiomRecord:
    """سجل بديهية — a formally registered axiom of the system.

    Each axiom is a foundational statement that is *assumed* true and
    upon which theorems depend.  Recording axioms as typed objects
    allows:

    * lookup by identifier
    * dependency tracking
    * proof-coverage analysis

    Implements the requirement::

        ∀ axiom ∈ Foundation:
            axiom.id ∈ Registry
            axiom.formal_statement is well-formed
            axiom.implemented_by ⊆ Codebase

    Fields
    ------
    axiom_id            unique identifier (e.g. ``"AX_001"``)
    name                human-readable name (Arabic or English)
    formal_statement    the symbolic / logical statement
    natural_language    plain-language description
    layer               the :class:`OntologicalLayer` this axiom governs
    dependencies        IDs of prior axioms this one depends on
    implemented_by      names of types/functions that embody this axiom
    status              current :class:`ProofStatus`
    notes               free-text annotation
    """

    axiom_id: str
    name: str
    formal_statement: str
    natural_language: str
    layer: OntologicalLayer
    dependencies: Tuple[str, ...] = ()
    implemented_by: Tuple[str, ...] = ()
    status: ProofStatus = ProofStatus.ASSUMED
    notes: str = ""


@dataclass(frozen=True)
class TheoremRecord:
    """سجل مبرهنة — a formally registered theorem derived from axioms.

    A theorem is a statement *derived* from one or more axioms (and
    possibly other theorems).  Recording them as typed objects enables
    traceability from any claim back to its foundational assumptions.

    Implements the requirement::

        ∀ thm ∈ Theorems:
            thm.axiom_deps ⊆ Axioms
            thm.theorem_deps ⊆ Theorems
            thm.proof_sketch ≠ ""

    Fields
    ------
    theorem_id          unique identifier (e.g. ``"TH_001"``)
    name                human-readable name
    formal_statement    the symbolic / logical statement
    natural_language    plain-language description
    axiom_dependencies  IDs of axioms this theorem depends on
    theorem_dependencies IDs of prior theorems this theorem depends on
    proof_sketch        concise proof outline
    status              current :class:`ProofStatus`
    test_reference      name of the test that verifies this theorem
    notes               free-text annotation
    """

    theorem_id: str
    name: str
    formal_statement: str
    natural_language: str
    axiom_dependencies: Tuple[str, ...] = ()
    theorem_dependencies: Tuple[str, ...] = ()
    proof_sketch: str = ""
    status: ProofStatus = ProofStatus.PENDING
    test_reference: str = ""
    notes: str = ""

    @property
    def all_dependencies(self) -> Tuple[str, ...]:
        """Return all dependency IDs (axiom + theorem)."""
        return self.axiom_dependencies + self.theorem_dependencies

    @property
    def is_proven(self) -> bool:
        """True when the theorem has been formally proven."""
        return self.status is ProofStatus.PROVEN


@dataclass(frozen=True)
class ProofDependencyGraph:
    """رسم بياني للاعتماد البرهاني — the proof-dependency DAG.

    Collects all :class:`AxiomRecord` and :class:`TheoremRecord` instances
    and provides navigation / validation helpers.

    Key invariants::

        1. The graph must be acyclic (is_acyclic)
        2. Every theorem dependency must reference existing axioms/theorems
        3. proof_coverage ∈ [0, 1]

    Fields
    ------
    axioms      all registered axioms
    theorems    all registered theorems
    """

    axioms: Tuple[AxiomRecord, ...]
    theorems: Tuple[TheoremRecord, ...]

    # ── Lookup ─────────────────────────────────────────────────────

    def get_axiom(self, axiom_id: str) -> Optional[AxiomRecord]:
        """Return the axiom with the given ID, or ``None``."""
        for ax in self.axioms:
            if ax.axiom_id == axiom_id:
                return ax
        return None

    def get_theorem(self, theorem_id: str) -> Optional[TheoremRecord]:
        """Return the theorem with the given ID, or ``None``."""
        for th in self.theorems:
            if th.theorem_id == theorem_id:
                return th
        return None

    # ── Dependency queries ─────────────────────────────────────────

    def dependencies_of(self, theorem_id: str) -> Tuple[str, ...]:
        """Return all dependency IDs for a theorem (axiom + theorem)."""
        th = self.get_theorem(theorem_id)
        if th is None:
            return ()
        return th.all_dependencies

    def dependents_of(self, axiom_id: str) -> Tuple[str, ...]:
        """Return IDs of all theorems that depend on the given axiom."""
        return tuple(th.theorem_id for th in self.theorems if axiom_id in th.axiom_dependencies)

    # ── Structural validation ──────────────────────────────────────

    def _all_ids(self) -> "frozenset[str]":
        """Return all axiom and theorem IDs."""
        ax_ids = frozenset(ax.axiom_id for ax in self.axioms)
        th_ids = frozenset(th.theorem_id for th in self.theorems)
        return ax_ids | th_ids

    def dangling_dependencies(self) -> Tuple[str, ...]:
        """Return dependency IDs that don't match any axiom or theorem."""
        known = self._all_ids()
        dangling: "list[str]" = []
        for th in self.theorems:
            for dep in th.all_dependencies:
                if dep not in known:
                    dangling.append(dep)
        return tuple(sorted(set(dangling)))

    def is_acyclic(self) -> bool:
        """Return ``True`` if the theorem dependency graph is a DAG.

        Uses iterative topological-sort (Kahn's algorithm) restricted
        to theorem-to-theorem edges.
        """
        th_ids = [th.theorem_id for th in self.theorems]
        adj: "dict[str, list[str]]" = {tid: [] for tid in th_ids}
        in_deg: "dict[str, int]" = {tid: 0 for tid in th_ids}
        for th in self.theorems:
            for dep in th.theorem_dependencies:
                if dep in adj:
                    adj[dep].append(th.theorem_id)
                    in_deg[th.theorem_id] += 1

        queue = [tid for tid, d in in_deg.items() if d == 0]
        visited = 0
        while queue:
            node = queue.pop(0)
            visited += 1
            for child in adj[node]:
                in_deg[child] -= 1
                if in_deg[child] == 0:
                    queue.append(child)
        return visited == len(th_ids)

    def proof_coverage(self) -> float:
        """Fraction of theorems whose status is PROVEN.

        Returns 0.0 when there are no theorems.
        """
        if not self.theorems:
            return 0.0
        proven = sum(1 for th in self.theorems if th.is_proven)
        return proven / len(self.theorems)

    def all_proven(self) -> bool:
        """True when every theorem has been proven."""
        return bool(self.theorems) and all(th.is_proven for th in self.theorems)


# ── Essence / Condition — الجوهر والشرط ──────────────────────────────


@dataclass(frozen=True)
class EssenceConditionPair:
    """ثنائية الجوهر والشرط — separates *what* an element is from the
    constraint that gates its realisation.

    Implements the principle::

        Core(x) = (Slot, Value)
        Cond(x) = Constraint      (شرط تحقق ≠ جزء من الماهية)

    This allows treating the constraint as an *external guard* rather
    than an intrinsic part of the element's essence.

    Fields
    ------
    element_id      identifier of the linguistic element
    slot            the structural position (موضع)
    value           the content occupying the slot (قيمة)
    constraint      optional :class:`ConditionToken` gating realisation
    layer           ontological layer
    notes           free-text annotation
    """

    element_id: str
    slot: str
    value: str
    constraint: Optional[ConditionToken] = None
    layer: OntologicalLayer = OntologicalLayer.CELL
    notes: str = ""

    @property
    def core(self) -> Tuple[str, str]:
        """Return ``(slot, value)`` — the essence, without constraint."""
        return (self.slot, self.value)

    @property
    def has_constraint(self) -> bool:
        """True when a realisation condition is attached."""
        return self.constraint is not None


# ── Ontology v1 — الجدول الأنطولوجي v1.0 ────────────────────────────


@dataclass(frozen=True)
class SignifierNode:
    """عقدة الدال — a node representing a signifier in the Ontology v1 model.

    Encodes the دال at any level (phonological, morphological, lexical,
    syntactic, textual, pragmatic, rhetorical, or uttered).  When the node
    represents a realised surface form (منطوق), ``signifier_class`` is
    ``SignifierClass.UTTERED_FORM`` and ``uttered_form_class`` carries the
    finer classification.

    Axiom 1 (الدال أعمّ من المنطوق):
        ``uttered_form_class`` is ``Optional`` — it is only set when
        ``signifier_class is SignifierClass.UTTERED_FORM``.

    Fields
    ------
    node_id             unique identifier (e.g. ``"SIG_001"``)
    signifier_class     broad class of this signifier
    uttered_form_class  finer classification when class is UTTERED_FORM
    surface             the surface string (if available)
    layer               ontological layer this signifier belongs to
    notes               free-text annotation
    """

    node_id: str
    signifier_class: SignifierClass
    surface: str
    layer: OntologicalLayer = OntologicalLayer.CELL
    uttered_form_class: Optional[UtteredFormClass] = None
    notes: str = ""

    @property
    def is_uttered(self) -> bool:
        """True when this signifier is a realised surface form (منطوق)."""
        return self.signifier_class is SignifierClass.UTTERED_FORM

    @property
    def uttered_form_is_set(self) -> bool:
        """True when the finer uttered-form class has been assigned."""
        return self.uttered_form_class is not None


@dataclass(frozen=True)
class SignifiedNode:
    """عقدة المدلول — a node representing a signified in the Ontology v1 model.

    Encodes the مدلول at any level.  When the node represents a conceptual
    structure (مفهوم), ``signified_class`` is ``SignifiedClass.CONCEPTUAL``
    and ``conceptual_class`` carries the finer classification.

    Axiom 2 (المدلول أعمّ من المفهوم):
        ``conceptual_class`` is ``Optional`` — it is only set when
        ``signified_class is SignifiedClass.CONCEPTUAL``.

    Fields
    ------
    node_id             unique identifier (e.g. ``"SFD_001"``)
    signified_class     broad class of this signified
    label               human-readable label for the signified
    semantic_type       reuses the existing :class:`SemanticType` classification
    conceptual_class    finer classification when class is CONCEPTUAL
    properties          arbitrary key/value metadata
    notes               free-text annotation
    """

    node_id: str
    signified_class: SignifiedClass
    label: str
    semantic_type: SemanticType = SemanticType.ENTITY
    conceptual_class: Optional[ConceptualSignifiedClass] = None
    properties: dict = field(default_factory=dict)
    notes: str = ""

    @property
    def is_conceptual(self) -> bool:
        """True when this signified is a conceptual structure (مفهوم)."""
        return self.signified_class is SignifiedClass.CONCEPTUAL

    @property
    def conceptual_class_is_set(self) -> bool:
        """True when the finer conceptual class has been assigned."""
        return self.conceptual_class is not None


@dataclass(frozen=True)
class CouplingRecord:
    """سجل علاقة الاقتران — the directed link from a signifier to its signified.

    Implements the coupling relation::

        CouplingRelation: Signifier × Signified → Meaning

    Axiom 3 (المنطوق لا ينتج المفهوم وحده بلا علاقة اقتران مفعّلة):
        Every ``OntologyV1Record`` carries exactly one ``CouplingRecord``.

    Fields
    ------
    coupling_id         unique identifier (e.g. ``"CRP_001"``)
    coupling_type       the kind of coupling (direct, figurative, etc.)
    signifier_id        ID of the source :class:`SignifierNode`
    signified_id        ID of the target :class:`SignifiedNode`
    confidence          coupling confidence ∈ [0, 1]
    evidence            human-readable evidence description
    active_constraints  IDs of constraints that govern this coupling
    """

    coupling_id: str
    coupling_type: CouplingRelationType
    signifier_id: str
    signified_id: str
    confidence: float = 1.0
    evidence: str = ""
    active_constraints: FrozenSet[str] = field(default_factory=frozenset)

    @property
    def is_direct(self) -> bool:
        """True when the coupling is a direct / conventional link."""
        return self.coupling_type is CouplingRelationType.DIRECT

    @property
    def is_figurative(self) -> bool:
        """True when the coupling crosses a rhetorical / figurative boundary."""
        return self.coupling_type is CouplingRelationType.FIGURATIVE


@dataclass(frozen=True)
class OntologicalConstraintRecord:
    """سجل قيد أنطولوجي — a single constraint in the Ontology v1 model.

    Axiom 5 (كل انتقال من منطوق إلى مفهوم يحتاج قيودًا تمنع الاحتمال الفاسد):
        An ``OntologyV1Record`` is *valid* only when all its constraint
        records have ``passes = True``.

    Fields
    ------
    constraint_id           unique identifier (e.g. ``"CON_001"``)
    constraint_type         the broad ontological constraint kind
    utterance_constraint    the specific utterance→concept check (if any)
    description_ar          Arabic description of this constraint
    passes                  whether the constraint is satisfied
    violated_by             description of the violation (empty when passing)
    """

    constraint_id: str
    constraint_type: OntologicalConstraintType
    description_ar: str
    passes: bool = True
    utterance_constraint: Optional[UtteranceToConceptConstraint] = None
    violated_by: str = ""

    @property
    def is_violated(self) -> bool:
        """True when the constraint is not satisfied."""
        return not self.passes


@dataclass(frozen=True)
class OntologyV1Record:
    """سجل الجدول الأنطولوجي v1.0 — the top-level unit of the ontology model.

    Ties together the four chapters of the ontology:
      1. الدال — :class:`SignifierNode`
      2. المدلول — :class:`SignifiedNode`
      3. علاقة الاقتران — :class:`CouplingRecord`
      4. القيود — ``Tuple[OntologicalConstraintRecord, ...]``

    Axiom 7 (التحليل الصحيح يبدأ بتعيين طبقة الدال…):
        Build this record via :func:`~arabic_engine.signified.ontology_v1.build_ontology_record`
        to guarantee the correct evaluation order.

    Fields
    ------
    record_id       unique identifier (e.g. ``"ONT_001"``)
    signifier       the دال node
    signified       the مدلول node
    coupling        the علاقة اقتران record
    constraints     all قيود evaluated for this record
    valid           True when all constraints pass
    notes           free-text annotation
    """

    record_id: str
    signifier: SignifierNode
    signified: SignifiedNode
    coupling: CouplingRecord
    constraints: Tuple["OntologicalConstraintRecord", ...]
    valid: bool
    notes: str = ""

    @property
    def failed_constraints(self) -> Tuple["OntologicalConstraintRecord", ...]:
        """Return all constraint records that did not pass."""
        return tuple(c for c in self.constraints if c.is_violated)


# ── Epistemic v1 — طبقة المعرفة العقلانية ──────────────────────────────


@dataclass(frozen=True)
class RealityAnchorRecord:
    """مرساة الواقع — the grounding of a cognitive episode in reality.

    Fields
    ------
    anchor_id    unique identifier
    kind         ontological character of the reality (:class:`RealityKind`)
    description  free-text description of the reality anchor
    """

    anchor_id: str
    kind: RealityKind
    description: str


@dataclass(frozen=True)
class SenseTraceRecord:
    """الأثر الحسي — the sensory imprint that connects reality to cognition.

    Fields
    ------
    trace_id    unique identifier
    modality    sensory channel (:class:`SenseModality`)
    mode        direct / reported / inferred (:class:`TraceMode`)
    description description of the sense trace
    """

    trace_id: str
    modality: SenseModality
    mode: TraceMode
    description: str


@dataclass(frozen=True)
class PriorInfoRecord:
    """المعلومة السابقة — pre-existing knowledge used in the episode.

    Fields
    ------
    info_id      unique identifier
    content      the prior knowledge content
    source       origin of the prior info (e.g. axiom id, theorem id)
    """

    info_id: str
    content: str
    source: str = ""


@dataclass(frozen=True)
class OpinionTraceRecord:
    """أثر الرأي المسبق — trace of prior opinion (must be excluded from the method).

    Fields
    ------
    opinion_id          unique identifier
    description         description of the opinion
    contamination_level degree of contamination (:class:`ContaminationLevel`)
    """

    opinion_id: str
    description: str
    contamination_level: ContaminationLevel


@dataclass(frozen=True)
class LinkingTraceRecord:
    """أثر الربط — the linking step connecting reality, sense, and prior info.

    Fields
    ------
    link_id      unique identifier
    kind         type of link (:class:`LinkKind`)
    description  description of the linking operation
    """

    link_id: str
    kind: LinkKind
    description: str


@dataclass(frozen=True)
class JudgementRecord:
    """سجل الحكم — the output judgement of a cognitive episode.

    Fields
    ------
    judgement_id  unique identifier
    judgement_type  scope of the judgement (:class:`JudgementType`)
    content         the content of the judgement
    """

    judgement_id: str
    judgement_type: JudgementType
    content: str


@dataclass(frozen=True)
class MethodRecord:
    """سجل الطريقة — the epistemological method applied in the episode.

    Fields
    ------
    method_id     unique identifier
    family        method family (:class:`MethodFamily`)
    name          human-readable name
    domain_fit    tuple of :class:`JudgementType` values the method can handle
    """

    method_id: str
    family: MethodFamily
    name: str
    domain_fit: Tuple[JudgementType, ...]


@dataclass(frozen=True)
class UtteranceRecord:
    """سجل المنطوق — the utterance (linguistic surface form) carrier.

    Fields
    ------
    utterance_id  unique identifier
    text          the surface text
    """

    utterance_id: str
    text: str


@dataclass(frozen=True)
class ConceptRecord:
    """سجل المفهوم — the concept (mental/semantic) carrier.

    Fields
    ------
    concept_record_id  unique identifier
    label              the concept label
    """

    concept_record_id: str
    label: str


@dataclass(frozen=True)
class LinguisticCarrierRecord:
    """سجل الحامل اللغوي — the linguistic transport for a cognitive episode.

    The linguistic transport has exactly two carriers: Utterance and Concept.
    ``carrier_type`` specifies which is present; when ``BOTH``, both
    ``utterance`` and ``concept`` must be non-None.

    Fields
    ------
    carrier_id    unique identifier
    carrier_type  which carriers are present (:class:`CarrierType`)
    utterance     the utterance carrier (required if type is UTTERANCE or BOTH)
    concept       the concept carrier (required if type is CONCEPT or BOTH)
    """

    carrier_id: str
    carrier_type: CarrierType
    utterance: Optional[UtteranceRecord]
    concept: Optional[ConceptRecord]


@dataclass(frozen=True)
class ProofPathRecord:
    """مسار الإثبات — the path of proof supporting a judgement.

    Fields
    ------
    path_id     unique identifier
    kind        proof path kind (:class:`ProofPathKind`)
    steps       ordered proof steps (as text)
    method_fit  the method family this path is compatible with
    """

    path_id: str
    kind: ProofPathKind
    steps: Tuple[str, ...]
    method_fit: MethodFamily


@dataclass(frozen=True)
class ConflictRuleRecord:
    """قاعدة التعارض — rule for resolving utterance/concept conflicts.

    Fields
    ------
    rule_id           unique identifier
    prefer_concept    True → concept wins on conflict; False → utterance wins
    rationale         explanation of the rule
    """

    rule_id: str
    prefer_concept: bool
    rationale: str


@dataclass(frozen=True)
class GapRecord:
    """سجل الفجوة — a detected gap in the cognitive episode.

    Fields
    ------
    gap_id      unique identifier
    code        the :class:`DecisionCode` that triggered this gap
    severity    how serious the gap is (:class:`GapSeverity`)
    description human-readable description
    """

    gap_id: str
    code: DecisionCode
    severity: GapSeverity
    description: str


@dataclass(frozen=True)
class KnowledgeEpisode:
    """خبرة معرفية — a complete cognitive episode for validation.

    This is the *internal* fully-typed representation.  Client code usually
    builds a :class:`KnowledgeEpisodeInput` first, then passes it to
    :func:`~arabic_engine.cognition.epistemic_v1.validate_episode`.

    Fields
    ------
    episode_id       unique identifier
    reality_anchor   the grounding in reality (required)
    sense_trace      the sensory imprint (required)
    prior_infos      at least one prior information record (required)
    opinion_traces   any detected prior-opinion traces (may be empty)
    linking_trace    the linking step (required)
    judgement        the output judgement (required)
    method           the epistemological method (required)
    carrier          the linguistic carrier (required)
    proof_path       the proof path (required)
    conflict_rule    the conflict resolution rule (required)
    """

    episode_id: str
    reality_anchor: RealityAnchorRecord
    sense_trace: SenseTraceRecord
    prior_infos: Tuple[PriorInfoRecord, ...]
    opinion_traces: Tuple[OpinionTraceRecord, ...]
    linking_trace: LinkingTraceRecord
    judgement: JudgementRecord
    method: MethodRecord
    carrier: LinguisticCarrierRecord
    proof_path: ProofPathRecord
    conflict_rule: ConflictRuleRecord


@dataclass(frozen=True)
class KnowledgeEpisodeInput:
    """مدخل الخبرة المعرفية — the input to the validator (all fields optional).

    Use this type to build up an episode incrementally.  Fields left as
    ``None`` will trigger the appropriate :class:`DecisionCode` failures.

    Fields mirror :class:`KnowledgeEpisode` but every field is ``Optional``.
    """

    episode_id: str
    reality_anchor: Optional[RealityAnchorRecord] = None
    sense_trace: Optional[SenseTraceRecord] = None
    prior_infos: Tuple[PriorInfoRecord, ...] = ()
    opinion_traces: Tuple[OpinionTraceRecord, ...] = ()
    linking_trace: Optional[LinkingTraceRecord] = None
    judgement: Optional[JudgementRecord] = None
    method: Optional[MethodRecord] = None
    carrier: Optional[LinguisticCarrierRecord] = None
    proof_path: Optional[ProofPathRecord] = None
    conflict_rule: Optional[ConflictRuleRecord] = None


@dataclass(frozen=True)
class ConflictResolutionResult:
    """نتيجة حل التعارض — result of resolving an utterance/concept conflict.

    Fields
    ------
    winner        ``"utterance"`` or ``"concept"``
    rule_applied  the :class:`ConflictRuleRecord` applied
    rationale     explanation of the resolution
    """

    winner: str
    rule_applied: ConflictRuleRecord
    rationale: str


@dataclass(frozen=True)
class ValidationResult:
    """نتيجة التحقق — the complete output of :func:`validate_episode`.

    Fields
    ------
    episode_id        mirrors the input episode id
    outcome           overall validity (:class:`ValidationOutcome`)
    codes             tuple of :class:`DecisionCode` failures (empty if valid)
    rank              assigned epistemic rank, or ``None`` if rejected/invalid
    insertion_policy  storage policy (:class:`InsertionPolicy`)
    gaps              detected gaps as :class:`GapRecord` tuples
    messages          human-readable messages (one per code)
    """

    episode_id: str
    outcome: ValidationOutcome
    codes: Tuple[DecisionCode, ...]
    rank: Optional[EpistemicRank]
    insertion_policy: InsertionPolicy
    gaps: Tuple[GapRecord, ...]
    messages: Tuple[str, ...]


# ── Backward-compatible Node types (restored for episode_validator) ───────────


@dataclass(frozen=True)
class SelfNode:
    """الذات — the knowing subject that undergoes a knowledge episode."""

    node_id: str
    self_kind: str = "individual"
    label: str = ""


@dataclass(frozen=True)
class RealityAnchorNode:
    """مرساة الواقع — the external reality that grounds a knowledge episode."""

    node_id: str
    reality_kind: RealityKind
    source_mode: str = "direct"
    anchoring_strength: int = 3
    label: str = ""


@dataclass(frozen=True)
class SenseTraceNode:
    """أثر الحس — the sensory evidence that attests the reality anchor."""

    node_id: str
    sense_modality: SenseModality
    trace_mode: TraceMode = TraceMode.DIRECT
    trace_quality: TraceQuality = TraceQuality.STRONG
    label: str = ""


@dataclass(frozen=True)
class PriorInfoNode:
    """معلومة سابقة — prior information used to interpret the reality anchor."""

    node_id: str
    info_kind: InfoKind
    source: str = ""
    is_verified: bool = True
    label: str = ""


@dataclass(frozen=True)
class OpinionTraceNode:
    """أثر الرأي السابق — a prior opinion that risks contaminating interpretation."""

    node_id: str
    contamination_level: ContaminationLevel = ContaminationLevel.NONE
    description: str = ""


@dataclass(frozen=True)
class LinkingTraceNode:
    """مسار الربط — the inferential chain from prior info to the judgement."""

    node_id: str
    link_kind: LinkKind
    step_count: int = 1
    is_explicit: bool = True
    label: str = ""


@dataclass(frozen=True)
class JudgementNode:
    """الحكم — the judgement issued by the knowledge episode."""

    node_id: str
    judgement_type: JudgementType
    judgement_text: str = ""
    label: str = ""


@dataclass(frozen=True)
class MethodNode:
    """المنهج — the epistemological method used in a knowledge episode."""

    node_id: str
    method_family: MethodFamily
    scope: str = ""
    requires_experiment: bool = False
    requires_formal_proof: bool = False
    requires_linguistic_anchor: bool = False


@dataclass(frozen=True)
class LinguisticCarrierNode:
    """الحامل اللغوي — the linguistic vehicle of a knowledge episode."""

    node_id: str
    carrier_class: CarrierClass
    label: str = ""


@dataclass(frozen=True)
class UtteranceNode:
    """المنطوق — a fully-vowelled utterance node."""

    node_id: str
    text_shakled: str
    utterance_mode: str = "nass"
    literal_scope: str = "direct"
    label: str = ""


@dataclass(frozen=True)
class ProofPathNode:
    """مسار الإثبات — the documented proof path supporting a knowledge episode."""

    node_id: str
    path_kind: PathKind
    is_complete: bool = True
    step_count: int = 1
    label: str = ""


@dataclass(frozen=True)
class ConflictRuleNode:
    """قاعدة التعارض — the conflict-resolution rule applied to a knowledge episode."""

    node_id: str
    rule_name: str
    priority_order: str = "Reality > Valid Proof > Concept specialization > Utterance > Suspend"
    action_on_conflict: str = "downgrade_or_reject"


@dataclass(frozen=True)
class GapNode:
    """فجوة معرفية — a detected gap in the knowledge episode."""

    node_id: str
    gap_type: str
    message: str = ""
    severity: GapSeverity = GapSeverity.MODERATE


@dataclass(frozen=True)
class EpistemicConceptNode:
    """المفهوم الإبستيمي — the conceptual meaning node within a knowledge episode."""

    node_id: str
    concept_name: str
    dalaala_type: str = "mutabaqa"
    concept_scope: str = "general"
    label: str = ""


@dataclass(frozen=True)
class EvidenceNode:
    """دليل — an individual piece of evidence supporting a proof path."""

    node_id: str
    description: str = ""
    strength: float = 1.0
    source: str = ""


@dataclass
class KnowledgeEpisodeNode:
    """خبرة معرفية — the central unit of epistemic analysis (mutable node)."""

    node_id: str
    domain_profile: str
    judgement_type: str
    method_family: str
    carrier_type: str
    method_ref: str = ""
    validation_state: ValidationState = ValidationState.PENDING
    epistemic_rank: Optional[EpistemicRank] = None
    label: str = ""


@dataclass(frozen=True)
class EpisodeValidationResult:
    """نتيجة فحص الخبرة المعرفية — the output of the EpisodeValidator."""

    episode_id: str
    validation_state: ValidationState
    epistemic_rank: Optional[EpistemicRank]
    errors: Tuple[str, ...]
    gaps: Tuple[GapNode, ...]


# ── Discourse Exchange types (Schema التداول المعرفي) ──────────────────────────


@dataclass(frozen=True)
class RationalSelfRecord:
    """الذات العاقلة الداخلة في التداول."""

    node_id: str
    self_kind: RationalSelfKind
    epistemic_capacity: str
    language_profile: str


@dataclass(frozen=True)
class SenderRoleRecord:
    """دور المرسل ضمن تبادل معرفي محدد."""

    node_id: str
    role_type: SenderRoleType
    authority_level: AuthorityLevel


@dataclass(frozen=True)
class ReceiverRoleRecord:
    """دور المستقبل ضمن تبادل معرفي محدد."""

    node_id: str
    role_type: ReceiverRoleType
    expected_action: ReceiverExpectedAction


@dataclass(frozen=True)
class ExchangePurposeRecord:
    """الغرض المقصود من التبادل المعرفي."""

    node_id: str
    purpose_type: PurposeType
    goal_statement: str


@dataclass(frozen=True)
class ExchangeStyleRecord:
    """أسلوب إخراج التبادل المعرفي."""

    node_id: str
    style_kind: StyleKind
    explicitness: ExplicitnessLevel


@dataclass(frozen=True)
class DiscourseCarrierRecord:
    """الحامل اللغوي للتداول (منطوق/مفهوم/كلاهما)."""

    node_id: str
    carrier_class: CarrierClass


@dataclass(frozen=True)
class DiscourseUtteranceRecord:
    """المنطوق المحمول في التبادل."""

    node_id: str
    text_shakled: str
    utterance_mode: UtteranceMode
    literal_scope: str


@dataclass(frozen=True)
class DiscourseConceptRecord:
    """المفهوم المحمول في التبادل."""

    node_id: str
    concept_name: str
    dalaala_kind: DalaalaKind
    concept_scope: str


@dataclass(frozen=True)
class ReceptionRecord:
    """واقعة استقبال الرسالة."""

    node_id: str
    reception_mode: ReceptionMode
    receiver_state: ReceiverState


@dataclass(frozen=True)
class ReceptionStateRecord:
    """حكم ما بعد الاستقبال."""

    node_id: str
    state_type: ReceptionStateType
    justification: str


@dataclass(frozen=True)
class TrustProfileRecord:
    """وزن ثقة المستقبل بالمصدر."""

    node_id: str
    trust_level: TrustLevel
    trust_basis: TrustBasis


@dataclass(frozen=True)
class InterpretiveOutcomeRecord:
    """المحصلة التأويلية للاستقبال."""

    node_id: str
    outcome_type: InterpretiveOutcomeType


@dataclass(frozen=True)
class DiscourseGapRecord:
    """فجوة مكتشفة في سلامة التداول المعرفي."""

    node_id: str
    gap_type: DiscourseGapType
    severity: GapSeverity
    detail: str


@dataclass(frozen=True)
class DiscourseExchangeResult:
    """نتيجة التحقق من تداول معرفي واحد."""

    exchange_id: str
    outcome: DiscourseValidationOutcome
    gaps: List[DiscourseGapRecord]
    status: ExchangeStatus


@dataclass
class DiscourseExchangeNode:
    """حادثة تداول معرفي مركزية (mutable for validator-written fields)."""

    node_id: str
    exchange_type: ExchangeType
    purpose_class: str
    style_class: str
    carrier_type: str
    status: ExchangeStatus
    sender: Optional[RationalSelfRecord] = None
    sender_role: Optional[SenderRoleRecord] = None
    receiver: Optional[RationalSelfRecord] = None
    receiver_role: Optional[ReceiverRoleRecord] = None
    purpose: Optional[ExchangePurposeRecord] = None
    style: Optional[ExchangeStyleRecord] = None
    carrier: Optional[DiscourseCarrierRecord] = None
    utterance: Optional[DiscourseUtteranceRecord] = None
    concept: Optional[DiscourseConceptRecord] = None
    transferred_knowledge: Optional[KnowledgeEpisodeNode] = None
    reception: Optional[ReceptionRecord] = None
    reception_state: Optional[ReceptionStateRecord] = None
    trust_profile: Optional[TrustProfileRecord] = None
    interpretive_outcome: Optional[InterpretiveOutcomeRecord] = None
    validation_outcome: DiscourseValidationOutcome = DiscourseValidationOutcome.INCOMPLETE
    gaps: List[DiscourseGapRecord] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════
# Fractal Kernel — Layered Hypothesis Graph Types
# ═══════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class UnicodeAtom:
    """ذرة يونيكودية — a single Unicode code-point with classification.

    Every character in the input is decomposed into an atom before any
    normalization or segmentation takes place.
    """

    atom_id: str
    char: str
    codepoint: int
    unicode_category: str
    combining_class: int
    position_index: int
    signal_type: SignalType = SignalType.UNKNOWN


@dataclass(frozen=True)
class SignalUnit:
    """وحدة إشارية — a normalised signal unit ready for analysis.

    Produced by the signal layer after normalization of Unicode atoms.
    """

    unit_id: str
    surface_text: str
    normalized_text: str
    source_span: Tuple[int, int]
    signal_type: SignalType = SignalType.BASE_LETTER


@dataclass(frozen=True)
class HypothesisNode:
    """عقدة فرضية — a single hypothesis in the layered graph.

    This is the **unified node type** for all hypothesis stages.
    Instead of creating separate dataclasses for morphological,
    conceptual, axis, relation, role, factor, case, and judgement
    hypotheses, we use a single parameterised node with a typed
    payload dictionary.

    Fields
    ------
    node_id         unique identifier for this hypothesis
    hypothesis_type short label (e.g. "morphology", "concept", "role")
    stage           which activation stage this belongs to
    source_refs     IDs of upstream nodes that generated this hypothesis
    payload         stage-specific data (root, pattern, label, etc.)
    confidence      score in [0.0, 1.0]
    status          lifecycle status of the hypothesis
    """

    node_id: str
    hypothesis_type: str
    stage: ActivationStage
    source_refs: Tuple[str, ...] = ()
    payload: Tuple[Tuple[str, object], ...] = ()
    confidence: float = 1.0
    status: HypothesisStatus = HypothesisStatus.ACTIVE

    def get(self, key: str, default: object = None) -> object:
        """Look up a key in the payload tuple-of-pairs."""
        for k, v in self.payload:
            if k == key:
                return v
        return default


@dataclass(frozen=True)
class ConstraintEdge:
    """حافة قيد — a constraint linking two hypotheses or a rule.

    Represents a directed restriction: *source_ref* constrains or
    influences *target_ref* with the given strength.
    """

    edge_id: str
    source_ref: str
    target_ref: str
    relation: str
    strength: ConstraintStrength = ConstraintStrength.MODERATE
    justification: str = ""


@dataclass(frozen=True)
class SupportEdge:
    """حافة دعم — an edge that supports a hypothesis.

    When a hypothesis at one layer is consistent with / entailed by a
    hypothesis at another layer, a support edge records that evidence.
    """

    edge_id: str
    supporter_ref: str
    target_ref: str
    weight: float = 1.0
    justification: str = ""


@dataclass(frozen=True)
class ConflictEdge:
    """حافة تعارض — an edge recording a conflict between hypotheses.

    Two hypotheses that cannot both be true are connected by a
    conflict edge.  The constraint engine uses these to prune.
    """

    edge_id: str
    node_a_ref: str
    node_b_ref: str
    conflict_state: ConflictState = ConflictState.HARD
    justification: str = ""


@dataclass(frozen=True)
class ActivationRecord:
    """سجل تفعيل — records the activation of a hypothesis node.

    Tracks when a hypothesis transitions from ACTIVE to STABILIZED
    (or to PRUNED / SUSPENDED) and why.
    """

    record_id: str
    node_ref: str
    old_status: HypothesisStatus
    new_status: HypothesisStatus
    reason: str = ""
    revision_type: Optional[RevisionType] = None


@dataclass(frozen=True)
class DecisionTrace:
    """أثر القرار — full causal trace of a single decision.

    Every decision in the engine (pruning, stabilization, revision)
    produces a trace so the complete reasoning chain is auditable.
    """

    trace_id: str
    stage: ActivationStage
    decision_type: str
    input_refs: Tuple[str, ...] = ()
    output_refs: Tuple[str, ...] = ()
    applied_rules: Tuple[str, ...] = ()
    rejected_refs: Tuple[str, ...] = ()
    justification: str = ""
    confidence: float = 1.0
    parent_trace_refs: Tuple[str, ...] = ()


# ══════════════════════════════════════════════════════════════════════
# Strict 7-Layer Analysis System Records
# النموذج الطبقي الصارم — سجلات الطبقات
# ══════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class MentalFoundationRecord:
    """سجل الطبقة العقلية المؤسسة — Layer 0 mental foundation record.

    Captures the epistemic primitives that must hold before any element
    can be classified: identity, difference, rank, constitutiveness,
    dependency, stability, transformation, causality, reality-match.
    """

    identity_strength: float        # قوة الهوية  [0, 1]
    distinctiveness: float          # التمايز     [0, 1]
    rank_position: float            # الرتبة      [0, 1]
    is_constitutive: bool           # مقوّم؟
    is_dependent: bool              # تابع؟
    stability_score: float          # ثبات        [0, 1]
    transformation_type: str = ""   # نوع التحول
    causal_source: str = ""         # مصدر العلية
    reality_match_score: float = 0.0  # مطابقة الواقع [0, 1]


@dataclass(frozen=True)
class GenerativeProfileRecord:
    """سجل القوام التوليدي — Layer 1 generative phonetic profile.

    Records how a sound is physically produced: vocal fold state,
    articulation place and mode, closure degree, resonance.
    """

    voicedness: bool                # مجهور / مهموس
    air_pressure: float             # ضغط الهواء     [0, 1]
    place_class: str                # صنف الموضع
    manner_class: str               # صنف نوع الاعتراض
    closure_value: float            # درجة الانغلاق  [0, 1]
    release_type: str = ""          # نوع الانفراج
    nasality: bool = False          # أنفي؟
    continuancy: bool = False       # استمراري؟
    sonority_level: float = 0.0     # مستوى الرنة   [0, 1]


@dataclass(frozen=True)
class AuditoryMinimumRecord:
    """سجل القوام السمعي الأدنى — Layer 2 auditory minimum record.

    Proves that the perceived element is a complete auditory unit
    with sufficient presence, boundary, cohesion, and unity.
    """

    audibility_score: float         # الحضور السمعي  [0, 1]
    temporal_span: float            # الامتداد الزمني [0, 1]
    phase_count: int                # عدد الأطوار
    order_score: float              # الانتظام       [0, 1]
    cohesion_score: float           # التماسك        [0, 1]
    unity_score: float              # الوحدة         [0, 1]


@dataclass(frozen=True)
class StructuralProfileRecord:
    """سجل القوام البنيوي — Layer 3 structural profile.

    Locates the unit within the syllable, the root, and the
    morphological pattern, scoring constitutiveness vs. dependency.
    """

    syllable_slot: str              # موضع مقطعي (onset / nucleus / coda)
    root_slot: str                  # موضع جذري (fa / ayn / lam / none)
    constitutiveness_score: float   # المقومية  [0, 1]
    dependency_score: float         # التبعية   [0, 1]
    attachment_score: float         # الإلصاق   [0, 1]
    augmentation_score: float       # الزيادة   [0, 1]
    fa_fitness: float = 0.0         # ملاءمة فاء [0, 1]
    ayn_fitness: float = 0.0        # ملاءمة عين [0, 1]
    lam_fitness: float = 0.0        # ملاءمة لام [0, 1]


@dataclass(frozen=True)
class TransformationProfileRecord:
    """سجل طبقة التحول — Layer 4 transformation record.

    Documents what changes affected the element while keeping
    structural analysis recoverable.
    """

    inflection_stability_score: float   # الثبات عبر التصريف [0, 1]
    recoverability_score: float         # إمكان الرد [0, 1]
    surface_presence: bool              # حاضر سطحيًا؟
    underlying_presence: bool           # حاضر عميقًا؟
    substitution_confidence: float = 0.0  # ثقة الإبدال [0, 1]
    deletion_confidence: float = 0.0    # ثقة الحذف   [0, 1]
    illal_confidence: float = 0.0       # ثقة الإعلال  [0, 1]
    idgham_confidence: float = 0.0      # ثقة الإدغام  [0, 1]


@dataclass(frozen=True)
class JudgmentRecordL5:
    """سجل الوظيفة العليا والحكم — Layer 5 judgment record.

    The final non-arbitrary judgment about an element's functional
    classification: original, augmented, substituted, deleted, etc.
    """

    final_judgment: JudgmentCategory    # الحكم النهائي
    judgment_confidence: float          # ثقة الحكم     [0, 1]
    functional_class: str               # الصنف الوظيفي
    deictic_score: float = 0.0          # إشارية       [0, 1]
    relational_score: float = 0.0       # علائقية      [0, 1]
    identity_preservation_score: float = 0.0  # حفظ الهوية [0, 1]


@dataclass(frozen=True)
class RepresentationRecord:
    """سجل التمثيل البرمجي — Layer 6 representation record.

    Converts the theoretical model into a codeable structure with
    full traceability back through all layers.
    """

    entity_id: str                      # معرّف الكيان
    layer_trace: Tuple[StrictLayerID, ...]  # مسار الطبقات
    feature_hash: str                   # بصمة الخصائص
    root_mapping: str = ""              # تقابل جذري
    rule_set: Tuple[str, ...] = ()      # مجموعة القواعد
    validation_status: bool = False     # صحة التحقق
    confidence_chain: Tuple[float, ...] = ()  # سلسلة الثقة
    graph_target: str = ""              # هدف الرسم البياني


@dataclass(frozen=True)
class TransitionGate:
    """بوابة الانتقال — transition gate between strict layers.

    Each gate enforces the conditions that must hold before an
    element can advance from one layer to the next.
    """

    source_layer: StrictLayerID         # الطبقة المصدر
    target_layer: StrictLayerID         # الطبقة الهدف
    conditions_met: Tuple[bool, ...]    # الشروط المستوفاة
    gate_status: TransitionGateStatus   # حالة البوابة
    failure_reasons: Tuple[str, ...] = ()  # أسباب الفشل


@dataclass(frozen=True)
class LayerTraceRecord:
    """سجل التتبع الطبقي — full trace of an element through all layers.

    Collects the results from each layer (if reached) plus the
    final gate status.  ``layer_results`` maps each
    :class:`StrictLayerID` to the corresponding record produced
    by that layer (the concrete type depends on the layer).
    """

    element_id: str                     # معرّف العنصر
    layer_0: Optional[MentalFoundationRecord] = None
    layer_1: Optional[GenerativeProfileRecord] = None
    layer_2: Optional[AuditoryMinimumRecord] = None
    layer_3: Optional[StructuralProfileRecord] = None
    layer_4: Optional[TransformationProfileRecord] = None
    layer_5: Optional[JudgmentRecordL5] = None
    layer_6: Optional[RepresentationRecord] = None
    gates: Tuple[TransitionGate, ...] = ()
    final_gate_status: TransitionGateStatus = TransitionGateStatus.INSUFFICIENT_DATA


# ── Masdar (verbal noun) types ──────────────────────────────────────


@dataclass
class MasdarRecord:
    """سجل المصدر — full record for a verbal noun (masdar).

    The masdar is the central bridge node between existential being
    (الكينونة الوجودية) and transformational being (الكينونة التحولية).
    It abstracts the event from temporal/personal assignment and fixes
    it as a conceptual unit ready for classification and derivation.
    """

    masdar_id: str                                  # معرف فريد
    surface: str                                    # الصورة اللفظية (كتابة، خروج)
    root: Tuple[str, ...]                           # الجذر الثلاثي
    pattern: str                                    # الوزن المصدري (فِعالة، فَعْل)
    masdar_type: MasdarType                         # نوع المصدر
    masdar_bab: MasdarBab                           # باب المصدر
    verb_form: str                                  # صورة الفعل المولّد
    kawn_type: KawnType = KawnType.MASDAR_BRIDGE    # نوع الكينونة
    event_core: str = ""                            # جوهر الحدث المجرد
    derivation_capacity: List[DerivationTarget] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class MasdarDerivation:
    """اشتقاق مصدري — a single derivation from a masdar to a target form.

    Records the derivational relationship from a masdar (source) to a
    derived form (target) such as active participle, passive participle,
    noun of time/place, noun of manner, or noun of instrument.
    """

    source_masdar_id: str           # معرف المصدر المصدر
    target_type: DerivationTarget   # نوع الهدف الاشتقاقي
    target_surface: str             # الصورة اللفظية للمشتق
    target_pattern: str             # الوزن الاشتقاقي
    derivation_rule_id: str = ""    # معرف قاعدة الاشتقاق
    confidence: float = 1.0


@dataclass
class FractalMasdarNode:
    """عقدة المصدر الفراكتالية — fractal node for the masdar constitution.

    The masdar fractal node is the central linking node in the
    constitutional architecture:
      Existential being → Masdar bridge → Transformational being
                                        → Weight fractal → Derivations

    completeness_score evaluates the 8 conditions of the minimal
    complete threshold (الحد الأدنى المكتمل):
      1. Thubūt  (الثبوت)    — has a lexical or interpretive form
      2. Ḥadd    (الحد)      — distinguished from verb, noun, adjective
      3. Imtidād (الامتداد)  — event, derivational, conceptual extension
      4. Muqawwim(المقوِّم)   — event core + nominal abstraction + derivability
      5. ʿAlāqa  (العلاقة)   — links root, pattern, verb, derivatives
      6. Intiẓām (الانتظام)  — ordered in morpho-semantic network
      7. Waḥda   (الوحدة)    — forms one event essence
      8. Taʿyīn  (التعيين)   — assignable as explicit/interpreted masdar
    """

    node_id: str
    masdar: MasdarRecord
    existential_link: str = ""                      # ربط بالكينونة الوجودية (الجامد)
    transformational_links: List[MasdarDerivation] = field(default_factory=list)
    fractal_children: List[str] = field(default_factory=list)
    fractal_depth: int = 0                          # عمق التكرار الذاتي
    completeness_score: float = 0.0                 # درجة اكتمال الحد الأدنى


# ═══════════════════════════════════════════════════════════════════════
# Epistemic Reception Constitution v1 — دستور الاستقبال المعرفي
# ═══════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class SubjectClassification:
    """تصنيف الموضوع الوارد — incoming subject classified into a genre (Art. 5–10)."""

    classification_id: str
    genre: SubjectGenre
    description: str
    is_closed: bool  # True when genre is determined; False = unclosed material (Art. 10)


@dataclass(frozen=True)
class ReceptionRankRecord:
    """سجل رتبة التلقي — a reception rank with its layer mapping (Art. 13–14)."""

    rank_id: str
    rank: ReceptionRank
    layer: ReceptionLayer
    description: str


@dataclass(frozen=True)
class CarryingAssignment:
    """خلية في المصفوفة الدستورية — a single cell in the carrying matrix (Art. 40)."""

    genre: SubjectGenre
    rank: ReceptionRank
    mode: CarryingMode
    qualification: str  # e.g. "أصيل في المحسوس / تبعي في غيره"


@dataclass(frozen=True)
class ReceptionPathRecord:
    """مسار الاستقبال — a subject's full journey through reception ranks."""

    path_id: str
    subject: SubjectClassification
    assignments: Tuple[CarryingAssignment, ...]
    current_rank: ReceptionRank


@dataclass(frozen=True)
class EpistemicReceptionInput:
    """مدخل التحقق من الاستقبال المعرفي — input to the reception validator."""

    reception_id: str
    subject: Optional[SubjectClassification] = None
    sense_present: bool = False
    feeling_present: bool = False
    thought_present: bool = False
    intention_present: bool = False
    choice_present: bool = False
    will_present: bool = False
    claimed_assignments: Tuple[CarryingAssignment, ...] = ()


@dataclass(frozen=True)
class EpistemicReceptionResult:
    """نتيجة التحقق من الاستقبال المعرفي — output of the reception validator."""

    reception_id: str
    outcome: ReceptionValidationOutcome
    codes: Tuple[ReceptionDecisionCode, ...] = ()
    corrected_assignments: Tuple[CarryingAssignment, ...] = ()
    path: Optional[ReceptionPathRecord] = None
    messages: Tuple[str, ...] = ()


# ── Semantic Direction Space Constitution v1 ────────────────────────


@dataclass(frozen=True)
class SemanticDirection:
    """جهة دلالية — a single direction point in the semantic space (Art. 6–12).

    Each direction is classified under one of the four supreme genera
    (:class:`SemanticDirectionGenus`) and indicates which weight patterns
    and root types can carry it.
    """

    direction_id: str                              # معرف الجهة
    genus: SemanticDirectionGenus                   # الجنس الأعلى
    derivational_direction: DerivationalDirection   # الجهة الاشتقاقية
    weight_conditions: Tuple[str, ...] = ()         # شروط حمل الوزن
    root_conditions: Tuple[str, ...] = ()           # شروط حمل الجذر
    boundary: DirectionBoundary = DirectionBoundary.HADD_FASIL  # الحد


@dataclass(frozen=True)
class DirectionRelationRecord:
    """سجل العلاقة بين جهتين — a relation edge in the direction space (Art. 34–40)."""

    source_direction_id: str         # الجهة المصدر
    target_direction_id: str         # الجهة الهدف
    relation: DirectionRelation      # نوع العلاقة
    conditions: Tuple[str, ...] = ()  # شروط العلاقة
    confidence: float = 1.0          # درجة الثقة


@dataclass(frozen=True)
class SemanticDirectionSpace:
    """فضاء الجهات الدلالية — the complete direction space (Art. 41–45).

    Gathers all directions and their inter-relations.  ``complete`` is
    True only when the space meets the minimum completeness condition:
    every genus has at least one direction, and all mandatory relations
    are present.
    """

    directions: Tuple[SemanticDirection, ...]              # الجهات
    relations: Tuple[DirectionRelationRecord, ...] = ()    # العلاقات
    genera: Tuple[SemanticDirectionGenus, ...] = ()         # الأجناس
    complete: bool = False                                  # اكتمال الفضاء


@dataclass(frozen=True)
class DirectionAssignment:
    """إسناد الجهة — assignment of a word to a semantic direction."""

    word_surface: str                            # اللفظ
    root: Tuple[str, ...]                        # الجذر
    pattern: str                                 # الوزن
    assigned_direction: SemanticDirection         # الجهة المسندة
    genus: SemanticDirectionGenus                 # الجنس الأعلى
    confidence: float = 1.0                      # درجة الثقة


# ── Weight Fractal Constitution v1 ──────────────────────────────────


@dataclass(frozen=True)
class WeightFormalTuple:
    """الصيغة الرسمية للوزن — formal 6-component tuple W = (R, V, A, S, D, P) (Art. 59).

    R: positional structure of root consonants
    V: vowel pattern structure
    A: augmentation positions
    S: syllabic structure
    D: general semantic direction
    P: carrying capacity for lexeme/derivative type
    """

    root_positions: Tuple[int, ...] = ()           # R — مواضع الرتب الجذرية
    vowel_pattern: Tuple[str, ...] = ()            # V — بنية الحركات
    augmentation_positions: Tuple[int, ...] = ()   # A — مواضع الزيادة
    syllable_structure: Tuple[str, ...] = ()       # S — البنية المقطعية
    semantic_direction_label: str = ""             # D — الجهة الدلالية العامة
    carrying_capacity: Tuple[str, ...] = ()        # P — القدرة على حمل نوع مفردي


@dataclass(frozen=True)
class VerbDoor:
    """باب فعلي — trilateral verb door linking past↔present patterns (Art. 43–46)."""

    bab: ThulathiBab                   # رقم الباب
    past_pattern: str                  # وزن الماضي (e.g. فَعَلَ)
    present_pattern: str               # وزن المضارع (e.g. يَفْعُلُ)
    example_root: Tuple[str, ...] = () # جذر مثال
    example_past: str = ""             # مثال ماضٍ
    example_present: str = ""          # مثال مضارع


@dataclass(frozen=True)
class WeightPossibilityResult:
    """نتيجة شرط الإمكان — 6-dimension possibility evaluation (Art. 9–17).

    Each dimension scores 0.0–1.0; the aggregate is their mean.
    """

    structural: float = 0.0     # بنيوي — BINYAWI
    syllabic: float = 0.0       # مقطعي — MAQTA3I
    morphological: float = 0.0  # صرفي — SARFI
    semantic: float = 0.0       # دلالي — DALALI
    generative: float = 0.0     # توليدي — TAWLIDI
    traceback: float = 0.0      # ردّي — RADDI
    aggregate: float = 0.0      # المجموع


@dataclass(frozen=True)
class WeightMWCScore:
    """الحد الأدنى المكتمل — 8-dimension Minimum Weight Completeness (Art. 18–26, 60).

    MWC(W) = (Th + Hd + Ex + Muq + Rel + Ord + Uni + Det) / 8
    """

    stability: float = 0.0            # الثبوت — Th
    boundary: float = 0.0             # الحد — Hd
    extension: float = 0.0            # الامتداد — Ex
    constituent: float = 0.0          # المقوِّم — Muq
    structural_relation: float = 0.0  # العلاقة البنائية — Rel
    regularity: float = 0.0           # الانتظام — Ord
    unity: float = 0.0                # الوحدة — Uni
    assignability: float = 0.0        # قابلية التعيين — Det
    aggregate: float = 0.0            # MWC(W)


@dataclass(frozen=True)
class WeightFractalScore:
    """درجة القانون الفراكتالي — 6-phase fractal law score (Art. 27–34, 61).

    FW(W) = (Id + Pr + Rb + Jd + Tr + Rc) / 6
    """

    identification: float = 0.0  # التعيين — Id
    preservation: float = 0.0    # الحفظ — Pr
    linkage: float = 0.0         # الربط — Rb
    judgement: float = 0.0       # الحكم — Jd
    transition: float = 0.0     # الانتقال — Tr
    return_score: float = 0.0   # الرد — Rc
    aggregate: float = 0.0      # FW(W)


@dataclass(frozen=True)
class WeightDirectionSuitability:
    """ملاءمة حمل الوزن للجهة — 4-condition suitability check (Art. 35–42, 62).

    Carrier(W, s_i) = 1 iff f(W1, W2, W3, W4) >= θ_w
    """

    structural_suitability: float = 0.0    # الملاءمة البنيوية — W1
    syllabic_suitability: float = 0.0      # الملاءمة المقطعية — W2
    morphological_suitability: float = 0.0 # الملاءمة الصرفية — W3
    semantic_suitability: float = 0.0      # الملاءمة الدلالية العامة — W4
    aggregate: float = 0.0                 # f(W1, W2, W3, W4)
    carries: bool = False                  # هل يحمل؟


@dataclass(frozen=True)
class WeightValidationResult:
    """نتيجة قبول/رفض الوزن — weight acceptance/rejection result (Art. 63–64)."""

    status: WeightValidationStatus = WeightValidationStatus.DEFICIENT
    acceptance_scores: Tuple[float, ...] = ()   # 6 acceptance criteria scores
    rejection_flags: Tuple[bool, ...] = ()      # 5 rejection criteria flags
    reason: str = ""                            # سبب الحكم


@dataclass(frozen=True)
class WeightProfile:
    """ملف الوزن — full weight profile for a single word (Art. 1–5).

    Captures the morphological pattern, its classification, radical count,
    augmentation letters, and how it carries a semantic direction.
    """

    pattern: str                                       # الوزن (فَعْل، فِعالة)
    weight_class: WeightClass                           # تصنيف الوزن
    radical_count: int                                  # عدد الحروف الأصلية
    augmentation_letters: Tuple[str, ...] = ()          # حروف الزيادة
    semantic_direction: SemanticDirectionGenus = SemanticDirectionGenus.WUJUD
    carrying_mode: WeightCarryingMode = WeightCarryingMode.ASLI
    weight_kind: WeightKind = WeightKind.PRODUCTIVE     # نوع الوزن (Art. 4–8)
    formal_tuple: Optional[WeightFormalTuple] = None    # الصيغة الرسمية (Art. 59)
    verb_door: Optional[VerbDoor] = None                # باب الفعل (Art. 43–46)


@dataclass(frozen=True)
class WeightDirectionMapping:
    """تطبيق الوزن على الجهات — maps a weight to permitted directions (Art. 11–15)."""

    pattern: str                                                            # الوزن
    permitted_directions: Tuple[DerivationalDirection, ...] = ()            # الجهات المباحة
    prohibited_directions: Tuple[DerivationalDirection, ...] = ()           # الجهات الممنوعة
    carrying_matrix: Tuple[Tuple[str, str], ...] = ()                       # مصفوفة الحمل


@dataclass(frozen=True)
class WeightFractalNode:
    """عقدة فراكتالية للوزن — a node in the fractal weight derivation tree (Art. 16–20)."""

    node_id: str                                           # معرف العقدة
    weight_profile: WeightProfile                          # ملف الوزن
    source_root: Tuple[str, ...] = ()                      # الجذر المصدر
    phase: WeightFractalPhase = WeightFractalPhase.TA3YIN  # الطور
    children: Tuple[str, ...] = ()                         # عقد الأبناء
    parent: Optional[str] = None                           # العقدة الأم
    direction_assignment: Optional[DirectionAssignment] = None  # إسناد الجهة


@dataclass(frozen=True)
class WeightFractalResult:
    """نتيجة التحليل الفراكتالي للوزن — result of weight fractal analysis."""

    root: Tuple[str, ...]                             # الجذر
    base_weight: WeightProfile                        # الوزن الأساسي
    fractal_tree: Tuple[WeightFractalNode, ...] = ()  # الشجرة الفراكتالية
    direction_map: Optional[WeightDirectionMapping] = None  # تطبيق الجهات
    completeness_score: float = 0.0                   # درجة الاكتمال
    is_closed: bool = False                           # هل أُقفل؟
    mwc_score: Optional[WeightMWCScore] = None        # الحد الأدنى المكتمل (Art. 60)
    fractal_score: Optional[WeightFractalScore] = None  # درجة الفراكتالية (Art. 61)
    possibility_result: Optional[WeightPossibilityResult] = None  # شرط الإمكان (Art. 9–17)
    validation: Optional[WeightValidationResult] = None  # حالة القبول/الرفض (Art. 63–64)


# ── Mufrad Closure (إقفال اللفظ المفرد) ─────────────────────────────


@dataclass(frozen=True)
class MufradClosureResult:
    """نتيجة إقفال اللفظ المفرد — complete, closed record for a single word.

    Assembles ALL dimensions of a single Arabic word into one
    deterministic, hierarchical, fractal structure.

    Ω(w) = R ∘ E ∘ D ∘ W ∘ S ∘ M ∘ P ∘ C ∘ N(w)
    """

    surface: str                                                 # الصورة السطحية
    normalized: str                                              # الصورة المعيارية
    lexical_closure: Optional[LexicalClosure] = None             # الإقفال المعجمي
    dmin: Optional[DMin] = None                                  # الأدنى المكتمل
    direction_assignment: Optional[DirectionAssignment] = None   # إسناد الجهة
    weight_fractal: Optional[WeightFractalResult] = None         # الوزن الفراكتالي
    masdar_record: Optional[MasdarRecord] = None                 # سجل المصدر
    concept: Optional[Concept] = None                            # المفهوم
    dalala_link: Optional[DalalaLink] = None                     # رابط الدلالة
    epistemic_reception: Optional[EpistemicReceptionResult] = None  # الاستقبال المعرفي
    is_closed: bool = False                                      # هل أُقفل كليًا؟
    closure_confidence: float = 0.0                              # درجة ثقة الإقفال


# ═══════════════════════════════════════════════════════════════════════
# Unicode as Cognitive Input — Types (Proof v1, Art. 41–46)
# ═══════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class CognitiveGateRecord:
    """سجل بوابة عبور عقلية — record of a gate decision at a layer boundary.

    Every transition Tᵢ: Uᵢ → Uᵢ₊₁ produces a gate record documenting
    whether the element passed, was rejected, suspended, or completed.
    (Art. 44)
    """

    gate_id: str
    from_layer: CognitiveLayerID
    to_layer: CognitiveLayerID
    decision: LayerGateDecision
    completeness_score: float        # Mᵢ(x) — الحد الأدنى المكتمل
    threshold: float                 # θᵢ — عتبة العبور
    has_blocker: bool                # Fᵢ(x) — المانع القاطع
    reason: str = ""
    evidence: Tuple[str, ...] = ()


@dataclass(frozen=True)
class AtomizedInput:
    """مُعطى مُعيَّن ذريًا — U₁: Unicode input decomposed into atoms.

    The result of Layer 0→1 transition: capturing each code-point,
    assigning it as an atom, classifying it, assigning initial function,
    and judging its validity.  (Art. 12–14)
    """

    atoms: Tuple[UnicodeAtom, ...]
    source_text: str
    atom_count: int
    valid_count: int
    suspended_count: int
    rejected_count: int


@dataclass(frozen=True)
class DifferentiatedUnit:
    """ذرّة متميزة متشاكلة أوليًا — U₂: differentiated + operationally coherent.

    Each atom is distinguished from its neighbours, typed, assigned
    initial coherence, and checked for combinability.  (Art. 15–17)
    """

    unit_id: str
    atom: UnicodeAtom
    neighbour_distinct: bool
    assigned_type: str
    initial_coherence: str
    combinable: bool


@dataclass(frozen=True)
class NormalizedUnit:
    """مُعطى مُطبَّع — U₃: clustered and normalized atoms.

    Atoms are grouped into meaningful clusters, original form is
    preserved, a canonical working form is produced, and the
    normalization policy is recorded.  (Art. 18–20)
    """

    unit_id: str
    surface_text: str
    normalized_text: str
    raw_preserved: str
    cluster_count: int
    normalization_policy: str


@dataclass(frozen=True)
class DesignatedUnit:
    """مُعطى حاضر مفروق مُعيَّن — U₄: present, differentiated, designated.

    The normalized material becomes present to the cognitive system,
    distinguished from what-it-is-not, and given an initial direction
    (what it is, its boundary, its position).  (Art. 21–25)
    """

    unit_id: str
    normalized_text: str
    is_present: bool
    is_distinct: bool
    initial_designation: str
    structural_position: str
    conception_ready: bool


@dataclass(frozen=True)
class InitialConceptionRecord:
    """تصور أولي — U₅: first organized mental closure.

    The first conceptual enclosure that makes the datum recallable
    in a determinate manner.  (Art. 26, 28)
    """

    conception_id: str
    source_designation: str
    initial_unity: str
    initial_boundary: str
    initial_direction: str
    recallable: bool


@dataclass(frozen=True)
class DisciplinedConceptionRecord:
    """تصور منضبط — U₆: disciplined conception meeting boundary & unity.

    The conception after boundary fixing, unity fixing, ambiguity
    removal, and validation for conceptual encoding.  (Art. 27, 29)
    """

    conception_id: str
    source_initial: str
    boundary_fixed: bool
    unity_fixed: bool
    ambiguity_removed: bool
    encoding_ready: bool


@dataclass(frozen=True)
class SemanticSubject:
    """موضوع دلالي محرر — U₇: semantically disciplined subject matter.

    The conception after conceptual encoding and semantic liberation —
    the subject matter is now determinate enough for dalāla and
    judgement.  (Art. 31–33)
    """

    subject_id: str
    source_conception: str
    conceptual_encoding: str
    semantic_determination: str
    dalala_ready: bool


@dataclass(frozen=True)
class JudgementReadyInput:
    """مُعطى صالح للحكم — U₈: input ready for judgement.

    The final stage of cognitive re-rationalisation: the subject
    has been liberated and a judgement direction assigned.
    (Art. 41, terminal)
    """

    input_id: str
    source_subject: str
    subject_liberated: bool
    judgement_direction: str
    ready: bool


@dataclass(frozen=True)
class CognitiveLayerResult:
    """نتيجة طبقة عقلية — result of processing one cognitive layer.

    Wraps the output of any Uᵢ → Uᵢ₊₁ transition with the gate
    record and trace information.  (Art. 44–45)
    """

    layer: CognitiveLayerID
    gate: CognitiveGateRecord
    membership: bool         # Cᵢ(x) ∈ {0,1} — Art. 42
    completeness: float      # Mᵢ(x) ∈ ℝ    — Art. 43
    blocker: bool            # Fᵢ(x)         — Art. 45
    evidence: Tuple[str, ...] = ()


@dataclass(frozen=True)
class CognitiveChainResult:
    """نتيجة سلسلة العقلنة الكاملة — result of the full U₀→U₈ chain.

    Aggregates all layer results and provides the final verdict on
    whether the Unicode input has been fully re-rationalised into
    judgement-ready material.  (Art. 46, 52)
    """

    source_text: str
    layer_results: Tuple[CognitiveLayerResult, ...]
    gates: Tuple[CognitiveGateRecord, ...]
    final_layer: CognitiveLayerID
    is_complete: bool
    jump_violations: Tuple[str, ...] = ()
    reason: str = ""


# ── Unified trace entry (SIVP-v1 § B1) ─────────────────────────────


@dataclass(frozen=True)
class UnifiedTraceEntry:
    """سجل أثر موحّد — single trace record for one pipeline layer.

    Collects the minimal evidence required by SIVP-v1 § B1 so that every
    layer execution is auditable and replayable:

    * **input_hash / output_hash** — SHA-256 digests for reproducibility.
    * **timestamp** — ISO-8601 wall-clock time of execution.
    * **state** — the gate decision that followed this layer.
    * **reason / evidence** — mandatory when ``state`` is SUSPEND or
      REJECT.
    """

    layer_index: int
    layer_name: str
    input_hash: str
    output_hash: str
    input_summary: str = ""
    output_summary: str = ""
    rules_applied: Tuple[str, ...] = ()
    completeness: float = 1.0
    state: LayerGateDecision = LayerGateDecision.PASS
    timestamp: str = ""
    reason: str = ""
    evidence: Tuple[str, ...] = ()
