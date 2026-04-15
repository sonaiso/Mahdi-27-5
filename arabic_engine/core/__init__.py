"""Core enums and types used across the engine.

This package re-exports all public enumerations from
:mod:`arabic_engine.core.enums` and all dataclass types from
:mod:`arabic_engine.core.types` so that client code can import from a
single namespace::

    from arabic_engine.core import POS, LexicalClosure, DMin

The :mod:`arabic_engine.core.contracts` module is intentionally *not*
re-exported here because it is a utility/verification module, not a data
type.
"""

# ── Enum re-exports ─────────────────────────────────────────────────
from .enums import (
    POS as POS,
)

# ── Fractal Kernel enum re-exports ──────────────────────────────────
from .enums import (
    ActivationStage as ActivationStage,
)
from .enums import (
    AffectiveDimension as AffectiveDimension,
)

# ── Strict 7-Layer System enum re-exports ─────────────────────────
from .enums import (
    AuditoryNode as AuditoryNode,
)
from .enums import (
    AuthorityLevel as AuthorityLevel,
)
from .enums import (
    CarrierClass as CarrierClass,
)
from .enums import (
    CarrierType as CarrierType,
)
from .enums import (
    CategorizationMode as CategorizationMode,
)
from .enums import (
    CausalRole as CausalRole,
)
from .enums import (
    CellType as CellType,
)
from .enums import (
    CombinationType as CombinationType,
)
from .enums import (
    ConceptFormationMode as ConceptFormationMode,
)
from .enums import (
    ConceptRelationType as ConceptRelationType,
)
from .enums import (
    ConceptualSignifiedClass as ConceptualSignifiedClass,
)
from .enums import (
    ConditionToken as ConditionToken,
)
from .enums import (
    ConflictState as ConflictState,
)
from .enums import (
    ConstraintStrength as ConstraintStrength,
)
from .enums import (
    ConstraintType as ConstraintType,
)
from .enums import (
    ContaminationLevel as ContaminationLevel,
)
from .enums import (
    CouplingRelationType as CouplingRelationType,
)
from .enums import (
    CulturalScope as CulturalScope,
)
from .enums import (
    DalaalaKind as DalaalaKind,
)
from .enums import (
    DalalaType as DalalaType,
)
from .enums import (
    DecisionCode as DecisionCode,
)

