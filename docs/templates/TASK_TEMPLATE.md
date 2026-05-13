# Task Template Guide

Use this guide when creating or maintaining task cards under `docs/tasks/`.

## Directory Layout

Use one directory per larger milestone:

```text
docs/tasks/vNN-short-milestone-name/
  README.md
  vNN-t01-verb-object.md
  vNN-t02-verb-object.md
```

Naming rules:

- Milestone directory: `vNN-short-milestone-name`
- Parent task: `README.md`
- Child task: `vNN-tMM-verb-object.md`

Do not repeat these naming rules inside every task card.

## Template Choice

- Use `docs/templates/TASK_PARENT_README_TEMPLATE.md` for the milestone README.
- Use `docs/templates/TASK_CHILD_TEMPLATE.md` for each executable child task.

Parent README responsibilities:

- Describe the full milestone goal and final player/editor experience.
- List child task order, dependencies, phase gates, and user confirmation points.
- Define final validation strategy across Editor checks, play flows, QA scenarios, and failure records.
- Keep shared guardrails such as scope boundaries, systems not to rebuild, and files or areas not to touch.

Child task responsibilities:

- Focus on one executable node.
- State the target outcome, deliverables, local guardrails, risks, and validation method.
- Reference the parent README for shared context instead of copying long background.
- Avoid locking concrete interfaces, class names, or method signatures unless existing code or the user already requires them.

## Task Authoring Rules

- Task cards guide agents away from scope drift; they are not full technical designs.
- Coding tasks should describe behavior, existing systems to integrate with, and what must not break.
- Placeholder or art tasks can be more specific about visible output, naming, hierarchy, color, state feedback, and replacement standards.
- QA tasks should state how to run the check, what to observe, and what to record on failure.
- If implementation depth is unclear, require the executor to ask whether the user wants a basic, complete, or expanded version.
- Preserve unknown project facts as `TBD`, `Open Questions`, or `Halt Conditions`.
