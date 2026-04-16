# Domain Taxonomy Map — خريطة تصنيف المجالات

> Canonical reference for every `Enum` class in `arabic_engine/core/enums.py`,
> organised by domain.  Each enum belongs to **exactly one** domain.

---

## Table of Contents — فهرس المحتويات

1. [Pipeline State & Control — حالة السلسلة والتحكم](#1-pipeline-state--control--حالة-السلسلة-والتحكم)
2. [Pre-U₀ Admissibility — القبول قبل U₀](#2-pre-u₀-admissibility--القبول-قبل-u₀)
3. [Layer Identification — تعريف الطبقات](#3-layer-identification--تعريف-الطبقات)
4. [Linguistic Core — اللُّب اللغوي](#4-linguistic-core--اللب-اللغوي)
5. [Phonological Analysis — التحليل الصوتي](#5-phonological-analysis--التحليل-الصوتي)
6. [Morphological Analysis — التحليل الصرفي](#6-morphological-analysis--التحليل-الصرفي)
7. [Syntactic Analysis — التحليل النحوي](#7-syntactic-analysis--التحليل-النحوي)
8. [Diacritics & Syllables — التشكيل والمقاطع](#8-diacritics--syllables--التشكيل-والمقاطع)
9. [Signification & Dalāla — الدلالة والإشارة](#9-signification--dalāla--الدلالة-والإشارة)
10. [Ontological Classification — التصنيف الوجودي](#10-ontological-classification--التصنيف-الوجودي)
11. [Epistemics & Validation — المعرفة والتحقق](#11-epistemics--validation--المعرفة-والتحقق)
12. [Semantic Direction — الاتجاه الدلالي](#12-semantic-direction--الاتجاه-الدلالي)
13. [Weight Fractal — الميزان الكسيري](#13-weight-fractal--الميزان-الكسيري)
14. [Masdar & Derivation — المصدر والاشتقاق](#14-masdar--derivation--المصدر-والاشتقاق)
15. [Reception & Receiver — الاستقبال والمتلقي](#15-reception--receiver--الاستقبال-والمتلقي)
16. [Concept Formation — تكوين المفاهيم](#16-concept-formation--تكوين-المفاهيم)
17. [Judgement & Proof — الحكم والإثبات](#17-judgement--proof--الحكم-والإثبات)
18. [Discourse & Communication — الخطاب والتواصل](#18-discourse--communication--الخطاب-والتواصل)
19. [Hypothesis & Constraints — الفرضيات والقيود](#19-hypothesis--constraints--الفرضيات-والقيود)
20. [7-Layer Element Analysis — تحليل العناصر السبعي](#20-7-layer-element-analysis--تحليل-العناصر-السبعي)
21. [Semantic Structuring — البناء الدلالي](#21-semantic-structuring--البناء-الدلالي)
22. [Cognitive Mediation — الوساطة الإدراكية](#22-cognitive-mediation--الوساطة-الإدراكية)
23. [Infrastructure & Utility — البنية التحتية](#23-infrastructure--utility--البنية-التحتية)
24. [Cross-Domain Mappings — الروابط بين المجالات](#24-cross-domain-mappings--الروابط-بين-المجالات)
25. [Domain Boundaries — حدود المجالات](#25-domain-boundaries--حدود-المجالات)

---

## 1. Pipeline State & Control — حالة السلسلة والتحكم

Controls the overall flow, gating, and termination of the main analytical
pipeline (`pipeline.py`).  These enums determine whether processing
continues, suspends, or halts at each layer boundary.

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `PipelineStatus` | 2368 | `SUCCESS`, `SUSPEND`, `FAILURE` | Final outcome of a full pipeline run |
| `LayerGateDecision` | 2350 | `PASS`, `REJECT`, `SUSPEND`, `COMPLETE` | Per-layer gate output between adjacent layers |
| `TransitionGateStatus` | 1891 | `PASSED`, `BLOCKED`, `INSUFFICIENT_DATA` | Transition verdict in the 7-layer element system |

**Cross-domain note:** These three enums participate in explicit
status-mapping chains documented in
[`docs/unified_state_model.md`](unified_state_model.md).

---

## 2. Pre-U₀ Admissibility — القبول قبل U₀

Guards the entrance to the cognitive processing chain.  Before any
input reaches the first cognitive layer (U₀), it must pass a six-dimension
admissibility check.

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `AdmissibilityDecision` | 2720 | `ACCEPT`, `SUSPEND`, `REJECT` | Outcome of the pre-U₀ admissibility check |
| `AdmissibilityDimension` | 2735 | `PRESENCE`, `DISTINGUISHABILITY`, `INITIAL_ADMISSIBILITY`, `PRIOR_KNOWLEDGE_BINDING`, `PRELIMINARY_INTERPRETATION`, `PRE_DESIGNATION_CONCEPTION` | The six dimensions evaluated before pipeline entry |

Used by: `signifier/admissibility.py`.

---

## 3. Layer Identification — تعريف الطبقات

Multiple pipeline systems coexist in the engine.  Each has its own
layer-ID enum to avoid conflation.

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `PipelineLayerID` | 2389 | `L0_NORMALIZE` … `L10_WORLD_MODEL` (12 values) | Identifies each stage in the main `pipeline.run()` |
| `CognitiveLayerID` | 2322 | `UNICODE_RAW` (U₀) … `JUDGEMENT_READY` (U₈) — 9 values | Cognitive re-rationalisation chain (Art. 41) |
| `StrictLayerID` | 1738 | `MENTAL_FOUNDATION` … `PROGRAMMATIC` — 7 values | 7-layer element analysis system |
| `EpicLayerID` | 2694 | `UNICODE` (E1) … `JUDGEMENT` (E8) — 8 values | 8-layer Epic scaffold |

These are related but **distinct**: `PipelineLayerID` maps the main
analytical pipeline, `CognitiveLayerID` maps cognitive input processing,
`StrictLayerID` maps the formal 7-layer element system, and `EpicLayerID`
maps the 8-layer Epic scaffold.

---

## 4. Linguistic Core — اللُّب اللغوي

Foundational linguistic categories that pervade the entire system —
part of speech, case, role, truth, guidance, and temporal/spatial
reference.

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `POS` | 14 | `ISM`, `FI3L`, `HARF`, … | Part-of-speech tag (اسم / فعل / حرف) |
| `SemanticType` | 31 | `ENTITY`, `EVENT`, `PROPERTY`, `RELATION`, … | Broad semantic type of a lexical unit |
| `DalalaType` | 46 | `MUTABAQA`, `TADAMMUN`, `ILTIZAM`, `ISNAD` | Dalāla (signification) type |
| `IrabCase` | 90 | `MARFU3`, `MANSUB`, `MAJRUR`, `MAJZUM` | I'rāb grammatical case |
| `IrabRole` | 101 | `FA3IL`, `MAF3UL_BIH`, `MUBTADA`, `KHABAR`, … | Syntactic role in i'rāb |
| `TimeRef` | 122 | `PAST`, `PRESENT`, `FUTURE`, `UNSPECIFIED` | Temporal reference |
| `SpaceRef` | 133 | `HERE`, `THERE`, `UNSPECIFIED`, … | Spatial reference |
| `TruthState` | 62 | `TRUE`, `FALSE`, `UNKNOWN`, `CONTRADICTORY` | Logical truth state of a proposition |
| `GuidanceState` | 76 | `GUIDED`, `MISGUIDED`, `NEUTRAL`, `UNKNOWN` | Normative/guidance state |
| `MafhumType` | 160 | `MUWAFAQA`, `MUKHALAFA`, `SHART`, `GHAYA`, … | Mafhūm (implied meaning) type — Ch. 21 |
| `ConstraintType` | 146 | `TYPE_CHECK`, `RANGE_CHECK`, `PRESENCE`, … | Layer-boundary constraint kind |

---

## 5. Phonological Analysis — التحليل الصوتي

Governs the phonological layer of the signifier (`signifier/` package),
covering phoneme classification, feature geometry, phonological
transformations, and transition rules.

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `PhonCategory` | 185 | `CONSONANT`, `VOWEL`, `SEMIVOWEL`, … | Phoneme category |
| `PhonGroup` | 198 | `LABIAL`, `DENTAL`, `PALATAL`, `VELAR`, `PHARYNGEAL`, `GLOTTAL`, … | Place-of-articulation group |
| `PhonFeature` | 236 | `VOICED`, `VOICELESS`, `EMPHATIC`, `NASAL`, … | Phonological feature flags |
| `PhonTransform` | 275 | `ASSIMILATION`, `ELISION`, `INSERTION`, `METATHESIS`, … | Phonological transformation type |
| `TransitionType` | 329 | `VOWEL_SHIFT`, `CLUSTER_RESOLVE`, … | Phonological transition kind |
| `TransitionLaw` | 338 | `OBLIGATORY`, `OPTIONAL`, `CONTEXT_DEPENDENT`, … | Transition rule strength |
| `TransitionCondition` | 350 | `WORD_BOUNDARY`, `SYLLABLE_BOUNDARY`, … | Condition triggering a transition |
| `SyllablePosition` | 360 | `ONSET`, `NUCLEUS`, `CODA` | Position within a syllable |
| `FunctionRole` | 369 | `CARRIER`, `MODIFIER`, `HEAD`, … | Phonological function role |

---

## 6. Morphological Analysis — التحليل الصرفي

Covers morpheme structure, affix types, and related morphological
intelligence used in L2 (lexical closure) and the Epic E4 layer.

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `AffixType` | 2510 | `PREFIX`, `SUFFIX`, `INFIX`, `CIRCUMFIX` | Affix position type |
| `MorphemeType` | 2525 | `ROOT`, `PATTERN`, `AFFIX`, `CLITIC`, … | Morpheme class |
| `NasikhCategory` | 2293 | Categories of nāsikh (abrogating particles) | Nāsikh grammatical classification |

---

## 7. Syntactic Analysis — التحليل النحوي

Dependency relations and syntactic structuring used in L3 (syntax)
and the Epic E5 layer.

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `DependencyRelation` | 2545 | `ISNAD`, `IDAFA`, `TAQYID`, `SILA`, `ATAF`, `BADAL`, `TAWKID`, `NIDA`, `ISTITHNA`, `TAMYIZ`, `HAL` | Arabic syntactic dependency relation type |

---

## 8. Diacritics & Syllables — التشكيل والمقاطع

Governs diacritic annotation logic and syllable formation — Epic layers
E2 and E3.

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `DiacriticType` | 2417 | `FATHA`, `DAMMA`, `KASRA`, `SUKUN`, `SHADDA`, `TANWIN_FATH`, … | Arabic diacritic mark type |
| `DiacriticRole` | 2444 | `CASE_MARKER`, `VOWEL_MARKER`, `STRESS_MARKER`, … | Functional role of a diacritic |
| `DiacriticConsistency` | 2459 | `CONSISTENT`, `INCONSISTENT`, `PARTIAL`, `MISSING` | Consistency status of diacritisation |
| `SyllableType` | 2477 | `OPEN`, `CLOSED`, `SUPER_HEAVY` | Syllable structure type |
| `SyllableWeight` | 2494 | `LIGHT`, `HEAVY`, `SUPER_HEAVY` | Syllable weight (mora count) |

---

## 9. Signification & Dalāla — الدلالة والإشارة

Enums that classify the signifier form, the signified concept, and the
link between them.  Central to the linkage layer (`linkage/`).

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `DalaalaKind` | 1061 | `MUTABAQA`, `TADHAMMUN`, `ILTIZAM`, `ISHARA` | Extended dalāla vocabulary |
| `SignifierClass` | 1135 | `LEXICAL`, `SYNTACTIC`, `PHONOLOGICAL`, `ORTHOGRAPHIC`, `UTTERED_FORM`, `RHETORICAL`, `MORPHOLOGICAL`, `PROSODIC` | Broad class of the signifier form |
| `SignifiedClass` | 1148 | `CONCEPTUAL`, `REFERENTIAL`, `RELATIONAL`, `NORMATIVE`, `ABSTRACT`, `ONTOLOGICAL`, … (22 values) | Broad class of the signified concept |
| `ConceptualSignifiedClass` | 1175 | `ENTITY_CONCEPT`, `EVENT_CONCEPT`, `PROPERTY_CONCEPT`, `UNIVERSAL`, `PARTICULAR`, `META_CONCEPT`, `RELATIONAL`, `CONCRETE` | Finer classification of the conceptual signified |
| `UtteredFormClass` | 1188 | `WORD_UTTERANCE`, `MARKED_UTTERANCE`, `PHRASE`, `CLAUSE`, `SENTENCE_UTTERANCE` | Classification of the uttered surface form |
| `OntologicalConstraintType` | 1198 | Constraint kinds at the ontological level | Ontological constraint classification |
| `UtteranceToConceptConstraint` | 1216 | Constraints from utterance to concept mapping | Utterance-to-concept constraint type |
| `CouplingRelationType` | 1231 | Coupling relations between signifier and signified | Signifier–signified coupling type |
| `LinkKind` | 1099 | `CAUSAL`, `TEMPORAL`, `LOGICAL`, `SEMANTIC`, `STRUCTURAL`, `CONTEXTUAL`, `TEXTUAL_INFERENCE` | Inter-node link kind |

---

## 10. Ontological Classification — التصنيف الوجودي

Classifies entities in the ontological layer (L4).

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `OntologicalLayer` | 652 | `ESSENCE`, `ATTRIBUTE`, `RELATION`, `EVENT`, … | Ontological stratum |
| `OntologicalMode` | 666 | `NECESSARY`, `POSSIBLE`, `IMPOSSIBLE`, `ACTUAL`, … | Modal status of an ontological entity |
| `TriadType` | 692 | `SUBSTANCE`, `ACCIDENT`, `RELATION` | Aristotelian triad classification |
| `RankType` | 712 | `GENUS`, `SPECIES`, `DIFFERENTIA`, `PROPERTY`, `ACCIDENT` | Porphyrian rank in the genus–species tree |

---

## 11. Epistemics & Validation — المعرفة والتحقق

Governs the epistemic standing of propositions, the reliability of
evidence, and validation outcomes throughout the pipeline.

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `EpistemicRank` | 1533 | Ranks of epistemic certainty | Epistemic certainty level |
| `EpistemicStatus` | 734 | `CERTAIN`, `PROBABLE`, `POSSIBLE`, `DOUBTFUL`, `UNKNOWN` | Epistemic status of a concept |
| `NormativeCategory` | 753 | `WAJIB`, `MANDUB`, `MUBAH`, `MAKRUH`, `HARAM` | Islamic normative (fiqh) category |
| `ValidationState` | 1354 | `VALID`, `INVALID`, `PENDING` | Epistemic validation outcome |
| `ValidationOutcome` | 1345 | `PASS`, `FAIL`, `WARN`, … | General validation outcome |
| `AuthorityLevel` | 1375 | Authority / trust levels | Source authority level |
| `EvidenceType` | 471 | `PHONOLOGICAL`, `MORPHOLOGICAL`, `SYNTACTIC`, `SEMANTIC`, … | Type of linguistic evidence |
| `SenseModality` | 1249 | `VISUAL`, `AUDITORY`, `TACTILE`, `OLFACTORY`, `GUSTATORY`, `PROPRIOCEPTIVE` | Perceptual modality |
| `TraceMode` | 1265 | `EXACT`, `APPROXIMATE`, `INFERRED` | Trace precision mode |
| `TraceQuality` | 1274 | `HIGH`, `MEDIUM`, `LOW` | Trace quality rating |
| `TrustBasis` | 1283 | `TESTIMONY`, `OBSERVATION`, `INFERENCE`, … | Basis of epistemic trust |
| `TrustLevel` | 1293 | `ABSOLUTE`, `HIGH`, `MEDIUM`, `LOW`, `NONE` | Degree of trust |

**Cross-domain note:** `ValidationState` maps to `PipelineStatus` as
documented in [`docs/unified_state_model.md`](unified_state_model.md).

---

## 12. Semantic Direction — الاتجاه الدلالي

Classifies the directionality of meaning — how derivation,
semantic genus, and boundary conditions relate forms to meanings.

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `SemanticDirectionGenus` | 2079 | Semantic direction genus categories | Genus of semantic direction |
| `DerivationalDirection` | 2098 | Derivational direction types | Direction of morphological derivation |
| `DirectionRelation` | 2135 | Direction relation types | Relation between semantic directions |
| `DirectionBoundary` | 2156 | Direction boundary types | Boundary conditions of directional semantics |

---

## 13. Weight Fractal — الميزان الكسيري

Implements the morphological weight system (al-mīzān al-ṣarfī) as a
fractal structure with phases, classes, and validation.

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `WeightCarryingMode` | 2172 | Carrying-mode values | How morphological weight is carried |
| `WeightFractalPhase` | 2187 | Fractal phase values | Phase within the weight fractal |
| `WeightClass` | 2206 | Weight class values | Morphological weight class |
| `WeightKind` | 2223 | Weight kind values | Kind of morphological weight |
| `WeightPossibilityDimension` | 2236 | Possibility dimensions | Dimensional axes of weight possibility |
| `WeightValidationStatus` | 2306 | `VALID`, `INVALID`, `PARTIAL` | Validation status of a weight analysis |
| `ThulathiBab` | 2255 | Thulāthi verb paradigm doors | Paradigm class (bāb) for triliteral verbs |
| `AugmentedSemanticLayer` | 2272 | Augmented semantic layers | Semantic layering for augmented forms |

---

## 14. Masdar & Derivation — المصدر والاشتقاق

Governs masdar (verbal noun) extraction, derivation targets, and the
existential kawn type — used in `signifier/masdar.py`.

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `MasdarType` | 1912 | `ORIGINAL`, `MEEM`, `INDUSTRIAL`, … | Type of masdar (verbal noun) |
| `MasdarBab` | 1931 | Bāb (paradigm) values for masdar | Masdar paradigm class |
| `DerivationTarget` | 1961 | `ISM_FA3IL`, `ISM_MAF3UL`, `SIFA_MUSHABBAHA`, … | Target of morphological derivation |
| `KawnType` | 1979 | `EXISTENTIAL`, `TRANSFORMATIONAL`, … | Kawn (being) type in masdar bridge |
| `SubjectGenre` | 1995 | Subject genre values | Genre classification of the subject |

---

## 15. Reception & Receiver — الاستقبال والمتلقي

Models how linguistic input is received, interpreted, and validated
from the perspective of the receiver (al-mutalaqqī).

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `ReceptionRank` | 2010 | Reception rank values | Rank of reception quality |
| `ReceptionLayer` | 2029 | Reception processing layers | Layer within reception processing |
| `CarryingMode` | 2042 | `LEXICAL`, `SYNTACTIC`, `SEMANTIC`, … | Mode of meaning-carrying |
| `ReceptionDecisionCode` | 2055 | Decision codes for reception | Reception gate decision |
| `ReceptionValidationOutcome` | 2068 | Validation outcomes | Reception validation result |
| `ReceptionStateType` | 1469 | Reception state types | State of the reception process |
| `ReceptionMode` | 1648 | Reception mode values | Mode of reception |
| `ReceiverRoleType` | 1626 | Receiver role types | Role of the receiver |
| `ReceiverExpectedAction` | 1637 | Expected receiver actions | Action expected from receiver |
| `ReceiverState` | 1658 | Receiver state values | Current state of the receiver |

---

## 16. Concept Formation — تكوين المفاهيم

A rich 20-dimensional concept model.  These enums classify how concepts
are formed, categorised, experienced, and situated across cultural,
historical, and modal dimensions.

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `AffectiveDimension` | 772 | `LOVE`, `FEAR`, `TRANQUILITY`, `ANXIETY`, `AWE`, … (12 values) | Affective/emotional charge (dim 3/20) |
| `MentalIntentionalType` | 792 | `BELIEF`, `DESIRE`, `INTENTION`, `ATTENTION`, `MEMORY`, … (10 values) | Intentional mental state type (dim 4/20) |
| `ModalCategory` | 810 | `POSSIBLE`, `NECESSARY`, `IMPOSSIBLE`, `COUNTERFACTUAL`, `HYPOTHETICAL`, `ACTUAL` | Alethic modal category (dim 5/20) |
| `FrameType` | 824 | `COMMERCIAL`, `JOURNEY`, `KINSHIP`, `CONFLICT`, `TEACHING`, … (10 values) | Conceptual frame / scene type (dim 6/20) |
| `ScriptPhase` | 843 | `PRECONDITION`, `INITIATION`, `DEVELOPMENT`, `CLIMAX`, `RESOLUTION`, `POSTCONDITION`, `NONE` | Phase in a cognitive script (dim 7/20) |
| `CausalRole` | 858 | `CAUSE`, `CONDITION`, `ENABLER`, `BLOCKER`, `MECHANISM`, `MEDIATOR`, `EFFECT`, `GOAL`, `LAW`, `NONE` | Causal/explanatory role (dim 8/20) |
| `InstitutionalCategory` | 876 | `STATE`, `LAW`, `PROPERTY`, `CONTRACT`, `POSITION`, `INSTITUTION`, `CURRENCY`, `NORM`, `RITUAL`, `NONE` | Social/institutional category (dim 9/20) |
| `CategorizationMode` | 894 | `CLASSICAL`, `PROTOTYPE_BASED`, `FUZZY_BOUNDED`, `GRADIENT_MEMBERSHIP`, `RADIAL` | Categorisation mode (dim 10/20) |
| `CulturalScope` | 907 | `UNIVERSAL`, `CULTURE_SPECIFIC`, `CIVILIZATIONAL`, `DOMAIN_SPECIFIC`, `RELIGIOUS_SPECIFIC` | Cultural/civilisational scope (dim 11/20) |
| `DiachronicStatus` | 920 | `ORIGINAL`, `SHIFTED`, `NARROWED`, `BROADENED`, `SPECIALIZED`, `GENERALIZED`, `OBSOLETE` | Diachronic semantic status (dim 12/20) |
| `ConceptFormationMode` | 935 | `PRIMITIVE`, `DERIVED`, `COMPOSED`, `BLENDED`, `ANALOGICALLY_EXTENDED`, `METAPHORICAL` | Concept formation mode (dim 13/20) |
| `MetaConceptualLevel` | 949 | `FIRST_ORDER`, `SECOND_ORDER`, `THIRD_ORDER` | Meta-conceptual order (dim 14/20) |
| `InterpretiveStability` | 961 | Stability values | Interpretive stability (dim 15/20) |
| `SalienceLevel` | 974 | Salience levels | Cognitive salience (dim 16/20) |
| `EmbodiedDomain` | 988 | Embodied domains | Embodied-cognition domain (dim 17/20) |
| `SelfModelAspect` | 1007 | Self-model aspects | Self-model dimension (dim 18/20) |
| `OperationalCapacity` | 1022 | Operational capacities | Operational capacity (dim 19/20) |
| `ConceptRelationType` | 1038 | `HYPERNYM`, `HYPONYM`, `MERONYM`, `SYNONYM`, `ANTONYM`, … | Concept-to-concept relation type (dim 20/20) |

---

## 17. Judgement & Proof — الحكم والإثبات

Classifies judgement types, proof paths, method families, and
review status — used in L6 (evaluation) and the Epic E8 layer.

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `JudgementType` | 1073 | `EXISTENCE`, `ESSENCE`, `ATTRIBUTE`, `RELATION`, `INTERPRETIVE`, `FORMAL_CONTRADICTION`, `NORMATIVE`, `PURE_LINGUISTIC`, `METAPHYSICAL`, `CAUSAL`, `FORMAL` | Type of logical or normative judgement |
| `JudgementRank` | 2657 | `DEFINITIVE`, `PREDOMINANT`, `PROBABLE`, `POSSIBLE`, `DOUBTFUL` | Rank/certainty of a judgement |
| `JudgmentCategory` | 1849 | Judgement categories | Broad judgement category |
| `MethodFamily` | 1089 | `RATIONAL`, `SCIENTIFIC`, `LINGUISTIC`, `MATHEMATICAL`, `PHYSICAL` | Family of inference/derivation method |
| `ProofPathKind` | 1111 | `DIRECT_PROOF`, `INDIRECT`, `CONSTRUCTIVE`, `REFUTATION` | Kind of proof path |
| `PathKind` | 1123 | `HISSI`, `AQLI`, `LINGUISTIC`, `FORMAL` | Evidence path type |
| `ReviewStatus` | 2674 | `PENDING`, `APPROVED`, `CONTESTED`, `REVISED`, `FINAL` | Review status of a judgement |
| `ProofStatus` | 632 | `PROVED`, `DISPROVED`, `PENDING`, `UNKNOWN` | Status of a formal proof |

---

## 18. Discourse & Communication — الخطاب والتواصل

Models discourse structure, utterance modes, sender/receiver roles,
and communicative intent.

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `UtteranceMode` | 1304 | Utterance mode values | Mode of utterance production |
| `SenderRoleType` | 1315 | Sender role types | Role of the sender in discourse |
| `StyleKind` | 1327 | Style kinds | Stylistic register of discourse |
| `PurposeType` | 1446 | Purpose types | Communicative purpose |
| `ExplicitnessLevel` | 1461 | Explicitness levels | How explicit the communication is |
| `InterpretiveOutcomeType` | 1481 | Interpretive outcomes | Outcome of an interpretive process |
| `DiscourseGapType` | 1503 | Discourse gap types | Type of gap in discourse |
| `DiscourseValidationOutcome` | 1522 | Discourse validation outcomes | Validation result at discourse level |
| `GapSeverity` | 1492 | Severity levels | Severity of a discourse gap |

---

## 19. Hypothesis & Constraints — الفرضيات والقيود

Manages the hypothesis lifecycle and constraint resolution in the
hypothesis layer (`hypothesis/`, `constraints/`).

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `HypothesisStatus` | 1685 | `ACTIVE`, `PRUNED`, `STABILIZED`, `SUSPENDED`, `REVISED` | Hypothesis lifecycle state |
| `ConstraintStrength` | 1695 | `HARD`, `SOFT`, `PREFERENCE` | Constraint enforcement level |
| `ConflictState` | 1705 | `NONE`, `DETECTED`, `RESOLVED`, `UNRESOLVABLE` | Conflict resolution state |
| `RevisionType` | 1714 | `REFINEMENT`, `RETRACTION`, `EXPANSION`, `CORRECTION` | Type of hypothesis revision |

**Cross-domain note:** `HypothesisStatus` maps to `LayerGateDecision` as
documented in [`docs/unified_state_model.md`](unified_state_model.md).

---

## 20. 7-Layer Element Analysis — تحليل العناصر السبعي

Enums supporting the formal 7-layer element analysis system
(`layers/` package), covering node types in each layer and edge
types between layers.

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `StrictLayerID` | 1738 | `MENTAL_FOUNDATION` … `PROGRAMMATIC` (7 values) | Layer identifier in the strict 7-layer system |
| `AuditoryNode` | 1750 | `PHONEME`, `SYLLABLE`, `WORD_FORM`, `PROSODIC`, `ONSET`, `NUCLEUS`, `CODA` | Node type in the auditory/phonological layer |
| `StructuralNode` | 1762 | Structural node types | Node type in the structural layer |
| `TransformationNode` | 1776 | Transformation node types | Node type in the transformation layer |
| `MentalPrimitive` | 1789 | Mental primitive types | Primitive in the mental-foundation layer |
| `MentalEdgeType` | 1803 | Mental edge types | Edge type between mental primitives |
| `LayerEdgeType` | 1815 | Layer edge types | Edge type between layers |
| `GenerativeNode` | 1863 | Generative node types | Node type in the generative layer |
| `RepresentationNode` | 1876 | Representation node types | Node type in the representation layer |

---

## 21. Semantic Structuring — البناء الدلالي

Semantic frame types and semantic relations — Epic E6 layer.

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `SemanticFrameType` | 2577 | `ACTION`, `STATE`, `TRANSFER`, `COGNITION`, `EVALUATION`, `EXISTENCE` | Semantic frame classification |
| `SemanticRelationType` | 2596 | `HYPERNYM`, `HYPONYM`, `MERONYM`, `HOLONYM`, `SYNONYM`, `ANTONYM`, `CAUSAL`, `TEMPORAL` | Semantic relation type |

---

## 22. Cognitive Mediation — الوساطة الإدراكية

Reasoning modes and evaluation criteria — Epic E7 layer.

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `ReasoningMode` | 2622 | `DEDUCTIVE`, `INDUCTIVE`, `ABDUCTIVE`, `ANALOGICAL` | Reasoning mode for cognitive mediation |
| `CriterionType` | 2637 | `SEMANTIC`, `SYNTACTIC`, `PRAGMATIC`, `EPISTEMIC`, `NORMATIVE` | Criterion type for subject evaluation |

---

## 23. Infrastructure & Utility — البنية التحتية

Low-level enums used across multiple modules for cell representation,
Unicode profiling, element classification, signal handling, and similar
infrastructure concerns.

| Enum | Line | Values | Purpose |
|------|------|--------|---------|
| `CellType` | 387 | Cell type values | Internal cell representation type |
| `FuncTransitionClass` | 459 | Functional transition classes | Functional transition classification |
| `ReversibleValue` | 482 | `TRUE`, `FALSE`, `UNKNOWN` | Three-valued reversible logic |
| `ConditionToken` | 490 | Condition token types | Token type in a condition expression |
| `ElementClass` | 584 | Element classes | Element classification |
| `ElementLayer` | 594 | Element layers | Element layer assignment |
| `ElementFunction` | 603 | Element functions | Element functional role |
| `CombinationType` | 615 | Combination types | How elements combine |
| `UnicodeProfileType` | 624 | Unicode profile types | Unicode character profile |
| `SlotState` | 644 | Slot states | State of a structural slot |
| `SignalType` | 1724 | Signal type values | Type of signal in the signal layer |
| `ActivationStage` | 1671 | Activation stages | Stage of cognitive activation |
| `InsertionPolicy` | 1542 | Insertion policies | Policy for inserting new entries |
| `ContaminationLevel` | 1551 | Contamination levels | Data contamination assessment |
| `RealityKind` | 1560 | Reality kinds | Kind of reality (actual, possible, etc.) |
| `CarrierType` | 1573 | Carrier types | Type of information carrier |
| `DecisionCode` | 1581 | Decision codes | General decision code |
| `InfoKind` | 1603 | Information kinds | Kind of information |
| `RationalSelfKind` | 1617 | Rational-self kinds | Kind of rational self |

---

## 24. Cross-Domain Mappings — الروابط بين المجالات

Several enum families participate in explicit **status-mapping chains**
that translate decisions from one domain into another.  All mappings are
codified in `core/types.py` (`STATUS_MAPPINGS` dict) and documented
formally in [`docs/unified_state_model.md`](unified_state_model.md).

### Mapping Chain Overview

```
TransitionGateStatus ──→ LayerGateDecision ──→ PipelineStatus
       (7-layer)              (per-layer gate)        (final result)

HypothesisStatus ──────→ LayerGateDecision ──→ PipelineStatus
   (hypothesis lifecycle)      (per-layer gate)       (final result)

ValidationState ───────────────────────────→ PipelineStatus
   (epistemic validation)                         (final result)
```

### Detailed Mapping Tables

**TransitionGateStatus → LayerGateDecision:**

| TransitionGateStatus | LayerGateDecision | Note |
|----------------------|-------------------|------|
| `PASSED` | `PASS` | Transition allowed |
| `BLOCKED` | `REJECT` | Transition blocked |
| `INSUFFICIENT_DATA` | `SUSPEND` | Cannot decide yet |

**LayerGateDecision → PipelineStatus:**

| LayerGateDecision | PipelineStatus | Note |
|-------------------|----------------|------|
| `PASS` | `SUCCESS` (continues) | Layer succeeded, chain continues |
| `COMPLETE` | `SUCCESS` (final) | Final layer completed |
| `SUSPEND` | `SUSPEND` | Incomplete output |
| `REJECT` | `FAILURE` | Blocking error, chain halts |

**HypothesisStatus → LayerGateDecision:**

| HypothesisStatus | LayerGateDecision | Note |
|------------------|-------------------|------|
| `ACTIVE` | `PASS` | Hypothesis is live |
| `STABILIZED` | `COMPLETE` | Hypothesis confirmed |
| `SUSPENDED` | `SUSPEND` | Hypothesis paused |
| `PRUNED` | `REJECT` | Hypothesis eliminated |
| `REVISED` | `PASS` | Hypothesis updated, continues |

**ValidationState → PipelineStatus:**

| ValidationState | PipelineStatus | Note |
|-----------------|----------------|------|
| `VALID` | `SUCCESS` | Epistemically verified |
| `PENDING` | `SUSPEND` | Awaiting further validation |
| `INVALID` | `FAILURE` | Epistemically rejected |

---

## 25. Domain Boundaries — حدود المجالات

### Principle — المبدأ

> **Each enum serves exactly one domain.**  Enums are never merged across
> domains, even when their value names look similar (e.g., `SUSPEND`
> appears in `PipelineStatus`, `LayerGateDecision`, `HypothesisStatus`,
> and `AdmissibilityDecision` — but each carries domain-specific semantics).

### Why Separate Domains? — لماذا مجالات منفصلة؟

1. **Type safety** — distinct enum types prevent accidental comparison
   across domains at the Python type level.
2. **Independent evolution** — adding a value to `HypothesisStatus`
   does not require changes to `PipelineStatus`.
3. **Explicit mapping** — cross-domain translations are always
   documented and codified (see §24), never implicit.
4. **Testability** — `tests/test_state_mapping.py` verifies that all
   declared mappings remain consistent after any change.

### Domain Assignment Rules — قواعد تعيين المجال

| Rule | Description |
|------|-------------|
| **Single ownership** | Every enum class belongs to exactly one domain section in this document. |
| **No re-export aliasing** | Enums are not re-exported under different names in other domains. |
| **Mapping, not merging** | When two domains need interop, a mapping function is used — enums are never combined into a single type. |
| **Contracts enforce boundaries** | `contracts.yaml` declares which enum types each pipeline layer may consume or produce. |

### Quick Domain Lookup — بحث سريع عن المجال

| If you are working on… | Look at domain… |
|------------------------|-----------------|
| Pipeline gating / status | §1 Pipeline State & Control |
| Input admissibility | §2 Pre-U₀ Admissibility |
| Which layer am I in? | §3 Layer Identification |
| POS tagging, case, role | §4 Linguistic Core |
| Sound patterns, phonemes | §5 Phonological Analysis |
| Roots, patterns, affixes | §6 Morphological Analysis |
| Dependency parsing | §7 Syntactic Analysis |
| Ḥarakāt, syllable weight | §8 Diacritics & Syllables |
| Signifier ↔ signified | §9 Signification & Dalāla |
| Ontological categories | §10 Ontological Classification |
| Certainty, trust, evidence | §11 Epistemics & Validation |
| Derivational direction | §12 Semantic Direction |
| Morphological weight | §13 Weight Fractal |
| Verbal nouns / masdar | §14 Masdar & Derivation |
| Receiver modelling | §15 Reception & Receiver |
| 20-dim concept model | §16 Concept Formation |
| Judgements, proofs | §17 Judgement & Proof |
| Discourse structure | §18 Discourse & Communication |
| Hypothesis lifecycle | §19 Hypothesis & Constraints |
| 7-layer element nodes | §20 7-Layer Element Analysis |
| Semantic frames | §21 Semantic Structuring |
| Reasoning modes | §22 Cognitive Mediation |
| Utility / infra enums | §23 Infrastructure & Utility |

---

*Source file: `arabic_engine/core/enums.py`*
*Cross-domain mappings: [`docs/unified_state_model.md`](unified_state_model.md)*
*Layer contracts: `arabic_engine/contracts.yaml`*
