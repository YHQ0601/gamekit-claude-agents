#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"

extract_prompt_with_python() {
  python -c 'import json, sys; data = sys.stdin.buffer.read().decode("utf-8", "replace"); parsed = json.loads(data); value = parsed.get("prompt", "") if isinstance(parsed, dict) else data; sys.stdout.buffer.write(("" if value is None else str(value)).encode("utf-8"))' 2>/dev/null
}

extract_prompt_with_jq() {
  if command -v jq >/dev/null 2>&1; then
    jq -r '.prompt // ""' 2>/dev/null
  else
    return 1
  fi
}

if command -v python >/dev/null 2>&1; then
  PROMPT="$(printf '%s' "$INPUT" | extract_prompt_with_python || printf '%s' "$INPUT" | extract_prompt_with_jq || printf '%s' "$INPUT")"
elif command -v jq >/dev/null 2>&1; then
  PROMPT="$(printf '%s' "$INPUT" | extract_prompt_with_jq || printf '%s' "$INPUT")"
else
  PROMPT="$INPUT"
fi

HINTS=()
RESEARCH_EXPLICIT=false
EVIDENCE_REQUEST=false

add_hint() {
  HINTS+=("$1")
}

prompt_matches() {
  printf '%s' "$PROMPT" | grep -Eqi "$1"
}

if prompt_matches '(^|[[:space:]])/?gamekit-research([[:space:]]|$)'; then
  RESEARCH_EXPLICIT=true
fi

if prompt_matches 'official docs?|official guidance|official recommendation|best practices?|search|look up|web search|reference|reference material|literature|sources?|community recommendation|community practice|latest|current practice|readme|examples?|do not rely on memory|without relying on memory|evidence-backed|联网|搜索|搜一下|查资料|查一下|官方|官方建议|社区推荐|社区实践|最佳实践|参考资料|参考文档|文献|资料来源|来源|不要只靠认知|不要凭记忆|最新|文档|示例'; then
  EVIDENCE_REQUEST=true
fi

prompt_py_readonly_intent() {
  command -v python >/dev/null 2>&1 || return 1
  printf '%s' "$PROMPT" | python -c 'import sys
s = sys.stdin.buffer.read().decode("utf-8", "replace").lower()
terms = ["read-only", "readonly", "only report", "report only", "do not edit", "do not change", "do not modify", "no edit", "no changes", "只读", "只检查", "只报告", "不要改", "别改", "不要修改", "不修改", "仅检查", "仅报告"]
raise SystemExit(0 if any(t.lower() in s for t in terms) else 1)' 2>/dev/null
}

prompt_py_direct_fix_intent() {
  command -v python >/dev/null 2>&1 || return 1
  printf '%s' "$PROMPT" | python -c 'import re, sys
s = sys.stdin.buffer.read().decode("utf-8", "replace").lower()
fix_terms = ["fix", "repair", "resolve", "correct", "change", "update", "修复", "解决", "改正", "修改", "改一下", "处理"]
clue_terms = ["compile error", "compiler error", "build error", "syntax", "using", "namespace", "typo", "semicolon", "comma", "parameter", "param", "constant", "enum", "condition", "predicate", "mapping", "label", "text", "编译报错", "编译错误", "构建错误", "语法", "命名空间", "少了", "标点", "分号", "逗号", "参数", "数值", "常量", "枚举", "条件", "判断", "映射", "文案", "错误"]
direct_value = re.search(r"(改成|应该是)\s*\S+", s) is not None
raise SystemExit(0 if direct_value or (any(t.lower() in s for t in fix_terms) and any(t.lower() in s for t in clue_terms)) else 1)' 2>/dev/null
}

