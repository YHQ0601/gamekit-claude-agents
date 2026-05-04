---
description: Thin Godot profile for scenes, resources, scripts, autoloads, export settings, and editor validation.
paths:
  - "project.godot"
  - "addons/**"
  - "**/*.gd"
  - "**/*.tscn"
  - "**/*.tres"
  - "**/*.res"
  - "**/*.import"
---

# Godot Profile

## Markers

Use this profile when the repository contains `project.godot`, `.tscn`, `.tres`, `.gd`, `.csproj` with Godot references, or the user asks for Godot work.

## Sensitive Files

Be careful with:

- `project.godot`
- `.tscn`
- `.tres`
- `.res`
- `.import`
- export presets and platform settings
- autoload/singleton configuration

## Recommended Minimal Structure

Respect the existing Godot project structure first. For a new or empty demo project, use `res://game/` as the default project-owned content root:

```text
res://game/
  scenes/
  scripts/
  assets/
  resources/
  ui/
  audio/
addons/
tests/
```

Keep third-party addons under `addons/`. Do not force existing flat Godot projects into `res://game/` unless the user asks for a structure cleanup.

## Safety Rules

- Do not hand-edit complex scene/resource files when a script or editor operation is safer.
- Do not modify autoloads, input maps, physics layers, or export presets unless the task explicitly requires it.
- Do not delete nodes or resources without checking references.
- Preserve node paths, exported variables, groups, and signal connections that existing code depends on.
- Keep generated/imported files out of source edits unless the project intentionally tracks them.

## Script Rules

- Prefer explicit exported references over brittle absolute node paths.
- Use groups, signals, and scene ownership consistently with existing project patterns.
- Avoid heavy node searches or allocations in `_process` and `_physics_process`.
- Keep runtime state separate from shared resource configuration unless the project pattern says otherwise.

## Validation

- Run or recommend the smallest relevant Godot editor, headless, unit, scene-load, or manual playtest check.
- Check missing node paths, broken signals, resource references, export variables, and scene instancing risks.
