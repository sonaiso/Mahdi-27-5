-- ============================================================================
-- Arabic Engine — PostgreSQL Seed Data (v1)
-- بيانات أولية — المحرك العربي
-- ============================================================================

-- ── Seed Lexicon Entries ───────────────────────────────────────────

INSERT INTO lexicon_entries (root, pattern, lemma, pos, base_meaning, frequency) VALUES
    ('{"ك","ت","ب"}', 'فَعَلَ', 'كَتَبَ', 'FI3L', 'writing', 100),
    ('{"ك","ت","ب"}', 'كِتَاب', 'كِتَاب', 'ISM', 'book', 95),
    ('{"ك","ت","ب"}', 'كَاتِب', 'كَاتِب', 'ISM', 'writer', 80),
    ('{"ق","ر","أ"}', 'فَعَلَ', 'قَرَأَ', 'FI3L', 'reading', 90),
    ('{"ع","ل","م"}', 'فَعِلَ', 'عَلِمَ', 'FI3L', 'knowing', 95),
    ('{"ع","ل","م"}', 'عِلْم', 'عِلْم', 'ISM', 'knowledge', 90),
    ('{"ذ","ه","ب"}', 'فَعَلَ', 'ذَهَبَ', 'FI3L', 'going', 80),
    ('{"ج","ل","س"}', 'فَعَلَ', 'جَلَسَ', 'FI3L', 'sitting', 75),
    ('{"ح","ك","م"}', 'فَعَلَ', 'حَكَمَ', 'FI3L', 'judging', 85),
    ('{"ح","ك","م"}', 'حُكْم', 'حُكْم', 'ISM', 'judgement', 85),
    ('{"ن","ص","ر"}', 'فَعَلَ', 'نَصَرَ', 'FI3L', 'helping', 70),
    ('{"ف","ت","ح"}', 'فَعَلَ', 'فَتَحَ', 'FI3L', 'opening', 75),
    ('{"ق","و","ل"}', 'فَعَلَ', 'قَالَ', 'FI3L', 'saying', 95),
    ('{"ر","ح","م"}', 'فَعِلَ', 'رَحِمَ', 'FI3L', 'mercy', 90),
    ('{"ح","م","د"}', 'فَعِلَ', 'حَمِدَ', 'FI3L', 'praising', 85);

-- ── Seed Concept Nodes ─────────────────────────────────────────────

INSERT INTO concept_nodes (concept_id, label, semantic_type, properties) VALUES
    ('C001', 'كتابة', 'EVENT', '{"domain": "communication"}'),
    ('C002', 'قراءة', 'EVENT', '{"domain": "communication"}'),
    ('C003', 'علم', 'ATTRIBUTE', '{"domain": "cognition"}'),
    ('C004', 'حكم', 'EVENT', '{"domain": "jurisprudence"}'),
    ('C005', 'رحمة', 'ATTRIBUTE', '{"domain": "ethics"}'),
    ('C006', 'ذهاب', 'EVENT', '{"domain": "motion"}'),
    ('C007', 'جلوس', 'EVENT', '{"domain": "posture"}'),
    ('C008', 'فتح', 'EVENT', '{"domain": "physical_action"}'),
    ('C009', 'نصر', 'EVENT', '{"domain": "support"}'),
    ('C010', 'قول', 'EVENT', '{"domain": "communication"}');

-- ── Seed Inference Rules ───────────────────────────────────────────

INSERT INTO inference_rules (rule_name, rule_type, premises, conclusion, confidence) VALUES
    ('transitivity', 'FORWARD_CHAIN',
     '[{"type": "predicate_match", "field": "predicate"}]',
     '{"derive": "transitive_conclusion"}', 0.9),
    ('negation_propagation', 'FORWARD_CHAIN',
     '[{"type": "polarity", "value": false}]',
     '{"derive": "negated_proposition"}', 0.95),
    ('event_existence', 'FORWARD_CHAIN',
     '[{"type": "semantic_type", "value": "EVENT"}]',
     '{"derive": "event_entails_existence"}', 0.85);

-- ── Seed World Facts ───────────────────────────────────────────────

INSERT INTO world_facts (subject, predicate, object, confidence, source) VALUES
    ('كتابة', 'يتطلب', 'أداة', 0.95, 'common_knowledge'),
    ('قراءة', 'يتطلب', 'نص', 0.95, 'common_knowledge'),
    ('علم', 'يؤدي_إلى', 'معرفة', 0.90, 'common_knowledge'),
    ('حكم', 'يتطلب', 'دليل', 0.85, 'domain_knowledge'),
    ('إنسان', 'قادر_على', 'كتابة', 0.80, 'common_knowledge');
