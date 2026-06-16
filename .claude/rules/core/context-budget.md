---
description: Keep agent context focused by summarizing noisy exploration, using subagents for broad searches, and preserving continuity without pasting long logs.
---

# Context Budget Rules

## Main Principle

The main conversation should keep conclusions, not raw exploration.

## Rules

- Prefer structured context before broad scanning: local session state, project brief, architecture index, system cards, then targeted files.
- Prefer reading index files, templates, and relevant examples before expanding to broad search.
- Do not scan entire folders unless necessary.
- Do not read more than a small set of large files before summarizing.
- For large Unity `.prefab`, `.unity`, or `.asset` YAML, prefer `gamekit-unity-yaml-context` to generate a compact summary before reading raw serialized content.
- For review or QA, identify changed files, affected systems, and active engine profile before reading implementation details.
- Use subagents for broad code search or noisy investigation when supported.
- Do not paste long logs into the final answer.
- Summarize long outputs before returning to the main conversation.
- If the session becomes long, create or update `.claude-local/SESSION_STATE.md`.

## Response Budget

- Lead with the conclusion, decision, or result before supporting detail.
- Keep background to 2-4 lines unless the user asks for a deeper narrative.
- Omit empty optional sections; write `None` only when the field itself carries useful signal.
- Keep top risks, options, and follow-ups to 1-3 items by default.
- Summarize logs, diffs, research notes, and search results instead of pasting raw output.
- Expand only for high-risk issues, explicit user requests, handoff continuity, or actionable findings that need evidence.
