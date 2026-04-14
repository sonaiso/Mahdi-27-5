// validate_episode.cypher — فحص الخبرة المعرفية في Neo4j
//
// Mirrors the Python checks in epistemic_v1.py.  Python is the SOURCE
// OF TRUTH; this file provides equivalent database-level checks for
// reporting and gap-writing only.
//
// Parameters (passed via driver):
//   $episode_id — the episode to validate
//
// Returns one row per gap found (empty result = no gaps = VALID).

MATCH (e:KnowledgeEpisode {episode_id: $episode_id})

// ── Collect the episode components ──────────────────────────────────────
OPTIONAL MATCH (e)-[:HAS_REALITY_ANCHOR]->(ra:RealityAnchor)
OPTIONAL MATCH (e)-[:HAS_SENSE_TRACE]->(st:SenseTrace)
OPTIONAL MATCH (e)-[:HAS_LINKING_TRACE]->(lt:LinkingTrace)
OPTIONAL MATCH (e)-[:HAS_JUDGEMENT]->(j:JudgementRecord)
OPTIONAL MATCH (e)-[:USES_METHOD]->(m:MethodRecord)
OPTIONAL MATCH (e)-[:HAS_CARRIER]->(c:LinguisticCarrier)
OPTIONAL MATCH (e)-[:HAS_PROOF_PATH]->(pp:ProofPath)
OPTIONAL MATCH (e)-[:HAS_CONFLICT_RULE]->(cr:ConflictRule)

// ── Use pattern comprehensions for multi-value relationships ─────────────
// (avoids cartesian product from multiple OPTIONAL MATCHes)
WITH e, ra, st, lt, j, m, c, pp, cr,
     [(e)-[:HAS_PRIOR_INFO]->(pi:PriorInfo) | pi]         AS prior_infos,
     [(e)-[:HAS_OPINION_TRACE]->(ot:OpinionTrace) | ot]   AS opinion_traces

// ── Gap accumulation (mirrors Python validate_episode checks) ────────────
WITH e, ra, st, prior_infos, opinion_traces, lt, j, m, c, pp, cr,
     CASE WHEN ra IS NULL
          THEN [{code: "EPI001_MISSING_REALITY",
                 severity: "FATAL",
                 description: "Missing RealityAnchor"}]
          ELSE [] END +
     CASE WHEN st IS NULL
          THEN [{code: "EPI002_MISSING_SENSE",
                 severity: "FATAL",
                 description: "Missing SenseTrace"}]
          ELSE [] END +
     CASE WHEN size(prior_infos) = 0
          THEN [{code: "EPI003_MISSING_PRIOR_INFO",
                 severity: "FATAL",
                 description: "Missing PriorInfo (at least one required)"}]
          ELSE [] END +
     CASE WHEN any(o IN opinion_traces WHERE o.contamination_level = "HIGH")
          THEN [{code: "EPI004_OPINION_CONTAMINATION",
                 severity: "FATAL",
                 description: "Opinion contamination HIGH detected"}]
          ELSE [] END +
     CASE WHEN lt IS NULL
          THEN [{code: "EPI005_MISSING_LINKING",
                 severity: "FATAL",
                 description: "Missing LinkingTrace"}]
          ELSE [] END +
     CASE WHEN j IS NULL
          THEN [{code: "EPI006_MISSING_JUDGEMENT",
                 severity: "FATAL",
                 description: "Missing JudgementRecord"}]
          ELSE [] END +
     CASE WHEN m IS NULL
          THEN [{code: "EPI007_MISSING_METHOD",
                 severity: "FATAL",
                 description: "Missing MethodRecord"}]
          ELSE [] END +
     CASE WHEN m IS NOT NULL AND j IS NOT NULL
               AND NOT j.judgement_type IN m.domain_fit
          THEN [{code: "EPI008_METHOD_FIT_FAILURE",
                 severity: "CRITICAL",
                 description: "Method does not fit judgement type"}]
          ELSE [] END +
     CASE WHEN c IS NULL
          THEN [{code: "EPI009_CARRIER_INVALID",
                 severity: "FATAL",
                 description: "Missing LinguisticCarrier"}]
          ELSE [] END +
     CASE WHEN pp IS NULL
          THEN [{code: "EPI010_MISSING_PROOF_PATH",
                 severity: "FATAL",
                 description: "Missing ProofPath"}]
          ELSE [] END +
     CASE WHEN cr IS NULL
          THEN [{code: "EPI011_MISSING_CONFLICT_RULE",
                 severity: "FATAL",
                 description: "Missing ConflictRule"}]
          ELSE [] END +
     CASE WHEN c IS NOT NULL AND c.carrier_type = "BOTH"
               AND (
                   NOT EXISTS { (c)-[:HAS_UTTERANCE]->(:Utterance) } OR
                   NOT EXISTS { (c)-[:HAS_CONCEPT]->(:ConceptNode) }
               )
          THEN [{code: "EPI012_CARRIER_BOTH_MISSING",
                 severity: "FATAL",
                 description: "CarrierType BOTH requires both utterance and concept"}]
          ELSE [] END +
     CASE WHEN m IS NOT NULL AND pp IS NOT NULL AND m.family <> pp.method_fit
          THEN [{code: "EPI013_PROOF_METHOD_MISMATCH",
                 severity: "CRITICAL",
                 description: "ProofPath method_fit does not match method family"}]
          ELSE [] END
     AS gaps

UNWIND gaps AS gap

// ── Write gap nodes back to the episode (optional persistence) ───────────
MERGE (g:EpistemicGap {
    gap_id: "GAP_" + gap.code + "_" + e.episode_id
})
ON CREATE SET
  g.episode_id  = e.episode_id,
  g.code        = gap.code,
  g.severity    = gap.severity,
  g.description = gap.description,
  g.created_at  = datetime()
MERGE (e)-[:HAS_GAP]->(g)

RETURN
  e.episode_id    AS episode_id,
  gap.code        AS code,
  gap.severity    AS severity,
  gap.description AS description
ORDER BY episode_id, code;