# ── Semantic Direction Space & Weight Fractal enum re-exports ──────
from .enums import (
    DerivationalDirection as DerivationalDirection,
)
from .enums import (
    DiachronicStatus as DiachronicStatus,
)
from .enums import (
    DirectionBoundary as DirectionBoundary,
)
from .enums import (
    DirectionRelation as DirectionRelation,
)
from .enums import (
    DiscourseGapType as DiscourseGapType,
)
from .enums import (
    DiscourseValidationOutcome as DiscourseValidationOutcome,
)
from .enums import (
    ElementClass as ElementClass,
)
from .enums import (
    ElementFunction as ElementFunction,
)
from .enums import (
    ElementLayer as ElementLayer,
)
from .enums import (
    EmbodiedDomain as EmbodiedDomain,
)
from .enums import (
    EpistemicRank as EpistemicRank,
)
from .enums import (
    EpistemicStatus as EpistemicStatus,
)
from .enums import (
    EvidenceType as EvidenceType,
)
from .enums import (
    ExchangePurposeType as ExchangePurposeType,
)
from .enums import (
    ExchangeStatus as ExchangeStatus,
)
from .enums import (
    ExchangeStyleType as ExchangeStyleType,
)
from .enums import (
    ExchangeType as ExchangeType,
)
from .enums import (
    ExplicitnessLevel as ExplicitnessLevel,
)
from .enums import (
    FrameType as FrameType,
)
from .enums import (
    FunctionRole as FunctionRole,
)
from .enums import (
    FuncTransitionClass as FuncTransitionClass,
)
from .enums import (
    GapSeverity as GapSeverity,
)
from .enums import (
    GenerativeNode as GenerativeNode,
)
from .enums import (
    GuidanceState as GuidanceState,
)
from .enums import (
    HypothesisStatus as HypothesisStatus,
)
from .enums import (
    InfoKind as InfoKind,
)
from .enums import (
    InsertionPolicy as InsertionPolicy,
)
from .enums import (
    InstitutionalCategory as InstitutionalCategory,
)
from .enums import (
    InterpretiveOutcomeType as InterpretiveOutcomeType,
)
from .enums import (
    InterpretiveStability as InterpretiveStability,
)
from .enums import (
    IrabCase as IrabCase,
)
from .enums import (
    IrabRole as IrabRole,
)
from .enums import (
    JudgementType as JudgementType,
)
from .enums import (
    JudgmentCategory as JudgmentCategory,
)
from .enums import (
    LayerEdgeType as LayerEdgeType,
)
from .enums import (
    LinkKind as LinkKind,
)
from .enums import (
    MafhumType as MafhumType,
)
from .enums import (
    MentalEdgeType as MentalEdgeType,
)
from .enums import (
    MentalIntentionalType as MentalIntentionalType,
)
from .enums import (
    MentalPrimitive as MentalPrimitive,
)
from .enums import (
    MetaConceptualLevel as MetaConceptualLevel,
)
from .enums import (
    MethodFamily as MethodFamily,
)
from .enums import (
    ModalCategory as ModalCategory,
)
from .enums import (
    NormativeCategory as NormativeCategory,
)
from .enums import (
    OntologicalConstraintType as OntologicalConstraintType,
)
from .enums import (
    OntologicalLayer as OntologicalLayer,
)
from .enums import (
    OntologicalMode as OntologicalMode,
)
from .enums import (
    OperationalCapacity as OperationalCapacity,
)
from .enums import (
    PathKind as PathKind,
)
from .enums import (
    PhonCategory as PhonCategory,
)
from .enums import (
    PhonFeature as PhonFeature,
)
from .enums import (
    PhonGroup as PhonGroup,
)
from .enums import (
    PhonTransform as PhonTransform,
)
from .enums import (
    ProofPathKind as ProofPathKind,
)
from .enums import (
    ProofStatus as ProofStatus,
)
from .enums import (
    PurposeType as PurposeType,
)
from .enums import (
    RankType as RankType,
)
from .enums import (
    RationalSelfKind as RationalSelfKind,
)
from .enums import (
    RealityKind as RealityKind,
)
from .enums import (
    ReceiverExpectedAction as ReceiverExpectedAction,
)
from .enums import (
    ReceiverRoleType as ReceiverRoleType,
)
from .enums import (
    ReceiverState as ReceiverState,
)
from .enums import (
    ReceptionMode as ReceptionMode,
)
from .enums import (
    ReceptionStateType as ReceptionStateType,
)
from .enums import (
    RepresentationNode as RepresentationNode,
)
from .enums import (
    ReversibleValue as ReversibleValue,
)
from .enums import (
    RevisionType as RevisionType,
)
from .enums import (
    SalienceLevel as SalienceLevel,
)
from .enums import (
    ScriptPhase as ScriptPhase,
)
from .enums import (
    SelfModelAspect as SelfModelAspect,
)
from .enums import (
    SemanticDirectionGenus as SemanticDirectionGenus,
)
from .enums import (
    SemanticType as SemanticType,
)
from .enums import (
    SenderRoleType as SenderRoleType,
)
from .enums import (
    SenseModality as SenseModality,
)
from .enums import (
    SignalType as SignalType,
)
from .enums import (
    SignifiedClass as SignifiedClass,
)
from .enums import (
    SignifierClass as SignifierClass,
)
from .enums import (
    SlotState as SlotState,
)
from .enums import (
    SpaceRef as SpaceRef,
)
from .enums import (
    StrictLayerID as StrictLayerID,
)
from .enums import (
    StructuralNode as StructuralNode,
)
from .enums import (
    StyleKind as StyleKind,
)
from .enums import (
    SyllablePosition as SyllablePosition,
)
from .enums import (
    TimeRef as TimeRef,
)
from .enums import (
    TraceMode as TraceMode,
)
from .enums import (
    TraceQuality as TraceQuality,
)
from .enums import (
    TransformationNode as TransformationNode,
)
from .enums import (
    TransitionCondition as TransitionCondition,
)
from .enums import (
    TransitionGateStatus as TransitionGateStatus,
)
from .enums import (
    TransitionLaw as TransitionLaw,
)
from .enums import (
    TransitionType as TransitionType,
)
from .enums import (
    TriadType as TriadType,
)
from .enums import (
    TrustBasis as TrustBasis,
)
from .enums import (
    TrustLevel as TrustLevel,
)
from .enums import (
    TruthState as TruthState,
)
from .enums import (
    UnicodeProfileType as UnicodeProfileType,
)
from .enums import (
    UtteranceMode as UtteranceMode,
)
from .enums import (
    UtteranceToConceptConstraint as UtteranceToConceptConstraint,
)
from .enums import (
    UtteredFormClass as UtteredFormClass,
)
from .enums import (
    ValidationOutcome as ValidationOutcome,
)
from .enums import (
    ValidationState as ValidationState,
)
from .enums import (
    WeightCarryingMode as WeightCarryingMode,
)
from .enums import (
    WeightClass as WeightClass,
)
from .enums import (
    WeightFractalPhase as WeightFractalPhase,
)
from .enums import (
    WeightKind as WeightKind,
)
from .enums import (
    WeightPossibilityDimension as WeightPossibilityDimension,
)
from .enums import (
    WeightValidationStatus as WeightValidationStatus,
)
from .enums import (
    ThulathiBab as ThulathiBab,
)
from .enums import (
    AugmentedSemanticLayer as AugmentedSemanticLayer,
)
from .enums import (
    NasikhCategory as NasikhCategory,
)

