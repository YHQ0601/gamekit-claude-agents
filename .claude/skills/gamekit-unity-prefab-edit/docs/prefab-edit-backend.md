# Unity Prefab/Scene Edit Backend

This backend lets an agent make narrow Unity prefab and scene edits through Unity Editor APIs instead of hand-editing serialized YAML.

## Files In This Scaffold

```text
.claude/skills/gamekit-unity-prefab-edit/templates/unity/Assets/Editor/AgentTools/PrefabEditTool.cs
.claude/skills/gamekit-unity-prefab-edit/scripts/install_unity_agent_tools.py
.claude/skills/gamekit-unity-prefab-edit/schemas/agent_prefab_ops.schema.json
```

## Files Installed Into A Unity Project

```text
Assets/Editor/AgentTools/PrefabEditTool.cs
.claude-local/unity-agent/agent_prefab_ops.json
.claude-local/unity-agent/agent_prefab_ops_result.json
```

`PrefabEditTool.cs` is a project tool file and should be committed. `.claude-local/` is local agent state and should be ignored by git.

The v1 installer does not create an `.asmdef`. This keeps installation simple and avoids changing a project's assembly layout. If a project requires asmdefs, add one manually as a project-specific follow-up.

## Install

From the target Unity project root:

```powershell
python .claude/skills/gamekit-unity-prefab-edit/scripts/install_unity_agent_tools.py --project-root .
```

From the GameKit scaffold repository:

```powershell
python .claude/skills/gamekit-unity-prefab-edit/scripts/install_unity_agent_tools.py --project-root "D:\MyUnityGame"
```

The installer checks for `ProjectSettings/ProjectVersion.txt` or `Packages/manifest.json`, copies the Editor tool, creates `.claude-local/unity-agent/`, and ensures `.claude-local/` is ignored.

## Execute

The agent writes `.claude-local/unity-agent/agent_prefab_ops.json`, then runs Unity in batch mode:

```powershell
Unity.exe -batchmode -quit `
  -projectPath "D:\MyUnityGame" `
  -executeMethod GameKit.AgentTools.PrefabEditTool.Run `
  -agentOpsPath "D:\MyUnityGame\.claude-local\unity-agent\agent_prefab_ops.json"
```

The tool writes `.claude-local/unity-agent/agent_prefab_ops_result.json` and exits non-zero on failure.

## Supported Operations

v1 supports only low-risk existing-object edits:

```text
SetActive
RenameGameObject
SetSerializedField
AssignReference
```

For scenes, `objectPath` must include the root GameObject name. For prefabs, `objectPath` may include or omit the prefab root name if the path remains unique.

The backend validates required operation fields at runtime before mutating assets. `active` must be a JSON boolean, and protocol fields such as `op`, `objectPath`, `componentType`, `propertyPath`, references, and `value` must be JSON strings when required.

`componentType` must resolve to exactly one component on the target GameObject. v1 refuses duplicate matching components instead of guessing. Use the component full name when short names are ambiguous; if multiple components of the same type exist on one object, handle that edit manually or extend the ops schema with a stronger identity field first.

Example ops file:

```json
{
  "schemaVersion": 1,
  "targetKind": "prefab",
  "targetPath": "Assets/Prefabs/Battle/CaptureZone.prefab",
  "resultPath": "D:/MyUnityGame/.claude-local/unity-agent/agent_prefab_ops_result.json",
  "operations": [
    {
      "operationId": "hide-radius-display",
      "op": "SetActive",
      "objectPath": "CaptureZone/RadiusDisplay",
      "active": false
    },
    {
      "operationId": "set-radius",
      "op": "SetSerializedField",
      "objectPath": "CaptureZone",
      "componentType": "CaptureZoneController",
      "propertyPath": "captureRadius",
      "valueType": "float",
      "value": "4.5"
    }
  ]
}
```

## Refused Scene Operations

Agents should refuse automatic execution and provide manual Unity Editor steps for:

```text
CreateGameObject
DeleteGameObject
Reparent
AddComponent
RemoveComponent
Modify scene roots
Modify lighting, navigation, render, or baked settings
Modify prefab instance overrides
Apply overrides back to a prefab asset
Batch edit many scenes
```

Prefer changing the prefab asset when the intended behavior belongs on the prefab rather than on a scene instance override.
