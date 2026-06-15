#!/usr/bin/env python3
"""Summarize Unity YAML files into compact Markdown.

This script is intentionally read-only. It never writes to Unity assets.
"""

from __future__ import annotations

import argparse
import collections
import dataclasses
import re
import sys
from pathlib import Path
from typing import Any


CLASS_NAMES = {
    "1": "GameObject",
    "4": "Transform",
    "20": "Camera",
    "21": "Material",
    "23": "MeshRenderer",
    "25": "Renderer",
    "28": "Texture2D",
    "33": "MeshFilter",
    "43": "Mesh",
    "48": "Shader",
    "50": "Rigidbody2D",
    "54": "Rigidbody",
    "58": "CircleCollider2D",
    "61": "BoxCollider2D",
    "64": "MeshCollider",
    "65": "BoxCollider",
    "70": "CapsuleCollider2D",
    "74": "AnimationClip",
    "81": "AudioListener",
    "82": "AudioSource",
    "95": "Animator",
    "100": "TextAsset",
    "108": "Light",
    "114": "MonoBehaviour",
    "115": "MonoScript",
    "128": "Font",
    "212": "SpriteRenderer",
    "213": "Sprite",
    "222": "CanvasRenderer",
    "223": "Canvas",
    "224": "RectTransform",
    "225": "CanvasGroup",
    "1001": "PrefabInstance",
    "1001480554": "Prefab",
    "11400000": "MonoBehaviourAsset",
}

SKIP_KEYS = {
    "serializedVersion",
    "m_ObjectHideFlags",
    "m_CorrespondingSourceObject",
    "m_PrefabInstance",
    "m_PrefabAsset",
    "m_GameObject",
    "m_Enabled",
    "m_EditorHideFlags",
    "m_Script",
    "m_Name",
    "m_EditorClassIdentifier",
    "m_Children",
    "m_Father",
    "m_RootOrder",
    "m_LocalEulerAnglesHint",
    "m_Component",
}

DEFAULT_ROOT_MARKERS = (
    Path("ProjectSettings") / "ProjectVersion.txt",
    Path("Packages") / "manifest.json",
    Path("Assets"),
)

SKIP_GUID_SCAN_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".vs",
    ".vscode",
    "build",
    "builds",
    "library",
    "logs",
    "obj",
    "temp",
    "usersettings",
}


@dataclasses.dataclass
class UnityEntry:
    class_id: str
    file_id: str
    class_name: str
    data: dict[str, Any]


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def find_project_root(start: Path) -> Path:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if any((candidate / marker).exists() for marker in DEFAULT_ROOT_MARKERS):
            return candidate
    return current


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def build_guid_map(project_root: Path) -> dict[str, str]:
    guid_map: dict[str, str] = {}
    pending = [project_root]
    while pending:
        current = pending.pop()
        try:
            children = list(current.iterdir())
        except OSError:
            continue
        for child in children:
            if child.is_dir():
                if child.name.lower() not in SKIP_GUID_SCAN_DIRS:
                    pending.append(child)
                continue
            if child.suffix != ".meta":
                continue
            meta_path = child
            try:
                text = read_text(meta_path)
            except OSError:
                continue
            match = re.search(r"(?m)^guid:\s*([0-9a-fA-F]+)\s*$", text)
            if not match:
                continue
            target = meta_path.with_suffix("")
            guid_map[match.group(1).lower()] = rel(target if target.exists() else meta_path, project_root)
    return guid_map


def split_unity_documents(text: str) -> list[tuple[str, str, str]]:
    docs: list[tuple[str, str, str]] = []
    current_header: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("---"):
            if current_header is not None:
                docs.append((current_header, "\n".join(current_lines), ""))
            current_header = line
            current_lines = []
        elif current_header is not None:
            current_lines.append(line)

    if current_header is not None:
        docs.append((current_header, "\n".join(current_lines), ""))

    return docs


def parse_header(header: str) -> tuple[str, str]:
    match = re.match(r"^---\s+!u!(?P<class_id>-?\d+)\s+&(?P<file_id>-?\d+)", header)
    if match:
        return match.group("class_id"), match.group("file_id")
    return "unknown", "unknown"


def import_yaml_module() -> Any:
    try:
        import yaml  # type: ignore

        return yaml
    except ImportError as exc:
        raise RuntimeError(
            "PyYAML is unavailable. Install unityparser for best results: "
            "python -m pip install unityparser"
        ) from exc


