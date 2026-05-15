---
name: gamekit-plan
description: Use this skill at the start of ambiguous or multi-part game development requests to classify the goal, run a compact engineering preflight, decide whether the work is necessary now, identify the smallest useful version, determine the active engine profile, choose workstreams and subagents, and decide whether implementation should start.
---

# gamekit-plan

Purpose: decide the safest small implementation path before work starts.

## Workflow

1. Restate the user's goal and scope.
2. Identify the active engine profile from project evidence or user intent.
3. Classify the request and decide whether it is necessary now.
4. Run a compact engineering preflight: compatibility, coupling, stability/regression, performance, production cost, and testability.
5. Identify the smallest useful slice.
6. Choose required workstreams and decide whether subagents are useful. Simple work should stay local.
7. If risks are high, several approaches are close, or the approach depends on third-party APIs, plugins, performance conventions, or uncertain architecture practice, use `gamekit-ask` for evidence-backed consultation or read-only `architecture-reviewer` before implementation.
8. Decide whether implementation should start or whether user input is needed.

## Output Format

## Goal / Scope

## Engineering Preflight

Include active engine profile, necessity, compatibility, coupling, stability/regression, performance, production cost, and testability. Keep it concise.

## Smallest Useful Slice

## Workstreams / Subagents

Mention whether to use `architecture-reviewer`, `game-code-worker`, `placeholder-asset-worker`, `game-qa-checker`, `task-card-manager`, or no subagent.

## Start Decision / Questions

Yes / No / Need user decision
