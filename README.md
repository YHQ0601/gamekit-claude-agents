# gamekit-claude-agents

Claude-first AI workflow scaffold for game development across engines.

面向多引擎游戏开发的 Claude 优先 AI 工作流模板。

## Overview / 概览

This repository is not a game framework and does not prescribe gameplay systems. It provides a lightweight workflow layer so Claude Code, Codex, and opencode can collaborate in the same game project while following one shared process.

这个仓库不是游戏框架，也不预设任何玩法系统。它提供的是一层轻量 AI 工作流，让 Claude Code、Codex 和 opencode 可以在同一个游戏项目中协作，并遵循同一套项目规则。

The key principle is:

核心原则是：

```text
Claude canonical workflow + thin engine profiles + thin tool adapters
Claude 主工作流 + 轻量引擎 profile + 轻量工具适配层
```

Claude Code is the canonical workflow. Codex and opencode are compatibility layers that follow Claude's process; they are not separate sources of truth.

Claude Code 是主流程和事实源。Codex 与 opencode 只是兼容适配层，用来跟随 Claude 的流程；它们不是第二套独立规则源。

## Where to Look / 看哪里

| Need / 需求 | File or Folder / 文件或目录 |
|---|---|
| Claude canonical workflow / Claude 主流程 | `CLAUDE.md` |
| Manual review rules / 手动审查规则 | `REVIEW.md` |
| Shared tool agreement / 多工具共享约定 | `AGENTS.md` |
| Rules / 规则 | `.claude/rules/` |
| Skills / 自动工作流 | `.claude/skills/` |
| Slash commands / 斜杠命令 | `.claude/commands/` |
| Codex adapter / Codex 适配层 | `.codex/`, `.agents/skills/` |
| opencode adapter / opencode 适配层 | `.opencode/`, `opencode.json` |
| Project docs / 项目文档 | `docs/knowledge/`, `docs/systems/`, `docs/decisions/`, `docs/templates/` |

## Design / 设计

The repository uses a layered model:

这个仓库使用分层模型：

- `core workflow`: engine-agnostic agents, skills, slash commands, rules, hooks, and docs.
- `core workflow`：与引擎无关的 agents、skills、斜杠命令、rules、hooks 和文档。
- `engine profiles`: thin rules for Unity, Godot, Unreal, and Web/JS game projects.
- `engine profiles`：Unity、Godot、Unreal、Web/JS 的轻量规则覆盖层。
- `tool adapters`: Codex and opencode mappings that follow the canonical Claude workflow.
- `tool adapters`：Codex 和 opencode 的映射层，跟随 Claude 主工作流。

Claude Code remains the source of truth:

Claude Code 保持为唯一主流程：

- `CLAUDE.md`
- `.claude/agents/`
- `.claude/skills/`
- `.claude/commands/`
- `.claude/rules/`
- `.claude/hooks/`
- `.claude/settings.json`

Codex and opencode support is intentionally thin. They should read `AGENTS.md` and use their adapter files, but they must not treat adapter instructions as a replacement for the canonical `.claude/` workflow.

Codex 和 opencode 的支持刻意保持轻量。它们应该读取 `AGENTS.md` 并使用自己的适配文件，但不能把这些适配文件当成 `.claude/` 主工作流的替代品。

Adapter files intentionally repeat small role summaries so each tool can discover and load the workflow independently.

适配层文件会有意重复少量角色说明，这样不同工具可以独立发现并加载同一套工作流。

## What It Includes / 包含内容

