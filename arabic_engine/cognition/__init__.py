"""Cognition layer — الإدراك: evaluation, time/space, world model, inference.

Public sub-modules
------------------
* :mod:`arabic_engine.cognition.evaluation` — Proposition construction
  (judgment, التعريف 7) and truth/guidance evaluation (التعريف 8).
* :mod:`arabic_engine.cognition.time_space` — Temporal and spatial
  anchoring for propositions.
* :mod:`arabic_engine.cognition.world_model` — In-memory knowledge base
  of world facts used to adjust evaluation confidence.
* :mod:`arabic_engine.cognition.inference_rules` — Forward-chaining
  rule engine for deriving new propositions.
* :mod:`arabic_engine.cognition.mafhum` — Mafhūm (implied meaning)
  analysis — minimal types (Ch. 21).
* :mod:`arabic_engine.cognition.knowledge_graph` — In-memory graph store
  for :class:`~arabic_engine.core.types.KnowledgeEpisodeNode` and its
  ten epistemic components.
* :mod:`arabic_engine.cognition.seed_data` — Bootstrap methods and
  conflict rules for the knowledge graph.
* :mod:`arabic_engine.cognition.episode_validator` —
  :class:`~arabic_engine.cognition.episode_validator.EpisodeValidator`
  that validates a knowledge episode against the ten epistemic conditions.
* :mod:`arabic_engine.cognition.discourse_exchange` —
  validator functions for inter-agent deliberative discourse exchange.
* :mod:`arabic_engine.cognition.explanation` — explicit why/evidence
  explanation payload construction for v3 pipeline output.
"""

__all__ = [
    "evaluation",
    "time_space",
    "world_model",
    "inference_rules",
    "mafhum",
    "knowledge_graph",
    "seed_data",
    "episode_validator",
    "discourse_exchange",
    "explanation",
]
