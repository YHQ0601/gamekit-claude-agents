---
description: Thin Unity profile for C#, serialized assets, prefabs, scenes, ProjectSettings, packages, and Unity Editor validation.
paths:
  - "Assets/**"
  - "ProjectSettings/**"
  - "Packages/manifest.json"
  - "**/*.asmdef"
  - "**/*.unity"
  - "**/*.prefab"
  - "**/*.asset"
  - "**/*.meta"
---

# Unity Profile

## Markers

Use this profile when the repository contains `ProjectSettings/ProjectVersion.txt`, `Packages/manifest.json`, `Assets/`, Unity `.meta` files, or the user asks for Unity work.

## Sensitive Files

Be careful with:

- `.meta`
- `.prefab`
- `.unity`
- `ProjectSettings/`
- `Packages/manifest.json`
- Addressables settings, groups, labels, and content catalogs
- generated asset import data

## Recommended Minimal Structure

Respect the existing Unity project structure first. For a new or empty demo project, use `Assets/Game/` as the default project-owned content root:

```text
Assets/Game/
  Scripts/
  Scenes/
  Prefabs/
  Art/
  Audio/
  UI/
  Settings/
  Editor/
  Tests/
```

Keep third-party packages, samples, plugins, generated data, and Asset Store content outside `Assets/Game/` unless the project already uses a different convention.

## Safety Rules

- Do not manually modify `.meta` files unless explicitly required.
- Do not hand-edit complex `.prefab` or `.unity` YAML unless explicitly approved.
- When the task requires editing Unity prefab or scene serialized data, use `gamekit-unity-prefab-edit`.
- When the task is to understand, inspect, summarize, or reduce context cost for `.prefab`, `.unity`, or `.asset` files, use `gamekit-unity-yaml-context` before reading full raw YAML.
- Treat ScriptableObject assets, prefab variants, scenes, Addressables groups, and package manifests as serialized reference surfaces.
- Prefer Unity Editor operations, Editor scripts, or controlled prefab generation for serialized assets.
- Do not modify `ProjectSettings` unless the task explicitly requires it.
- Do not add, remove, or upgrade Unity packages without approval.
- If many `.meta`, prefab, scene, ScriptableObject, Addressables, or project setting files change, warn the user.

## C# Rules

- Prefer `[SerializeField] private` fields over public mutable fields for Inspector references.
- Be careful when renaming serialized fields; use a migration strategy such as `FormerlySerializedAs` when serialized data must survive the rename.
- Prefer ScriptableObject or existing config patterns for skills, items, characters, levels, and balance data.
- Do not store runtime combat state in ScriptableObjects unless the project already does so intentionally.
- Avoid fragile runtime scene/UI wiring such as `GameObject.Find(...)`, `transform.Find(...)`, `GetComponent("...")`, and repeated scene-wide discovery.
- Cache type-safe `GetComponent<T>()` calls when they are repeated or used from hot paths.
- Keep `Update`, `LateUpdate`, `FixedUpdate`, coroutines, animation callbacks, and render callbacks bounded; avoid avoidable allocations, LINQ churn, string formatting, and scene-wide searches there.
- Do not use editor-only APIs in player/runtime assemblies unless they are behind editor-only compilation and assembly boundaries.

## Validation

- Run or recommend the smallest relevant Unity compile, EditMode, PlayMode, or manual Editor check.
- Inspect NullReference, Missing Script, Missing Reference, prefab/scene/ScriptableObject reference, serialized field migration, Addressables, package, input, and render pipeline risks when affected.
- Use the Profiler or allocation inspection only when the change touches hot paths, loading, rendering, physics, animation, UI rebuilds, or repeated per-frame work.
