---
description: Guide focused game implementation toward simple, engine-aware, testable, and maintainable code.
---

# Game Code Rules

## General

- Prefer simple, explicit code.
- Avoid over-engineering for one-off features.
- Do not refactor unrelated systems.
- Keep gameplay responsibilities focused.
- Do not add packages, plugins, engine modules, SDKs, or major dependencies without approval.
- Before adding a new abstraction, inspect existing local patterns.

## Engine Profile

- Identify the active engine or runtime before implementation.
- Load the relevant profile from `.claude/rules/profiles/` when engine-specific files or workflows are involved.
- If the engine is unknown, inspect repository structure and `docs/ai/PROJECT_BRIEF.md`; keep assumptions as `TBD`.
- In mixed-engine repositories, scope changes to the explicitly requested runtime.

## Gameplay Data

- Prefer the existing data/config pattern for skills, items, characters, levels, balance, and progression.
- Do not hardcode long-term balance data in runtime behavior unless that is already the project pattern.
- Runtime state should live in runtime systems, not in static configuration assets.
- Treat save data, economy data, and network protocols as architecture-sensitive.

## Runtime Performance

- Avoid expensive scene-wide searches, allocations, and dependency lookups in hot paths.
- Keep per-frame logic bounded and measurable.
- Do not introduce pooling, caching layers, or async infrastructure before there is a real repeated cost.
- Recommend profiling when performance concerns are uncertain.

## References and Wiring

- Prefer explicit references and local setup patterns over fragile name/path/string lookups.
- If an engine profile permits a lookup in editor-only setup, migration, or tests, document the reason and include null/error handling.
- Do not rename serialized, persisted, or externally referenced fields without considering migration.
