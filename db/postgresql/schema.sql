-- ============================================================================
-- Arabic Engine — PostgreSQL Schema (v1)
-- مخطط قاعدة البيانات — المحرك العربي
--
-- Tables:
--   lexicon_entries    — المعجم: root/pattern/lemma/POS
--   concept_nodes      — المفاهيم: ontological concept nodes
--   dalala_rules       — قواعد الدلالة: signification rules
--   inference_rules    — قواعد الاستدلال: inference rule definitions
--   layer_traces       — أثر الطبقات: unified processing traces
--   analysis_sessions  — جلسات التحليل: analysis session metadata
--   world_facts        — حقائق النموذج العالمي: world model facts
-- ============================================================================

-- ── Lexicon ────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS lexicon_entries (
    id          SERIAL PRIMARY KEY,
    root        TEXT[]       NOT NULL,           -- consonantal root e.g. {"ك","ت","ب"}
    pattern     TEXT         NOT NULL DEFAULT '', -- morphological pattern e.g. "فَعَلَ"
    lemma       TEXT         NOT NULL,           -- dictionary form
    pos         TEXT         NOT NULL DEFAULT 'UNKNOWN', -- POS enum name
    features    JSONB        NOT NULL DEFAULT '{}',
    frequency   INTEGER      NOT NULL DEFAULT 0,
    base_meaning TEXT        NOT NULL DEFAULT '',
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (root, pattern, lemma)
);

CREATE INDEX idx_lexicon_root ON lexicon_entries USING GIN (root);
CREATE INDEX idx_lexicon_lemma ON lexicon_entries (lemma);

-- ── Concept Nodes ──────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS concept_nodes (
    id              SERIAL PRIMARY KEY,
    concept_id      TEXT         NOT NULL UNIQUE,
    label           TEXT         NOT NULL,
    semantic_type   TEXT         NOT NULL DEFAULT 'ENTITY',
    properties      JSONB        NOT NULL DEFAULT '{}',
    parent_id       TEXT,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_concept_label ON concept_nodes (label);
CREATE INDEX idx_concept_type ON concept_nodes (semantic_type);

-- ── Dalala Rules ───────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS dalala_rules (
    id              SERIAL PRIMARY KEY,
    signifier       TEXT         NOT NULL,
    signified       TEXT         NOT NULL,
    dalala_type     TEXT         NOT NULL,  -- MUTABAQA / TADAMMUN / ILTIZAM / ISNAD
    confidence      FLOAT        NOT NULL DEFAULT 1.0,
    conditions      JSONB        NOT NULL DEFAULT '[]',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_dalala_signifier ON dalala_rules (signifier);

-- ── Inference Rules ────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS inference_rules (
    id              SERIAL PRIMARY KEY,
    rule_name       TEXT         NOT NULL UNIQUE,
    rule_type       TEXT         NOT NULL DEFAULT 'FORWARD_CHAIN',
    premises        JSONB        NOT NULL DEFAULT '[]',
    conclusion      JSONB        NOT NULL DEFAULT '{}',
    confidence      FLOAT        NOT NULL DEFAULT 1.0,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ── Layer Traces ───────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS layer_traces (
    id              SERIAL PRIMARY KEY,
    request_id      UUID         NOT NULL,
    layer_id        VARCHAR(4)   NOT NULL,  -- E1/E2/.../E8
    layer_name      VARCHAR(50)  NOT NULL,
    input_hash      VARCHAR(64)  NOT NULL,
    input_summary   TEXT,
    output_summary  TEXT,
    rules_applied   JSONB        NOT NULL DEFAULT '[]',
    confidence      FLOAT,
    duration_ms     FLOAT,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    metadata        JSONB        NOT NULL DEFAULT '{}'
);

CREATE INDEX idx_trace_request ON layer_traces (request_id);
CREATE INDEX idx_trace_layer ON layer_traces (layer_id);
CREATE INDEX idx_trace_created ON layer_traces (created_at);

-- ── Analysis Sessions ──────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS analysis_sessions (
    id              SERIAL PRIMARY KEY,
    session_id      UUID         NOT NULL UNIQUE,
    input_text      TEXT         NOT NULL,
    started_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    status          TEXT         NOT NULL DEFAULT 'IN_PROGRESS',
    result_summary  JSONB,
    error_message   TEXT
);

CREATE INDEX idx_session_status ON analysis_sessions (status);

-- ── World Facts ────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS world_facts (
    id              SERIAL PRIMARY KEY,
    subject         TEXT         NOT NULL,
    predicate       TEXT         NOT NULL,
    object          TEXT,
    confidence      FLOAT        NOT NULL DEFAULT 1.0,
    source          TEXT         NOT NULL DEFAULT 'manual',
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_fact_subject ON world_facts (subject);
CREATE INDEX idx_fact_predicate ON world_facts (predicate);
