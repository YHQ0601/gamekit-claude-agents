---
description: Thin Unity profile for C#, serialized assets, prefabs, scenes, ProjectSettings, packages, and Unity Editor validation.
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
- Prefer Unity Editor operations, Editor scripts, or controlled prefab generation for serialized assets.
- Do not modify `ProjectSettings` unless the task explicitly requires it.
- Do not add, remove, or upgrade Unity packages without approval.
- If many `.meta`, prefab, or scene files change, warn the user.

## C# Rules

- Prefer `[SerializeField] private` fields over public mutable fields for Inspector references.
- Be careful when renaming serialized fields.
- Prefer ScriptableObject or existing config patterns for skills, items, characters, levels, and balance data.
- Do not store runtime combat state in ScriptableObjects unless the project already does so intentionally.
- Avoid fragile runtime scene/UI wiring such as `GameObject.Find(...)`, `transform.Find(...)`, `GetComponent("...")`, and repeated scene-wide discovery.
- Cache type-safe `GetComponent<T>()` calls when they are used repeatedly.

## Validation

- Run or recommend the smallest relevant Unity compile, EditMode, PlayMode, or manual Editor check.
- Inspect NullReference, Missing Reference, prefab/scene reference, serialized field migration, and hot-path allocation risks.