# ── Unicode Cognitive Input Proof enum re-exports ───────────────────
from .enums import (
    CognitiveLayerID as CognitiveLayerID,
)
from .enums import (
    LayerGateDecision as LayerGateDecision,
)

# ── Wad' & Mental Meaning Constitution v1 enum re-exports ───────────
from .enums import (
    ExpressionMode as ExpressionMode,
)
from .enums import (
    MentalMeaningSource as MentalMeaningSource,
)
from .enums import (
    NisbaType as NisbaType,
)
from .enums import (
    WadElement as WadElement,
)
from .enums import (
    WadJumpViolation as WadJumpViolation,
)

# ── Kernel re-exports ───────────────────────────────────────────────
from .kernel import (
    KERNEL_RELATION_PAIRS as KERNEL_RELATION_PAIRS,
)
from .kernel import (
    KERNEL_REQUIRED_FIELDS as KERNEL_REQUIRED_FIELDS,
)
from .kernel import (
    KernelDiscourseExchange as KernelDiscourseExchange,
)
from .kernel import (
    KernelEdge as KernelEdge,
)
from .kernel import (
    KernelGraph as KernelGraph,
)
from .kernel import (
    KernelKnowledgeEpisode as KernelKnowledgeEpisode,
)
from .kernel import (
    KernelLabel as KernelLabel,
)
from .kernel import (
    KernelLinguisticProfile as KernelLinguisticProfile,
)
from .kernel import (
    KernelNode as KernelNode,
)
from .kernel import (
    KernelRelation as KernelRelation,
)
from .kernel import (
    KernelReusableModel as KernelReusableModel,
)
from .kernel import (
    KernelUtterance as KernelUtterance,
)
from .kernel import (
    KernelValidationResult as KernelValidationResult,
)
from .kernel import (
    derive_discourse_exchange as derive_discourse_exchange,
)
from .kernel import (
    derive_knowledge_episode as derive_knowledge_episode,
)
from .kernel import (
    derive_linguistic_profile as derive_linguistic_profile,
)
from .kernel import (
    derive_reusable_model as derive_reusable_model,
)
from .kernel import (
    derive_utterance_from_carrier as derive_utterance_from_carrier,
)
from .kernel import (
    validate_kernel_graph as validate_kernel_graph,
)