prompt_py_check_intent() {
  command -v python >/dev/null 2>&1 || return 1
  printf '%s' "$PROMPT" | python -c 'import sys
s = sys.stdin.buffer.read().decode("utf-8", "replace").lower()
terms = ["check", "test", "validate", "verify", "verification", "qa", "risk", "safe", "problem", "bug", "regression", "missing reference", "manual test", "playtest", "debug", "crash", "log", "检查", "测试", "验证", "风险", "安全", "有没有问题", "有问题吗", "哪里有问题", "排查", "问题排查", "偶现", "报错", "回归", "引用丢失", "手动测试", "调试", "崩溃", "日志"]
raise SystemExit(0 if any(t.lower() in s for t in terms) else 1)' 2>/dev/null
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
REVIEW_FIX_REQUEST=false
REVIEW_REQUEST=false
PLACEHOLDER_ASSET_REQUEST=false
INTEGRATION_REQUEST=false
EXPLICIT_BUILD_PLACEHOLDER=false
CHECK_COMMAND_REQUEST=false
CHECK_READONLY_REQUEST=false
DIRECT_FIX_REQUEST=false
CHECK_INTENT_REQUEST=false

if prompt_matches '(fix|address|resolve|implement|apply|handle|follow up).*(review|comment|finding|feedback|issue|suggestion)|((review|comment|finding|feedback).*(fix|address|resolve|implement|apply|handle|follow up))|(修复|处理|解决|应用).*(review|审查|评审|意见|反馈|问题|finding)|(根据|按照).*(review|审查|评审|意见|反馈|问题|finding).*(修改|修复|处理|解决|应用)'; then
  REVIEW_FIX_REQUEST=true
fi

if [ "$REVIEW_FIX_REQUEST" != "true" ] && prompt_matches 'gamekit-review|code review([[:space:]]+(current|this|the|diff|changes|patch|pr|pull request|staged|unstaged))?|review[[:space:]]+(current|this|the)[[:space:]]+(diff|changes|patch|pr|pull request|staged|unstaged)|review[[:space:]]+(staged|unstaged)[[:space:]]+changes|review[[:space:]]+this[[:space:]]+pr|pr review|pull request review|pre-commit review|staged review|审查(当前|这次|本次|diff|PR|pr|改动|修改)|代码审查|评审(当前|这次|本次|diff|PR|pr|改动|修改)'; then
  REVIEW_REQUEST=true
fi

if prompt_matches 'temporary asset|placeholder|blockout|greybox|whitebox|mock visual|prototype visual|primitive|artist handoff|artist replacement|replacement anchor|placeholder prefab|placeholder material|placeholder icon|placeholder vfx|placeholder ui|VFX|vfx|特效|投射物|占位|白盒|灰盒|临时资源|临时模型|美术交接|美术替换|替换锚点|占位图标|占位特效|占位界面'; then
  PLACEHOLDER_ASSET_REQUEST=true
fi

if prompt_matches 'UnitDef|ScriptableObject|config|configuration|configure|wire|wiring|assign|bind|attach|set|配置|绑定|挂载|接入|设置|分配'; then
  INTEGRATION_REQUEST=true
fi

if prompt_matches 'gamekit-build' && [ "$PLACEHOLDER_ASSET_REQUEST" = "true" ]; then
  EXPLICIT_BUILD_PLACEHOLDER=true
fi

if prompt_matches '(^|[^[:alnum:]_-])/?gamekit-check([^[:alnum:]_-]|$)'; then
  CHECK_COMMAND_REQUEST=true
fi

if prompt_matches 'read[- ]?only|readonly|only report|report only|do not edit|do not change|do not modify|don.t edit|don.t change|no edits?|no changes?|只读|只检查|只报告|不要改|别改|不要修改|不修改|仅检查|仅报告' || prompt_py_readonly_intent; then
  CHECK_READONLY_REQUEST=true
fi

if prompt_matches '((fix|repair|resolve|correct|change|update|修复|解决|改正|修改|改一下|处理).*(compile error|compiler error|build error|syntax|using|namespace|typo|semicolon|comma|parameter|param|constant|enum|condition|predicate|mapping|label|text|编译报错|编译错误|构建错误|语法|命名空间|少了|标点|分号|逗号|参数|数值|常量|枚举|条件|判断|映射|文案|错误))|((compile error|compiler error|build error|syntax|using|namespace|typo|semicolon|comma|parameter|param|constant|enum|condition|predicate|mapping|label|text|编译报错|编译错误|构建错误|语法|命名空间|少了|标点|分号|逗号|参数|数值|常量|枚举|条件|判断|映射|文案|错误).*(fix|repair|resolve|correct|change|update|修复|解决|改正|修改|改一下|处理))|改成[[:space:]]*[^[:space:]]+|应该是[[:space:]]*[^[:space:]]+' || prompt_py_direct_fix_intent; then
  DIRECT_FIX_REQUEST=true
fi

if [ "$CHECK_COMMAND_REQUEST" = "true" ] && prompt_matches 'compile error|compiler error|build error|syntax|using|namespace|typo|semicolon|comma|parameter|param|constant|enum|condition|predicate|mapping|label|text'; then
  DIRECT_FIX_REQUEST=true
fi

if prompt_matches 'check|test|validate|verify|verification|qa|risk|safe|problem|bug|regression|serialization|missing reference|manual test|playtest|debug|crash|log|检查|测试|验证|风险|安全|有没有问题|有问题吗|哪里有问题|检查.*问题|验证.*问题|测试.*问题|排查.*问题|问题排查|回归|引用丢失|手动测试|调试|排查|崩溃|日志' || prompt_py_check_intent; then
  CHECK_INTENT_REQUEST=true
fi

case "$(printf '%s' "$ENGINE" | tr '[:upper:]' '[:lower:]')" in
  unity*) add_hint "Detected Unity profile. Load .claude/rules/profiles/unity.md before engine-specific work." ;;
  godot*) add_hint "Detected Godot profile. Load .claude/rules/profiles/godot.md before engine-specific work." ;;
  unreal*) add_hint "Detected Unreal profile. Load .claude/rules/profiles/unreal.md before engine-specific work." ;;
  web*|javascript*|js*) add_hint "Detected Web/JS profile. Load .claude/rules/profiles/web-js.md before engine-specific work." ;;
