---
name: gamekit-unity-prefab-edit
description: Use this skill when editing Unity serialized scene or prefab content, especially `.prefab` or `.unity` files, prefab variants, prefab instances in scenes, GameObject or Component bindings, serialized MonoBehaviour fields, Inspector references, fileID/GUID references, Missing Script or Missing Reference repairs, or migrations that require scene/prefab data changes. Trigger for requests to edit, modify, update, set, add, remove, rename, wire, rewire, assign, repair, fix, migrate, or consolidate Unity prefab or scene content. For read-only inspect, summarize, parse, or understand requests, use gamekit-unity-yaml-context instead.
---

# gamekit-unity-prefab-edit

Purpose: make small, auditable Unity prefab and scene edits without breaking serialized object identity.

This skill is a workflow plus an optional Unity Editor backend. The backend is installed into target Unity projects only when mutation is needed.

## Workflow

1. Load `.claude/rules/core/*.md` and `.claude/rules/profiles/unity.md`.
2. Confirm the request is a mutation. For read-only YAML inspection, use `gamekit-unity-yaml-context` and stop before editing.
3. Identify the exact target files and serialized surface: prefab asset, prefab variant, scene object, scene prefab instance override, ScriptableObject reference, or C# serialized field migration.
4. Read current code and local patterns before editing serialized data. The repository code is the source of truth.
5. Use `gamekit-unity-yaml-context` before reading full `.prefab`, `.unity`, or `.asset` YAML.
6. Build an identity map before editing:
   - GameObject name and fileID.
   - Transform fileID and parent/child relationships.
   - Component type, component fileID, MonoBehaviour fileID, script GUID, and script path.
   - Referenced GameObject, Transform, Component, and external asset GUID paths.
   - Prefab instance, variant, or override records when a `.unity` scene is involved.
7. If the target Unity project needs prefab or scene mutation and lacks `Assets/Editor/AgentTools/PrefabEditTool.cs`, automatically install the backend with:

   ```bash
   python .claude/skills/gamekit-unity-prefab-edit/scripts/install_unity_agent_tools.py --project-root <unity-project-root>
   ```

   The installed `PrefabEditTool.cs` is a project tool file and should be committed. `.claude-local/` is local agent state and should be ignored.
8. Prefer the Unity Editor backend for supported prefab edits and low-risk scene edits. Write operations to `.claude-local/unity-agent/agent_prefab_ops.json` and call:

   ```bash
   Unity.exe -batchmode -quit -projectPath <unity-project-root> -executeMethod GameKit.AgentTools.PrefabEditTool.Run -agentOpsPath <unity-project-root>/.claude-local/unity-agent/agent_prefab_ops.json
   ```

   Windows is the supported v1 execution environment. If `Unity.exe` cannot be found or the same project is already open in Unity Editor, stop and report the blocker.
9. Refuse high-risk scene operations in v1. Give manual Unity Editor steps instead of creating task cards automatically.
10. If direct YAML editing is necessary, change only the smallest known serialized field surface and preserve stable identity.
11. Edit C# serialized fields before serialized assets. For renamed serialized fields, use a migration strategy such as `FormerlySerializedAs` when existing data must survive.
12. Re-run the YAML summary and targeted raw searches after editing.
13. Run the smallest available Unity compile, EditMode test, PlayMode test, or manual Editor validation. If unavailable, state the exact blocker and the required manual Editor check.

## Unity Editor Backend

Backend files live with this skill:

```text
templates/unity/Assets/Editor/AgentTools/PrefabEditTool.cs
scripts/install_unity_agent_tools.py
schemas/agent_prefab_ops.schema.json
docs/prefab-edit-backend.md
```

Installed target-project files:

```text
Assets/Editor/AgentTools/PrefabEditTool.cs
.claude-local/unity-agent/agent_prefab_ops.json
.claude-local/unity-agent/agent_prefab_ops_result.json
```

Supported backend operations:

