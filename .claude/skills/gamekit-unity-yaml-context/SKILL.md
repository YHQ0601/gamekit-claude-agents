---
name: gamekit-unity-yaml-context
description: Use this skill when Codex or Claude needs to understand, summarize, inspect, or reduce token/context cost for Unity YAML files, especially .prefab, .unity scene, and .asset files. Trigger for Unity YAML, prefab, scene, ScriptableObject, MonoBehaviour, Inspector, Hierarchy, serialized fields, GameObject hierarchy, GUID references, Missing Script, Missing Reference, token budget, context compression, summarize scene, summarize prefab, summarize asset, parse Unity asset, parse scene, parse prefab, understand Unity Editor content, or Chinese-language requests about these Unity asset concepts.
---

# gamekit-unity-yaml-context

Purpose: summarize Unity serialized YAML into compact Markdown before reading raw `.prefab`, `.unity`, or `.asset` files.

## Workflow

1. Use this before loading large Unity YAML into the model context.
2. Keep the operation read-only. Do not edit `.prefab`, `.unity`, `.asset`, or `.meta` files with this skill.
3. Run:

```bash
python .claude/skills/gamekit-unity-yaml-context/scripts/summarize_unity_yaml.py <unity-yaml-file> --project-root <unity-project-root>
```

4. If `--project-root` is omitted, let the script search upward for `Assets/`, `ProjectSettings/ProjectVersion.txt`, or `Packages/manifest.json`.
5. Use the Markdown summary for analysis. Read raw YAML only when the user asks for exact source text or a field-level trace that is absent from the summary.

## Output Contract

The summary should include:

- file type, parser mode, object counts, and class counts;
- GameObject hierarchy for scenes and prefabs;
- component lists, MonoBehaviour script paths, active/enabled state, Transform, layer, and tag;
- important serialized scalar fields and short collections;
- external GUID references resolved through `.meta` files when possible;
- unresolved internal references, missing scripts, missing references, and large omitted fields.

The summary should omit noisy data by default: long arrays, long strings, repeated default values, editor internals, and large blobs. It should report omissions with counts or compact markers.

## Dependency Policy

Prefer `unityparser` from `socialpoint-labs/unity-yaml-parser` for Unity YAML fidelity. If it is unavailable, the bundled script uses a read-only PyYAML fallback when possible and prints an installation hint. Never install dependencies automatically.

## Write Policy

This v1 skill is not a YAML writer. If a future task needs prefab or scene mutation, first propose a separate v2 workflow with backup, diff, small patch scope, and Unity Editor validation.
