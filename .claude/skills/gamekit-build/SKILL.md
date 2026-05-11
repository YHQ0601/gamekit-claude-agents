---
name: gamekit-build
description: Use this skill when implementing a focused game feature or gameplay change across Unity, Godot, Unreal, Web/JS, or another game runtime. It keeps implementation minimal, profile-aware, and verified.
---

# gamekit-build

Purpose: run a minimal, engine-aware game implementation workflow.

## Workflow

1. Restate the goal.
2. Identify the active engine profile.
3. Classify workstreams.
4. Read project brief, architecture index, and relevant system cards if they exist.
5. Verify current code and local engine patterns.
6. Use the smallest viable implementation.
7. Avoid unrelated refactors and dependency changes.
8. Run or propose validation appropriate to the active profile.
9. End with a `project-memory-curator` memory update decision. Update `.claude-local/SESSION_STATE.md` when implementation produced verified facts, validation results, risks, or next steps.

## Guardrails

- Use `.claude/rules/core/*.md` for all work.
- Use exactly one `.claude/rules/profiles/*.md` when engine-specific files are involved.
- Ask before adding packages, plugins, modules, SDKs, or major dependencies.
- Treat save data, networking, economy, and serialized/editor-facing API as compatibility-sensitive.
- If the implementation caused large changes, workflow/schema/template changes, or system boundary changes, make the memory update explicit and propose shared knowledge updates rather than silently editing shared docs.
