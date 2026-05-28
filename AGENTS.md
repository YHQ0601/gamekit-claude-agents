# GameKit AI Agent Working Agreement

This repository is a Claude-first game development workflow scaffold for Claude Code, Codex, opencode, and compatible agent tools.

The current repository code, engine assets, scenes/prefabs, and configuration are the source of truth for their actual state. Project knowledge files are navigation aids, not proof that a gameplay system exists.

## Tool Entry Points

- Claude Code keeps using `CLAUDE.md`, `.claude/agents/`, `.claude/skills/`, `.claude/commands/`, `.claude/rules/`, and `.claude/hooks/`. Do not change that workflow when adding Codex or opencode support.
- Manual review should use `REVIEW.md` and `gamekit-review`. Reviewers must return findings, risk level, per-finding fix plans, and validation recommendations instead of applying fixes.
- Manual task-card management should use `gamekit-task`, `task-card-manager`, `docs/templates/TASK_TEMPLATE.md`, and parent/child task cards under `docs/tasks/`.
- Unity YAML context work should use `gamekit-unity-yaml-context` before reading full `.prefab`, `.unity`, or `.asset` files.
- Unity prefab or scene mutation work should use `gamekit-unity-prefab-edit`; use `gamekit-unity-yaml-context` before reading raw serialized YAML. When mutation requires the Unity Editor backend and `Assets/Editor/AgentTools/PrefabEditTool.cs` is missing, install it from the skill template automatically.
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

Workflow routing:

- `gamekit-plan`: use before ambiguous or multi-part implementation work. It should include a compact engineering preflight and decide whether subagents are useful.
- `gamekit-ask`: use for read-only engineering consultation about implementation approach, architecture, compatibility, coupling, stability, performance, production method, or testability. Use its Research Mode when the user asks for official guidance, references, best practices, latest/current practice, or evidence-backed advice.
- `gamekit-check`: use after behavior-affecting changes or for debug triage. It validates risks but does not implement fixes.
- `gamekit-review`: use only for explicit review requests. It remains read-only and findings-first.

Subagent flow:

- The main agent remains the orchestrator. Simple work should stay local.
- Use subagents automatically only when the active tool supports them and the user's request already authorizes that kind of work.
- `gamekit-plan` may route to `architecture-reviewer`, `game-code-worker`, `placeholder-asset-worker`, `game-qa-checker`, or `task-card-manager`.
- `gamekit-ask` usually uses no subagent; serious architecture tradeoffs may use or recommend read-only `architecture-reviewer`.
- `gamekit-check` may use `game-qa-checker`; `gamekit-review` must use `code-reviewer` for explicit review when subagent delegation is available.

- `architecture-reviewer`: use before implementation when work may affect architecture, gameplay system boundaries, data models, save data, economy, networking, performance, extensibility, or long-term maintainability. This role must not edit files.
- `game-code-worker`: use for focused game implementation, engine scripts, gameplay logic, input handling, UI logic, compile/build fixes, and small refactors.
- `placeholder-asset-worker`: use when temporary assets, blockouts, placeholder prefabs/scenes/nodes/blueprints, VFX placeholders, UI placeholders, icons, or replacement plans are needed.
- `game-qa-checker`: use after code, asset, scene, content, package, dependency, or behavior-affecting changes, and when the user asks for verification or risk review. This role must not implement features.
- `code-reviewer`: use only when the user explicitly asks for code review, PR review, diff review, staged change review, or pre-commit review. This role must not edit files or implement fixes; it returns findings, risk levels, per-finding fix plans, and validation recommendations.
- `task-card-manager`: use manually when the user asks to create, split, refine, claim, block, close, or audit task cards under `docs/tasks/`. This role writes task cards for later execution and must not implement code.
- `project-memory-curator`: use after meaningful tasks, architecture decisions, major file moves, or stale memory risks. Shared knowledge updates require user approval; local session state may be updated more frequently.

Do not ask the user to manually tag agents unless routing is ambiguous.

Use `project-memory-curator` proactively at these checkpoints:

