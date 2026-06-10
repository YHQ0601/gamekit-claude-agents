---
name: gamekit-research
description: Use this skill for explicit web research, official guidance, current or latest practices, references, literature, community evidence, and version-sensitive external facts. It must search the web in an isolated read-only subagent and return a compact evidence summary. Do not use it for local-repository-only questions, implementation, review, or validation.
context: fork
agent: web-researcher
---

# gamekit-research

Purpose: collect external evidence without filling the main conversation with search noise.

## Workflow

1. Restate the research question and relevant version or date constraints.
2. Search the web. Do not answer from model memory alone.
3. Prefer current official docs, release notes, specifications, source code, and maintainer repositories.
4. When official evidence is insufficient, use actively maintained and widely adopted community repositories or technical references.
5. Record the research date, match evidence to the relevant version, and prefer recently updated sources for fast-changing topics.
6. One authoritative source may be enough for a clear fact. Cross-check recommendations, uncertain claims, and conflicting behavior.
7. Return only evidence that can affect the parent workflow's decision.

If web search is unavailable, report the blocker. Do not present an unverified answer as researched evidence.

## Boundaries

- Read-only. Do not edit files, implement changes, review diffs, or run validation.
- Distinguish sourced facts from inference.
- Include direct links and note relevant dates, version limits, conflicts, or insufficient evidence.
- Do not collect sources only to meet a number.

## Output Format

## Research Question

## Sources

## Findings

## Conflicts / Limits

## Implication
