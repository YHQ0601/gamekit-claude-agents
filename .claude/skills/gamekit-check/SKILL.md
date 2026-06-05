---
name: gamekit-check
description: Use this skill after code, asset, scene, content, package, dependency, or behavior-affecting changes to assess build, runtime, serialization, reference, asset, and performance risks across game engines. It can also triage bugs or debug reports before a fix.
---

# gamekit-check

Purpose: profile-aware post-change validation and debug triage for game projects.

Use this as a debug triage workflow when the user reports a bug, crash, missing reference, asset load failure, performance drop, or broken gameplay behavior. It should identify likely risk areas, logs or checks to inspect, and the smallest next validation step. It is not a full debugging implementation workflow.

## Workflow

1. Identify changed files and changed area.
2. Identify the active engine profile.
3. Map affected systems using structured context first.
4. Check engine-specific asset, scene, content, package, dependency, and reference risks.
5. Check compile/build, runtime, serialization, save data, and performance risks.
6. For eligible Unity C#-only changes, prefer the Unity profile's `dotnet build <solution>.sln --no-restore` proxy check first, but never treat it as Unity validation.
7. For Unity scene checks, include prefab instances, referenced prefab assets, and overrides when scene configuration depends on them.
8. Identify existing or missing test coverage.
9. Recommend the smallest useful automated or manual validation.
10. Expand file reading only when the initial risk map is insufficient.
11. For debug triage, identify reproduction clues, likely failure surface, and next evidence to collect before proposing fixes.
12. Do not implement fixes. If fixes are needed, return control to the main implementation workflow.
13. Keep the output's purpose/scope context short enough to forward to another agent for review.
14. End with a `project-memory-curator` memory update decision when validation, QA, or triage establishes new facts, remaining risks, stale assumptions, or next checks.

## Output Format

## Check Summary

Purpose:

Scope:

Engine:

Result: Pass / Risky / Fail

Top Risks: list 1-3 terse risks or `None`

## Risk Matrix

Cover engine/assets/references, build/package, serialization/save, runtime, performance, and test coverage.

## Validation

Run:

Recommended:

Untested / Blocked:

## Follow-up

Fix Workflow:

Memory / Knowledge:
