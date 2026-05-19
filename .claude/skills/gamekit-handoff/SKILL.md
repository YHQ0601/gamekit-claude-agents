---
name: gamekit-handoff
description: Use this skill when preparing a concise continuation summary across sessions, before pausing long tasks, before context compaction, when the user says to continue later, or when summarizing current focus, last useful commit, files touched, decisions, next step, and stale facts that must be re-verified.
---

# gamekit-handoff

Purpose: lightweight multi-session continuity summary.

Before writing the handoff, run a `project-memory-curator` memory update decision. Update `.claude-local/SESSION_STATE.md` when there are verified or user-confirmed facts, but do not silently change shared knowledge files.

Handoff is for continuity into a future session. It may recommend updates to `docs/knowledge/`, `docs/systems/`, or `docs/decisions/`, but shared docs are not written during handoff unless the user explicitly asks for knowledge maintenance.

Use current repository code as the source of truth. Prefer the latest `.claude-local/SESSION_STATE.md` for continuity, but re-verify stale or high-impact facts from code or explicit user decisions.

## Ambiguity Handling

- Always include `Unclear / Ask Before Continuing`.
- Put blocking or high-impact questions near the top of the handoff.
- Do not fill gaps with guesses when the ambiguity affects scope, acceptance, compatibility, migration, risk, cost, or next implementation steps.
- If the user is still available in the current conversation, ask the necessary questions before treating the handoff as complete.
- If the handoff is for a future session, phrase unclear items as direct questions that the next agent can ask the user.

## Output Format

## Unclear / Ask Before Continuing

## Current Focus

## Last Useful Commit

## Active Engine Profile

## Files Touched

## Decisions

## Next Step

## Stale / Verify Before Use

## Shared Knowledge Recommendations
