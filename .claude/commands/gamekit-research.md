Use the canonical workflow in `.claude/skills/gamekit-research/SKILL.md`.

Apply it to the user's research question. This explicit command must attempt web search through the isolated `web-researcher` subagent, return compact sourced evidence, and report a blocker rather than answering from model memory when search is unavailable.