esac

if [ "$RESEARCH_EXPLICIT" != "true" ] && [ "$EVIDENCE_REQUEST" != "true" ] && prompt_matches 'unity|c#|csharp|monobehaviour|scriptableobject|prefab|\.prefab|\.unity|projectsettings|unity editor|\.meta|预制体|Unity[[:space:]]*场景|组件|脚本'; then
  add_hint "This looks like Unity-specific work. Use .claude/rules/profiles/unity.md and consider game-code-worker or game-qa-checker."
fi

if { prompt_matches '(unity yaml|unity serialized|serialized yaml|serialized (asset|scene|prefab|file)|prefab yaml|scene yaml|asset yaml|prefab file|scene file|asset file|\.prefab|\.unity|\.asset|Unity序列化|Unity 序列化|场景文件|预制体文件|资产文件)' && prompt_matches '(^|[^[:alnum:]_])(read|load|open|view|inspect|summarize|parse|analy[sz]e|understand)([^[:alnum:]_]|$)|读取|加载|打开|查看|看|检查|总结|摘要|解析|分析|理解'; } || { prompt_matches '(^|[^[:alnum:]_])(prefab|scene|asset)([^[:alnum:]_]|$)|预制体|场景|资产' && prompt_matches '(^|[^[:alnum:]_])parse([^[:alnum:]_]|$)|解析'; }; then
  add_hint "Use gamekit-unity-yaml-context before reading full Unity YAML files."
fi

if { prompt_matches 'unity[[:space:]]*(scene|prefab|serialized|yaml)|\.prefab|\.unity|(^|[^[:alnum:]_])prefab([^[:alnum:]_]|$)|预制体|Unity[[:space:]]*场景' && prompt_matches '(^|[^[:alnum:]_])(edit|modify|change|update|set|add|remove|delete|rename|wire|rewire|assign|repair|fix|migrate|consolidate)([^[:alnum:]_]|$)|编辑|修改|更新|设置|添加|删除|移除|重命名|绑定|重新绑定|分配|修复|迁移|合并|配置'; }; then
  add_hint "Use gamekit-unity-prefab-edit for Unity prefab or scene mutation. Use gamekit-unity-yaml-context before reading full Unity YAML; auto-install the Unity Editor backend if mutation needs it and Assets/Editor/AgentTools/PrefabEditTool.cs is missing."
fi

if prompt_matches 'godot|gdscript|node|scene tree|\.tscn|\.tres|signal|autoload|project.godot'; then
  add_hint "This looks like Godot-specific work. Use .claude/rules/profiles/godot.md and consider game-code-worker or game-qa-checker."
fi

if prompt_matches 'unreal|ue5|ue4|blueprint|uasset|umap|uproject|uclass|uproperty|uobject|(unreal|ue[45]).*(module|plugin)|(module|plugin).*(unreal|ue[45])'; then
  add_hint "This looks like Unreal-specific work. Use .claude/rules/profiles/unreal.md and consider game-code-worker or game-qa-checker."
fi

if prompt_matches 'phaser|three\.?js|pixi|babylon|vite|canvas|webgl|webgpu|browser game|npm|package.json|网页游戏'; then
  add_hint "This looks like Web/JS game work. Use .claude/rules/profiles/web-js.md and consider game-code-worker or game-qa-checker."
fi

