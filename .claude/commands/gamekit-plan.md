Use the canonical workflow in `.claude/skills/gamekit-plan/SKILL.md`.

Apply it to the user's current request. Classify the goal and scope, run a compact engineering preflight, add concise Planning Notes for reuse, cleanup, alternatives, and concrete risk sources when complexity warrants it, identify the active engine profile, define the smallest useful slice, choose workstreams and subagents, choose validation depth, and decide whether implementation should start or user input is needed.

Keep simple explicit tasks light. If the user asks for official guidance, references, latest/current practice, community practice, literature, or evidence-backed advice, use `gamekit-research` for evidence and `gamekit-ask` for the recommendation, then return here only when planning is still needed.

Do not default every plan to `gamekit-check`. Use `Validation Depth: none / build-local / gamekit-check / gamekit-check + game-qa-checker` based on risk and user intent.