- `SetActive`
- `RenameGameObject`
- `SetSerializedField`
- `AssignReference`

For component operations, `componentType` must identify exactly one component on the target GameObject. If multiple components match, stop instead of guessing.

The backend must validate required operation fields before mutating assets. Do not rely on Unity `JsonUtility` defaults for missing or mistyped fields.

Do not add an `.asmdef` in v1. If a target project requires asmdefs, stop and ask for a project-specific upgrade.

## Direct YAML Edit Policy

Safe when the target object is known:

- Replace, add, or remove scalar fields inside one existing MonoBehaviour.
- Assign an internal reference to an existing fileID in the same prefab or scene.
- Assign an external reference through a resolved `.meta` GUID and expected fileID/type.

Needs explicit caution or approval:

- Editing `m_Component`, `m_Children`, `m_Father`, scene roots, prefab instance overrides, stripped references, or prefab variant links.
- Adding, deleting, duplicating, or reordering GameObjects or Components.
- Changing script GUIDs, `.meta` files, import settings, Addressables, ProjectSettings, or generated/baked data.
- Touching many prefabs, scenes, ScriptableObjects, or serialized references at once.

Never rebuild an object just to make a field edit. Do not regenerate GUIDs. Do not rewrite unrelated YAML sections.

## Scene-Specific Rules

- Treat `.unity` scenes as higher risk than prefab assets because they may include prefab instance overrides, scene roots, lighting, navigation, baked data, and render settings.
- When modifying a prefab instance inside a scene, keep the distinction between editing the prefab asset and editing the instance override explicit.
- Do not apply broad override churn to a scene when the intended change belongs on the prefab asset.
- Prefer Editor validation for scene edits, including opening the scene and checking Missing Script, Missing Reference, and unintended dirty objects.
- Automatically execute only low-risk scene edits on existing objects and fields: `SetActive`, `RenameGameObject`, `SetSerializedField`, and `AssignReference`.
- Refuse automatic execution for high-risk scene work: creating, deleting, or reparenting GameObjects; adding or removing Components; modifying scene roots; touching lighting, navigation, render, or baked settings; modifying prefab instance overrides; applying overrides back to prefab assets; or batch-editing many scenes.
- For refused scene work, explain why it is high risk and provide direct manual Unity Editor steps plus validation checks.

## Field Migration Pattern

When consolidating duplicated Inspector configuration:

1. Pick one owner component for shared references.
2. Move shared serialized fields to that owner.
3. Change consumer components to serialize only a reference to the owner.
4. Expose read-only properties from the owner.
5. Add lightweight validation for required references.
6. Update prefab or scene data so the owner has shared references and consumers point to the owner.

Do not move behavior into the config owner just to reduce component count. Prefer centralized configuration with distributed behavior.

## Verification Checklist

- `Assets/Editor/AgentTools/PrefabEditTool.cs` was installed only when mutation required it and was not overwritten if it differed from the template.
- New serialized fields match C# field names exactly.
- Removed or renamed fields are not still serialized unless intentionally migrated.
- Internal references point to existing fileIDs in the same prefab or scene.
- External references resolve through `.meta` GUIDs.
- Component operations identify exactly one target component; duplicate matching components are refused.
- No Missing Script, `m_Script: {fileID: 0}`, unresolved fileID, or stale GUID reference was introduced.
- Prefab hierarchy, scene roots, component identity, fileIDs, and GUIDs are unchanged unless intentionally edited.
- Prefab instance overrides and variant links did not gain unrelated churn.
- Summary-tool omissions are checked against raw YAML before declaring a reference missing.

## Final Response

Report:

- Prefab, scene, or asset paths changed.
- Whether `Assets/Editor/AgentTools/PrefabEditTool.cs` was installed or already present.
- Components and serialized fields changed.
- Identity surfaces intentionally preserved: fileIDs, GUIDs, hierarchy, component order, scene roots, and `.meta`.
- Validation commands run and any remaining Unity Editor checks.