- `CLAUDE.md`: Claude Code working agreement for the main orchestrator.
- `CLAUDE.md`：Claude Code 主 orchestrator 的工作约定。
- `AGENTS.md`: shared working agreement for Codex, opencode, and other compatible tools.
- `AGENTS.md`：Codex、opencode 和其他兼容工具的共享工作约定。
- `REVIEW.md`: manual review-only rules for `gamekit-review`, PR review, and diff review.
- `REVIEW.md`：`gamekit-review`、PR review 和 diff review 的手动只读审查规则。
- `.claude/agents/`: Claude project subagents for architecture review, code review, task-card management, focused game code work, placeholder assets, QA, and project memory.
- `.claude/agents/`：Claude 项目级 subagents，包括架构评审、代码审查、任务卡管理、游戏代码实现、占位资源、QA 和项目记忆。
- `.claude/skills/`: canonical reusable workflows for planning, engineering consultation, task-card management, implementation, placeholder assets, validation, manual review, and handoff.
- `.claude/skills/gamekit-unity-prefab-edit/`: Unity prefab/scene mutation workflow plus an optional Editor backend template and installer for target Unity projects.
- `.claude/skills/`：主流程 skills，包括任务 intake、任务卡管理、功能实现、占位资源、验证、手动审查和交接。
- `.claude/commands/`: thin slash-command entry points for manually invoking the `gamekit-*` workflows.
- `.claude/commands/`：轻量斜杠命令入口，用于手动触发 `gamekit-*` 工作流。
- `.claude/rules/core/`: always-relevant game workflow rules.
- `.claude/rules/core/`：始终生效的通用游戏开发规则。
- `.claude/rules/profiles/`: thin engine profiles for Unity, Godot, Unreal, and Web/JS.
- `.claude/rules/profiles/`：Unity、Godot、Unreal、Web/JS 的轻量引擎 profile。
- `.claude/hooks/`: session bootstrap and prompt-routing hints.
- `.claude/hooks/`：会话启动和用户 prompt 路由提示。
- `.codex/`: Codex project agents, config, and hook adapters.
- `.codex/`：Codex 项目 agents、配置和 hook 适配。
- `.agents/skills/`: Codex wrapper skills that point back to canonical `.claude/skills/`.
- `.agents/skills/`：Codex wrapper skills，指回主流程 `.claude/skills/`。
- `.opencode/` and `opencode.json`: opencode project agents and rule loading.
- `.opencode/` 与 `opencode.json`：opencode 项目 agents 和规则加载配置。
- `docs/knowledge/`: project brief and short knowledge index.
- `docs/ai/`: deprecated compatibility pointer to `docs/knowledge/`.
- `docs/systems/`: System Cards for code-verified system entry points and safe modification notes.
- `docs/decisions/`: ADRs for important long-term decisions.
- `docs/knowledge/`：项目简报和架构索引。
- `docs/templates/`: task, knowledge index, system card, ADR, session state, and placeholder asset templates.
- `docs/templates/`：任务卡、系统卡、ADR 和占位资源模板。

## Intended Use / 使用场景

Copy this scaffold into the root of a game repository when you want agent tools to:

当你希望 AI 工具在游戏项目中做到以下事情时，可以把这个模板复制到项目根目录：

- understand the user's goal before editing;
- 编辑前先理解用户目标；
- prefer small, useful changes over broad refactors;
- 优先做小而有用的修改，而不是大范围重构；
- route specialized work to focused roles;
- 把不同类型任务路由给专门角色；
- avoid unsafe engine-specific file edits;
- 避免危险的引擎专用文件修改；
- keep project knowledge tied to verified code;
- 让项目知识以已验证代码为准；
- support Claude Code first, while still allowing Codex and opencode to contribute.
- 以 Claude Code 为主，同时允许 Codex 和 opencode 共同协作。

## Current Workflow / 当前流程

Startup flow:

启动流程：

1. Run `.claude/hooks/bootstrap-session.sh`.
2. Read `CLAUDE.md`.
3. Load `.claude/rules/core/*.md`.
4. Detect the active engine profile from project files or `docs/knowledge/PROJECT_BRIEF.md`.
5. Load one matching profile from `.claude/rules/profiles/` only when relevant.
6. Use `.claude/hooks/route-user-prompt.sh` to provide routing hints for each user request.

1. 运行 `.claude/hooks/bootstrap-session.sh`。
2. 读取 `CLAUDE.md`。
3. 加载 `.claude/rules/core/*.md`。
4. 根据项目文件或 `docs/knowledge/PROJECT_BRIEF.md` 检测当前引擎 profile。
5. 只有在相关时，加载 `.claude/rules/profiles/` 中对应的一个 profile。
6. 每次用户输入后，通过 `.claude/hooks/route-user-prompt.sh` 给出路由提示。

