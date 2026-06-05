---
name: gamekit-check
description: Use this skill after code, asset, scene, content, package, dependency, or behavior-affecting changes to assess build, runtime, serialization, reference, asset, and performance risks across game engines. It can also triage bugs or debug reports before a fix.
---

# gamekit-check

Purpose: profile-aware post-change validation and debug triage for game projects.

Use this as a debug triage workflow when the user reports a bug, crash, missing reference, asset load failure, performance drop, or broken gameplay behavior. It should identify likely risk areas, logs or checks to inspect, and the smallest next validation step. It is not a full debugging implementation workflow.

When invoked through the explicit `/gamekit-check` command, Safe Auto-Fix Escalation may route one narrow `Direct Fix Candidate` through `gamekit-build`, then return here for validation. This workflow itself does not edit files.

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
12. For explicit `/gamekit-check` only, decide whether a failed check qualifies for Safe Auto-Fix Escalation.
13. Do not implement fixes inside this workflow. If fixes are needed, return control to `gamekit-build`; if auto-fix escalation is allowed, route one narrow fix through `gamekit-build` and then rerun the smallest useful `gamekit-check` validation.
14. Keep the output's purpose/scope context short enough to forward to another agent for review.
15. End with a `project-memory-curator` memory update decision when validation, QA, or triage establishes new facts, remaining risks, stale assumptions, or next checks.

## Safe Auto-Fix Escalation

Use this only for explicit `/gamekit-check` requests when the user did not ask for read-only, only report, do not edit, only check, or equivalent.

A `Direct Fix Candidate` must have clear location, clear expected behavior, local low-risk scope, and a smallest validation path. Typical cases include compile errors, syntax/using/namespace mistakes, obvious parameter or enum mistakes, inverted conditions, and local UI state/text mapping errors.

Do not auto-fix unknown root causes, intermittent bugs, performance problems, architecture or data model issues, save data changes, prefab/scene YAML, ScriptableObject migrations, `ProjectSettings`, `Packages`, cross-system flow, or Unity Inspector binding risk. In those cases, report the issue and put the recommended implementation path in `Fix Workflow:`.

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

State whether Safe Auto-Fix Escalation was unavailable, skipped, recommended, or used. If used, include the `gamekit-build` fix scope and the follow-up validation result.

Memory / Knowledge:
