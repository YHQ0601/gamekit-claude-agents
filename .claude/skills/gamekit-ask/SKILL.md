---
name: gamekit-ask
description: Use this skill for read-only engineering consultation before implementation when the user asks how to build something more safely, compare implementation approaches, evaluate architecture, performance, compatibility, coupling, stability, production method, or testability tradeoffs. Use official docs, plugin/repository docs, examples, or mature community practice when external APIs, plugins, performance conventions, or uncertain architecture choices affect the answer. Do not use it for code review, post-change validation, task-card authoring, or implementation.
---

# gamekit-ask

Purpose: answer engineering implementation questions before code is changed.

Use this workflow when the user wants better thinking about implementation shape, architecture, performance, coupling, compatibility, stability, production method, or testability. Keep the answer compact and practical.

## Workflow

1. Restate the engineering question.
2. Read structured context first: local session state, project brief, architecture index, relevant system cards, then targeted files only as needed.
3. Identify the active engine profile from evidence or user intent.
4. When external APIs, plugins, repositories, performance conventions, or uncertain architecture choices affect the answer, check evidence before relying on memory: official docs first, then plugin/repository docs and examples, then mature community practice.
5. Compare the smallest useful set of realistic options, usually two or three.
6. Evaluate tradeoffs across compatibility, coupling, stability/regression, performance, production cost, and testability.
7. Recommend one approach and state when to use `gamekit-plan`, `gamekit-build`, `gamekit-check`, `gamekit-review`, or `gamekit-task` next.
8. If the question is architecture-sensitive, use read-only `architecture-reviewer` only when the active tool supports agents and the user's request already authorizes that workflow; otherwise recommend it. Do not use implementation workers from `gamekit-ask` alone.

## Boundaries

- Read-only by default. Do not edit code, assets, task cards, project memory, or shared docs.
- Do not perform diff review. Use `gamekit-review` for explicit review requests.
- Do not perform post-change validation. Use `gamekit-check` for verification, QA, debug triage, or risk review after changes.
- Do not turn the answer into a full design document unless the user asks for one.
- Do not paste long quotes or broad research notes. Summarize only evidence that changes the recommendation.
- When a recommendation becomes user-confirmed design, trigger `project-memory-curator` after confirmation so it can record the approved design without marking it as code-verified.

## Output Format

## Question

## Context

Include one compact `Evidence checked:` line. Use `local repo only; no external API/plugin involved` when external lookup was not needed.

## Options

## Tradeoffs

Cover compatibility, coupling, stability/regression, performance, production cost, and testability.

## Recommendation / Next Workflow