Task flow:

任务流程：

1. Classify ambiguous or multi-part requests with `gamekit-plan`; include a compact engineering preflight and subagent decision.
2. Use `gamekit-ask` for read-only engineering consultation before implementation; use its Research Mode when the user asks for official guidance, references, best practices, latest/current practice, or evidence-backed advice.
3. Use `architecture-reviewer` before architecture-sensitive work.
4. Use `gamekit-build` and `game-code-worker` for focused implementation.
5. Use `gamekit-assets` and `placeholder-asset-worker` for temporary art/blockout work.
6. Use `gamekit-check` and `game-qa-checker` after behavior-affecting changes or for debug triage.
7. Use `gamekit-review` and `code-reviewer` only when the user explicitly asks for review.
8. Use `gamekit-handoff` and `project-memory-curator` when continuity or memory updates are useful.

Use `gamekit-task` and `task-card-manager` manually when the user wants to create, split, refine, claim, block, close, or audit parent/child task cards under `docs/tasks/` for later execution.

当用户想创建、拆分、细化、领取、阻塞、关闭或审计 `docs/tasks/` 下的父子任务卡以供后续执行时，手动使用 `gamekit-task` 和 `task-card-manager`。

1. 需求不明确或包含多个部分时，使用 `gamekit-plan` 分类。
2. 涉及架构风险时，先使用 `architecture-reviewer`。
3. 聚焦实现时，使用 `gamekit-build` 和 `game-code-worker`。
4. 需要临时美术、白盒或占位资源时，使用 `gamekit-assets` 和 `placeholder-asset-worker`。
5. 影响行为的修改完成后，使用 `gamekit-check` 和 `game-qa-checker`。
6. 只有当用户明确要求 review 时，使用 `gamekit-review` 和 `code-reviewer`。
7. 需要跨会话延续或记忆更新时，使用 `gamekit-handoff` 和 `project-memory-curator`。

Manual slash commands:

手动斜杠命令：

- `/gamekit-plan`: classify goal and scope, run a compact engineering preflight, choose the smallest useful slice, and decide workstreams/subagents.
- `/gamekit-ask`: compare implementation approaches and engineering tradeoffs before editing files; Research Mode checks evidence when official guidance, references, best practices, latest/current practice, or evidence-backed advice is requested.
- `/gamekit-task`: create, split, refine, claim, block, close, or audit task cards under `docs/tasks/` without implementing them.
- `/gamekit-plan`：分类范围、必要性、引擎 profile 和工作流。
- `/gamekit-task`：创建、拆分、细化、领取、阻塞、关闭或审计 `docs/tasks/` 下的任务卡，但不实现任务。
- `/gamekit-build`: implement the smallest useful game change.
- `/gamekit-build`：实现最小有用游戏改动。
- `/gamekit-check`: summarize changed area, risk matrix, recommended validation, and result after behavior-affecting changes or debug triage.
- `/gamekit-check`：验证构建、运行时、资源引用、存档和性能风险，也可用于 debug triage。
- `/gamekit-assets`: plan or create temporary assets and replacement anchors.
- `/gamekit-assets`：规划或创建临时资源和替换锚点。
- `/gamekit-review`: manually review a diff, staged changes, PR patch, or named files; return findings, risk level, fix plan, validation recommendation, and overall correctness without editing.
- `/gamekit-review`：手动只读审查 diff、staged changes、PR patch 或指定文件；返回 findings、风险等级、修复方案和验证建议。
- `/gamekit-handoff`: summarize continuity, decisions, next step, and stale facts.
- `/gamekit-handoff`：总结连续性信息、决策、下一步和需要复查的事实。

Unity prefab/scene backend:

