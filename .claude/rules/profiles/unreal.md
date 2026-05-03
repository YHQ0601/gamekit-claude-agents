---
description: Thin Unreal profile for C++, Blueprints, assets, maps, modules, plugins, config files, and editor validation.
---

# Unreal Profile

## Markers

Use this profile when the repository contains `*.uproject`, `Source/`, `Content/`, `Config/DefaultEngine.ini`, `.uasset`, `.umap`, or the user asks for Unreal work.

## Sensitive Files

Be careful with:

- `.uasset`
- `.umap`
- `.uproject`
- `Config/*.ini`
- `Source/*/*.Build.cs`
- plugin descriptors and module files
- generated project files

## Recommended Minimal Structure

Respect the existing Unreal project structure first. For a new or empty demo project, use `Content/Game/` as the default project-owned content root:

```text
Content/Game/
  Blueprints/
  Maps/
  Art/
  UI/
  Audio/
  Data/
Source/
Config/
```

For a mature or Marketplace-oriented project, prefer `Content/<ProjectName>/` over `Content/Game/`. Do not hand-move existing assets broadly unless redirects and editor-side references can be handled safely.

## Safety Rules

- Do not hand-edit binary assets such as `.uasset` or `.umap`.
- Do not add modules, plugins, or engine version changes without approval.
- Do not modify collision channels, input mappings, config defaults, or project settings unless required.
- Preserve Blueprint references, exposed properties, sockets, tags, and asset paths.
- Avoid broad content folder moves unless redirectors and references can be handled in the editor.

## C++ / Blueprint Rules

- Follow existing module boundaries and naming conventions.
- Treat `UCLASS`, `UPROPERTY`, `UFUNCTION`, replication, save data, and Blueprint-exposed API changes as compatibility-sensitive.
- Avoid expensive world searches, actor iteration, allocations, or ticking work without bounds.
- Prefer explicit references, components, interfaces, gameplay tags, or project patterns over brittle name lookups.

## Validation

- Run or recommend the smallest relevant compile, editor load, asset validation, map load, automation test, or manual PIE check.
- Check Blueprint compile risk, missing references, config migration, packaging, replication, and hot-path tick risks.
