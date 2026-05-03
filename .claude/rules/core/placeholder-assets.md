---
description: Keep placeholder assets temporary, replaceable, clearly named, co-located by default for demo speed, and easy to replace later.
---

# Placeholder Asset Rules

## Purpose

Placeholder assets are temporary, replaceable assets used to test gameplay and communicate intent before final art is ready.

## Naming

- Placeholder assets must include a clear marker such as `_PH` or the project's existing placeholder convention.
- Prefer `_PH` for placeholder assets and `MAT_PH_` for placeholder materials.
- Artist replacement briefs should use `[AssetName]_ArtistBrief.md`.
- Placeholder textures, sprites, prefabs, scenes, nodes, blueprints, and generated files should be named by gameplay purpose.
- Avoid final-art names or style claims for temporary assets.

## Placement

Default to placing placeholder assets next to the target/final asset location. This keeps demo and small-project workflows fast and makes later artist replacement obvious.

Example:

```text
Characters/Hero/Hero_PH.prefab
Characters/Hero/MAT_PH_Hero.mat
Characters/Hero/Hero_ArtistBrief.md
```

Co-located placeholders are allowed only when they are clearly marked, documented, and do not overwrite final assets.

Use a dedicated placeholder, prototype, blockout, or generated-art folder when the project outgrows the simple co-located workflow.

## Upgrade To Dedicated Placeholder Folders

Recommend migrating placeholders to a dedicated folder when any of these become true:

- There are roughly 50 or more placeholder assets.
- The project has multiple contributors or dedicated artists.
- The demo is becoming a long-running project.
- The project uses dynamic loading, Addressables, AssetBundles, Pak files, remote assets, DLC, mods, or similar asset pipelines.
- Placeholder cleanup is hard to audit.
- The same placeholder asset is referenced by many systems.
- The project needs strict separation between demo/licensed assets and final art.

## Replacement Anchors

- Gameplay code should reference stable anchors, sockets, nodes, exported references, or documented attachment points, not disposable placeholder geometry.
- Artists should be able to replace visuals without breaking gameplay references.
- Keep gameplay and replacement anchors stable when applicable, such as `GameplayRoot`, `VisualRoot`, `Model_ReplaceHere`, `VFX_Anchor`, `SFX_Anchor`, `UI_Anchor`, and `HitboxPreview`.

## Materials and Visuals

- Use simple readable colors and shapes.
- Prefer primitives, flat colors, simple sprites, low-poly meshes, or tool-generated blockouts.
- Do not create final art or decide final art style beyond functional readability.
- Avoid complex shaders or expensive effects for placeholders.

## Do Not

- Do not overwrite artist-created assets.
- Do not create unmarked placeholder assets in target/final asset folders.
- Do not hand-edit complex engine asset formats unless explicitly approved.
- Do not bind gameplay directly to disposable placeholder meshes or sprites.
