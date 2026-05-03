---
description: Keep project folder decisions lightweight, engine-aware, and consistent while avoiding unnecessary directory churn.
---

# Project Structure Rules

## Main Principle

Respect the existing project structure first. Use the recommended engine structure only when the project is new, empty, inconsistent, or missing an obvious home for the new file.

## When This Rule Applies

Use this rule when creating or relocating:

- gameplay code;
- scenes, maps, levels, or prefabs;
- UI files;
- art, audio, VFX, or placeholder assets;
- data, config, resources, or tests;
- editor/tooling scripts.

## Default Project Root Name

When the project name is unknown, use `Game` as the default content root.

Examples:

- Unity: `Assets/Game/`
- Unreal: `Content/Game/`
- Godot: `res://game/`
- Web/JS: `src/game/`

For a mature or named project, prefer the existing project name or established root instead of forcing `Game`.

## Decision Rules

- Do not reorganize an existing project just to match this template.
- Do not create a deep folder tree for one small feature.
- Prefer the nearest existing folder that matches the feature's domain.
- If no folder exists, create the smallest useful folder under the active engine's recommended root.
- Keep third-party, plugin, marketplace, sample, generated, and engine-owned content separate from project-owned content.
- Keep runtime code, editor/tooling code, tests, and content assets in their appropriate engine-specific locations.
- For placeholder assets, default to the target asset folder with `_PH` naming and `[AssetName]_ArtistBrief.md`; move to dedicated placeholder folders only when project scale or asset-pipeline risk justifies it.

## When To Ask Before Moving Files

Ask or propose a plan before broad file moves when:

- many existing references may change;
- scenes, prefabs, resources, blueprints, import metadata, or generated files are involved;
- package, plugin, module, or build configuration paths may change;
- the move affects public API, save data, remote asset paths, or deployment paths.