# ── Trace module re-exports ─────────────────────────────────────────
from .trace import (
    DecisionState as DecisionState,
)
from .trace import (
    HypothesisState as HypothesisState,
)
from .trace import (
    KernelRuntimeState as KernelRuntimeState,
)
from .trace import (
    SignalState as SignalState,
)

# ── Type re-exports ─────────────────────────────────────────────────
from .types import (  # noqa: F401 -- intentional re-exports
    AEU as AEU,
)

# ── Fractal Kernel type re-exports ──────────────────────────────────
from .types import (
    ActivationRecord as ActivationRecord,
)

# ── Strict 7-Layer System type re-exports ─────────────────────────
from .types import (
    AuditoryMinimumRecord as AuditoryMinimumRecord,
)
from .types import (
    AxiomRecord as AxiomRecord,
)
from .types import (
    Concept as Concept,
)
from .types import (
    ConceptRelation as ConceptRelation,
)
from .types import (
    ConflictEdge as ConflictEdge,
)
from .types import (
    ConflictRuleNode as ConflictRuleNode,
)
from .types import (
    ConstraintEdge as ConstraintEdge,
)
from .types import (
    CouplingRecord as CouplingRecord,
)
from .types import (
    DalalaLink as DalalaLink,
)
from .types import (
    DecisionTrace as DecisionTrace,
)

