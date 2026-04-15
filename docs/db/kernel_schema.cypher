// kernel_schema.cypher — canonical Kernel-14 schema (minimal)
// Use this schema as the primary epistemic kernel baseline.

// ── Uniqueness constraints (14 labels only) ────────────────────────────────
CREATE CONSTRAINT kernel_self_id_unique IF NOT EXISTS
FOR (n:Self) REQUIRE n.self_id IS UNIQUE;

CREATE CONSTRAINT kernel_reality_id_unique IF NOT EXISTS
FOR (n:Reality) REQUIRE n.reality_id IS UNIQUE;

CREATE CONSTRAINT kernel_sense_id_unique IF NOT EXISTS
FOR (n:Sense) REQUIRE n.sense_id IS UNIQUE;

CREATE CONSTRAINT kernel_prior_info_id_unique IF NOT EXISTS
FOR (n:PriorInfo) REQUIRE n.prior_info_id IS UNIQUE;

CREATE CONSTRAINT kernel_link_id_unique IF NOT EXISTS
FOR (n:Link) REQUIRE n.link_id IS UNIQUE;

CREATE CONSTRAINT kernel_concept_id_unique IF NOT EXISTS
FOR (n:Concept) REQUIRE n.concept_id IS UNIQUE;

CREATE CONSTRAINT kernel_judgement_id_unique IF NOT EXISTS
FOR (n:Judgement) REQUIRE n.judgement_id IS UNIQUE;

CREATE CONSTRAINT kernel_method_id_unique IF NOT EXISTS
FOR (n:Method) REQUIRE n.method_id IS UNIQUE;

CREATE CONSTRAINT kernel_proof_id_unique IF NOT EXISTS
FOR (n:Proof) REQUIRE n.proof_id IS UNIQUE;

CREATE CONSTRAINT kernel_carrier_id_unique IF NOT EXISTS
FOR (n:Carrier) REQUIRE n.carrier_id IS UNIQUE;

CREATE CONSTRAINT kernel_exchange_id_unique IF NOT EXISTS
FOR (n:Exchange) REQUIRE n.exchange_id IS UNIQUE;

CREATE CONSTRAINT kernel_model_id_unique IF NOT EXISTS
FOR (n:Model) REQUIRE n.model_id IS UNIQUE;

CREATE CONSTRAINT kernel_constraint_id_unique IF NOT EXISTS
FOR (n:Constraint) REQUIRE n.constraint_id IS UNIQUE;

CREATE CONSTRAINT kernel_state_id_unique IF NOT EXISTS
FOR (n:State) REQUIRE n.state_id IS UNIQUE;

// ── Minimal required field existence constraints ───────────────────────────
CREATE CONSTRAINT kernel_self_name_exists IF NOT EXISTS
FOR (n:Self) REQUIRE n.name IS NOT NULL;

CREATE CONSTRAINT kernel_reality_kind_exists IF NOT EXISTS
FOR (n:Reality) REQUIRE n.kind IS NOT NULL;

CREATE CONSTRAINT kernel_sense_modality_exists IF NOT EXISTS
FOR (n:Sense) REQUIRE n.modality IS NOT NULL;

CREATE CONSTRAINT kernel_judgement_type_exists IF NOT EXISTS
FOR (n:Judgement) REQUIRE n.judgement_type IS NOT NULL;

CREATE CONSTRAINT kernel_method_family_exists IF NOT EXISTS
FOR (n:Method) REQUIRE n.family IS NOT NULL;

CREATE CONSTRAINT kernel_proof_kind_exists IF NOT EXISTS
FOR (n:Proof) REQUIRE n.proof_kind IS NOT NULL;

CREATE CONSTRAINT kernel_carrier_type_exists IF NOT EXISTS
FOR (n:Carrier) REQUIRE n.carrier_type IS NOT NULL;

CREATE CONSTRAINT kernel_exchange_type_exists IF NOT EXISTS
FOR (n:Exchange) REQUIRE n.exchange_type IS NOT NULL;

CREATE CONSTRAINT kernel_constraint_type_exists IF NOT EXISTS
FOR (n:Constraint) REQUIRE n.constraint_type IS NOT NULL;

CREATE CONSTRAINT kernel_state_type_exists IF NOT EXISTS
FOR (n:State) REQUIRE n.state_type IS NOT NULL;