if prompt_matches 'gamekit-task|task-card-manager|task card|docs/tasks|claim task|close task|split task|refine task|audit task|next task|create task|write task|arrange task|plan task|work order|todo|in progress|blocked|done|任务卡|领取任务|关闭任务|拆分任务|细化任务|审计任务|下一任务|布置任务|创建任务|写任务|制定任务|生成任务|安排任务|规划任务|任务拆分|任务设计|执行工单|工单|待办任务|任务待办|进行中任务|任务进行中|阻塞任务|任务阻塞|标记.*完成|完成.*任务卡|任务卡.*完成|完成.*工单|工单.*完成|已完成任务'; then
  add_hint "This looks like task-card workflow. Consider gamekit-task and task-card-manager; read docs/templates/TASK_TEMPLATE.md and relevant docs/tasks/** task cards, and do not claim a task unless the user explicitly asks."
fi

if [ "$REVIEW_REQUEST" != "true" ] && [ "$PLACEHOLDER_ASSET_REQUEST" != "true" ] && [ "$CHECK_INTENT_REQUEST" != "true" ] && prompt_matches 'implement[[:space:]]+(this|the|a|an)?[[:space:]]*(feature|change|system|mechanic|ui)|code|script|component|gameplay|combat|inventory|quest|level|spawn|controller|manager|compile|build|error|exception|input|ui logic|ability|item|character|代码|脚本|玩法|战斗|背包|关卡|生成|控制器|管理器|编译|构建|报错|输入|技能|道具|角色|完成.*功能|完成.*系统|完成.*菜单|完成.*界面|完成.*UI|完成.*脚本|完成.*代码|完成.*玩法|完成.*关卡|完成.*模块|完成.*组件|任务系统|任务奖励|任务玩法|任务逻辑|任务功能|任务界面|任务UI|任务数据|任务链|任务目标|任务进度|任务追踪|任务完成|任务提交|任务领取|任务触发|任务条件|任务面板|任务脚本|任务管理器|实现.*任务|修复.*任务|添加.*任务|开发.*任务|制作.*任务|任务.*系统|任务.*奖励'; then
  add_hint "This looks like focused implementation work. Consider gamekit-build and game-code-worker."
fi

if prompt_matches 'plan|design|scope|should we|worth it|requirement|feature request|unclear|break down|better approach|better way|alternative|reuse|cleanup|clean up|old code|legacy code|existing code|risk source|risk point|方案|计划|规划|范围|要不要|是否值得|需求|不明确|拆分|更好做法|更好方案|更合理|复用|旧代码|老代码|已有代码|清理|风险点|风险来源'; then
  add_hint "This may need task classification or planning notes. Consider gamekit-plan before implementation, especially for reuse, cleanup, alternatives, and concrete risk sources."
fi

if prompt_matches 'architecture|refactor|system boundary|data model|save data|economy|networking|performance|extensible|scalable|abstraction|maintainability|架构|重构|系统边界|数据模型|存档|经济|网络|性能|扩展性|抽象|可维护'; then
  add_hint "This may affect architecture or long-term maintainability. Consider architecture-reviewer before implementation."
fi

if [ "$EXPLICIT_BUILD_PLACEHOLDER" = "true" ]; then
  add_hint "Do not use gamekit-build as the primary workflow for placeholder asset creation. Use gamekit-assets or placeholder-asset-worker first; gamekit-build can handle integration after the asset handoff."
elif [ "$PLACEHOLDER_ASSET_REQUEST" = "true" ] && [ "$INTEGRATION_REQUEST" = "true" ]; then
  add_hint "This is mixed placeholder asset plus integration work. Use gamekit-assets or placeholder-asset-worker for placeholder creation first, then gamekit-build for code/data/UnitDef/prefab/scene integration, then gamekit-check for validation."
elif [ "$PLACEHOLDER_ASSET_REQUEST" = "true" ]; then
  add_hint "This includes temporary or replaceable asset work. Consider gamekit-assets and placeholder-asset-worker."
elif [ "$REVIEW_REQUEST" != "true" ] && [ "$INTEGRATION_REQUEST" = "true" ] && prompt_matches 'UnitDef|ScriptableObject|config|configuration|configure|wire|wiring|assign|bind|attach|set|配置|绑定|挂载|接入|设置|分配'; then
  add_hint "This looks like asset/data integration work. Consider gamekit-build for wiring/configuration and gamekit-check for validation."
fi

if [ "$REVIEW_REQUEST" = "true" ]; then
  add_hint "This is an explicit manual review request. Use gamekit-review and delegate the review body to code-reviewer when subagents are available; do not edit files during review."
fi

