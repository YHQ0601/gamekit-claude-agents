---
name: gamekit-ask
description: Use this skill for read-only engineering consultation before implementation when the user asks how to build something more safely, compare implementation approaches, evaluate architecture, performance, compatibility, coupling, stability, production method, or testability tradeoffs. It invokes gamekit-research when external evidence is required, then combines that evidence with local repository facts. Do not use it for code review, post-change validation, task-card authoring, or implementation.
---

# gamekit-ask

Purpose: answer engineering implementation questions before code is changed.

Use this workflow when the user wants better thinking about implementation shape, architecture, performance, coupling, compatibility, stability, production method, or testability. Keep the answer compact and practical.

## Workflow

1. Restate the engineering question.
2. Read structured context first: local session state, project brief, architecture index, relevant system cards, then targeted files only as needed.
3. Identify the active engine profile from evidence or user intent.
4. Apply the Evidence Gate. Invoke `gamekit-research` and wait for its result when the user asks for official, current, community, literature, source-backed, or best-practice evidence; when version-sensitive external APIs, SDKs, plugins, packages, or engine behavior matter; or when an external fact could change an architecture, compatibility, dependency, or performance recommendation.
5. Skip research when current repository evidence is sufficient, the knowledge is stable and version-independent, or the user explicitly requests local-only analysis.
6. Compare the smallest useful set of realistic options, usually two or three.
7. Evaluate tradeoffs across compatibility, coupling, stability/regression, performance, production cost, and testability.
8. Recommend one approach and state when to use `gamekit-plan`, `gamekit-build`, `gamekit-check`, `gamekit-review`, or `gamekit-task` next.
9. If the question is architecture-sensitive, use read-only `architecture-reviewer` only when the active tool supports agents and the user's request already authorizes that workflow; otherwise recommend it. Do not use implementation workers from `gamekit-ask` alone.
10. Keep the answer conclusion-first and compact; expand only on tradeoffs that change the recommendation.

## Boundaries

- Read-only by default. Do not edit code, assets, task cards, project memory, or shared docs.
- `gamekit-research` is the only external evidence workflow. Do not simulate research inside `gamekit-ask`.
- If research is unavailable, identify the limitation and keep any local-only recommendation provisional.
- Evidence lookup is not permission to implement. If implementation is also requested, answer the consultation first, then route back to `gamekit-build`.
- Do not perform diff review. Use `gamekit-review` for explicit review requests.
- Do not perform post-change validation. Use `gamekit-check` for verification, QA, debug triage, or risk review after changes.
- Do not turn the answer into a full design document unless the user asks for one.
- Do not paste long quotes or broad research notes. Summarize only evidence that changes the recommendation.
- When a recommendation becomes user-confirmed design, trigger `project-memory-curator` after confirmation so it can record the approved design without marking it as code-verified.

## Output Format

## Question

## Context

Include one compact `Evidence checked:` line. Summarize the research result or use `local repo only` when external lookup was not needed.

## Options

## Tradeoffs

Cover compatibility, coupling, stability/regression, performance, production cost, and testability.

## Recommendation / Next Workflow
