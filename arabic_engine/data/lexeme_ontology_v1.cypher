// lexeme_ontology_v1.cypher — Lexeme Epistemic Core graph schema
//
// Defines the node types and edge types for the Rational Self Ontology v1
// Lexeme Epistemic Core as a Neo4j graph schema.

// ── Node Constraints ─────────────────────────────────────────────────────

CREATE CONSTRAINT lexeme_unicode_unit_id IF NOT EXISTS
FOR (u:UnicodeUnit) REQUIRE u.id IS UNIQUE;

CREATE CONSTRAINT lexeme_grapheme_unit_id IF NOT EXISTS
FOR (g:GraphemeUnit) REQUIRE g.id IS UNIQUE;

CREATE CONSTRAINT lexeme_phono_unit_id IF NOT EXISTS
FOR (p:PhonoUnit) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT lexeme_haraka_unit_id IF NOT EXISTS
FOR (h:HarakaUnit) REQUIRE h.id IS UNIQUE;

CREATE CONSTRAINT lexeme_bare_material_id IF NOT EXISTS
FOR (b:BareLexicalMaterial) REQUIRE b.id IS UNIQUE;

CREATE CONSTRAINT lexeme_root_node_id IF NOT EXISTS
FOR (r:RootNode) REQUIRE r.id IS UNIQUE;

CREATE CONSTRAINT lexeme_weight_node_id IF NOT EXISTS
FOR (w:WeightNode) REQUIRE w.id IS UNIQUE;

CREATE CONSTRAINT lexeme_closed_template_id IF NOT EXISTS
FOR (ct:ClosedTemplateNode) REQUIRE ct.id IS UNIQUE;

CREATE CONSTRAINT lexeme_lexeme_node_id IF NOT EXISTS
FOR (l:LexemeNode) REQUIRE l.id IS UNIQUE;

CREATE CONSTRAINT lexeme_concept_node_id IF NOT EXISTS
FOR (c:ConceptNode) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT lexeme_noun_node_ref IF NOT EXISTS
FOR (n:NounNode) REQUIRE n.lexeme_ref IS NOT NULL;

CREATE CONSTRAINT lexeme_verb_node_ref IF NOT EXISTS
FOR (v:VerbNode) REQUIRE v.lexeme_ref IS NOT NULL;

CREATE CONSTRAINT lexeme_particle_node_ref IF NOT EXISTS
FOR (p:ParticleNode) REQUIRE p.lexeme_ref IS NOT NULL;

CREATE CONSTRAINT lexeme_derived_node_ref IF NOT EXISTS
FOR (d:DerivedNode) REQUIRE d.lexeme_ref IS NOT NULL;

CREATE CONSTRAINT lexeme_jamid_node_ref IF NOT EXISTS
FOR (j:JamidNode) REQUIRE j.lexeme_ref IS NOT NULL;

CREATE CONSTRAINT lexeme_actional_node_id IF NOT EXISTS
FOR (a:ActionalityNode) REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT lexeme_referential_node_id IF NOT EXISTS
FOR (r:ReferentialNode) REQUIRE r.id IS UNIQUE;

CREATE CONSTRAINT lexeme_relational_node_id IF NOT EXISTS
FOR (r:RelationalNode) REQUIRE r.id IS UNIQUE;

CREATE CONSTRAINT lexeme_composition_ready_ref IF NOT EXISTS
FOR (cr:CompositionReadyNode) REQUIRE cr.lexeme_ref IS NOT NULL;

// ── Edge Type Examples ───────────────────────────────────────────────────
//
// ENCODES:             (u:UnicodeUnit)-[:ENCODES]->(g:GraphemeUnit)
// REALIZES:            (g:GraphemeUnit)-[:REALIZES]->(p:PhonoUnit)
// MODULATES:           (h:HarakaUnit)-[:MODULATES]->(p:PhonoUnit)
// FORMS_MATERIAL:      (g:GraphemeUnit)-[:FORMS_MATERIAL]->(b:BareLexicalMaterial)
// INSTANTIATES_ROOT:   (b:BareLexicalMaterial)-[:INSTANTIATES_ROOT]->(r:RootNode)
// INSTANTIATES_WEIGHT: (b:BareLexicalMaterial)-[:INSTANTIATES_WEIGHT]->(w:WeightNode)
// FILLS_TEMPLATE:      (r:RootNode)-[:FILLS_TEMPLATE]->(w:WeightNode)
// STABILIZES_AS:       (w:WeightNode)-[:STABILIZES_AS]->(l:LexemeNode)
// TYPED_AS:            (l:LexemeNode)-[:TYPED_AS]->(c:ConceptNode)
// FINALIZED_AS:        (l:LexemeNode)-[:FINALIZED_AS]->(n:NounNode|v:VerbNode|p:ParticleNode)
// DERIVED_FROM:        (d:DerivedNode)-[:DERIVED_FROM]->(r:RootNode)
// REFERS_TO:           (n:NounNode)-[:REFERS_TO]->(r:ReferentialNode)
// DENOTES_EVENT:       (v:VerbNode)-[:DENOTES_EVENT]->(a:ActionalityNode)
// BINDS_RELATION:      (p:ParticleNode)-[:BINDS_RELATION]->(r:RelationalNode)
// PREPARES_FOR:        (l:LexemeNode)-[:PREPARES_FOR]->(cr:CompositionReadyNode)
// RECOVERS_TO:         (any)-[:RECOVERS_TO]->(lower layer node)
// DESIGNATES:          (s:Self)-[:DESIGNATES]->(l:LexemeNode)
// INTENDS_COMPOSITION: (s:Self)-[:INTENDS_COMPOSITION]->(cr:CompositionReadyNode)
