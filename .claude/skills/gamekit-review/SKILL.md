---
name: gamekit-review
description: Use this skill only when the user explicitly asks for code review, PR review, diff review, staged change review, or pre-commit review. It reviews changes without editing files.
---

# gamekit-review

Purpose: manual, game-aware review of changed code or content.

This workflow is intentionally not automatic. Use it when the user explicitly asks for review, then return findings, risk level, per-finding fix plans, and validation recommendations to the main development conversation for discussion or follow-up implementation.

When the active tool supports subagents, the main agent must delegate the review body to `code-reviewer`. The main agent should confirm scope, pass changed-file context and review policy, then relay or summarize findings. If subagent delegation is unavailable, state `Subagent delegation unavailable; following code-reviewer instructions manually.` and follow `code-reviewer` instructions manually.

## Workflow

1. Confirm the requested review scope: current diff, staged changes, unstaged changes, PR patch, or named files.
2. Read `REVIEW.md`, `CLAUDE.md`, and relevant `.claude/rules/core/*.md`.
3. Must delegate the substantive review to `code-reviewer` when subagent delegation is available.
4. Identify the active engine profile from project evidence, changed files, or user intent.
5. Load exactly one `.claude/rules/profiles/*.md` when the reviewed changes are engine-specific.
6. Inspect the diff before reading wider context.
7. Flag only actionable issues introduced by the reviewed changes.
8. Prioritize findings by impact and likelihood.
9. Provide advisory per-finding fix plans and validation recommendations.
10. For eligible Unity C#-only changes, recommend the Unity profile's `C# compile-layer proxy check` only as a proxy check, not as Unity validation.
11. Do not edit files, apply patches, or execute fixes; return review findings to the main session.
12. If the review reveals durable project facts, stale assumptions, or shared-knowledge drift, provide a `project-memory-curator` recommendation. Review remains read-only; do not directly edit memory or shared docs during review unless the user explicitly asks for memory maintenance.

## Finding Criteria

Report findings that affect:

- correctness or gameplay behavior;
- engine assets, scenes, prefabs, nodes, blueprints, resources, packages, or serialized references;
- save data, schema, migration, networking, economy, or compatibility;
- build, packaging, dependency, platform, or runtime behavior;
- hot-path performance, allocation, render loop, tick/update, or loading behavior;
- missing validation when a concrete risk is otherwise hidden.

Each finding must be introduced or exposed by the reviewed change and must identify a concrete affected path, code path, asset path, scene path, or runtime/editor scenario. Do not report low-confidence issues, broad preferences, or risks that are not actionable.

Avoid:

- subjective style comments;
- broad architecture advice unless the diff introduces a concrete risk;
- speculation without an affected file, code path, asset path, scene path, or runtime scenario.

## Boundaries

- Reviewer is a risk assessor and fix-plan advisor, not an implementer.
- Do not edit files, apply patches, run formatters, or execute fixes.
- If the user asks to fix review findings, return control to the main development workflow.
- If project knowledge needs updating, provide a `Knowledge Update Recommendation`. Do not silently change `docs/knowledge/*`, `docs/systems/*`, `docs/decisions/*`, skill docs, or `.claude-local/SESSION_STATE.md` as part of review.

## Output Format

## Findings

- `[P0] Short issue title`
  - Location: `path/to/file` line, code path, asset path, prefab path, or scene path
  - Scenario: when this breaks
  - Impact: why this matters
  - Fix Plan: advisory change plan only
  - Validation: smallest useful check

Use `[P0]`, `[P1]`, `[P2]`, or `[P3]` prefixes. If there are no actionable findings, write `No actionable findings.`

## Risk Level

Low / Medium / High / Critical

## Review Scope / Engine

## Validation Recommendation

## Untested Areas

## Overall Correctness

Patch is correct / Patch is risky / Patch is incorrect

## Memory / Knowledge Recommendation
