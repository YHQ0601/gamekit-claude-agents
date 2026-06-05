Use the canonical workflow in `.claude/skills/gamekit-check/SKILL.md`.

Apply it to the user's current request. Summarize changed area and active engine profile, build a concise risk matrix, recommend validation, and report pass/risky/fail status.

Safe Auto-Fix Escalation: because this command is an explicit `/gamekit-check` request, it may route one narrow `Direct Fix Candidate` through `gamekit-build`, then immediately rerun the smallest useful `gamekit-check` validation. Do not use this escalation when the user asks for read-only, only report, do not edit, only check, or equivalent.

`gamekit-check` itself does not edit files; any auto-fix must be performed by `gamekit-build` Direct Fix Mode and reported back with the follow-up validation result.
