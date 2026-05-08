---
name: gamekit-unity-prefab-edit
description: Use this skill when editing Unity serialized scene or prefab content, especially `.prefab` or `.unity` files, prefab variants, prefab instances in scenes, GameObject or Component bindings, serialized MonoBehaviour fields, Inspector references, fileID/GUID references, Missing Script or Missing Reference repairs, or migrations that require scene/prefab data changes. Trigger for requests to edit, modify, update, set, add, remove, rename, wire, rewire, assign, repair, fix, migrate, or consolidate Unity prefab or scene content. For read-only inspect, summarize, parse, or understand requests, use gamekit-unity-yaml-context instead.
---

# gamekit-unity-prefab-edit

Purpose: make small, auditable Unity prefab and scene edits without breaking serialized object identity.

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
7. Prefer Unity Editor operations, a narrow Editor script, or controlled prefab generation for broad hierarchy/component changes.
8. If direct YAML editing is necessary, change only the smallest known serialized field surface and preserve stable identity.
9. Edit C# serialized fields before serialized assets. For renamed serialized fields, use a migration strategy such as `FormerlySerializedAs` when existing data must survive.
10. Re-run the YAML summary and targeted raw searches after editing.
11. Run the smallest available Unity compile, EditMode test, PlayMode test, or manual Editor validation. If unavailable, state the exact blocker and the required manual Editor check.

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

- New serialized fields match C# field names exactly.
- Removed or renamed fields are not still serialized unless intentionally migrated.
- Internal references point to existing fileIDs in the same prefab or scene.
- External references resolve through `.meta` GUIDs.
- No Missing Script, `m_Script: {fileID: 0}`, unresolved fileID, or stale GUID reference was introduced.
- Prefab hierarchy, scene roots, component identity, fileIDs, and GUIDs are unchanged unless intentionally edited.
- Prefab instance overrides and variant links did not gain unrelated churn.
- Summary-tool omissions are checked against raw YAML before declaring a reference missing.

## Final Response

Report:

- Prefab, scene, or asset paths changed.
- Components and serialized fields changed.
- Identity surfaces intentionally preserved: fileIDs, GUIDs, hierarchy, component order, scene roots, and `.meta`.
- Validation commands run and any remaining Unity Editor checks.
