# Task: [Name]

Status: Todo
Owner Agent: TBD
Created: YYYY-MM-DD
Started:
Completed:

## Source / Design Input

## Requirement Summary

## Goal

## Engine / Runtime

TBD

Unity impact, if applicable:

- Scenes:
- Prefabs:
- ScriptableObjects:
- Packages / ProjectSettings:

## Executor Summary

One or two sentences that let a future executor start without rereading the original conversation.

## Scope

## Out of Scope

## Suggested Agent / Workstream

## File Ownership

Allowed to edit:

- TBD

## Do Not Touch

- TBD

## Related Files

- TBD

## Implementation Notes

Existing pattern:

- TBD

Constraints:

- TBD
- For Unity tasks, record whether the work touches `.meta`, `.unity`, `.prefab`, `.asset`, `ProjectSettings/`, `Packages/manifest.json`, Addressables, input settings, or render pipeline settings.

Source references:

- TBD

## Workstreams

- Architecture:
- Code:
- Placeholder Asset:
- QA:
- Knowledge:

## Acceptance Criteria

- [ ] AC1:

## Tasks / Subtasks

- [ ] Task 1 (AC: 1)
  - [ ] Subtask 1.1

## Validation Plan

- TBD
- For Unity tasks, choose the smallest relevant check: optional `C# compile-layer proxy check` for eligible C#-only changes, Unity compile, EditMode test, PlayMode test, manual scene/prefab inspection, or Profiler/allocation check when hot paths are affected.

## Close Criteria

- Acceptance criteria are satisfied.
- Validation plan has been completed or explicitly marked not runnable with a reason.
- Execution Record is filled.

## Executor Permissions

Allowed task-card updates:

- Tasks / Subtasks checkboxes
- Execution Record
- File List
- Change Log
- Status, Started, and Completed only when the task policy allows it

Do not update:

- Source / Design Input
- Requirement Summary
- Goal
- Scope
- Acceptance Criteria
- Validation Plan

## Halt Conditions

Stop and ask if:

- Required files, systems, or engine/runtime facts are missing.
- The task requires editing files outside File Ownership.
- The task requires adding packages, plugins, engine modules, SDKs, or major dependencies.
- The task may affect save data, networking, economy, serialization, project settings, or asset references beyond the documented scope.
- For Unity tasks, the work requires modifying `ProjectSettings/`, `Packages/manifest.json`, complex `.prefab` or `.unity` YAML, Addressables configuration, input/render pipeline settings, or many `.meta` files.

## Blocked Reason

## Risks

## Open Questions

## Execution Record

Agent Model:
Started:
Checks Run:
Files Changed:
Completion Notes:
Issues Encountered:

## File List

- TBD

## Change Log

- YYYY-MM-DD: Created.

## Next Step
