# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] — 2026-04-07

### Added

- Heuristic syntax layer (`syntax/syntax.py`) — assigns verb/subject/object/adverb roles.
- Temporal and spatial anchoring (`cognition/time_space.py`).
- In-memory world model (`cognition/world_model.py`).
- Forward-chaining inference rules (`cognition/inference_rules.py`).
- Declarative layer contracts (`contracts.yaml`) with runtime verification.
- General closure verification (`closure.py`) per Chapter 19.
- *Mafhūm* types module (`cognition/mafhum.py`) per Chapter 21.
- Updated core types for `case_mark`, `syntax_role`, `temporal`, `spatial`, `confidence`.

## [0.1.0] — 2026-04-07

### Added

- Initial engine with signifier, signified, linkage, and evaluation layers.
- Unicode normalisation and phonology modules.
- Root-pattern extraction.
- Ontological mapping and dalāla validation.
- Pipeline runner (`pipeline.py`) and example script (`example_run.py`).