- `gamekit-unity-prefab-edit` auto-installs `Assets/Editor/AgentTools/PrefabEditTool.cs` into a target Unity project when prefab or scene mutation requires the backend and the file is missing.
- The installed Editor tool is a project file and should be committed; `.claude-local/unity-agent/` stores local ops/result files and should stay ignored.
- v1 supports Windows Unity batchmode execution, prefab edits, and low-risk existing-object scene edits. High-risk scene structure, prefab instance override, lighting, navigation, render, baked-data, or broad batch edits are refused with manual Editor steps.

`gamekit-review` is manual-only. It should not be triggered automatically after every implementation, and the reviewer must return findings, risk level, recommended fix plan, and validation recommendation to the main development conversation instead of applying fixes.

`gamekit-review` 只手动触发。它不应该在每次实现后自动运行，reviewer 必须把 findings、风险等级、修复方案和验证建议带回主开发会话，而不是直接修复。

Placeholder asset placement:

占位资源放置策略：

- Default for demos and small projects: place placeholders next to the target/final asset location.
- Demo 和小项目默认：占位资源放在最终目标资源目录旁边。
- Placeholder assets must use `_PH`; placeholder materials should use `MAT_PH_`; replacement briefs should use `[AssetName]_ArtistBrief.md`.
- 占位资源必须使用 `_PH`；占位材质建议使用 `MAT_PH_`；替换说明使用 `[AssetName]_ArtistBrief.md`。
- Keep stable anchors such as `GameplayRoot`, `VisualRoot`, `Model_ReplaceHere`, `VFX_Anchor`, `SFX_Anchor`, `UI_Anchor`, and `HitboxPreview`.
- 保留稳定锚点，例如 `GameplayRoot`、`VisualRoot`、`Model_ReplaceHere`、`VFX_Anchor`、`SFX_Anchor`、`UI_Anchor` 和 `HitboxPreview`。
- Move to a dedicated placeholder/prototype folder when the project grows, asset cleanup becomes hard, or an asset pipeline such as Addressables, AssetBundles, Pak files, remote assets, DLC, or mods appears.
- 当项目变大、资源清理变困难，或出现 Addressables、AssetBundles、Pak、远程资源、DLC、Mod 等资源管线时，再迁移到独立 placeholder/prototype 目录。

Project structure:

项目结构：

- Agents use `.claude/rules/core/project-structure.md` when they need to decide where new files should go.
- 当 agent 需要判断新文件应该放在哪里时，会使用 `.claude/rules/core/project-structure.md`。
- Existing project structure always wins; the recommended structures are fallbacks for new, empty, or inconsistent demo projects.
- 已有项目结构始终优先；推荐结构只作为新项目、空项目或结构混乱 demo 的 fallback。
- When the real project name is unknown, GameKit uses `Game` as the default project content root.
- 当真实项目名未知时，GameKit 使用 `Game` 作为默认项目内容根目录。
- Engine defaults are `Assets/Game/` for Unity, `Content/Game/` for Unreal, `res://game/` for Godot, and `src/game/` for Web/JS.
- 引擎默认值是 Unity 的 `Assets/Game/`、Unreal 的 `Content/Game/`、Godot 的 `res://game/`、Web/JS 的 `src/game/`。

## Engine Profiles / 引擎 Profiles

Core rules are always relevant. Engine profiles are used only when the project declares or reveals an engine:

核心规则始终生效。引擎 profile 只在项目声明或显露某个引擎时使用：

- Claude opens or works on files matched by a profile's `paths` frontmatter; or
- Claude 打开或处理匹配 profile `paths` frontmatter 的文件；或者
- `docs/knowledge/PROJECT_BRIEF.md` has `Engine: Unity`, `Godot`, `Unreal`, or `Web/JS`; or
- `docs/knowledge/PROJECT_BRIEF.md` 中写明 `Engine: Unity`、`Godot`、`Unreal` 或 `Web/JS`；或者
- the repository contains clear engine markers such as `ProjectSettings/`, `project.godot`, `*.uproject`, or `package.json`; or
- 仓库中存在清晰的引擎标记，例如 `ProjectSettings/`、`project.godot`、`*.uproject` 或 `package.json`；或者
- the user asks for engine-specific work.
- 用户明确提出某个引擎相关任务。

Available profiles:

可用 profiles：

