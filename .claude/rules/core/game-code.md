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

## Architecture Quality Gate

For non-trivial implementation, quickly check these lenses before editing and again before final validation:

- Compatibility: Will this touch serialized fields, save data, public APIs, network contracts, asset references, config formats, or existing user workflows?
- Coupling: Does it add hidden dependencies through globals, singletons, service locators, string lookups, scene-wide searches, or implicit execution order?
- Stability: What existing behavior could regress, and what should explicitly stay unchanged?
- Ownership: Which module owns the behavior, data, lifecycle, and validation? Keep gameplay logic, UI, data/config, persistence, and editor tooling responsibilities separate.
- Testability: Can the change be checked with a small automated test, editor validation, scene/prefab check, or focused manual scenario?

Prefer the smallest design that passes these checks. If a lens exposes meaningful risk, simplify the approach or use `architecture-reviewer` before implementation.

## Domain Invariant Gate

- Before changing a domain formula, condition, eligibility rule, or state transition, search for its canonical owner/helper and semantic sibling consumers.
- Reuse or extend the canonical owner. Express intentional differences with a named policy or parameter instead of copying the rule inline.
- Safely consolidate duplicate paths touched by the task; return to planning if consolidation expands across systems or changes a behavior contract.
- Abstract only behavior that should change together. Do not create abstractions from incidental textual similarity.

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