# ── Semantic Direction Space & Weight Fractal type re-exports ──────
from .types import (
    DirectionAssignment as DirectionAssignment,
)
from .types import (
    DirectionRelationRecord as DirectionRelationRecord,
)
from .types import (
    DiscourseCarrierRecord as DiscourseCarrierRecord,
)
from .types import (
    DiscourseConceptRecord as DiscourseConceptRecord,
)
from .types import (
    DiscourseExchangeNode as DiscourseExchangeNode,
)
from .types import (
    DiscourseExchangeResult as DiscourseExchangeResult,
)
from .types import (
    DiscourseGapRecord as DiscourseGapRecord,
)
from .types import (
    DiscourseUtteranceRecord as DiscourseUtteranceRecord,
)
from .types import (
    DMin as DMin,
)
from .types import (
    EpisodeValidationResult as EpisodeValidationResult,
)
from .types import (
    EpistemicConceptNode as EpistemicConceptNode,
)
from .types import (
    EssenceConditionPair as EssenceConditionPair,
)
from .types import (
    EvalResult as EvalResult,
)
from .types import (
    EvidenceNode as EvidenceNode,
)
from .types import (
    ExchangePurposeRecord as ExchangePurposeRecord,
)
from .types import (
    ExchangeStyleRecord as ExchangeStyleRecord,
)
from .types import (
    GapNode as GapNode,
)
from .types import (
    GapRecord as GapRecord,
)
from .types import (
    GenerativeProfileRecord as GenerativeProfileRecord,
)
from .types import (
    Grapheme as Grapheme,
)
from .types import (
    HypothesisNode as HypothesisNode,
)
from .types import (
    InferenceResult as InferenceResult,
)
from .types import (
    InterpretiveOutcomeRecord as InterpretiveOutcomeRecord,
)
from .types import (
    JudgementNode as JudgementNode,
)
from .types import (
    JudgementRecord as JudgementRecord,
)
from .types import (
    JudgmentRecordL5 as JudgmentRecordL5,
)
from .types import (
    KnowledgeEpisode as KnowledgeEpisode,
)
from .types import (
    KnowledgeEpisodeInput as KnowledgeEpisodeInput,
)
from .types import (
    KnowledgeEpisodeNode as KnowledgeEpisodeNode,
)
from .types import (
    LayerPromotionRule as LayerPromotionRule,
)
from .types import (
    LayerTraceRecord as LayerTraceRecord,
)
from .types import (
    LexicalClosure as LexicalClosure,
)
from .types import (
    LinguisticCarrierNode as LinguisticCarrierNode,
)
from .types import (
    LinguisticCarrierRecord as LinguisticCarrierRecord,
)
from .types import (
    LinkingTraceNode as LinkingTraceNode,
)
from .types import (
    LinkingTraceRecord as LinkingTraceRecord,
)
from .types import (
    MentalFoundationRecord as MentalFoundationRecord,
)
from .types import (
    MethodNode as MethodNode,
)
from .types import (
    MethodRecord as MethodRecord,
)
from .types import (
    MufradClosureResult as MufradClosureResult,
)
from .types import (
    OntologicalConstraintRecord as OntologicalConstraintRecord,
)
from .types import (
    OntologyV1Record as OntologyV1Record,
)
from .types import (
    OpinionTraceNode as OpinionTraceNode,
)
from .types import (
    OpinionTraceRecord as OpinionTraceRecord,
)
from .types import (
    PriorInfoNode as PriorInfoNode,
)
from .types import (
    PriorInfoRecord as PriorInfoRecord,
)
from .types import (
    ProofDependencyGraph as ProofDependencyGraph,
)
from .types import (
    ProofPathNode as ProofPathNode,
)
from .types import (
    ProofPathRecord as ProofPathRecord,
)
from .types import (
    Proposition as Proposition,
)
from .types import (
    RationalSelfRecord as RationalSelfRecord,
)
from .types import (
    RealityAnchorNode as RealityAnchorNode,
)
from .types import (
    RealityAnchorRecord as RealityAnchorRecord,
)
from .types import (
    ReceiverRoleRecord as ReceiverRoleRecord,
)
from .types import (
    ReceptionRecord as ReceptionRecord,
)
from .types import (
    ReceptionStateRecord as ReceptionStateRecord,
)
from .types import (
    RepresentationRecord as RepresentationRecord,
)
from .types import (
    RootPattern as RootPattern,
)
from .types import (
    SelfNode as SelfNode,
)
from .types import (
    SemanticDirection as SemanticDirection,
)
from .types import (
    SemanticDirectionSpace as SemanticDirectionSpace,
)
from .types import (
    SenderRoleRecord as SenderRoleRecord,
)
from .types import (
    SenseTraceNode as SenseTraceNode,
)
from .types import (
    SenseTraceRecord as SenseTraceRecord,
)
from .types import (
    SignalUnit as SignalUnit,
)
from .types import (
    SignifiedNode as SignifiedNode,
)
from .types import (
    SignifierNode as SignifierNode,
)
from .types import (
    StructuralProfileRecord as StructuralProfileRecord,
)
from .types import (
    SupportEdge as SupportEdge,
)
from .types import (
    Syllable as Syllable,
)
from .types import (
    SyntaxNode as SyntaxNode,
)
from .types import (
    TheoremRecord as TheoremRecord,
)
from .types import (
    TimeSpaceTag as TimeSpaceTag,
)
from .types import (
    TransformationProfileRecord as TransformationProfileRecord,
)
from .types import (
    TransitionGate as TransitionGate,
)
from .types import (
    TriadicBlockRecord as TriadicBlockRecord,
)
from .types import (
    TrustProfileRecord as TrustProfileRecord,
)
from .types import (
    UnicodeAtom as UnicodeAtom,
)
from .types import (
    UtteranceNode as UtteranceNode,
)
from .types import (
    UtteranceRecord as UtteranceRecord,
)
from .types import (
    ValidationResult as ValidationResult,
)
from .types import (
    WeightDirectionMapping as WeightDirectionMapping,
)
from .types import (
    WeightFractalNode as WeightFractalNode,
)
from .types import (
    WeightFractalResult as WeightFractalResult,
)
from .types import (
    WeightProfile as WeightProfile,
)
from .types import (
    WeightFormalTuple as WeightFormalTuple,
)
from .types import (
    VerbDoor as VerbDoor,
)
from .types import (
    WeightPossibilityResult as WeightPossibilityResult,
)
from .types import (
    WeightMWCScore as WeightMWCScore,
)
from .types import (
    WeightFractalScore as WeightFractalScore,
)
from .types import (
    WeightDirectionSuitability as WeightDirectionSuitability,
)
from .types import (
    WeightValidationResult as WeightValidationResult,
)
from .types import (
    WorldFact as WorldFact,
)
from .types import (
    ZeroSlotRecord as ZeroSlotRecord,
)

