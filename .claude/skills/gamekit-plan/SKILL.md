---
name: gamekit-plan
description: Use this skill at the start of ambiguous or multi-part game development requests to classify the goal, run a compact engineering preflight, decide whether the work is necessary now, identify the smallest useful version, check reuse/cleanup/alternatives/risks when complexity warrants it, choose workstreams and subagents, and decide whether implementation should start.
---

# gamekit-plan

Purpose: decide the safest small implementation path before work starts. This workflow is read-only: it plans, routes, and asks questions, but does not implement, clean up, or edit task cards.

## Workflow

1. Restate the user's goal and scope.
2. Identify the active engine profile from project evidence or user intent.
3. Classify the request and decide whether it is necessary now.
4. Run a compact engineering preflight: compatibility, coupling, stability/regression, performance, production cost, and testability.
5. Add Planning Notes when the task is ambiguous, multi-file, multi-system, serialized-data-heavy, architecture-sensitive, task-splitting work, or when the user asks about reuse, cleanup, better approaches, alternatives, or risk. Use targeted repository inspection before broad scanning.
6. Keep simple bug fixes and small explicit tasks light: Planning Notes may be one short line and the plan may recommend going directly to `gamekit-build`.
7. If the user asks for official guidance, references, latest/current practice, community practice, literature, or evidence-backed advice, use `gamekit-ask` Research Mode first; then return to `gamekit-plan` only if scope, workstreams, or start decision are still unclear.
8. Identify the smallest useful slice.
9. Choose required workstreams and decide whether subagents are useful. Simple work should stay local.
10. If risks are high, several approaches are close, or the approach depends on third-party APIs, plugins, performance conventions, or uncertain architecture practice, use `gamekit-ask` for evidence-backed consultation or read-only `architecture-reviewer` before implementation.
11. Choose validation depth for the eventual work. Do not default every plan to `gamekit-check`; recommend it only when risk, user intent, or the affected surface warrants it.
12. Decide whether implementation should start or whether user input is needed.

## Validation Depth

- `none`: discussion, task splitting, planning, or no implementation.
- `build-local`: clear small fix or local code change; `gamekit-build` should run the smallest relevant validation.
- `gamekit-check`: behavior, configuration, UI, asset reference, Unity serialized, prefab/scene/ScriptableObject, or multi-file risk.
- `gamekit-check + game-qa-checker`: multi-system, high-risk, pre-commit, handoff, release, or user-requested QA.

## Output Format

## Goal / Scope

## Engineering Preflight

Include active engine profile, necessity, compatibility, coupling, stability/regression, performance, production cost, and testability. Keep it concise.

## Planning Notes

Include reuse, cleanup, alternative, and concrete risk sources. For non-trivial domain logic, `Reuse` should name the canonical owner/helper and semantic sibling paths that must stay aligned. For simple tasks, compress this to one line; for complex tasks, keep it short but specific.

Reuse:

Cleanup:

Alternative:

Risk Sources:

## Smallest Useful Slice

## Workstreams / Subagents

Mention whether to use `architecture-reviewer`, `game-code-worker`, `placeholder-asset-worker`, `game-qa-checker`, `task-card-manager`, or no subagent.

## Start Decision / Questions

Yes / No / Need user decision

Validation Depth: none / build-local / gamekit-check / gamekit-check + game-qa-checker
