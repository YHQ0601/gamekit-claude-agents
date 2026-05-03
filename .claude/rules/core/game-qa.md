---
description: Validate game changes by checking build risk, runtime risk, asset/reference risk, performance risk, and engine-profile-specific concerns.
---

# Game QA Rules

## Validation Order

1. Identify changed files and affected systems.
2. Identify the active engine profile.
3. Check build or compile risk.
4. Check runtime behavior and error risk.
5. Check asset, scene, level, prefab, node, blueprint, or content reference risk.
6. Check serialization, save data, and migration risk.
7. Check performance risk in hot paths.
8. Recommend the smallest useful automated or manual validation.

## Boundaries

- QA roles should not implement features.
- QA roles should not make product decisions.
- If a check cannot be run locally, explain the missing command, engine installation, or manual editor step.
- Do not treat documentation as proof that a system exists; verify against repository files.
