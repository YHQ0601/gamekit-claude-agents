#!/usr/bin/env python3
"""Install the GameKit Unity Editor backend into a Unity project."""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path


TOOL_RELATIVE_PATH = Path("Assets/Editor/AgentTools/PrefabEditTool.cs")
LOCAL_AGENT_DIR = Path(".claude-local/unity-agent")
GITIGNORE_LINE = ".claude-local/"


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def template_path() -> Path:
    return skill_root() / "templates" / "unity" / TOOL_RELATIVE_PATH


def is_unity_project(project_root: Path) -> bool:
    return (
        (project_root / "ProjectSettings" / "ProjectVersion.txt").is_file()
        or (project_root / "Packages" / "manifest.json").is_file()
    )


def ensure_gitignore(project_root: Path, dry_run: bool) -> str:
    gitignore = project_root / ".gitignore"
    if gitignore.exists():
        text = gitignore.read_text(encoding="utf-8")
        lines = [line.strip() for line in text.splitlines()]
        if GITIGNORE_LINE in lines:
            return "unchanged"

        suffix = "" if text.endswith("\n") or not text else "\n"
        addition = f"{suffix}\n# GameKit local agent state\n{GITIGNORE_LINE}\n"
        if not dry_run:
            gitignore.write_text(text + addition, encoding="utf-8")
        return "updated"

    if not dry_run:
        gitignore.write_text(f"# GameKit local agent state\n{GITIGNORE_LINE}\n", encoding="utf-8")
    return "created"


def install(project_root: Path, force: bool, dry_run: bool) -> int:
    project_root = project_root.resolve()
    source = template_path()
    destination = project_root / TOOL_RELATIVE_PATH
    local_dir = project_root / LOCAL_AGENT_DIR

    if not source.is_file():
        print(f"Template not found: {source}", file=sys.stderr)
        return 2

    if not is_unity_project(project_root):
        print(
            "Project root does not look like a Unity project. Expected "
            "ProjectSettings/ProjectVersion.txt or Packages/manifest.json.",
            file=sys.stderr,
        )
        return 2

    status = "installed"
    if destination.exists():
        if filecmp.cmp(source, destination, shallow=False):
            status = "unchanged"
        elif not force:
            print(
                f"Existing tool differs and will not be overwritten without --force: {destination}",
                file=sys.stderr,
            )
            return 3
        else:
            status = "overwritten"

    if not dry_run and status != "unchanged":
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    if not dry_run:
        local_dir.mkdir(parents=True, exist_ok=True)

    gitignore_status = ensure_gitignore(project_root, dry_run)

    print(f"project_root={project_root}")
    print(f"tool={destination}")
    print(f"tool_status={status}")
    print(f"local_agent_dir={local_dir}")
    print(f"gitignore_status={gitignore_status}")
    print("note=PrefabEditTool.cs is a project tool file and should be committed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        default=".",
        help="Unity project root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing PrefabEditTool.cs that differs from the template.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned changes without writing files.",
    )
    args = parser.parse_args()

    return install(Path(args.project_root), args.force, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
