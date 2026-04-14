-- ─────────────────────────────────────────────────────────────────────────────
-- Ontology v1.0 — Relational Schema (Laravel-compatible MySQL / PostgreSQL)
-- الجدول الأنطولوجي v1.0 — مخطط العلاقات
--
-- Tables
--   signifier_nodes         الدال
--   signified_nodes         المدلول
--   coupling_records        علاقة الاقتران
--   ontological_constraints القيود
--   ontology_v1_records     السجل الرئيسي
-- ─────────────────────────────────────────────────────────────────────────────

-- ── Enum types ──────────────────────────────────────────────────────────────

-- SignifierClass (صنف الدال)
-- Values: PHONOLOGICAL | MORPHOLOGICAL | LEXICAL | SYNTACTIC |
--         TEXTUAL | PRAGMATIC | RHETORICAL | UTTERED_FORM

-- UtteredFormClass (صنف المنطوق)
-- Values: PHONETIC_UTTERANCE | WORD_UTTERANCE | EXPRESSION_UTTERANCE |
--         SENTENCE_UTTERANCE | MARKED_UTTERANCE

-- SignifiedClass (صنف المدلول)
-- Values: ONTOLOGICAL | PROPERTY | EVENT | RELATIONAL | PROPOSITIONAL |
--         REFERENTIAL | FUNCTIONAL | PRAGMATIC_SIGNIFIED | LOGICAL |
--         RHETORICAL_SIGNIFIED | EPISTEMIC | NORMATIVE | AFFECTIVE |
--         MODAL | INSTITUTIONAL | EMBODIED | SELF_MODEL | FRAME |
--         SCRIPT | CAUSAL_EXPLANATORY | META_CONCEPTUAL | CONCEPTUAL

-- ConceptualSignifiedClass (صنف المفهوم)
-- Values: ENTITY_CONCEPT | PROPERTY_CONCEPT | EVENT_CONCEPT | RELATION_CONCEPT |
--         NORM_CONCEPT | MENTAL_CONCEPT | ABSTRACT_CONCEPT | META_CONCEPT

-- CouplingRelationType (نوع علاقة الاقتران)
-- Values: DIRECT | POLYSEMOUS | COMPOSITIONAL | HIERARCHICAL | CONTEXTUAL |
--         INFERENTIAL | FIGURATIVE | PERFORMATIVE | FUNCTIONAL_COUPLING |
--         REFERENTIAL_COUPLING

-- OntologicalConstraintType (نوع القيد الأنطولوجي)
-- Values: STRUCTURAL | PHONOLOGICAL_CONSTRAINT | MORPHOLOGICAL_CONSTRAINT |
--         LEXICAL_CONSTRAINT | SYNTACTIC_CONSTRAINT | REFERENTIAL_CONSTRAINT |
--         CONTEXTUAL_CONSTRAINT | PRAGMATIC_CONSTRAINT | LOGICAL_CONSTRAINT |
--         RHETORICAL_CONSTRAINT | EPISTEMIC_CONSTRAINT |
--         INSTITUTIONAL_CONSTRAINT | INTERPRETIVE_CONSTRAINT

-- UtteranceToConceptConstraint (قيود سلسلة المنطوق→المفهوم)
-- Values: SURFACE_VALIDITY | LEXICAL_ACCESS | CONTEXT_RESOLUTION |
--         CONCEPT_SELECTION | FIGURATIVE_DISAMBIGUATION |
--         REFERENTIAL_RESOLUTION | LOGICAL_COHERENCE

-- OntologicalLayer (الطبقة الوجودية — reused from existing schema)
-- Values: CELL | TRANSITION | SYLLABLE | ROOT | PATTERN

-- ── signifier_nodes ─────────────────────────────────────────────────────────

CREATE TABLE signifier_nodes (
    id              VARCHAR(16)  NOT NULL,          -- e.g. SIG_001
    signifier_class VARCHAR(32)  NOT NULL,          -- SignifierClass enum
    uttered_form_class VARCHAR(32) DEFAULT NULL,    -- UtteredFormClass (nullable)
    surface         TEXT         NOT NULL,
    layer           VARCHAR(16)  NOT NULL,          -- OntologicalLayer enum
    notes           TEXT         NOT NULL DEFAULT '',
    created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_signifier_class (signifier_class),
    INDEX idx_uttered_form_class (uttered_form_class),
    INDEX idx_layer (layer)
);

