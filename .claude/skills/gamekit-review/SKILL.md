---
name: gamekit-review
description: Use this skill only when the user explicitly asks for code review, PR review, diff review, staged change review, or pre-commit review. It reviews changes without editing files.
---

# gamekit-review

Purpose: manual, game-aware review of changed code or content.

This workflow is intentionally not automatic. Use it when the user explicitly asks for review, then return a short review summary, actionable findings, per-finding fix plans, validation recommendations, and follow-up recommendations to the main development conversation for discussion or follow-up implementation.

When the active tool supports subagents, the main agent must delegate the review body to `code-reviewer`. The main agent should confirm scope, pass changed-file context and review policy, then relay or summarize findings. If subagent delegation is unavailable, state `Subagent delegation unavailable; following code-reviewer instructions manually.` and follow `code-reviewer` instructions manually.

## Workflow

1. Confirm the requested review scope: current diff, staged changes, unstaged changes, PR patch, or named files.
2. Read `REVIEW.md`, `CLAUDE.md`, and relevant `.claude/rules/core/*.md`.
3. Must delegate the substantive review to `code-reviewer` when subagent delegation is available.
4. Identify the active engine profile from project evidence, changed files, or user intent.
5. Load exactly one `.claude/rules/profiles/*.md` when the reviewed changes are engine-specific.
6. Inspect the diff before reading wider context.
7. Flag only actionable issues introduced by the reviewed changes.
8. Apply the Maintainability Lens below to catch concrete reuse, duplication, architecture, cleanup, validation, and behavior-contract risks.
9. Prioritize findings by impact and likelihood.
10. Provide advisory per-finding fix plans and validation recommendations.
11. For eligible Unity C#-only changes, recommend the Unity profile's `C# compile-layer proxy check` only as a proxy check, not as Unity validation.
12. Do not edit files, apply patches, or execute fixes; return review findings to the main session.
13. If the review reveals durable project facts, stale assumptions, or shared-knowledge drift, provide a `project-memory-curator` recommendation. Review remains read-only; do not directly edit memory or shared docs during review unless the user explicitly asks for memory maintenance.

## Finding Criteria

Report findings that affect:

- correctness or gameplay behavior;
- engine assets, scenes, prefabs, nodes, blueprints, resources, packages, or serialized references;
- save data, schema, migration, networking, economy, or compatibility;
- build, packaging, dependency, platform, or runtime behavior;
- hot-path performance, allocation, render loop, tick/update, or loading behavior;
- missing validation when a concrete risk is otherwise hidden.

Maintainability Lens:

- Scope drift: the diff changes behavior outside the requested review scope or task intent.
- Duplicate / reuse risk: new code, data, assets, or wiring repeats an existing local pattern instead of reusing it, creating behavior divergence, maintenance cost, missed validation, or migration risk.
- Parallel path: old and new code paths, configs, entry points, references, or assets remain active for the same behavior.
- Ownership / source of truth: logic, runtime state, data, lifecycle, or validation moves into the wrong owner/layer or bypasses the existing source of truth.
- Cleanup residue: obsolete fields, registrations, references, assets, config, temporary code, or TODOs remain in a way that can cause behavior splits, misuse, missing references, or maintenance risk.
- Validation mismatch: the recommended or performed validation does not cover the actual changed surface.
- Behavior contract regression: the diff changes existing inputs, outputs, lifecycle, event order, serialized contracts, or gameplay assumptions without an explicit migration or validation path.

Each finding must be introduced or exposed by the reviewed change and must identify a concrete affected path, code path, asset path, scene path, or runtime/editor scenario. Do not report low-confidence issues, broad preferences, or risks that are not actionable.

For duplicate/reuse findings, cite the existing reusable path or the specific new/old parallel paths. For ownership or architecture findings, name the bypassed owner, layer, or source of truth. For cleanup findings, explain how the residue can be used accidentally, diverge behavior, or break references.

Avoid:

- subjective style comments;
- broad architecture advice unless the diff introduces a concrete risk;
- speculation without an affected file, code path, asset path, scene path, or runtime scenario.

## Boundaries

- Reviewer is a risk assessor and fix-plan advisor, not an implementer.
- Do not edit files, apply patches, run formatters, or execute fixes.
- If the user asks to fix review findings, return control to the main development workflow.
- If project knowledge needs updating, propose it. Do not silently change `docs/ai/*`, `docs/systems/*`, `docs/decisions/*`, skill docs, or `.claude-local/SESSION_STATE.md` as part of review.

## Output Format

## Review Summary

Purpose:

Scope:

Engine:

Verdict: Pass / Risky / Incorrect

Top Risks: list 1-3 terse risks or `None`

## Findings

- `[P0] Short issue title`
  - Location: `path/to/file` line, code path, asset path, prefab path, or scene path
  - Scenario: when this breaks
  - Impact: why this matters
  - Fix Plan: advisory change plan only
  - Validation: smallest useful check

Use `[P0]`, `[P1]`, `[P2]`, or `[P3]` prefixes. If there are no actionable findings, write `No actionable findings.`

## Validation

Recommended:

Untested:

## Follow-up

Memory / Knowledge:
