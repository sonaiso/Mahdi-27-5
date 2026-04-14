// seed.cypher — بذور Neo4j للمنهج العقلي
//
// Bootstraps the default MethodRecord and ConflictRule nodes that the
// epistemic_v1 validator uses as default values.
//
// Run AFTER schema.cypher.

// ── Default Methods ───────────────────────────────────────────────────────

MERGE (m1:MethodRecord {method_id: "METHOD_RATIONAL"})
ON CREATE SET
  m1.family       = "RATIONAL",
  m1.name         = "الطريقة العقلية — the universal rational method",
  m1.domain_fit   = ["EXISTENCE", "ESSENCE", "ATTRIBUTE", "RELATION",
                     "INTERPRETIVE", "FORMAL_CONTRADICTION"];

MERGE (m2:MethodRecord {method_id: "METHOD_SCIENTIFIC"})
ON CREATE SET
  m2.family       = "SCIENTIFIC",
  m2.name         = "الطريقة العلمية — empirical material inquiry only",
  m2.domain_fit   = ["EXISTENCE"];

MERGE (m3:MethodRecord {method_id: "METHOD_TEXTUAL"})
ON CREATE SET
  m3.family       = "TEXTUAL",
  m3.name         = "الطريقة النقلية — transmission-based",
  m3.domain_fit   = ["EXISTENCE", "ESSENCE", "ATTRIBUTE", "RELATION",
                     "INTERPRETIVE"];

MERGE (m4:MethodRecord {method_id: "METHOD_DEDUCTIVE"})
ON CREATE SET
  m4.family       = "DEDUCTIVE",
  m4.name         = "الطريقة الاستنباطية — formal deduction",
  m4.domain_fit   = ["EXISTENCE", "ESSENCE", "ATTRIBUTE", "RELATION",
                     "INTERPRETIVE", "FORMAL_CONTRADICTION"];

MERGE (m5:MethodRecord {method_id: "METHOD_INDUCTIVE"})
ON CREATE SET
  m5.family       = "INDUCTIVE",
  m5.name         = "الطريقة الاستقرائية — induction from instances",
  m5.domain_fit   = ["EXISTENCE", "ATTRIBUTE", "RELATION"];

// ── Default Conflict Rule ─────────────────────────────────────────────────

MERGE (cr:ConflictRule {rule_id: "CR_DEFAULT_CONCEPT_WINS"})
ON CREATE SET
  cr.prefer_concept = true,
  cr.rationale      = "المفهوم مقدّم على المنطوق عند التعارض — "
                      "concept takes precedence over utterance by default";
