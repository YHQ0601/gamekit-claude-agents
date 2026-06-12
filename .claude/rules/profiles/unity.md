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

Inspector contract for project-owned code:

- Prefer `[SerializeField] private` over public mutable Inspector fields, and give each field a concise `[Tooltip]`. Follow the project's established Inspector language; otherwise use the user's primary conversation language, and ask if still unclear. Do not infer it from the operating-system locale.
- When a prefab reference requires a component on its root, serialize that component type instead of `GameObject` plus `GetComponent`. Use `GameObject` only for intentionally heterogeneous prefabs, with `OnValidate` or equivalent editor validation.
- Assign prefab assets from the Project window, not scene or prefab-instance objects from the Hierarchy. Validate asset-versus-scene identity when that distinction matters.
- Check required Inspector, configuration, or injected dependencies at the earliest practical validation point. On absence, emit one actionable `Debug.LogWarning(..., this)` naming the missing dependency and repair action; avoid silent failure and per-frame warning spam, then return, disable, or degrade safely as appropriate.
- Be careful when renaming serialized fields; use a migration strategy such as `FormerlySerializedAs` when serialized data must survive the rename.
- Prefer ScriptableObject or existing config patterns for skills, items, characters, levels, and balance data.
- Do not store runtime combat state in ScriptableObjects unless the project already does so intentionally.
- For Unity UI, prefer authored prefabs or scene UI hierarchies with `[SerializeField] private` references over building full UI layouts at runtime. Runtime code may update state, bind events, toggle visibility, and instantiate known item or row prefabs into existing containers, but should not construct the primary UI structure from scratch unless explicitly requested or already established by the project.
- UI components should only render lightweight ViewData and handle local interaction. They must not directly query config tables, save data, services, global singletons, root contexts, or gameplay managers.
- Build UI ViewData in a page, system, coordinator, Builder, or Provider layer before passing it into reusable components. Reused components should keep one stable ViewData input shape; scene-specific differences belong in the Builder/Provider, not in main-menu/battle/preview branches inside the component.
- Avoid fragile runtime scene/UI wiring such as `GameObject.Find(...)`, `transform.Find(...)`, `GetComponent("...")`, and repeated scene-wide discovery.
- Cache type-safe `GetComponent<T>()` calls when they are repeated or used from hot paths.
- Keep `Update`, `LateUpdate`, `FixedUpdate`, coroutines, animation callbacks, and render callbacks bounded; avoid avoidable allocations, LINQ churn, string formatting, and scene-wide searches there.
- Do not use editor-only APIs in player/runtime assemblies unless they are behind editor-only compilation and assembly boundaries.

## Wiring Rules

- Prefer one composition root per feature, prefab, or scene. Put Inspector references there, validate them there, and use it to initialize child systems.
- Dependencies should flow from the root/coordinator into focused components. Avoid child components holding a broad root/context reference just to fetch unrelated systems.
- Components should receive only what they need, through explicit `Initialize(...)` methods or narrowly scoped serialized fields. Do not turn context/root objects into service locators.
- UI dependencies should flow from page/coordinator/provider code into focused UI components. Reusable child UI components should not fetch global state or branch on scene-specific business modes.
- Do not use `SendMessage`, `BroadcastMessage`, reflection, or string method names for core gameplay/application flow. Use typed C# events, explicit references, or interfaces.
- Event producers own and invoke events. Consumers subscribe/unsubscribe explicitly. Producers should not know about optional UI, debug, analytics, VFX, audio, or presentation consumers.
- Optional debug/UI/presentation components should consume state and events. Core gameplay should still run if those optional consumers are disabled or removed.
- When changing Unity serialized fields, either preserve bindings with `FormerlySerializedAs` or explicitly document the required manual prefab/scene rebinds.
- Avoid hand-editing prefab/scene YAML for wiring unless the task explicitly requires it. Prefer Unity Editor operations or controlled editor scripts for serialized asset changes.
- After wiring changes, run the smallest compile/build check and inspect affected prefabs/scenes for missing scripts, missing references, and required root assignments.

## Validation

- Fast C# compile proxy check: for low-risk ordinary C# script-only changes that do not touch serialized assets, scenes, prefabs, ScriptableObjects, Addressables, `Packages/`, `ProjectSettings/`, `.asmdef`, platform config, serialized fields, Inspector bindings, serialized field migration, or gameplay-flow-sensitive wiring, prefer `dotnet build <solution>.sln --no-restore` as the first sanity check when a root `.sln` exists.
- Discover the solution at the repository root. Prefer the `.sln` matching the repository directory name; if multiple remain, choose the clearest main project solution and report the choice.
- Report a passing proxy check only as `C# compile-layer proxy check passed`, never as Unity validation. If it fails, distinguish stale Unity-generated project files or local .NET environment issues from errors in changed source.
- Run or recommend the smallest relevant Unity compile, EditMode, PlayMode, or manual Editor check.
- When serialized fields or Inspector wiring change, verify Tooltip coverage, prefab field types, missing-dependency warnings, and prefab/scene bindings.
- When checking scene configuration, include prefab instances, referenced prefab assets, overrides, Missing Script, Missing Reference, and stale GUID risks; use `gamekit-unity-yaml-context` for referenced `.prefab` summaries when the scene summary is insufficient.
- Inspect NullReference, Missing Script, Missing Reference, prefab/scene/ScriptableObject reference, serialized field migration, Addressables, package, input, and render pipeline risks when affected.
- Use the Profiler or allocation inspection only when the change touches hot paths, loading, rendering, physics, animation, UI rebuilds, or repeated per-frame work.
