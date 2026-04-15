# Neo4j Cypher Scripts

This directory contains [Cypher](https://neo4j.com/developer/cypher/) scripts
for a Neo4j graph database that mirrors the knowledge-graph structures used by
the Arabic engine.

## Files

| File | Purpose |
|------|---------|
| `schema.cypher` | Base schema (node labels, relationship types, constraints) |
| `seed.cypher` | Initial seed data for the knowledge graph |
| `kernel_schema.cypher` | Kernel-14 schema for epistemic labels |
| `kernel_seed.cypher` | Kernel-14 seed data |
| `validate_episode.cypher` | Episode validation queries |

## Usage

These scripts are intended for **reference and external tooling**.  The Python
runtime uses an in-memory graph via `arabic_engine.cognition.knowledge_graph`
and does not connect to Neo4j at runtime.

To load into a running Neo4j instance:

```bash
cypher-shell -u neo4j -p <password> < schema.cypher
cypher-shell -u neo4j -p <password> < seed.cypher
```
