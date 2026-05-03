#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
if command -v jq >/dev/null 2>&1; then
  PROMPT="$(printf '%s' "$INPUT" | jq -r '.prompt // ""' 2>/dev/null || printf '%s' "$INPUT")"
else
  PROMPT="$INPUT"
fi

HINTS=()

add_hint() {
  HINTS+=("$1")
}

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

case "$(printf '%s' "$ENGINE" | tr '[:upper:]' '[:lower:]')" in
  unity*) add_hint "Detected Unity profile. Load .claude/rules/profiles/unity.md before engine-specific work." ;;
  godot*) add_hint "Detected Godot profile. Load .claude/rules/profiles/godot.md before engine-specific work." ;;
  unreal*) add_hint "Detected Unreal profile. Load .claude/rules/profiles/unreal.md before engine-specific work." ;;
  web*|javascript*|js*) add_hint "Detected Web/JS profile. Load .claude/rules/profiles/web-js.md before engine-specific work." ;;
esac

if echo "$PROMPT" | grep -Eqi 'unity|c#|csharp|monobehaviour|scriptableobject|prefab|scene|projectsettings|unity editor|\.meta|预制体|场景|组件|脚本'; then
  add_hint "This looks like Unity-specific work. Use .claude/rules/profiles/unity.md and consider game-code-worker or game-qa-checker."
fi

if echo "$PROMPT" | grep -Eqi 'godot|gdscript|node|scene tree|\.tscn|\.tres|signal|autoload|project.godot'; then
  add_hint "This looks like Godot-specific work. Use .claude/rules/profiles/godot.md and consider game-code-worker or game-qa-checker."
fi

if echo "$PROMPT" | grep -Eqi 'unreal|ue5|ue4|blueprint|uasset|umap|uproject|uclass|uproperty|uobject|module|plugin'; then
  add_hint "This looks like Unreal-specific work. Use .claude/rules/profiles/unreal.md and consider game-code-worker or game-qa-checker."
fi

if echo "$PROMPT" | grep -Eqi 'phaser|three\.?js|pixi|babylon|vite|canvas|webgl|webgpu|browser game|npm|package.json|网页游戏'; then
  add_hint "This looks like Web/JS game work. Use .claude/rules/profiles/web-js.md and consider game-code-worker or game-qa-checker."
fi

if echo "$PROMPT" | grep -Eqi 'code|script|component|gameplay|combat|inventory|quest|level|spawn|controller|manager|compile|build|error|exception|input|ui logic|ability|item|character|代码|脚本|玩法|战斗|背包|任务|关卡|生成|控制器|管理器|编译|构建|报错|输入|技能|道具|角色'; then
  add_hint "This looks like focused implementation work. Consider gamekit-build and game-code-worker."
fi

if echo "$PROMPT" | grep -Eqi 'plan|design|scope|should we|worth it|requirement|feature request|unclear|break down|方案|计划|范围|要不要|是否值得|需求|不明确|拆分'; then
  add_hint "This may need task classification. Consider gamekit-plan before implementation."
fi

if echo "$PROMPT" | grep -Eqi 'task card|docs/tasks|claim task|close task|next task|todo|in progress|blocked|done|任务卡|领取任务|关闭任务|下一个任务|未完成任务|进行中|阻塞|已完成'; then
  add_hint "This looks like task-card workflow. Read docs/templates/TASK_TEMPLATE.md and docs/tasks/*.md; do not claim a task unless the user explicitly asks."
fi

if echo "$PROMPT" | grep -Eqi 'architecture|refactor|system boundary|data model|save data|economy|networking|performance|extensible|scalable|abstraction|maintainability|架构|重构|系统边界|数据模型|存档|经济|网络|性能|扩展性|抽象|可维护'; then
  add_hint "This may affect architecture or long-term maintainability. Consider architecture-reviewer before implementation."
fi

if echo "$PROMPT" | grep -Eqi 'temporary asset|placeholder|blockout|greybox|whitebox|mock visual|prototype visual|primitive|artist handoff|artist replacement|replacement anchor|placeholder prefab|placeholder material|placeholder icon|placeholder vfx|placeholder ui|临时资源|占位|白盒|灰盒|临时模型|美术交接|美术替换|替换锚点|占位图标|占位特效|占位界面'; then
  add_hint "This includes temporary or replaceable asset work. Consider gamekit-assets and placeholder-asset-worker."
fi

if echo "$PROMPT" | grep -Eqi 'check|test|validate|verify|verification|review|qa|risk|safe|problem|bug|regression|serialization|missing reference|manual test|playtest|检查|测试|验证|评审|风险|安全|有没有问题|回归|引用丢失|手动测试'; then
  add_hint "This asks for verification or risk review. Consider gamekit-check and game-qa-checker."
fi

if echo "$PROMPT" | grep -Eqi 'handoff|summary|summarize|continue later|session state|memory|document decision|adr|what changed|next step|stale|交接|总结|下次继续|会话状态|记忆|记录决策|决策记录|改了什么|下一步|过期信息'; then
  add_hint "This looks like continuity or project memory work. Consider gamekit-handoff and project-memory-curator."
fi

if [ "${#HINTS[@]}" -gt 0 ]; then
  echo "## Auto Routing Hints"
  for hint in "${HINTS[@]}"; do
    echo "- $hint"
  done
fi
