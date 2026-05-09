Use the canonical workflow in `.claude/skills/gamekit-unity-prefab-edit/SKILL.md`.

Apply it to the user's current request. Edit Unity `.prefab` or `.unity` serialized content only when mutation is required, use `gamekit-unity-yaml-context` before reading full raw YAML, preserve serialized identity, auto-install `Assets/Editor/AgentTools/PrefabEditTool.cs` when the Unity backend is missing, and run or propose the smallest relevant Unity validation.

For v1 scene edits, execute only low-risk existing-object operations through the Unity Editor backend. Refuse high-risk scene structure, prefab instance override, lighting, navigation, render, baked-data, or broad batch edits and provide manual Unity Editor steps instead.
