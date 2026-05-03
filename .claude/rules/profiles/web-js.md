---
description: Thin Web/JS game profile for browser runtimes, package scripts, assets, rendering, input, and browser validation.
---

# Web/JS Profile

## Markers

Use this profile when the repository contains `package.json`, Vite/Webpack/Next config, `src/` browser code, Phaser, Three.js, Pixi, Babylon, Canvas/WebGL/WebGPU code, or the user asks for browser game work.

## Sensitive Files

Be careful with:

- `package.json`
- lockfiles
- bundler config
- public/static asset folders
- shader files
- save/local storage schema
- deployment config

## Recommended Minimal Structure

Respect the existing Web/JS project structure first. For a new or empty browser game project, use `src/game/` for source-owned game code and `public/assets/` for static assets that must be served directly:

```text
src/game/
  scenes/
  systems/
  ui/
  assets/
public/assets/
```

Keep bundler conventions intact. If the project already separates imported source assets from public runtime assets, follow that convention instead of forcing this layout.

## Safety Rules

- Do not add or upgrade npm dependencies without approval.
- Do not rewrite bundler or deployment config unless the task requires it.
- Keep generated assets separate from source assets.
- Preserve public asset paths used by runtime loading.
- Treat save data, local storage keys, network protocol, and leaderboard/account integrations as compatibility-sensitive.

## Runtime Rules

- Keep the main loop bounded and avoid avoidable allocations.
- Use requestAnimationFrame/game-engine loops consistently with existing project patterns.
- Avoid blocking asset loads, synchronous heavy work, or layout thrash during gameplay.
- Prefer proven engine/library systems for physics, animation, tilemaps, and asset loading when the project already uses them.
- Make controls and HUD responsive across desktop and mobile when applicable.

## Validation

- Run or recommend the smallest relevant `npm` script, browser smoke test, canvas/WebGL nonblank check, input test, responsive check, or manual playtest.
- Check console errors, failed asset loads, frame loop regressions, pointer/keyboard/touch behavior, and production build risk.
