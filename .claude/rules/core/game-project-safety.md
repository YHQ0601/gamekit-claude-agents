---
description: Protect engine-sensitive files, generated data, assets, and project settings from accidental unsafe edits.
---

# Game Project Safety Rules

## Source-Control-Sensitive Files

Be careful with:

- engine project settings;
- generated import metadata;
- scene, level, prefab, blueprint, node, and asset files;
- package, plugin, module, and dependency manifests;
- save data schemas and migrations;
- platform export/build settings.

## General

- Do not modify project settings unless the task explicitly requires it.
- Do not add, remove, or upgrade dependencies without approval.
- Do not delete assets unless usage has been checked.
- Do not hand-edit complex binary, generated, or serialized asset formats unless the active engine profile explicitly allows it.
- If many generated or serialized files change, warn the user and explain why.

## Assets

- Keep temporary assets clearly marked with `_PH` or the project convention; co-located placeholders are allowed for demo speed when they include an artist brief and do not overwrite final assets.
- Do not overwrite artist-created assets.
- Preserve stable anchors and references used by gameplay.
- Prefer controlled editor/tool generation over manual editing for complex engine assets.

## Validation

- After behavior-affecting work, run the smallest relevant check or clearly state what manual editor/gameplay validation remains.
- For risky engine files, summarize changed paths and likely reference or serialization risks.