- Unity: `.claude/rules/profiles/unity.md`
- Godot: `.claude/rules/profiles/godot.md`
- Unreal: `.claude/rules/profiles/unreal.md`
- Web/JS: `.claude/rules/profiles/web-js.md`

Profiles are thin by design. They contain safety constraints and validation reminders, not a full duplicate workflow.

Profile 是轻量覆盖层，只包含安全约束和验证提醒，不复制一整套 workflow。

The `paths` metadata helps Claude load engine rules when relevant files are touched. Hooks and adapters still use project markers and `PROJECT_BRIEF.md` so tools that do not support path-scoped rules can follow the same intent.

`paths` 元数据帮助 Claude 在相关文件被触及时加载对应引擎规则。Hooks 和 adapters 仍会使用项目标记与 `PROJECT_BRIEF.md`，让不支持 path-scoped rules 的工具也能遵循同一意图。

## Tool Entry Points / 不同工具入口

### Claude Code

Claude Code uses the canonical workflow directly:

Claude Code 直接使用主流程：

- read `CLAUDE.md` first;
- 先读取 `CLAUDE.md`；
- use `.claude/agents/`, `.claude/skills/`, `.claude/commands/`, `.claude/rules/`, and `.claude/hooks/`;
- 使用 `.claude/agents/`、`.claude/skills/`、`.claude/commands/`、`.claude/rules/` 和 `.claude/hooks/`；
- keep `.claude/settings.json` as the Claude hook configuration.
- 使用 `.claude/settings.json` 作为 Claude hook 配置。

### Codex

Codex follows the Claude workflow through adapters:

Codex 通过适配层跟随 Claude 工作流：

- read `AGENTS.md` for the shared project agreement;
- 读取 `AGENTS.md` 作为共享项目约定；
- use `.codex/agents/*.toml` for mapped roles;
- 使用 `.codex/agents/*.toml` 作为角色映射；
- use `.agents/skills/codex-*/SKILL.md` wrapper skills;
- 使用 `.agents/skills/codex-*/SKILL.md` wrapper skills；
- reuse `.claude/hooks/` through `.codex/hooks.json` when project hooks are trusted.
- 在项目信任 hook 后，通过 `.codex/hooks.json` 复用 `.claude/hooks/`。

### opencode

opencode follows the shared agreement and project agents:

opencode 通过共享约定和项目 agents 跟随主流程：

- read `AGENTS.md` for the shared project agreement;
- 读取 `AGENTS.md` 作为共享项目约定；
- use `.opencode/agents/*.md` for mapped roles;
- 使用 `.opencode/agents/*.md` 作为角色映射；
- use canonical `.claude/skills/*/SKILL.md` through Claude-compatible skill discovery when available;
- 在支持 Claude-compatible skill discovery 时，直接使用 `.claude/skills/*/SKILL.md`；
- `opencode.json` loads `CLAUDE.md`, shared core rules, and denies `codex-*` wrapper skills to avoid duplicates.
- `opencode.json` 加载 `CLAUDE.md` 和共享核心规则，并禁用 `codex-*` wrapper skills，避免重复展示。

## Task Cards / 任务卡

`docs/tasks/` is the lightweight shared parent/child task queue. Milestones live at `docs/tasks/vNN-short-milestone-name/README.md`, and executable child tasks live beside them as `vNN-tMM-verb-object.md`. New sessions may list open task cards when their status is `Todo`, `In Progress`, or `Blocked`, but agents should not claim or start a task automatically.

`docs/tasks/` 是轻量共享父子任务队列。大版本父任务位于 `docs/tasks/vNN-short-milestone-name/README.md`，可执行子任务与它同目录，命名为 `vNN-tMM-verb-object.md`。新会话可以列出状态为 `Todo`、`In Progress` 或 `Blocked` 的任务卡，但 agent 不应该自动领取或开始任务。

Use `docs/templates/TASK_TEMPLATE.md` to choose the parent README or child task template when creating tasks.

创建任务时使用 `docs/templates/TASK_TEMPLATE.md` 选择父任务 README 模板或子任务模板。

