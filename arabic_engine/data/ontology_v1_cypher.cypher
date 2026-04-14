// ─────────────────────────────────────────────────────────────────────────────
// Ontology v1.0 — Neo4j Cypher Schema
// الجدول الأنطولوجي v1.0 — مخطط Neo4j
//
// Node labels
//   :Signifier   — الدال
//   :Signified   — المدلول
//   :Constraint  — القيد
//
// Relationship types
//   [:COUPLED_BY]     — علاقة الاقتران  (Signifier → Signified)
//   [:HAS_CONSTRAINT] — القيد           (COUPLED_BY → Constraint)
// ─────────────────────────────────────────────────────────────────────────────

// ── Constraints (unique IDs) ──────────────────────────────────────────────────

CREATE CONSTRAINT signifier_id IF NOT EXISTS
    FOR (s:Signifier) REQUIRE s.node_id IS UNIQUE;

CREATE CONSTRAINT signified_id IF NOT EXISTS
    FOR (d:Signified) REQUIRE d.node_id IS UNIQUE;

CREATE CONSTRAINT constraint_id IF NOT EXISTS
    FOR (c:Constraint) REQUIRE c.constraint_id IS UNIQUE;

CREATE CONSTRAINT ontology_record_id IF NOT EXISTS
    FOR (r:OntologyRecord) REQUIRE r.record_id IS UNIQUE;

// ── Indexes ───────────────────────────────────────────────────────────────────

CREATE INDEX signifier_class_idx IF NOT EXISTS
    FOR (s:Signifier) ON (s.signifier_class);

CREATE INDEX uttered_form_class_idx IF NOT EXISTS
    FOR (s:Signifier) ON (s.uttered_form_class);

CREATE INDEX signified_class_idx IF NOT EXISTS
    FOR (d:Signified) ON (d.signified_class);

CREATE INDEX conceptual_class_idx IF NOT EXISTS
    FOR (d:Signified) ON (d.conceptual_class);

CREATE INDEX coupling_type_idx IF NOT EXISTS
    FOR ()-[r:COUPLED_BY]-() ON (r.coupling_type);

CREATE INDEX constraint_type_idx IF NOT EXISTS
    FOR (c:Constraint) ON (c.constraint_type);

CREATE INDEX constraint_passes_idx IF NOT EXISTS
    FOR (c:Constraint) ON (c.passes);

// ── Example: create a :Signifier node ────────────────────────────────────────
//
//   MERGE (sig:Signifier {node_id: 'SIG_001'})
//   SET sig.signifier_class    = 'UTTERED_FORM',
//       sig.uttered_form_class = 'WORD_UTTERANCE',
//       sig.surface            = 'الأَسَد',
//       sig.layer              = 'ROOT',
//       sig.notes              = ''

// ── Example: create a :Signified node ────────────────────────────────────────
//
//   MERGE (sfd:Signified {node_id: 'SFD_001'})
//   SET sfd.signified_class  = 'CONCEPTUAL',
//       sfd.conceptual_class = 'ENTITY_CONCEPT',
//       sfd.label            = 'أسد',
//       sfd.semantic_type    = 'ENTITY',
//       sfd.notes            = ''

// ── Example: create a [:COUPLED_BY] relationship ─────────────────────────────
//
//   MATCH (sig:Signifier {node_id: 'SIG_001'}),
//         (sfd:Signified {node_id: 'SFD_001'})
//   MERGE (sig)-[r:COUPLED_BY {coupling_id: 'CRP_001'}]->(sfd)
//   SET r.coupling_type = 'DIRECT',
//       r.confidence    = 1.0,
//       r.evidence      = 'MUTABAQA'

// ── Example: create a :Constraint node and attach to coupling ─────────────────
//
//   MATCH (sig:Signifier {node_id: 'SIG_001'})-[r:COUPLED_BY]->(sfd:Signified)
//   MERGE (con:Constraint {constraint_id: 'CON_001'})
//   SET con.constraint_type      = 'STRUCTURAL',
//       con.utterance_constraint = 'SURFACE_VALIDITY',
//       con.description_ar       = 'هل المنطوق سليم في بنيته؟',
//       con.passes               = true,
//       con.violated_by          = ''
//   MERGE (sig)-[:HAS_CONSTRAINT {coupling_id: r.coupling_id}]->(con)

// ── Example: create an :OntologyRecord node ──────────────────────────────────
//
//   MATCH (sig:Signifier {node_id: 'SIG_001'}),
//         (sfd:Signified {node_id: 'SFD_001'}),
//         (sig)-[r:COUPLED_BY]->(sfd)
//   MERGE (ont:OntologyRecord {record_id: 'ONT_001'})
//   SET ont.valid = true,
//       ont.notes = ''
//   MERGE (ont)-[:HAS_SIGNIFIER]->(sig)
//   MERGE (ont)-[:HAS_SIGNIFIED]->(sfd)
//   SET ont.coupling_id = r.coupling_id

// ── Useful queries ────────────────────────────────────────────────────────────

// All records whose constraints all pass:
//   MATCH (sig:Signifier)-[r:COUPLED_BY]->(sfd:Signified)
//   WHERE NOT EXISTS {
//       MATCH (sig)-[:HAS_CONSTRAINT]->(c:Constraint)
//       WHERE c.passes = false
//   }
//   RETURN sig.surface, sfd.label, r.coupling_type

// All figurative couplings:
//   MATCH (sig:Signifier)-[r:COUPLED_BY {coupling_type:'FIGURATIVE'}]->(sfd:Signified)
//   RETURN sig.surface, sfd.label, r.confidence

// All referential signifieds with their antecedents:
//   MATCH (sig:Signifier)-[:COUPLED_BY]->(sfd:Signified {signified_class:'REFERENTIAL'})
//   RETURN sig.surface, sfd.label

// Find violated constraints for a specific record:
//   MATCH (sig:Signifier)-[:HAS_CONSTRAINT]->(c:Constraint)
//   WHERE sig.node_id = 'SIG_001' AND c.passes = false
//   RETURN c.constraint_type, c.violated_by