def load_with_yaml_fallback(path: Path, warning: str) -> tuple[list[UnityEntry], list[str]]:
    yaml = import_yaml_module()
    warnings = [warning]
    entries: list[UnityEntry] = []

    for header, body, _ in split_unity_documents(read_text(path)):
        class_id, file_id = parse_header(header)
        try:
            loaded = yaml.safe_load(body) if body.strip() else {}
        except Exception as exc:  # noqa: BLE001 - keep malformed docs visible.
            warnings.append(f"Could not parse document &{file_id}: {exc}")
            loaded = {}

        if isinstance(loaded, dict) and len(loaded) == 1:
            class_name, data = next(iter(loaded.items()))
            if not isinstance(data, dict):
                data = {"value": data}
        else:
            class_name = CLASS_NAMES.get(class_id, f"Class{class_id}")
            data = loaded if isinstance(loaded, dict) else {"value": loaded}

        entries.append(
            UnityEntry(
                class_id=class_id,
                file_id=str(file_id),
                class_name=str(class_name),
                data=data,
            )
        )

    return entries, warnings


def safe_vars(value: Any) -> dict[str, Any]:
    try:
        raw = vars(value)
    except TypeError:
        return {}
    return {key: item for key, item in raw.items() if not key.startswith("_") and key != "anchor"}