- After completing a meaningful task, especially when code, assets, scenes, prefabs, configuration, workflow files, or task-card status changed.
- After large changes such as multi-file edits, system boundary changes, directory moves, batch renames, schema/template updates, or workflow changes.
- Before or after a commit, recording current facts, change summary, validation status, and last useful commit.
- Before handoff. Run the memory update decision first, then prepare the handoff summary.
- After git pulls or external syncs that changed key project areas.
- After architecture decisions, newly stable systems, confirmed engine identity, or major constraints are established.
- When the user explicitly confirms a design is done, final, approved, fully settled, or says to proceed with that design.
- When the session becomes long, context may be compacted, or the user asks to continue later, summarize, hand off, or remember something.

## Task Cards

`docs/tasks/` is the shared parent/child task queue. Use `vNN-short-milestone-name/README.md` for parent milestones and `vNN-tMM-verb-object.md` for executable child tasks.

- Session start may list open task cards with `Status: Todo`, `Status: In Progress`, or `Status: Blocked`.
- Use `gamekit-task` and `task-card-manager` for manual task-card authoring and queue maintenance.
- Task-card work should prepare executable work orders for later agents or cheaper models; it is not implementation.
- Parent README files should define the milestone goal, child order, dependencies, phase gates, user confirmation points, shared boundaries, and final validation strategy.
- Child task cards should include a single-node goal, executor summary, checkbox subtasks mapped to acceptance criteria, implementation notes, executor permissions, halt conditions, validation method, and execution record sections.
- Child task cards should reference the parent README instead of copying long milestone background, and should not lock interfaces or APIs unless code or user requirements already do.
- Do not claim or start a task automatically.
- Claim a task only when the user names a task card or explicitly asks for the next task.
- When claiming a task, set `Status: In Progress` and fill `Owner Agent` when editing the task card is allowed.
- Close a task only after acceptance criteria and validation plan are satisfied.
- When closing a task, set `Status: Done`, fill `Completed`, and summarize checks run.
- Use `Status: Blocked` with `Blocked Reason` when missing information prevents progress.

`.claude-local/SESSION_STATE.md` is continuity memory, not the source of truth for task status.

## Knowledge Update Policy

- `docs/knowledge/` is the canonical shared project knowledge entry. Keep it as a short navigation index, not a complete fact database.
- Local session state should be updated aggressively when facts are verified in code or explicitly confirmed by the user.
- Existing System Cards under `docs/systems/` may be refreshed only when the user explicitly asks for knowledge maintenance or runs a knowledge gate, and the changes are code-verified and scoped to stable entry points. New System Cards require user confirmation or an explicit knowledge gate.
- ADRs under `docs/decisions/` require user confirmation before writing. Review, check, and push gates may propose ADRs but must not silently create accepted decisions.
- Handoff updates `.claude-local/SESSION_STATE.md` first and only proposes shared knowledge updates.
- Push, pre-push, and publish requests should trigger a lightweight knowledge gate recommendation; do not add hard Git hooks by default.
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

## Context Budget

- Prefer structured project context before broad scanning: `.claude-local/SESSION_STATE.md`, `docs/knowledge/PROJECT_BRIEF.md`, `docs/knowledge/KNOWLEDGE_INDEX.md`, relevant system cards, then targeted files.
- Read index files, templates, and relevant examples before expanding to broad search.
- Do not read too many large files before summarizing.
- For Unity `.prefab`, `.unity`, and `.asset` files, use the canonical `.claude/skills/gamekit-unity-yaml-context/SKILL.md` workflow to generate a compact Markdown summary before reading raw YAML.
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
- Code review is manual-only. Do not automatically review every implementation or edit files while reviewing. If the user asks to fix review findings, return to the main development workflow.
- After code changes, run or propose the smallest relevant verification.

## Compatibility Boundaries

- Claude Code hooks remain under `.claude/hooks/` and continue to be configured by `.claude/settings.json`.
- Codex can reuse those shell scripts through `.codex/hooks.json` when project hooks are trusted and enabled.
- opencode support in this scaffold uses `AGENTS.md`, `.opencode/agents/`, core rule loading, and skill discovery. This repository does not add an opencode plugin hook because opencode plugin events are not a drop-in equivalent to Claude or Codex command hooks.
- Tool-specific security, sandboxing, approvals, and model settings still apply.
