---
description: Explain how and when to load thin engine profiles without turning them into duplicate workflows.
---

# Engine Profile Rules

## Profile Selection

Use core rules for all work. Load a profile only when:

- Claude opens or works on files matching a profile's `paths` frontmatter;
- `docs/knowledge/PROJECT_BRIEF.md` declares an engine;
- repository files identify an engine;
- the user names an engine or engine-specific file type;
- the task touches engine-specific build, editor, scene, asset, or package behavior.

Profile `paths` are a convenience for Claude's path-specific rule loading. Hooks and adapters should still use the markers below when the engine is known from project files or the user's request.

## Available Profiles

- Unity: `.claude/rules/profiles/unity.md`
- Godot: `.claude/rules/profiles/godot.md`
- Unreal: `.claude/rules/profiles/unreal.md`
- Web/JS: `.claude/rules/profiles/web-js.md`

## Mixed Projects

If multiple profiles match, do not combine rules blindly. Identify the requested runtime and scope edits to that area. Ask only when the requested runtime cannot be inferred from the task or changed files.

## Profile Boundaries

Profiles are thin overlays. They should include:

- sensitive file types;
- safe edit patterns;
- dependency/package rules;
- build and validation reminders;
- engine-specific anti-patterns.

Profiles should not duplicate the core workflow, task system, memory policy, or agent routing.
