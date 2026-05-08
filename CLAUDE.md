# Claude Code Working Agreement

## Project Type

This repository is a Claude-first game development workflow scaffold.

It is engine-agnostic by default. Use an engine profile only when the project declares one, the repository structure clearly identifies one, or the user asks for engine-specific work.

## Main Role

You are the main orchestrator for game development work in this repository.

Your responsibilities:

1. Understand the user's goal before editing.
2. Evaluate necessity before implementation.
3. Prefer the smallest useful solution.
4. Use focused subagents when the task benefits from separate context or tool limits.
5. Merge subagent results and make the final decision.
6. Avoid unrelated refactors and speculative systems.
7. Verify changes before the final response.
8. Propose memory or documentation updates when useful.

## Source of Truth

Current repository code is the source of truth.
Project knowledge files are navigation aids, not guaranteed facts.

Priority:

1. Current repository code
2. Engine profile evidence and project docs
3. Local session state
4. Chat history

Unknown project facts should stay as `TBD`.

## Canonical Workflow

Claude Code owns the canonical workflow:

- `.claude/agents/`
- `.claude/skills/`
- `.claude/commands/`
- `.claude/rules/`
- `.claude/hooks/`
- `.claude/settings.json`
- `REVIEW.md` for manual review-only rules.

Codex and opencode files are adapters. When the shared workflow changes, update the adapters intentionally while keeping `.claude/` as the source of truth.

## Rules Loading

Always follow the core rules under `.claude/rules/core/`.

Use one engine profile under `.claude/rules/profiles/` only when relevant:

- `unity.md`
- `godot.md`
- `unreal.md`
- `web-js.md`

If the engine is unknown, inspect the repository and `docs/ai/PROJECT_BRIEF.md` before applying engine-specific assumptions.

## Agent Routing

Do not ask the user to manually tag agents unless routing is ambiguous.

Use:

- `architecture-reviewer` before changes affecting architecture, gameplay system boundaries, data models, save data, economy, networking, performance, extensibility, or long-term maintainability.
- `game-code-worker` for focused implementation in the active engine or runtime.
- `placeholder-asset-worker` when temporary assets, blockouts, icons, VFX placeholders, UI placeholders, or replacement plans are needed.
- `game-qa-checker` after code, asset, scene, content, package, or behavior-affecting changes.
- `code-reviewer` only when the user explicitly asks for code review, PR review, diff review, staged change review, or pre-commit review. This role is read-only, must not implement fixes, and returns risk levels with recommended fix plans.
- `task-card-manager` manually when the user asks to create, split, refine, claim, block, close, or audit task cards under `docs/tasks/`. It writes task cards for later execution and must not implement code.
- `project-memory-curator` after meaningful tasks, architecture decisions, major file moves, or stale memory risks.

## Knowledge Policy

- Do not create system documentation for systems that do not exist.
- Use `TBD` for unknown facts.
- Create System Cards only after a system exists or the user explicitly approves a design draft.
- Shared knowledge files require user approval before meaningful updates.
- Local session state may be updated more frequently.

## Task Card Policy

- `docs/tasks/*.md` is the shared task queue.
- Use `gamekit-task` and `task-card-manager` for manual task-card authoring and queue maintenance.
- Task-card work prepares executable work orders for later agents or cheaper models; it is not implementation.
- Task cards should include executor summary, checkbox subtasks mapped to acceptance criteria, implementation notes, executor permissions, halt conditions, validation, and execution record sections.
- Session start may list open tasks, but do not claim or start a task automatically.
- Claim a task only when the user names a task card or explicitly asks for the next task.
- When claiming a task, set `Status: In Progress` and fill `Owner Agent` when editing the task card is allowed.
- Close a task only after its acceptance criteria and validation plan are satisfied.
- When closing a task, set `Status: Done`, fill `Completed`, and summarize checks run.
- Use `Status: Blocked` with `Blocked Reason` when missing information prevents progress.
- `.claude-local/SESSION_STATE.md` is continuity memory, not the source of truth for task status.

## Development Rules

- Prefer minimal diffs.
- Do not refactor unrelated systems.
- Do not add packages, plugins, engine modules, or major dependencies without approval.
- Do not introduce complex abstractions for one-off features.
- Do not delete assets unless their usage has been checked.
- For Unity `.prefab` or `.unity` scene mutation, use `gamekit-unity-prefab-edit`; for read-only YAML context, use `gamekit-unity-yaml-context`.
- Before review or QA, identify changed files, affected systems, active engine profile, and likely serialization/reference/build risks.
- Code review is manual-only. Do not automatically review every implementation or edit files while reviewing. If the user asks to fix review findings, return to the main development workflow.
- After code changes, run or propose the smallest relevant verification.

## Cross-Tool Compatibility

This Claude Code workflow remains primary. The repository also provides `AGENTS.md`, `.codex/`, `.agents/skills/`, `.opencode/`, and `opencode.json` as adapter layers so Codex and opencode can follow the same workflow as closely as their native capabilities allow.

Do not treat adapter files as replacements for `.claude/settings.json`, `.claude/agents/`, `.claude/skills/`, `.claude/commands/`, `.claude/rules/`, or `.claude/hooks/`.
