# GameKit Review Rules

Use this file for manual review-only work such as `/gamekit-review`, "review this diff", "review this PR", or "审查当前改动".

## Scope

Review the current diff, staged changes, unstaged changes, PR patch, or explicitly named files. Inspect the diff before reading wider context. Do not review unrelated areas unless the changed code proves they are affected.

## Review Priorities

Focus on issues the author would likely fix:

1. Correctness and gameplay regressions
2. Engine serialization, reference, scene, prefab, node, blueprint, or asset breakage
3. Save data, schema, migration, networking, economy, or compatibility risk
4. Build, packaging, dependency, or platform risk
5. Runtime errors, null or missing references, race conditions, and lifecycle issues
6. Hot-path performance, allocation, render loop, tick/update, or loading regressions
7. Missing tests or manual checks only when they hide a concrete risk

For Unity review scope, also check affected `Assets/`, `ProjectSettings/`, `Packages/manifest.json`, `.asmdef`, `.unity`, `.prefab`, `.asset`, and `.meta` changes for Missing Script, Missing Reference, serialized field migration, editor-only API, package/input/render pipeline, Addressables, prefab variant, scene, and ScriptableObject reference risks.

For Unity `.prefab`, `.unity`, or `.asset` review, use `gamekit-unity-yaml-context` before reading full serialized YAML unless the diff itself already provides enough evidence.

For low-risk Unity C#-only review recommendations, `dotnet build <solution>.sln --no-restore` may be suggested as a `C# compile-layer proxy check`, but not as Unity validation.

## Finding Quality Gate

Report a finding only when it is:

- introduced or exposed by the reviewed change;
- actionable by the author;
- backed by a concrete affected path, code path, asset path, scene path, prefab path, or runtime/editor scenario;
- important enough to fix before merge or explicitly accept as risk.

Do not report low-confidence speculation, broad preferences, or generic best-practice advice.

## Boundaries

- Review only. Do not edit files.
- Do not apply patches, write files, run formatters, or execute fixes.
- Do not make product decisions.
- Do not flag broad style preferences unless they obscure behavior or violate a documented project rule.
- Do not speculate about possible breakage without identifying the affected code path, asset path, scene path, or runtime scenario.
- Include the risk level and a per-finding fix plan for each actionable finding.
- Keep fix plans advisory. The main development session decides whether to implement them.
- Do not treat project documentation as proof that a system exists; verify against repository files.
- Prefer fewer high-confidence findings over long lists of weak concerns.
- If no actionable issue is found, say so clearly and mention remaining untested risk.

## Output

When used as a local review workflow, report:

## Findings

- `[P0]`: blocking release or major usage
- `[P1]`: urgent, should fix before merge
- `[P2]`: normal actionable bug or maintainability risk
- `[P3]`: low severity, optional improvement

Use this shape for every actionable finding:

- `[P1] Short issue title`
  - Location: `path/to/file` line, code path, asset path, prefab path, or scene path
  - Scenario: when this breaks
  - Impact: why this matters
  - Fix Plan: advisory change plan only
  - Validation: smallest useful check

If there are no actionable findings, write `No actionable findings.`

## Risk Level

Low / Medium / High / Critical

## Review Scope / Engine

## Validation Recommendation

## Untested Areas

## Overall Correctness

Patch is correct / Patch is risky / Patch is incorrect

## Memory / Knowledge Recommendation
