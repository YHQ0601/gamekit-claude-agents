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
6. Identify existing or missing test coverage.
7. Recommend the smallest useful automated or manual validation.
8. Expand file reading only when the initial risk map is insufficient.
9. For debug triage, identify reproduction clues, likely failure surface, and next evidence to collect before proposing fixes.

## Output Format

## Changed Area

## Active Engine Profile

## Affected Systems

## Engine / Asset Risks

## Serialization / Save Risks

## Runtime Risks

## Performance Risks

## Test Recommendation

## Manual Checks

## Debug Triage

## Pass / Risky / Fail
