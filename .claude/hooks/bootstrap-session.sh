#!/usr/bin/env bash
set -euo pipefail

brief_engine() {
  if [ -f "docs/ai/PROJECT_BRIEF.md" ]; then
    awk '
      BEGIN { in_engine_section = 0 }
      /^[[:space:]]*Engine[[:space:]]*:/ {
        value = $0
        sub(/^[[:space:]]*Engine[[:space:]]*:[[:space:]]*/, "", value)
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
        print value
        exit
      }
      /^[[:space:]]*##[[:space:]]+Engine[[:space:]]*$/ {
        in_engine_section = 1
        next
      }
      in_engine_section && /^[[:space:]]*##[[:space:]]+/ {
        exit
      }
      in_engine_section && NF {
        value = $0
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
        print value
        exit
      }
    ' docs/ai/PROJECT_BRIEF.md
  fi
}

detect_engine() {
  local declared
  declared="$(brief_engine || true)"
  if [ -n "${declared:-}" ] && ! printf '%s' "$declared" | grep -Eqi '^(TBD|Unknown|None)$'; then
    printf '%s' "$declared"
    return
  fi

  if [ -f "ProjectSettings/ProjectVersion.txt" ] || [ -f "Packages/manifest.json" ]; then
    printf 'Unity'
  elif [ -f "project.godot" ]; then
    printf 'Godot'
  elif find . -maxdepth 2 -name '*.uproject' -type f 2>/dev/null | grep -q .; then
    printf 'Unreal'
  elif [ -f "package.json" ]; then
    printf 'Web/JS'
  else
    printf 'TBD'
  fi
}

ENGINE="$(detect_engine)"

echo "## GameKit Workflow Bootstrap"
echo "- Read CLAUDE.md first."
echo "- This is a Claude-first game development workflow scaffold."
echo "- Current repository code is the source of truth."
echo "- Project docs are navigation aids, not guaranteed facts."
echo "- Active engine profile: ${ENGINE}."
echo "- Use .claude/rules/core/*.md by default."
echo "- Use .claude/rules/profiles/*.md only when the engine is known or requested."
if printf '%s' "$ENGINE" | grep -Eqi '^Unity'; then
  echo "- For Unity .prefab, .unity, or .asset context, use gamekit-unity-yaml-context before reading full raw YAML."
fi
echo "- Use REVIEW.md and gamekit-review only for explicit manual review requests."
echo "- Use gamekit-task and task-card-manager only for explicit task-card management requests."
echo "- Use docs/ai/PROJECT_BRIEF.md for project overview if needed."
echo "- Use docs/ai/ARCHITECTURE_INDEX.md for known system map if needed."
echo "- Use .claude-local/SESSION_STATE.md for local continuity if present."
echo
echo "## Git State"
git branch --show-current 2>/dev/null | sed 's/^/- Branch: /' || true
git rev-parse --short HEAD 2>/dev/null | sed 's/^/- HEAD: /' || true

OPEN_TASKS=""

while IFS= read -r task_file; do
  [ -n "$task_file" ] || continue
  status="$(grep -Eim1 '^Status:[[:space:]]*(Todo|In Progress|Blocked)' "$task_file" | sed -E 's/^Status:[[:space:]]*//I' || true)"
  if [ -n "$status" ]; then
    OPEN_TASKS="${OPEN_TASKS}- ${task_file} [${status}]
"
  fi
done <<EOF
$(find docs/tasks -maxdepth 1 -type f -name '*.md' ! -name '.gitkeep' 2>/dev/null | sort || true)
EOF

if [ -n "$OPEN_TASKS" ]; then
  echo
  echo "## Open Tasks"
  printf "%s" "$OPEN_TASKS"
  echo "- Do not claim a task automatically. Wait for the user to name a task or ask for the next task."
  echo "- Use gamekit-task and task-card-manager when the user asks to create, split, refine, claim, block, close, or audit task cards."
fi