def to_plain(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [to_plain(item) for item in value]
    if isinstance(value, tuple):
        return [to_plain(item) for item in value]
    if isinstance(value, dict):
        return {str(key): to_plain(item) for key, item in value.items()}
    attrs = safe_vars(value)
    if attrs:
        return {str(key): to_plain(item) for key, item in attrs.items()}
    return str(value)


def load_with_unityparser(path: Path) -> tuple[list[UnityEntry], list[str], bool]:
    try:
        from unityparser import UnityDocument  # type: ignore
    except ImportError:
        entries, warnings = load_with_yaml_fallback(
            path,
            "unityparser is not installed; using read-only PyYAML fallback. "
            "Install with: python -m pip install unityparser",
        )
        return entries, warnings, False

    headers = [parse_header(header) for header, _, _ in split_unity_documents(read_text(path))]
    try:
        document = UnityDocument.load_yaml(str(path))
    except Exception as exc:  # noqa: BLE001 - fallback keeps the skill useful.
        entries, warnings = load_with_yaml_fallback(
            path,
            f"unityparser failed, using read-only PyYAML fallback: {exc}",
        )
        return entries, warnings, False

    raw_entries = getattr(document, "entries", None)
    if raw_entries is None:
        raw_entries = document if isinstance(document, list) else []

    entries: list[UnityEntry] = []
    for index, raw_entry in enumerate(raw_entries):
        anchor = getattr(raw_entry, "anchor", None)
        class_id, file_id = headers[index] if index < len(headers) else ("unknown", str(anchor or index))
        plain = to_plain(raw_entry)
        if isinstance(plain, dict) and len(plain) == 1:
            class_name, data = next(iter(plain.items()))
            if not isinstance(data, dict):
                data = {"value": data}
        else:
            class_name = getattr(raw_entry, "__class__", type(raw_entry)).__name__
            data = plain if isinstance(plain, dict) else {"value": plain}
        entries.append(UnityEntry(class_id, file_id, str(class_name), data))

    if not entries:
        entries, warnings = load_with_yaml_fallback(
            path,
            "unityparser produced no entries; using read-only PyYAML fallback.",
        )
        return entries, warnings, False

    return entries, [], True


def get_ref_id(value: Any) -> str | None:
    if isinstance(value, dict) and "fileID" in value:
        file_id = value.get("fileID")
        if file_id not in (None, "", 0, "0"):
            return str(file_id)
    return None


def get_guid(value: Any) -> str | None:
    if isinstance(value, dict):
        guid = value.get("guid")
        if isinstance(guid, str) and guid and not re.fullmatch(r"0+", guid):
            return guid.lower()
    return None


def is_ref_dict(value: Any) -> bool:
    return isinstance(value, dict) and ("fileID" in value or "guid" in value)


def short_scalar(value: Any, max_string: int) -> str:
    if isinstance(value, str):
        clean = value.replace("\n", "\\n")
        if len(clean) > max_string:
            return repr(clean[:max_string] + f"... <{len(clean) - max_string} chars omitted>")
        return repr(clean)
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    return str(value)


def compact_value(value: Any, max_string: int, max_array: int, depth: int = 0) -> str:
    if depth > 2:
        return "<nested>"
    if isinstance(value, (str, int, float, bool)) or value is None:
        return short_scalar(value, max_string)
    if is_ref_dict(value):
        file_id = value.get("fileID", 0)
        guid = value.get("guid")
        type_id = value.get("type")
        parts = [f"fileID={file_id}"]
        if guid:
            parts.append(f"guid={guid}")
        if type_id not in (None, 0, "0"):
            parts.append(f"type={type_id}")
        return "{" + ", ".join(parts) + "}"
    if isinstance(value, list):
        if not value:
            return "[]"
        items = value[:max_array]
        rendered = [compact_value(item, max_string, max_array, depth + 1) for item in items]
        if len(value) > max_array:
            rendered.append(f"... <{len(value) - max_array} items omitted>")
        return "[" + ", ".join(rendered) + "]"
    if isinstance(value, dict):
        if not value:
            return "{}"
        pairs = []
        for index, (key, item) in enumerate(value.items()):
            if index >= max_array:
                pairs.append(f"... <{len(value) - max_array} keys omitted>")
                break
            pairs.append(f"{key}: {compact_value(item, max_string, max_array, depth + 1)}")
        return "{" + ", ".join(pairs) + "}"
    return short_scalar(str(value), max_string)


def walk_values(value: Any, path: str = ""):
    yield path, value
    if isinstance(value, dict):
        for key, item in value.items():
            yield from walk_values(item, f"{path}.{key}" if path else str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk_values(item, f"{path}[{index}]")


def component_label(entry: UnityEntry, guid_map: dict[str, str]) -> str:
    data = entry.data
    if entry.class_name == "MonoBehaviour":
        script_ref = data.get("m_Script")
        guid = get_guid(script_ref)
        if guid:
            script = guid_map.get(guid, f"unresolved-guid:{guid}")
            return f"MonoBehaviour({script})"
        return "MonoBehaviour(Missing Script)"
    name = data.get("m_Name")
    if name:
        return f"{entry.class_name}({name})"
    return entry.class_name


def transform_summary(entry: UnityEntry | None, max_string: int, max_array: int) -> str:
    if entry is None:
        return ""
    data = entry.data
    parts: list[str] = []
    for key, label in (
        ("m_LocalPosition", "pos"),
        ("m_LocalRotation", "rot"),
        ("m_LocalScale", "scale"),
        ("m_AnchoredPosition", "anchored"),
        ("m_SizeDelta", "size"),
    ):
        if key in data:
            parts.append(f"{label}={compact_value(data[key], max_string, max_array)}")
    return ", ".join(parts)


def important_fields(data: dict[str, Any], max_string: int, max_array: int) -> list[str]:
    lines: list[str] = []
    omitted = 0
    for key, value in data.items():
        if key in SKIP_KEYS:
            continue
        if value in (None, "", [], {}):
            continue
        rendered = compact_value(value, max_string, max_array)
        if "omitted" in rendered or rendered == "<nested>":
            omitted += 1
        lines.append(f"{key}: {rendered}")
        if len(lines) >= 12:
            remaining = len([k for k in data.keys() if k not in SKIP_KEYS]) - len(lines)
            if remaining > 0:
                lines.append(f"... <{remaining} fields omitted>")
            break
    if omitted:
        lines.append(f"<{omitted} noisy fields compacted>")
    return lines


def build_indexes(entries: list[UnityEntry]) -> dict[str, Any]:
    by_id = {entry.file_id: entry for entry in entries}
    gameobjects = {entry.file_id: entry for entry in entries if entry.class_name == "GameObject"}
    transforms: dict[str, UnityEntry] = {}
    components_by_go: dict[str, list[UnityEntry]] = collections.defaultdict(list)
    transform_by_go: dict[str, UnityEntry] = {}
    children_by_transform: dict[str, list[str]] = collections.defaultdict(list)
    transform_to_go: dict[str, str] = {}

    for entry in entries:
        go_ref = get_ref_id(entry.data.get("m_GameObject"))
        if go_ref:
            components_by_go[go_ref].append(entry)
            if entry.class_name in {"Transform", "RectTransform"}:
                transforms[entry.file_id] = entry
                transform_by_go[go_ref] = entry
                transform_to_go[entry.file_id] = go_ref
                parent = get_ref_id(entry.data.get("m_Father"))
                if parent:
                    children_by_transform[parent].append(entry.file_id)

    for go_id, go_entry in gameobjects.items():
        for item in go_entry.data.get("m_Component", []) or []:
            comp_ref = get_ref_id(item.get("component") if isinstance(item, dict) else item)
            comp = by_id.get(comp_ref or "")
            if comp and comp not in components_by_go[go_id]:
                components_by_go[go_id].append(comp)

    return {
        "by_id": by_id,
        "gameobjects": gameobjects,
        "components_by_go": components_by_go,
        "transform_by_go": transform_by_go,
        "children_by_transform": children_by_transform,
        "transform_to_go": transform_to_go,
    }


def go_name(entry: UnityEntry) -> str:
    return str(entry.data.get("m_Name") or f"GameObject &{entry.file_id}")


def render_hierarchy(
    indexes: dict[str, Any],
    guid_map: dict[str, str],
    max_depth: int,
    max_string: int,
    max_array: int,
    max_objects: int,
) -> list[str]:
    gameobjects: dict[str, UnityEntry] = indexes["gameobjects"]
    transform_by_go: dict[str, UnityEntry] = indexes["transform_by_go"]
    children_by_transform: dict[str, list[str]] = indexes["children_by_transform"]
    transform_to_go: dict[str, str] = indexes["transform_to_go"]
    components_by_go: dict[str, list[UnityEntry]] = indexes["components_by_go"]

    child_go_ids = {
        transform_to_go[child_transform]
        for children in children_by_transform.values()
        for child_transform in children
        if child_transform in transform_to_go
    }
    root_go_ids = [go_id for go_id in gameobjects if go_id not in child_go_ids]
    root_go_ids.sort(key=lambda item: go_name(gameobjects[item]).lower())

    lines: list[str] = []
    visited = 0

    def visit(go_id: str, depth: int) -> None:
        nonlocal visited
        if visited >= max_objects:
            return
        visited += 1
        entry = gameobjects[go_id]
        data = entry.data
        active = data.get("m_IsActive")
        layer = data.get("m_Layer")
        tag = data.get("m_TagString")
        details = [f"&{go_id}"]
        if active is not None:
            details.append(f"active={active}")
        if layer is not None:
            details.append(f"layer={layer}")
        if tag:
            details.append(f"tag={tag}")
        indent = "  " * depth
        lines.append(f"{indent}- {go_name(entry)} [{', '.join(details)}]")

        transform = transform_by_go.get(go_id)
        t_summary = transform_summary(transform, max_string, max_array)
        if t_summary:
            lines.append(f"{indent}  transform: {t_summary}")

        components = [
            component
            for component in components_by_go.get(go_id, [])
            if component.class_name not in {"Transform", "RectTransform"}
        ]
        if components:
            labels = [component_label(component, guid_map) for component in components]
            lines.append(f"{indent}  components: {', '.join(labels)}")

        if depth >= max_depth:
            if transform:
                hidden = len(children_by_transform.get(transform.file_id, []))
                if hidden:
                    lines.append(f"{indent}  ... <{hidden} child transforms omitted by depth limit>")
            return

        if transform:
            for child_transform in children_by_transform.get(transform.file_id, []):
                child_go = transform_to_go.get(child_transform)
                if child_go in gameobjects:
                    visit(child_go, depth + 1)

    for root_go_id in root_go_ids:
        visit(root_go_id, 0)
        if visited >= max_objects:
            remaining = max(0, len(gameobjects) - visited)
            if remaining:
                lines.append(f"- ... <{remaining} GameObjects omitted by object limit>")
            break

    return lines or ["- No GameObject hierarchy found."]


def collect_references(
    entries: list[UnityEntry],
    by_id: dict[str, UnityEntry],
    guid_map: dict[str, str],
) -> tuple[list[str], list[str], list[str]]:
    external: set[str] = set()
    unresolved: set[str] = set()
    risks: set[str] = set()

    for entry in entries:
        for path, value in walk_values(entry.data):
            if not isinstance(value, dict):
                continue
            guid = get_guid(value)
            file_id = get_ref_id(value)
            if guid:
                target = guid_map.get(guid)
                external.add(f"&{entry.file_id} {entry.class_name}.{path} -> {target or 'unresolved-guid:' + guid}")
                if target is None:
                    risks.add(f"Unresolved external GUID {guid} at &{entry.file_id} {path}.")
            elif file_id and file_id not in by_id:
                unresolved.add(f"&{entry.file_id} {entry.class_name}.{path} -> missing local fileID {file_id}")
                if path.endswith("m_Script"):
                    risks.add(f"Missing Script at &{entry.file_id}.")
                else:
                    risks.add(f"Missing local reference {file_id} at &{entry.file_id} {path}.")

        if entry.class_name == "MonoBehaviour":
            script_ref = entry.data.get("m_Script")
            if isinstance(script_ref, dict):
                script_id = str(script_ref.get("fileID", "0"))
                script_guid = get_guid(script_ref)
                if script_id in {"0", "None", ""} and not script_guid:
                    risks.add(f"Missing Script at MonoBehaviour &{entry.file_id}.")
                elif script_guid and script_guid not in guid_map:
                    risks.add(f"MonoBehaviour &{entry.file_id} script GUID is unresolved: {script_guid}.")

    return sorted(external), sorted(unresolved), sorted(risks)


def render_asset_entries(
    entries: list[UnityEntry],
    guid_map: dict[str, str],
    max_string: int,
    max_array: int,
    max_objects: int,
) -> list[str]:
    lines: list[str] = []
    for entry in entries[:max_objects]:
        name = entry.data.get("m_Name")
        label = f"- {entry.class_name} &{entry.file_id}"
        if name:
            label += f" name={name!r}"
        if entry.class_name == "MonoBehaviour":
            label += f" script={component_label(entry, guid_map)}"
        lines.append(label)
        for field in important_fields(entry.data, max_string, max_array)[:8]:
            lines.append(f"  - {field}")
    if len(entries) > max_objects:
        lines.append(f"- ... <{len(entries) - max_objects} objects omitted by object limit>")
    return lines or ["- No serialized objects found."]


def summarize(
    path: Path,
    project_root: Path,
    max_string: int,
    max_array: int,
    max_depth: int,
    max_objects: int,
) -> str:
    entries, warnings, used_unityparser = load_with_unityparser(path)
    guid_map = build_guid_map(project_root)
    indexes = build_indexes(entries)
    by_id: dict[str, UnityEntry] = indexes["by_id"]
    class_counts = collections.Counter(entry.class_name for entry in entries)
    external, unresolved, risks = collect_references(entries, by_id, guid_map)
    extension = path.suffix.lower()

    lines = [
        f"# Unity YAML Summary: {rel(path, project_root)}",
        "",
        "## Overview",
        "",
        f"- File: `{rel(path, project_root)}`",
        f"- Project root: `{project_root.as_posix()}`",
        f"- File type: `{extension or 'unknown'}`",
        f"- Parser: `{'unityparser' if used_unityparser else 'PyYAML fallback'}`",
        f"- Serialized objects: {len(entries)}",
        f"- External GUIDs resolved: {len(guid_map)} known `.meta` GUIDs",
    ]

    if class_counts:
        rendered_counts = ", ".join(f"{name}={count}" for name, count in class_counts.most_common())
        lines.append(f"- Class counts: {rendered_counts}")

    if warnings:
        lines.extend(["", "## Parser Notes", ""])
        lines.extend(f"- {warning}" for warning in warnings)

    lines.extend(["", "## Hierarchy", ""])
    lines.extend(render_hierarchy(indexes, guid_map, max_depth, max_string, max_array, max_objects))

    lines.extend(["", "## Serialized Object Details", ""])
    detail_entries = entries
    if indexes["gameobjects"]:
        detail_entries = [
            entry
            for entry in entries
            if entry.class_name not in {"GameObject", "Transform", "RectTransform"}
        ]
    lines.extend(render_asset_entries(detail_entries, guid_map, max_string, max_array, max_objects))

    lines.extend(["", "## External GUID References", ""])
    if external:
        lines.extend(f"- {item}" for item in external[:max_objects])
        if len(external) > max_objects:
            lines.append(f"- ... <{len(external) - max_objects} references omitted>")
    else:
        lines.append("- No external GUID references found.")

    lines.extend(["", "## Unresolved References", ""])
    if unresolved:
        lines.extend(f"- {item}" for item in unresolved[:max_objects])
    else:
        lines.append("- No unresolved local fileID references found.")

    lines.extend(["", "## Risks", ""])
    if risks:
        lines.extend(f"- {item}" for item in sorted(risks)[:max_objects])
    else:
        lines.append("- No Missing Script or unresolved reference risk detected from YAML summary.")

    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize a Unity .prefab, .unity, or .asset YAML file into Markdown."
    )
    parser.add_argument("unity_yaml_file", type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--max-string", type=int, default=160)
    parser.add_argument("--max-array", type=int, default=12)
    parser.add_argument("--max-depth", type=int, default=8)
    parser.add_argument("--max-objects", type=int, default=120)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    path = args.unity_yaml_file.resolve()
    if not path.exists():
        eprint(f"Unity YAML file not found: {path}")
        return 2
    if path.suffix.lower() not in {".prefab", ".unity", ".asset"}:
        eprint(f"Warning: expected .prefab, .unity, or .asset; got {path.suffix or '<none>'}.")

    project_root = args.project_root.resolve() if args.project_root else find_project_root(path)
    try:
        output = summarize(
            path=path,
            project_root=project_root,
            max_string=args.max_string,
            max_array=args.max_array,
            max_depth=args.max_depth,
            max_objects=args.max_objects,
        )
    except RuntimeError as exc:
        eprint(str(exc))
        return 3

    sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
