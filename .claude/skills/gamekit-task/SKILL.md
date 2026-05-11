---
name: gamekit-task
description: Use this skill when manually arranging, creating, writing, splitting, refining, claiming, blocking, closing, or auditing task cards in docs/tasks/ so stronger planning models can prepare work for cheaper execution models. This includes Chinese requests like 布置任务, 创建任务, 写任务, 任务卡, or 工单.
---

# gamekit-task

Purpose: manage `docs/tasks/*.md` as executable work orders without implementing the work.

## Workflow

1. Restate the user's task-management intent.
2. Read `docs/templates/TASK_TEMPLATE.md`.
3. Read existing relevant task cards under `docs/tasks/`.
4. Read `docs/ai/PROJECT_BRIEF.md`, `docs/ai/ARCHITECTURE_INDEX.md`, and relevant code only as needed.
5. Identify the active engine profile from project evidence or user intent.
6. Create, split, refine, claim, block, close, or audit task cards.
7. Keep every task small enough for a focused executor.
8. Add executor-ready details: checkbox subtasks, acceptance-criteria mapping, implementation notes, permissions, halt conditions, and validation.
9. Preserve unknown facts as `TBD`.
10. When claiming, closing, or blocking a task, run a `project-memory-curator` memory update decision so local session state reflects task status, validation status, and any open questions.
11. Return the changed task files and executor guidance.

## Guardrails

- This workflow is manual-only. Do not run it automatically for every request.
- Default write scope is `docs/tasks/*.md`.
- Do not implement code, create assets, perform QA, or update shared architecture docs unless explicitly requested.
- Do not close a task without satisfied acceptance criteria and a completed validation note.
- If the user provides design material from a stronger model, preserve the source in `Source / Design Input` and convert it into executable task cards.
- If a task is intended for a cheaper model, make ownership, boundaries, validation, and risks explicit.
- Do not invent systems, files, or engine facts. Use `TBD`, `Open Questions`, or `Halt Conditions` when evidence is missing.
- Task-card status changes may update `.claude-local/SESSION_STATE.md`, but shared architecture or project knowledge docs still require explicit user approval.

## Task Card Rules

- Use `Status: Todo` for new executable work.
- Use `Status: In Progress` only when the user names the task or asks to claim it.
- Use `Status: Blocked` only when missing information prevents meaningful progress.
- Use `Status: Done` only after close criteria and validation plan are satisfied.
- Fill `Owner Agent` with the intended executor role when known; otherwise use `TBD`.
- Include `File Ownership` and `Do Not Touch` for parallel work.
- Include `Executor Summary` so a future worker can start without rereading the full conversation.
- Include `Tasks / Subtasks` with checkboxes. Map each top-level task to acceptance criteria when possible, for example `(AC: 1, 2)`.
- Include `Implementation Notes` with verified existing patterns, constraints, and source references.
- Include `Executor Permissions` so weaker executors know which task-card sections they may update.
- Include `Halt Conditions` for missing facts, scope expansion, dependency changes, or compatibility-sensitive surfaces.
- Leave `Execution Record`, `File List`, and `Change Log` ready for the executor to fill during implementation.

## Output Format

## Task Card Decision

Created / Updated / Split / Blocked / No change needed

## Files Changed

## Active Engine Profile

Unity / Godot / Unreal / Web/JS / Mixed / TBD

## Executor Guidance

## Open Questions

## Validation Needed

## Memory Update Decision
