---
name: gamekit-review
description: Use this skill only when the user explicitly asks for code review, PR review, diff review, staged change review, or pre-commit review. It reviews changes without editing files.
---

# gamekit-review

Purpose: manual, game-aware review of changed code or content.

This workflow is intentionally not automatic. Use it when the user asks for review, then return findings, risk level, and recommended fix plans to the main development conversation for discussion or follow-up implementation.

## Workflow

1. Confirm the requested review scope: current diff, staged changes, unstaged changes, PR patch, or named files.
2. Read `REVIEW.md`, `CLAUDE.md`, and relevant `.claude/rules/core/*.md`.
3. Identify the active engine profile from project evidence, changed files, or user intent.
4. Load exactly one `.claude/rules/profiles/*.md` when the reviewed changes are engine-specific.
5. Inspect the diff before reading wider context.
6. Flag only actionable issues introduced by the reviewed changes.
7. Prioritize findings by impact and likelihood.
8. Provide advisory fix plans and validation recommendations.
9. Do not edit files, apply patches, or execute fixes; return review findings to the main session.

## Finding Criteria

Report findings that affect:

- correctness or gameplay behavior;
- engine assets, scenes, prefabs, nodes, blueprints, resources, packages, or serialized references;
- save data, schema, migration, networking, economy, or compatibility;
- build, packaging, dependency, platform, or runtime behavior;
- hot-path performance, allocation, render loop, tick/update, or loading behavior;
- missing validation when a concrete risk is otherwise hidden.

Avoid:

- subjective style comments;
- broad architecture advice unless the diff introduces a concrete risk;
- speculation without an affected file, code path, asset path, scene path, or runtime scenario.

## Boundaries

- Reviewer is a risk assessor and fix-plan advisor, not an implementer.
- Do not edit files, apply patches, run formatters, or execute fixes.
- If the user asks to fix review findings, return control to the main development workflow.

## Output Format

## Findings

Use `[P0]`, `[P1]`, `[P2]`, or `[P3]` prefixes.

## Risk Level

Low / Medium / High / Critical

## Active Engine Profile

Unity / Godot / Unreal / Web/JS / Mixed / TBD

## Review Scope

## Recommended Fix Plan

Advisory only. Do not implement fixes.

## Validation Recommendation

## Untested Areas

## Overall Correctness

Patch is correct / Patch is risky / Patch is incorrect