if [ "$REVIEW_FIX_REQUEST" = "true" ]; then
  add_hint "This asks to address review feedback. Return to the main development workflow with gamekit-build or game-code-worker; do not use code-reviewer unless the user asks for a new review."
fi

if [ "$CHECK_COMMAND_REQUEST" = "true" ] && [ "$CHECK_READONLY_REQUEST" = "true" ]; then
  add_hint "This is an explicit read-only /gamekit-check request. Use gamekit-check for validation or triage only; do not use Safe Auto-Fix Escalation."
elif [ "$CHECK_COMMAND_REQUEST" = "true" ] && [ "$DIRECT_FIX_REQUEST" = "true" ] && [ "$REVIEW_FIX_REQUEST" != "true" ]; then
  add_hint "Explicit /gamekit-check may use Safe Auto-Fix Escalation if the safety contract holds: gamekit-check -> gamekit-build Direct Fix Mode -> gamekit-check validation."
elif [ "$DIRECT_FIX_REQUEST" = "true" ] && [ "$REVIEW_FIX_REQUEST" != "true" ]; then
  add_hint "This looks like a Direct Fix Candidate. Use gamekit-build for one narrow fix, then gamekit-check for validation."
elif [ "$CHECK_INTENT_REQUEST" = "true" ] && [ "$EVIDENCE_REQUEST" != "true" ]; then
  add_hint "This asks for verification or risk review. Consider gamekit-check and game-qa-checker."
fi

if prompt_matches 'handoff|summary|summarize|continue later|session state|project memory|memory update|update memory|remember this|document decision|adr|what changed|next step|stale|交接|总结|下次继续|会话状态|记忆|记录决策|决策记录|改了什么|下一步|过期信息'; then
  add_hint "This looks like continuity or project memory work. Consider gamekit-handoff and project-memory-curator."
fi

ASK_EXPLICIT=false
ASK_RESEARCH_INTENT="$EVIDENCE_REQUEST"
ASK_ENGINEERING_TARGET=false
ASK_CONSULTATION_INTENT=false

if prompt_matches 'gamekit-ask|engineering consultation'; then
  ASK_EXPLICIT=true
fi

if prompt_matches 'implementation|implementation approach|implementation strategy|architecture|performance|compatibility|coupling|api|plugin|sdk|package|repository|repo|framework|engine|production method|stability|testability|third-party|实现|实现方式|接入|架构|性能|兼容|耦合|API|接口|插件|SDK|包|仓库|框架|引擎|制作方式|稳定|可测试|第三方'; then
  ASK_ENGINEERING_TARGET=true
fi

if prompt_matches 'better implementation|safer implementation|tradeoff|trade-off|compare|comparison|how should|how would|how to|what approach|方案|怎么做|如何做|怎么接|如何接|更稳|更合理|取舍|对比|比较|讨论|咨询'; then
  ASK_CONSULTATION_INTENT=true
fi

if [ "$RESEARCH_EXPLICIT" = "true" ]; then
  add_hint "This explicitly asks for gamekit-research. Use the isolated read-only web-researcher subagent and return sourced evidence."
elif [ "$ASK_EXPLICIT" = "true" ]; then
  add_hint "This explicitly asks for gamekit-ask. Apply its Evidence Gate; invoke gamekit-research and wait for the result when external evidence is required."
elif [ "$REVIEW_REQUEST" != "true" ] && [ "$ASK_RESEARCH_INTENT" = "true" ] && { [ "$ASK_ENGINEERING_TARGET" = "true" ] || [ "$ASK_CONSULTATION_INTENT" = "true" ]; }; then
  add_hint "This asks for evidence-backed engineering consultation. Use gamekit-research for external evidence, then gamekit-ask for the recommendation."
elif [ "$REVIEW_REQUEST" != "true" ] && [ "$ASK_RESEARCH_INTENT" = "true" ]; then
  add_hint "This asks for external evidence. Use gamekit-research."
elif [ "$REVIEW_REQUEST" != "true" ] && [ "$ASK_CONSULTATION_INTENT" = "true" ] && [ "$ASK_ENGINEERING_TARGET" = "true" ]; then
  add_hint "This looks like pre-implementation engineering consultation. Consider gamekit-ask; use gamekit-plan when scope, workstreams, or start decision are still unclear."
fi

if [ "${#HINTS[@]}" -gt 0 ]; then
  echo "## Auto Routing Hints"
  for hint in "${HINTS[@]}"; do
    echo "- $hint"
  done
fi
