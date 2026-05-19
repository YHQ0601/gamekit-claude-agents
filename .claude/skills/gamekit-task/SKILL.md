---
name: gamekit-task
description: Use this skill when manually arranging, creating, writing, splitting, refining, claiming, blocking, closing, or auditing task cards in docs/tasks/ so stronger planning models can prepare work for cheaper execution models. This includes Chinese requests like 布置任务, 创建任务, 写任务, 任务卡, or 工单.
---

# gamekit-task

Purpose: manage parent/child task cards under `docs/tasks/` as executable work orders without implementing the work.

## Workflow

1. Restate the user's task-management intent.
2. Read `docs/templates/TASK_TEMPLATE.md`, then use the parent or child template it points to.
3. Read existing relevant parent README and child task cards under `docs/tasks/`.
4. Read `docs/knowledge/PROJECT_BRIEF.md`, `docs/knowledge/KNOWLEDGE_INDEX.md`, and relevant code only as needed.
5. Identify the active engine profile from project evidence or user intent.
6. Create, split, refine, claim, block, close, or audit task cards.
7. Keep parent tasks focused on milestone context and child tasks small enough for a focused executor.
8. Add executor-ready child details: checkbox subtasks, acceptance-criteria mapping, implementation notes, permissions, halt conditions, and validation.
9. Preserve unknown facts as `TBD`.
10. When claiming, closing, or blocking a task, run a `project-memory-curator` memory update decision so local session state reflects task status, validation status, and any open questions.
11. Return the changed task files and executor guidance.

## Guardrails

- This workflow is manual-only. Do not run it automatically for every request.
- Default write scope is `docs/tasks/**`.
- Do not implement code, create assets, perform QA, or update shared architecture docs unless explicitly requested.
- Do not close a task without satisfied acceptance criteria and a completed validation note.
- If the user provides design material from a stronger model, preserve the source in `Source / Design Input` and convert it into parent milestones plus executable child task cards.
- If a task is intended for a cheaper model, make ownership, boundaries, validation, and risks explicit.
- Do not invent systems, files, or engine facts. Use `TBD`, `Open Questions`, or `Halt Conditions` when evidence is missing.
- Task-card status changes may update `.claude-local/SESSION_STATE.md`, but shared knowledge docs still require explicit user approval or a knowledge gate.
- Do not copy long parent milestone background into every child task. Child tasks should reference the parent README for shared guardrails.
- Do not lock concrete interfaces, class names, or method signatures in child tasks unless existing code or the user already requires them.

## Task Card Rules

- Use milestone directories named `vNN-short-milestone-name/`.
- Use `README.md` for the parent milestone task.
- Use child task files named `vNN-tMM-verb-object.md` in the same milestone directory.
- Keep naming rules in templates and workflow policy; do not repeat them in every task card.
- Use `Status: Todo` for new executable work.
- Use `Status: In Progress` only when the user names the task or asks to claim it.
- Use `Status: Blocked` only when missing information prevents meaningful progress.
- Use `Status: Done` only after close criteria and validation plan are satisfied.
- Fill `Owner Agent` with the intended executor role when known; otherwise use `TBD`.
- Parent README files describe the milestone goal, final experience, child order, dependencies, phase gates, user confirmation points, shared boundaries, and final validation strategy.
- Child task files describe one node's outcome, deliverables, local boundaries, risks, acceptance criteria, and validation method.
- Child coding tasks should emphasize behavior, existing systems to integrate with, and what must not break.
- Child placeholder/art tasks should emphasize visible result, naming, hierarchy, color, state feedback, and replacement standards.
- Child QA tasks should emphasize how to run checks, what to observe, and what to record on failure.
- Include `File Ownership` and `Do Not Touch` in child tasks for parallel work.
- Include `Executor Summary` so a future worker can start without rereading the full conversation.
- Include `Tasks / Subtasks` with checkboxes in child tasks. Map each top-level task to acceptance criteria when possible, for example `(AC: 1, 2)`.
- Include `Implementation Notes` with verified existing patterns, constraints, and source references.
- Include `Executor Permissions` so weaker executors know which task-card sections they may update.
- Include `Halt Conditions` for missing facts, unclear implementation depth, scope expansion, dependency changes, or compatibility-sensitive surfaces.
- Leave `Execution Record`, `File List`, and `Change Log` ready for the child task executor to fill during implementation.

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