# ── Unicode Cognitive Input Proof type re-exports ───────────────────
from .types import (
    AtomizedInput as AtomizedInput,
)
from .types import (
    CognitiveChainResult as CognitiveChainResult,
)
from .types import (
    CognitiveGateRecord as CognitiveGateRecord,
)
from .types import (
    CognitiveLayerResult as CognitiveLayerResult,
)
from .types import (
    DesignatedUnit as DesignatedUnit,
)
from .types import (
    DifferentiatedUnit as DifferentiatedUnit,
)
from .types import (
    DisciplinedConceptionRecord as DisciplinedConceptionRecord,
)
from .types import (
    InitialConceptionRecord as InitialConceptionRecord,
)
from .types import (
    JudgementReadyInput as JudgementReadyInput,
)
from .types import (
    NormalizedUnit as NormalizedUnit,
)
from .types import (
    SemanticSubject as SemanticSubject,
)

# ── Wad' & Mental Meaning Constitution v1 type re-exports ───────────
from .types import (
    MentalMeaningRecord as MentalMeaningRecord,
)
from .types import (
    NisbaRecord as NisbaRecord,
)
from .types import (
    WadConstitutionResult as WadConstitutionResult,
)
from .types import (
    WadJumpCheckResult as WadJumpCheckResult,
)
from .types import (
    WadRecord as WadRecord,
)

