// kernel_seed.cypher — minimal seed for Kernel-14
// Run after db/kernel_schema.cypher

MERGE (self:Self {self_id: "SELF_001"})
ON CREATE SET self.name = "default-self";

MERGE (reality:Reality {reality_id: "REALITY_001"})
ON CREATE SET reality.kind = "material";

MERGE (sense:Sense {sense_id: "SENSE_001"})
ON CREATE SET sense.modality = "visual";

MERGE (prior:PriorInfo {prior_info_id: "PRIOR_001"})
ON CREATE SET prior.source = "seed";

MERGE (link:Link {link_id: "LINK_001"})
ON CREATE SET link.link_kind = "causal";

MERGE (concept:Concept {concept_id: "CONCEPT_001"})
ON CREATE SET concept.label = "seed-concept";

MERGE (judgement:Judgement {judgement_id: "JUDGEMENT_001"})
ON CREATE SET judgement.judgement_type = "existence";

MERGE (method:Method {method_id: "METHOD_001"})
ON CREATE SET method.family = "rational";

MERGE (proof:Proof {proof_id: "PROOF_001"})
ON CREATE SET proof.proof_kind = "aqli";

MERGE (carrier:Carrier {carrier_id: "CARRIER_001"})
ON CREATE SET carrier.carrier_type = "both";

MERGE (exchange:Exchange {exchange_id: "EXCHANGE_001"})
ON CREATE SET exchange.exchange_type = "report";

MERGE (model:Model {model_id: "MODEL_001"})
ON CREATE SET model.name = "seed-model";

MERGE (constraint:Constraint {constraint_id: "CONSTRAINT_001"})
ON CREATE SET constraint.constraint_type = "logical";

MERGE (state:State {state_id: "STATE_001"})
ON CREATE SET state.state_type = "validated";

// Core relationship skeleton
MERGE (self)-[:KNOWS]->(concept);
MERGE (self)-[:EMITS]->(carrier);
MERGE (self)-[:RECEIVES]->(carrier);
MERGE (reality)-[:IS_SENSED_AS]->(sense);
MERGE (sense)-[:IS_INTERPRETED_WITH]->(prior);
MERGE (prior)-[:ARE_BOUND_BY]->(link);
MERGE (link)-[:YIELDS]->(concept);
MERGE (concept)-[:IS_JUDGED_AS]->(judgement);
MERGE (judgement)-[:IS_EVALUATED_BY]->(method);
MERGE (judgement)-[:IS_JUSTIFIED_BY]->(proof);
MERGE (judgement)-[:IS_LIMITED_BY]->(constraint);
MERGE (judgement)-[:HAS_STATE]->(state);
MERGE (concept)-[:ARE_CARRIED_BY]->(carrier);
MERGE (carrier)-[:PARTICIPATES_IN]->(exchange);
MERGE (exchange)-[:INVOLVES]->(self);
MERGE (exchange)-[:FORMS]->(model);
MERGE (model)-[:HAS_STATE]->(state);