Use `gamekit-task` and `task-card-manager` for deliberate task-card authoring and queue maintenance. Task-card work prepares executable work orders for later agents or cheaper models; it is not implementation.

需要专门编写或维护任务卡时，手动使用 `gamekit-task` 和 `task-card-manager`。任务卡工作是给后续 agent 或更经济模型准备可执行工单，不是直接实现。

Parent README files define milestone goals, child order, phase gates, shared boundaries, and final validation. Executor-ready child task cards include a single-node goal, checkbox subtasks mapped to acceptance criteria, implementation notes, executor permissions, halt conditions, validation method, and execution records.

父任务 README 定义大版本目标、子任务顺序、阶段门、共享边界和最终验收。可执行子任务卡应包含单节点目标、映射到验收标准的复选框子任务、实现备注、执行者权限、停止条件、验证方式和执行记录。

Typical task status flow:

典型任务状态流：

- `Todo`: ready to claim.
- `Todo`：可以领取。
- `In Progress`: explicitly claimed by the user or current agent.
- `In Progress`：已由用户或当前 agent 明确领取。
- `Blocked`: waiting for missing information or approval.
- `Blocked`：等待缺失信息或批准。
- `Done`: acceptance criteria and validation plan are satisfied.
- `Done`：验收标准和验证计划已满足。

`.claude-local/SESSION_STATE.md` is local continuity memory, not the source of truth for task status.

`.claude-local/SESSION_STATE.md` 是本地连续性记忆，不是任务状态的事实源。

## Project Knowledge Policy / 项目知识规则

The repository code is the source of truth. Unity prefabs/scenes, configuration, and assets are also authoritative for their own serialized state. Documentation is navigation and memory, not proof that a gameplay system exists.

仓库代码是事实源。文档用于导航和记忆，不等于某个玩法系统已经真实存在。

`docs/knowledge/` is the canonical project knowledge entry and should stay short: project brief, system card index, ADR index, stale reminders, and last verified status. `docs/ai/` is deprecated compatibility space and should not receive active facts.

Unknown project facts should stay as `TBD`. Existing System Cards may be refreshed only when the user explicitly asks for knowledge maintenance or runs a knowledge gate, and the changes are code-verified and scoped to stable entry points. New System Cards require user confirmation or an explicit knowledge gate.

ADRs in `docs/decisions/` require user confirmation before writing. Review/check workflows only recommend knowledge updates. Handoff updates `.claude-local/SESSION_STATE.md` first and only proposes shared documentation updates.

Push, pre-push, and publish requests should run a lightweight knowledge gate, but this scaffold does not install a hard Git pre-push hook by default.

未知项目事实应保持为 `TBD`。只有当系统已在代码中存在，或用户明确批准设计草案时，才创建 System Card。

## Compatibility Boundaries / 兼容边界

Claude workflow changes should be made in `.claude/` first. Adapter files for Codex and opencode should be updated only to reflect that canonical workflow.

工作流变更应先发生在 `.claude/` 中。Codex 和 opencode 的适配文件只用于反映这个主流程。

Do not duplicate full workflows per engine or per tool. Add shared behavior to core rules, add engine-specific safety to profiles, and add tool-specific wiring only to adapters.

不要为每个引擎或每个工具复制完整 workflow。共享行为放到 core rules，引擎专用安全约束放到 profiles，工具专用连接放到 adapters。

## References / 参考

- Claude Code memory: https://code.claude.com/docs/en/memory
- Claude Code subagents: https://code.claude.com/docs/en/subagents
- Claude Code skills: https://code.claude.com/docs/en/slash-commands
- Claude Code hooks: https://code.claude.com/docs/en/hooks
- Claude Code review: https://code.claude.com/docs/en/code-review
- Codex AGENTS.md: https://developers.openai.com/codex/guides/agents-md
- Codex code reviews: https://developers.openai.com/codex/use-cases/github-code-reviews
- opencode rules: https://opencode.ai/docs/rules
- opencode agents: https://opencode.ai/docs/agents
- opencode skills: https://opencode.ai/docs/skills