__all__ = [
    # ── enums ───────────────────────────────────────────────────────
    "POS",
    "AffectiveDimension",
    "AuthorityLevel",
    "CarrierClass",
    "CarrierType",
    "CategorizationMode",
    "CausalRole",
    "CellType",
    "CombinationType",
    "ConceptFormationMode",
    "ConceptRelationType",
    "ConceptualSignifiedClass",
    "ConditionToken",
    "ConstraintType",
    "ContaminationLevel",
    "CouplingRelationType",
    "CulturalScope",
    "DalaalaKind",
    "DalalaType",
    "DecisionCode",
    "DiachronicStatus",
    "DiscourseGapType",
    "DiscourseValidationOutcome",
    "ElementClass",
    "ElementFunction",
    "ElementLayer",
    "EmbodiedDomain",
    "EpistemicRank",
    "EpistemicStatus",
    "EvidenceType",
    "ExchangeStatus",
    "ExchangePurposeType",
    "ExchangeStyleType",
    "ExchangeType",
    "ExplicitnessLevel",
    "FrameType",
    "FuncTransitionClass",
    "FunctionRole",
    "GapSeverity",
    "GuidanceState",
    "InfoKind",
    "InsertionPolicy",
    "InstitutionalCategory",
    "InterpretiveOutcomeType",
    "InterpretiveStability",
    "IrabCase",
    "IrabRole",
    "JudgementType",
    "LinkKind",
    "MafhumType",
    "MentalIntentionalType",
    "MetaConceptualLevel",
    "MethodFamily",
    "ModalCategory",
    "NormativeCategory",
    "OntologicalConstraintType",
    "OntologicalLayer",
    "OntologicalMode",
    "OperationalCapacity",
    "PathKind",
    "PhonCategory",
    "PhonFeature",
    "PhonGroup",
    "PhonTransform",
    "ProofPathKind",
    "ProofStatus",
    "PurposeType",
    "RankType",
    "RationalSelfKind",
    "RealityKind",
    "ReceiverExpectedAction",
    "ReceiverRoleType",
    "ReceiverState",
    "ReceptionMode",
    "ReceptionStateType",
    "ReversibleValue",
    "SalienceLevel",
    "ScriptPhase",
    "SelfModelAspect",
    "SemanticType",
    "SenderRoleType",
    "SenseModality",
    "SignifiedClass",
    "SignifierClass",
    "SlotState",
    "SpaceRef",
    "StyleKind",
    "SyllablePosition",
    "TimeRef",
    "TraceMode",
    "TraceQuality",
    "TransitionCondition",
    "TransitionLaw",
    "TransitionType",
    "TriadType",
    "TrustBasis",
    "TrustLevel",
    "TruthState",
    "UnicodeProfileType",
    "UtteranceMode",
    "UtteranceToConceptConstraint",
    "UtteredFormClass",
    "ValidationOutcome",
    "ValidationState",
    # ── Semantic Direction Space & Weight Fractal enums ────────────
    "DerivationalDirection",
    "DirectionBoundary",
    "DirectionRelation",
    "SemanticDirectionGenus",
    "WeightCarryingMode",
    "WeightClass",
    "WeightFractalPhase",
    "WeightKind",
    "WeightPossibilityDimension",
    "WeightValidationStatus",
    "ThulathiBab",
    "AugmentedSemanticLayer",
    "NasikhCategory",
    # ── Fractal Kernel enums ───────────────────────────────────────
    "ActivationStage",
    "ConflictState",
    "ConstraintStrength",
    "HypothesisStatus",
    "RevisionType",
    "SignalType",
    # ── kernel ──────────────────────────────────────────────────────
    "KERNEL_RELATION_PAIRS",
    "KERNEL_REQUIRED_FIELDS",
    "KernelDiscourseExchange",
    "KernelEdge",
    "KernelGraph",
    "KernelKnowledgeEpisode",
    "KernelLabel",
    "KernelLinguisticProfile",
    "KernelNode",
    "KernelRelation",
    "KernelReusableModel",
    "KernelUtterance",
    "KernelValidationResult",
    "derive_discourse_exchange",
    "derive_knowledge_episode",
    "derive_linguistic_profile",
    "derive_reusable_model",
    "derive_utterance_from_carrier",
    "validate_kernel_graph",
    # ── types ───────────────────────────────────────────────────────
    "AEU",
    "AxiomRecord",
    "Concept",
    "ConceptRelation",
    "ConflictRuleNode",
    "CouplingRecord",
    "DalalaLink",
    "DiscourseCarrierRecord",
    "DiscourseConceptRecord",
    "DiscourseExchangeNode",
    "DiscourseExchangeResult",
    "DiscourseGapRecord",
    "DiscourseUtteranceRecord",
    "DMin",
    "EpisodeValidationResult",
    "EpistemicConceptNode",
    "EssenceConditionPair",
    "EvalResult",
    "EvidenceNode",
    "ExchangePurposeRecord",
    "ExchangeStyleRecord",
    "GapNode",
    "GapRecord",
    "Grapheme",
    "InferenceResult",
    "InterpretiveOutcomeRecord",
    "JudgementNode",
    "JudgementRecord",
    "KnowledgeEpisode",
    "KnowledgeEpisodeInput",
    "KnowledgeEpisodeNode",
    "LayerPromotionRule",
    "LexicalClosure",
    "LinguisticCarrierNode",
    "LinguisticCarrierRecord",
    "LinkingTraceNode",
    "LinkingTraceRecord",
    "MethodNode",
    "MethodRecord",
    "OntologicalConstraintRecord",
    "OntologyV1Record",
    "OpinionTraceNode",
    "OpinionTraceRecord",
    "PriorInfoNode",
    "PriorInfoRecord",
    "ProofDependencyGraph",
    "ProofPathNode",
    "ProofPathRecord",
    "Proposition",
    "RationalSelfRecord",
    "RealityAnchorNode",
    "RealityAnchorRecord",
    "ReceiverRoleRecord",
    "ReceptionRecord",
    "ReceptionStateRecord",
    "RootPattern",
    "SelfNode",
    "SenderRoleRecord",
    "SenseTraceNode",
    "SenseTraceRecord",
    "SignifiedNode",
    "SignifierNode",
    "Syllable",
    "SyntaxNode",
    "TheoremRecord",
    "TimeSpaceTag",
    "TriadicBlockRecord",
    "TrustProfileRecord",
    "UtteranceNode",
    "UtteranceRecord",
    "ValidationResult",
    "WorldFact",
    "ZeroSlotRecord",
    # ── Fractal Kernel types ───────────────────────────────────────
    "ActivationRecord",
    "ConflictEdge",
    "ConstraintEdge",
    "DecisionTrace",
    "HypothesisNode",
    "SignalUnit",
    "SupportEdge",
    "UnicodeAtom",
    # ── Trace module ───────────────────────────────────────────────
    "DecisionState",
    "HypothesisState",
    "KernelRuntimeState",
    "SignalState",
    # ── Strict 7-Layer System enums ────────────────────────────────
    "AuditoryNode",
    "GenerativeNode",
    "JudgmentCategory",
    "LayerEdgeType",
    "MentalEdgeType",
    "MentalPrimitive",
    "RepresentationNode",
    "StrictLayerID",
    "StructuralNode",
    "TransformationNode",
    "TransitionGateStatus",
    # ── Strict 7-Layer System types ────────────────────────────────
    "AuditoryMinimumRecord",
    "GenerativeProfileRecord",
    "JudgmentRecordL5",
    "LayerTraceRecord",
    "MentalFoundationRecord",
    "RepresentationRecord",
    "StructuralProfileRecord",
    "TransformationProfileRecord",
    "TransitionGate",
    # ── Semantic Direction Space & Weight Fractal types ────────────
    "DirectionAssignment",
    "DirectionRelationRecord",
    "MufradClosureResult",
    "SemanticDirection",
    "SemanticDirectionSpace",
    "WeightDirectionMapping",
    "WeightFractalNode",
    "WeightFractalResult",
    "WeightProfile",
    "WeightFormalTuple",
    "VerbDoor",
    "WeightPossibilityResult",
    "WeightMWCScore",
    "WeightFractalScore",
    "WeightDirectionSuitability",
    "WeightValidationResult",
    # ── Unicode Cognitive Input Proof ──────────────────────────────
    "CognitiveLayerID",
    "LayerGateDecision",
    "AtomizedInput",
    "CognitiveChainResult",
    "CognitiveGateRecord",
    "CognitiveLayerResult",
    "DesignatedUnit",
    "DifferentiatedUnit",
    "DisciplinedConceptionRecord",
    "InitialConceptionRecord",
    "JudgementReadyInput",
    "NormalizedUnit",
    "SemanticSubject",
    # ── Wad' & Mental Meaning Constitution v1 ─────────────────────
    "ExpressionMode",
    "MentalMeaningSource",
    "NisbaType",
    "WadElement",
    "WadJumpViolation",
    "MentalMeaningRecord",
    "NisbaRecord",
    "WadConstitutionResult",
    "WadJumpCheckResult",
    "WadRecord",
]