-- ── signified_nodes ─────────────────────────────────────────────────────────

CREATE TABLE signified_nodes (
    id                  VARCHAR(16)  NOT NULL,      -- e.g. SFD_001
    signified_class     VARCHAR(32)  NOT NULL,      -- SignifiedClass enum
    conceptual_class    VARCHAR(32)  DEFAULT NULL,  -- ConceptualSignifiedClass (nullable)
    label               TEXT         NOT NULL,
    semantic_type       VARCHAR(16)  NOT NULL,      -- SemanticType enum (existing)
    properties          JSON         NOT NULL,      -- arbitrary key/value metadata
    notes               TEXT         NOT NULL DEFAULT '',
    created_at          TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_signified_class (signified_class),
    INDEX idx_conceptual_class (conceptual_class),
    INDEX idx_semantic_type (semantic_type)
);

-- ── coupling_records ────────────────────────────────────────────────────────

CREATE TABLE coupling_records (
    id               VARCHAR(16)   NOT NULL,        -- e.g. CRP_001
    coupling_type    VARCHAR(32)   NOT NULL,        -- CouplingRelationType enum
    signifier_id     VARCHAR(16)   NOT NULL,        -- FK → signifier_nodes.id
    signified_id     VARCHAR(16)   NOT NULL,        -- FK → signified_nodes.id
    confidence       DECIMAL(5,4)  NOT NULL DEFAULT 1.0,
    evidence         TEXT          NOT NULL DEFAULT '',
    created_at       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_coupling_type (coupling_type),
    INDEX idx_signifier_id (signifier_id),
    INDEX idx_signified_id (signified_id),

    CONSTRAINT fk_coupling_signifier
        FOREIGN KEY (signifier_id) REFERENCES signifier_nodes (id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_coupling_signified
        FOREIGN KEY (signified_id) REFERENCES signified_nodes (id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ── ontological_constraints ─────────────────────────────────────────────────

CREATE TABLE ontological_constraints (
    id                   VARCHAR(16)  NOT NULL,     -- e.g. CON_001
    coupling_id          VARCHAR(16)  NOT NULL,     -- FK → coupling_records.id
    constraint_type      VARCHAR(32)  NOT NULL,     -- OntologicalConstraintType enum
    utterance_constraint VARCHAR(32)  DEFAULT NULL, -- UtteranceToConceptConstraint (nullable)
    description_ar       TEXT         NOT NULL,
    passes               TINYINT(1)   NOT NULL DEFAULT 1,
    violated_by          TEXT         NOT NULL DEFAULT '',
    created_at           TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_constraint_coupling (coupling_id),
    INDEX idx_constraint_type (constraint_type),
    INDEX idx_passes (passes),

    CONSTRAINT fk_constraint_coupling
        FOREIGN KEY (coupling_id) REFERENCES coupling_records (id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ── ontology_v1_records ─────────────────────────────────────────────────────

CREATE TABLE ontology_v1_records (
    id            VARCHAR(16)  NOT NULL,            -- e.g. ONT_001
    signifier_id  VARCHAR(16)  NOT NULL,            -- FK → signifier_nodes.id
    signified_id  VARCHAR(16)  NOT NULL,            -- FK → signified_nodes.id
    coupling_id   VARCHAR(16)  NOT NULL,            -- FK → coupling_records.id
    valid         TINYINT(1)   NOT NULL DEFAULT 1,
    notes         TEXT         NOT NULL DEFAULT '',
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_valid (valid),
    INDEX idx_ont_signifier (signifier_id),
    INDEX idx_ont_signified (signified_id),
    INDEX idx_ont_coupling (coupling_id),

    CONSTRAINT fk_ont_signifier
        FOREIGN KEY (signifier_id) REFERENCES signifier_nodes (id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_ont_signified
        FOREIGN KEY (signified_id) REFERENCES signified_nodes (id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_ont_coupling
        FOREIGN KEY (coupling_id) REFERENCES coupling_records (id)
        ON DELETE CASCADE ON UPDATE CASCADE
);
