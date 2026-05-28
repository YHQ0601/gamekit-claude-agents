Use the canonical workflow in `.claude/skills/gamekit-review/SKILL.md`.

Apply it to the user's explicit review request. Must delegate the review body to `code-reviewer` when subagent delegation is available; do not perform the substantive review in the main agent unless delegation is unavailable. Review the current diff, staged changes, unstaged changes, PR patch, or named files without editing. Use `REVIEW.md` and return prioritized findings, risk level, per-finding fix plans, and validation recommendations to the main conversation. Do not apply fixes.
