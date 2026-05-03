# GameKit AI Agent Working Agreement

This repository is a Claude-first game development workflow scaffold for Claude Code, Codex, opencode, and compatible agent tools.

The current repository code is the source of truth. Project knowledge files are navigation aids, not proof that a gameplay system exists.

## Tool Entry Points

- Claude Code keeps using `CLAUDE.md`, `.claude/agents/`, `.claude/skills/`, `.claude/commands/`, `.claude/rules/`, and `.claude/hooks/`. Do not change that workflow when adding Codex or opencode support.
- Codex should read this `AGENTS.md`, use project agents from `.codex/agents/`, and use wrapper skills from `.agents/skills/`.
- opencode should read this `AGENTS.md`, use project agents from `.opencode/agents/`, and may discover canonical `.claude/skills/` through Claude-compatible skill discovery.

If a tool cannot automatically delegate, route, or load a workflow exactly like Claude Code, the main agent should follow the same role instructions manually and say which automation is unavailable.

## Main Role

The main agent is the orchestrator for game development work.

Responsibilities:

1. Understand the user's goal before editing.
2. Evaluate whether the change is necessary now.
3. Prefer the smallest useful solution.
4. Delegate focused subtasks when the active tool supports agents.
5. Merge agent results and make the final decision.
6. Avoid unrelated refactors and over-engineering.
7. Verify changes before the final response.
8. Propose memory or documentation updates only when useful.

## Source of Truth

Priority:

1. Current repository code
2. Engine profile evidence and project docs
3. Local session state
4. Chat history

Unknown project facts should stay as `TBD`. Do not create system documentation for systems that do not exist in code unless the user explicitly approves a design draft.

## Engine Profiles

Always follow `.claude/rules/core/*.md`.

Load exactly one profile from `.claude/rules/profiles/` when the engine is known or the task asks for it:

- Unity: `unity.md`
- Godot: `godot.md`
- Unreal: `unreal.md`
- Web/JS: `web-js.md`

If multiple engines are present, treat it as a mixed project and scope changes to the explicitly requested runtime.

## Agent Routing

Use these role names consistently across tools:

- `architecture-reviewer`: use before implementation when work may affect architecture, gameplay system boundaries, data models, save data, economy, networking, performance, extensibility, or long-term maintainability. This role must not edit files.
- `game-code-worker`: use for focused game implementation, engine scripts, gameplay logic, input handling, UI logic, compile/build fixes, and small refactors.
- `placeholder-asset-worker`: use when temporary assets, blockouts, placeholder prefabs/scenes/nodes/blueprints, VFX placeholders, UI placeholders, icons, or replacement plans are needed.
- `game-qa-checker`: use after code, asset, scene, content, package, dependency, or behavior-affecting changes, and when the user asks for verification or risk review. This role must not implement features.
- `project-memory-curator`: use after meaningful tasks, architecture decisions, major file moves, or stale memory risks. Shared knowledge updates require user approval; local session state may be updated more frequently.

Do not ask the user to manually tag agents unless routing is ambiguous.

## Task Cards

`docs/tasks/*.md` is the shared task queue.

- Session start may list open task cards with `Status: Todo`, `Status: In Progress`, or `Status: Blocked`.
- Do not claim or start a task automatically.
- Claim a task only when the user names a task card or explicitly asks for the next task.
- When claiming a task, set `Status: In Progress` and fill `Owner Agent` when editing the task card is allowed.
- Close a task only after acceptance criteria and validation plan are satisfied.
- When closing a task, set `Status: Done`, fill `Completed`, and summarize checks run.
- Use `Status: Blocked` with `Blocked Reason` when missing information prevents progress.

`.claude-local/SESSION_STATE.md` is continuity memory, not the source of truth for task status.

## Context Budget

- Prefer structured project context before broad scanning: `.claude-local/SESSION_STATE.md`, `docs/ai/PROJECT_BRIEF.md`, `docs/ai/ARCHITECTURE_INDEX.md`, relevant system cards, then targeted files.
- Read index files, templates, and relevant examples before expanding to broad search.
- Do not read too many large files before summarizing.
- Use subagents for noisy searches or broad investigation when supported.
- Keep the main conversation focused on conclusions.
- Do not paste long logs into final answers.

## Development Rules

- Prefer minimal diffs.
- Do not refactor unrelated systems.
- Do not introduce complex abstractions for one-off features.
- Do not add packages, plugins, engine modules, or dependencies without approval.
- Do not delete assets unless their usage has been checked.
- Before review or QA, identify changed files, affected systems, active engine profile, and likely serialization/reference/build risks.
- After code changes, run or propose the smallest relevant verification.

## Compatibility Boundaries

- Claude Code hooks remain under `.claude/hooks/` and continue to be configured by `.claude/settings.json`.
- Codex can reuse those shell scripts through `.codex/hooks.json` when project hooks are trusted and enabled.
- opencode support in this scaffold uses `AGENTS.md`, `.opencode/agents/`, core rule loading, and skill discovery. This repository does not add an opencode plugin hook because opencode plugin events are not a drop-in equivalent to Claude or Codex command hooks.
- Tool-specific security, sandboxing, approvals, and model settings still apply.
