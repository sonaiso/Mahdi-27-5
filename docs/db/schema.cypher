// schema.cypher — قيود مخطط Neo4j للمنهج العقلي
//
// This file contains ONLY uniqueness and existence constraints.
// Validation logic lives in Python (epistemic_v1.py); this file
// mirrors the node model it uses.
//
// Run once on an empty database to set up the schema.

// ── KnowledgeEpisode ─────────────────────────────────────────────────────
CREATE CONSTRAINT episode_id_unique IF NOT EXISTS
FOR (e:KnowledgeEpisode) REQUIRE e.episode_id IS UNIQUE;

CREATE CONSTRAINT episode_id_exists IF NOT EXISTS
FOR (e:KnowledgeEpisode) REQUIRE e.episode_id IS NOT NULL;

// ── RealityAnchor ────────────────────────────────────────────────────────
CREATE CONSTRAINT reality_anchor_id_unique IF NOT EXISTS
FOR (r:RealityAnchor) REQUIRE r.anchor_id IS UNIQUE;

CREATE CONSTRAINT reality_anchor_kind_exists IF NOT EXISTS
FOR (r:RealityAnchor) REQUIRE r.kind IS NOT NULL;

// ── SenseTrace ───────────────────────────────────────────────────────────
CREATE CONSTRAINT sense_trace_id_unique IF NOT EXISTS
FOR (s:SenseTrace) REQUIRE s.trace_id IS UNIQUE;

CREATE CONSTRAINT sense_trace_modality_exists IF NOT EXISTS
FOR (s:SenseTrace) REQUIRE s.modality IS NOT NULL;

// ── PriorInfo ────────────────────────────────────────────────────────────
CREATE CONSTRAINT prior_info_id_unique IF NOT EXISTS
FOR (p:PriorInfo) REQUIRE p.info_id IS UNIQUE;

// ── OpinionTrace ─────────────────────────────────────────────────────────
CREATE CONSTRAINT opinion_trace_id_unique IF NOT EXISTS
FOR (o:OpinionTrace) REQUIRE o.opinion_id IS UNIQUE;

// ── LinkingTrace ─────────────────────────────────────────────────────────
CREATE CONSTRAINT linking_trace_id_unique IF NOT EXISTS
FOR (l:LinkingTrace) REQUIRE l.link_id IS UNIQUE;

// ── JudgementRecord ──────────────────────────────────────────────────────
CREATE CONSTRAINT judgement_id_unique IF NOT EXISTS
FOR (j:JudgementRecord) REQUIRE j.judgement_id IS UNIQUE;

CREATE CONSTRAINT judgement_type_exists IF NOT EXISTS
FOR (j:JudgementRecord) REQUIRE j.judgement_type IS NOT NULL;

// ── MethodRecord ─────────────────────────────────────────────────────────
CREATE CONSTRAINT method_id_unique IF NOT EXISTS
FOR (m:MethodRecord) REQUIRE m.method_id IS UNIQUE;

CREATE CONSTRAINT method_family_exists IF NOT EXISTS
FOR (m:MethodRecord) REQUIRE m.family IS NOT NULL;

// ── LinguisticCarrier ────────────────────────────────────────────────────
CREATE CONSTRAINT carrier_id_unique IF NOT EXISTS
FOR (c:LinguisticCarrier) REQUIRE c.carrier_id IS UNIQUE;

CREATE CONSTRAINT carrier_type_exists IF NOT EXISTS
FOR (c:LinguisticCarrier) REQUIRE c.carrier_type IS NOT NULL;

// ── ProofPath ────────────────────────────────────────────────────────────
CREATE CONSTRAINT proof_path_id_unique IF NOT EXISTS
FOR (pp:ProofPath) REQUIRE pp.path_id IS UNIQUE;

// ── ConflictRule ─────────────────────────────────────────────────────────
CREATE CONSTRAINT conflict_rule_id_unique IF NOT EXISTS
FOR (cr:ConflictRule) REQUIRE cr.rule_id IS UNIQUE;

// ── ValidationResult ─────────────────────────────────────────────────────
CREATE CONSTRAINT validation_result_episode_id_unique IF NOT EXISTS
FOR (vr:ValidationResult) REQUIRE vr.episode_id IS UNIQUE;
