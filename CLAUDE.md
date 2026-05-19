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

Current repository code, engine assets, scenes/prefabs, and configuration are the source of truth for their actual state.
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

If the engine is unknown, inspect the repository and `docs/knowledge/PROJECT_BRIEF.md` before applying engine-specific assumptions.

## Agent Routing

Do not ask the user to manually tag agents unless routing is ambiguous.

Workflow routing:

- Use `gamekit-plan` for ambiguous or multi-part requests before implementation. It should include a compact engineering preflight and decide whether subagents are useful.
- Use `gamekit-ask` for read-only engineering consultation about implementation approach, architecture, compatibility, coupling, stability, performance, production method, or testability. Use its Research Mode when the user asks for official guidance, references, best practices, latest/current practice, or evidence-backed advice.
- Use `gamekit-check` after behavior-affecting changes or for debug triage. It validates risks but does not implement fixes.
- Use `gamekit-review` only for explicit review requests. It is read-only and findings-first.

Subagent flow:

- The main agent remains the orchestrator. Simple work should stay local.
- Use subagents automatically only when the active tool supports them and the user's request already authorizes that kind of work.
- `gamekit-plan` may route to `architecture-reviewer`, `game-code-worker`, `placeholder-asset-worker`, `game-qa-checker`, or `task-card-manager`.
- `gamekit-ask` usually uses no subagent; serious architecture tradeoffs may use or recommend read-only `architecture-reviewer`.
- `gamekit-check` may use `game-qa-checker`; `gamekit-review` may use `code-reviewer` only for explicit review.

Use:

- `architecture-reviewer` before changes affecting architecture, gameplay system boundaries, data models, save data, economy, networking, performance, extensibility, or long-term maintainability.
- `game-code-worker` for focused implementation in the active engine or runtime.
- `placeholder-asset-worker` when temporary assets, blockouts, icons, VFX placeholders, UI placeholders, or replacement plans are needed.
- `game-qa-checker` after code, asset, scene, content, package, or behavior-affecting changes.
- `code-reviewer` only when the user explicitly asks for code review, PR review, diff review, staged change review, or pre-commit review. This role is read-only, must not implement fixes, and returns risk levels with recommended fix plans.
- `task-card-manager` manually when the user asks to create, split, refine, claim, block, close, or audit task cards under `docs/tasks/`. It writes task cards for later execution and must not implement code.
- `project-memory-curator` after meaningful tasks, architecture decisions, major file moves, or stale memory risks.

Use `project-memory-curator` proactively at these checkpoints:

- After completing a meaningful task, especially when code, assets, scenes, prefabs, configuration, workflow files, or task-card status changed.
- After large changes such as multi-file edits, system boundary changes, directory moves, batch renames, schema/template updates, or workflow changes.
- Before or after a commit, recording current facts, change summary, validation status, and last useful commit.
- Before handoff. Run the memory update decision first, then prepare the handoff summary.
- After git pulls or external syncs that changed key project areas.
- After architecture decisions, newly stable systems, confirmed engine identity, or major constraints are established.
- When the user explicitly confirms a design is done, final, approved, fully settled, or says to proceed with that design.
- When the session becomes long, context may be compacted, or the user asks to continue later, summarize, hand off, or remember something.

## Knowledge Policy

- `docs/knowledge/` is the canonical shared project knowledge entry. Keep it as a short navigation index, not a complete fact database.
- Do not create system documentation for systems that do not exist.
- Use `TBD` for unknown facts.
- Existing System Cards under `docs/systems/` may be refreshed only when the user explicitly asks for knowledge maintenance or runs a knowledge gate, and the changes are code-verified and scoped to stable entry points. New System Cards require user confirmation or an explicit knowledge gate.
- ADRs under `docs/decisions/` require user confirmation before writing. Review, check, and push gates may propose ADRs but must not silently create accepted decisions.
- Handoff updates `.claude-local/SESSION_STATE.md` first and only proposes shared knowledge updates.
- Push, pre-push, and publish requests should trigger a lightweight knowledge gate recommendation; do not add hard Git hooks by default.
- Local session state should be updated aggressively when the facts are verified or user-confirmed.
- Shared knowledge updates should be proposed, not silently applied, for `docs/knowledge/*`, new `docs/systems/*`, `docs/decisions/*`, and skill documentation.
- User-confirmed designs should be recorded as approved design facts. If a design is not implemented yet, label it as approved but not code-verified.

When creating or refreshing `.claude-local/SESSION_STATE.md`, use `docs/templates/SESSION_STATE_TEMPLATE.md` as the tracked template. Suggested sections:

- Current Focus
- Verified Facts
- User-Confirmed Decisions
- Approved Designs
- Recent Changes
- Validation Status
- Open Risks / Stale Facts
- Unclear / Ask Before Continuing
- Next Step
- Last Verified Commit

## Task Card Policy

- `docs/tasks/` is the shared parent/child task queue. Use `vNN-short-milestone-name/README.md` for parent milestones and `vNN-tMM-verb-object.md` for executable child tasks.
- Use `gamekit-task` and `task-card-manager` for manual task-card authoring and queue maintenance.
- Task-card work prepares executable work orders for later agents or cheaper models; it is not implementation.
- Parent README files should define the milestone goal, child order, dependencies, phase gates, user confirmation points, shared boundaries, and final validation strategy.
- Child task cards should include a single-node goal, executor summary, checkbox subtasks mapped to acceptance criteria, implementation notes, executor permissions, halt conditions, validation method, and execution record sections.
- Child task cards should reference the parent README instead of copying long milestone background, and should not lock interfaces or APIs unless code or user requirements already do.
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
- For Unity `.prefab` or `.unity` scene mutation, use `gamekit-unity-prefab-edit`; for read-only YAML context, use `gamekit-unity-yaml-context`. When mutation requires the Unity Editor backend and `Assets/Editor/AgentTools/PrefabEditTool.cs` is missing, install it from the skill template automatically.
- Before review or QA, identify changed files, affected systems, active engine profile, and likely serialization/reference/build risks.
- Code review is manual-only. Do not automatically review every implementation or edit files while reviewing. If the user asks to fix review findings, return to the main development workflow.
- After code changes, run or propose the smallest relevant verification.

## Cross-Tool Compatibility

This Claude Code workflow remains primary. The repository also provides `AGENTS.md`, `.codex/`, `.agents/skills/`, `.opencode/`, and `opencode.json` as adapter layers so Codex and opencode can follow the same workflow as closely as their native capabilities allow.

Do not treat adapter files as replacements for `.claude/settings.json`, `.claude/agents/`, `.claude/skills/`, `.claude/commands/`, `.claude/rules/`, or `.claude/hooks/`.
