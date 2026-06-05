#!/usr/bin/env python3
"""Approve project-local read-only Bash permission requests.

Exit 0 means "auto-approve". Exit 1 means "fall through to Claude Code".
The policy is intentionally conservative: unknown syntax or commands are not
denied, they are simply not auto-approved.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path


PROJECT_MARKERS = (
    ".claude",
    "AGENTS.md",
    ".git",
    "ProjectSettings/ProjectVersion.txt",
    "Packages/manifest.json",
    "package.json",
)

READ_COMMANDS = {
    "rg",
    "grep",
    "cat",
    "head",
    "tail",
    "sed",
    "awk",
    "nl",
    "wc",
    "sort",
    "uniq",
    "find",
    "ls",
    "pwd",
    "echo",
    "findstr",
    "type",
    "dir",
    "get-content",
    "get-childitem",
    "select-string",
    "read",
    "xxd",
    "tree",
    "du",
    "stat",
    "printf",
    "test",
    "[",
}

GIT_READ_SUBCOMMANDS = {
    "status",
    "diff",
    "log",
    "show",
    "ls-files",
    "grep",
    "check-ignore",
    "cat-file",
    "merge-tree",
}

FIND_EXEC_READ_COMMANDS = {"grep", "cat", "head", "tail", "wc", "sed", "awk", "printf"}

DANGEROUS_COMMANDS = {
    "rm",
    "rmdir",
    "del",
    "remove-item",
    "mv",
    "move",
    "cp",
    "copy",
    "touch",
    "mkdir",
    "new-item",
    "set-content",
    "add-content",
    "out-file",
    "chmod",
    "chown",
    "npm",
    "curl",
    "unity.exe",
}

SCRIPT_COMMANDS = {"python", "python3", "node", "bash", "sh", "pwsh", "powershell"}
WRAPPERS = {"time", "timeout", "nice", "nohup", "stdbuf", "command"}


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 1

    command = extract_command(payload)
    if not command:
        return 1

    cwd = extract_cwd(payload)
    project_root = find_project_root(cwd)
    if project_root is None:
        return 1

    policy = Policy(project_root=project_root, start_cwd=cwd)
    return 0 if policy.is_safe(command) else 1


def extract_command(payload: object) -> str:
    if not isinstance(payload, dict):
        return ""
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict) and isinstance(tool_input.get("command"), str):
        return tool_input["command"]
    command = payload.get("command")
    return command if isinstance(command, str) else ""


def extract_cwd(payload: object) -> Path:
    if isinstance(payload, dict):
        tool_input = payload.get("tool_input")
        candidates = []
        if isinstance(tool_input, dict):
            candidates.extend([tool_input.get("cwd"), tool_input.get("workdir")])
        candidates.extend([payload.get("cwd"), payload.get("workdir")])
        for candidate in candidates:
            if isinstance(candidate, str) and candidate.strip():
                return normalize_raw_path(candidate, Path.cwd()) or Path.cwd()
    return Path.cwd()


def find_project_root(cwd: Path) -> Path | None:
    cwd = cwd.resolve()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=3,
        )
        if result.returncode == 0 and result.stdout.strip():
            root = normalize_raw_path(result.stdout.strip(), cwd)
            if root is not None:
                return root.resolve()
    except Exception:
        pass

    for current in (cwd, *cwd.parents):
        for marker in PROJECT_MARKERS:
            if (current / marker).exists():
                return current.resolve()
    return None


class Policy:
    def __init__(self, project_root: Path, start_cwd: Path) -> None:
        self.project_root = project_root.resolve()
        self.cwd = start_cwd.resolve()
        if not self.is_under_project(self.cwd):
            self.cwd = self.project_root

    def is_safe(self, command: str) -> bool:
        if has_unsupported_shell_syntax(command):
            return False
        if has_unsafe_redirection(command):
            return False

        try:
            segments = split_compound(command)
        except ValueError:
            return False
        if not segments:
            return False

        for segment in segments:
            if not self.is_safe_segment(segment):
                return False
        return True

    def is_safe_segment(self, segment: str) -> bool:
        try:
            tokens = tokenize(segment)
        except ValueError:
            return False
        tokens = strip_leading_env_assignments(tokens)
        tokens = strip_wrappers(tokens)
        if not tokens:
            return False

        command = tokens[0].lower()

        if command == "cd":
            return self.apply_cd(tokens)
        if command == "git":
            return self.is_safe_git(tokens)
        if command == "find":
            return self.is_safe_find(tokens)
        if command in SCRIPT_COMMANDS:
            return self.is_safe_trusted_skill_script(tokens)
        if command in DANGEROUS_COMMANDS:
            return False
        if command in READ_COMMANDS:
            return self.paths_are_project_local(tokens)
        return False

    def apply_cd(self, tokens: list[str]) -> bool:
        if len(tokens) != 2:
            return False
        target = tokens[1]
        if target in {"-", "~"}:
            return False
        resolved = normalize_raw_path(target, self.cwd)
        if resolved is None or not self.is_under_project(resolved):
            return False
        self.cwd = resolved.resolve()
        return True

    def is_safe_git(self, tokens: list[str]) -> bool:
        if len(tokens) < 2:
            return False
        return tokens[1] in GIT_READ_SUBCOMMANDS

    def is_safe_find(self, tokens: list[str]) -> bool:
        if "-delete" in tokens or "-execdir" in tokens:
            return False

        roots = []
        i = 1
        while i < len(tokens):
            token = tokens[i]
            if token == "--":
                i += 1
                continue
            if token.startswith("-") or token in {"(", ")", "!", "not"}:
                break
            roots.append(token)
            i += 1

        if not roots:
            roots = ["."]
        for root in roots:
            if not self.path_token_is_project_local(root):
                return False

        i = 1
        while i < len(tokens):
            token = tokens[i]
            if token in {"-exec", "-ok"}:
                exec_tokens = []
                i += 1
                while i < len(tokens) and tokens[i] not in {";", "+"}:
                    exec_tokens.append(tokens[i])
                    i += 1
                if not self.is_safe_find_exec(exec_tokens):
                    return False
            i += 1
        return self.paths_are_project_local(tokens, find_mode=True)

    def is_safe_find_exec(self, tokens: list[str]) -> bool:
        if not tokens:
            return False
        command = tokens[0].lower()
        if command not in FIND_EXEC_READ_COMMANDS:
            return False
        if any(token.lower() in DANGEROUS_COMMANDS or token.lower() in SCRIPT_COMMANDS for token in tokens):
            return False
        return self.paths_are_project_local(tokens, find_exec_mode=True)

    def is_safe_trusted_skill_script(self, tokens: list[str]) -> bool:
        if len(tokens) < 2:
            return False
        script = normalize_raw_path(tokens[1], self.cwd)
        if script is None or not self.is_under_project(script):
            return False
        try:
            rel = script.resolve().relative_to(self.project_root)
        except ValueError:
            return False
        return len(rel.parts) >= 3 and rel.parts[0] == ".claude" and rel.parts[1] == "skills"

    def paths_are_project_local(
        self,
        tokens: list[str],
        *,
        find_mode: bool = False,
        find_exec_mode: bool = False,
    ) -> bool:
        for index, token in enumerate(tokens):
            if should_skip_token(tokens, index, find_mode=find_mode, find_exec_mode=find_exec_mode):
                continue
            if token == "/dev/null":
                continue
            if looks_like_absolute_path(token):
                path = normalize_raw_path(path_prefix_before_glob(token), self.cwd)
                if path is None or not self.is_under_project(path):
                    return False
                continue
            if looks_like_path_token(token) and not self.path_token_is_project_local(token):
                return False
        return True

    def path_token_is_project_local(self, token: str) -> bool:
        path = normalize_raw_path(path_prefix_before_glob(token), self.cwd)
        return path is not None and self.is_under_project(path)

    def is_under_project(self, path: Path) -> bool:
        try:
            common = os.path.commonpath([os.path.normcase(str(self.project_root)), os.path.normcase(str(path.resolve()))])
        except ValueError:
            return False
        return common == os.path.normcase(str(self.project_root))


def split_compound(command: str) -> list[str]:
    segments: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escaped = False
    i = 0

    while i < len(command):
        char = command[i]
        if escaped:
            current.append("\\" + char)
            escaped = False
            i += 1
            continue
        if char == "\\":
            escaped = True
            i += 1
            continue
        if quote:
            current.append(char)
            if char == quote:
                quote = None
            i += 1
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            i += 1
            continue
        if command.startswith("&&", i) or command.startswith("||", i):
            add_segment(segments, current)
            current = []
            i += 2
            continue
        if char in {";", "|"}:
            add_segment(segments, current)
            current = []
            i += 1
            continue
        current.append(char)
        i += 1

    if escaped or quote:
        raise ValueError("unterminated escape or quote")
    add_segment(segments, current)
    return segments


def add_segment(segments: list[str], current: list[str]) -> None:
    segment = "".join(current).strip()
    if segment:
        segments.append(segment)


def tokenize(segment: str) -> list[str]:
    lexer = shlex.shlex(segment, posix=False)
    lexer.whitespace_split = True
    lexer.commenters = ""
    tokens = [strip_shell_quotes(token) for token in lexer]
    return [";" if token == r"\;" else token for token in tokens]


def strip_shell_quotes(token: str) -> str:
    if len(token) >= 2 and token[0] == token[-1] and token[0] in {"'", '"'}:
        return token[1:-1]
    return token


def strip_leading_env_assignments(tokens: list[str]) -> list[str]:
    index = 0
    while index < len(tokens) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[index]):
        index += 1
    return tokens[index:]


def strip_wrappers(tokens: list[str]) -> list[str]:
    while tokens and tokens[0] in WRAPPERS:
        wrapper = tokens.pop(0)
        if wrapper == "timeout" and tokens and re.match(r"^[0-9.]+[smhd]?$", tokens[0]):
            tokens.pop(0)
        while tokens and tokens[0].startswith("-"):
            tokens.pop(0)
    return tokens


def normalize_raw_path(raw: str, cwd: Path) -> Path | None:
    raw = raw.strip().strip("'\"")
    if not raw or raw == "/dev/null":
        return None
    converted = convert_msys_path(raw)
    if converted is None:
        return None
    path = Path(converted)
    if not path.is_absolute():
        path = cwd / path
    try:
        return path.resolve()
    except OSError:
        return path.absolute()


def convert_msys_path(raw: str) -> str | None:
    value = raw.replace("\\", "/")
    if re.match(r"^[A-Za-z]:/", value):
        return value
    match = re.match(r"^/([A-Za-z])/(.*)$", value)
    if match:
        return f"{match.group(1).upper()}:/{match.group(2)}"
    match = re.match(r"^/mnt/([A-Za-z])/(.*)$", value)
    if match:
        return f"{match.group(1).upper()}:/{match.group(2)}"
    if value.startswith("/"):
        return value
    return value


def has_unsupported_shell_syntax(command: str) -> bool:
    unsupported = ("$(", "`", "<(", ">(", "<<")
    return any(pattern in command for pattern in unsupported)


def has_unsafe_redirection(command: str) -> bool:
    quote: str | None = None
    escaped = False
    i = 0
    while i < len(command):
        char = command[i]
        if escaped:
            escaped = False
            i += 1
            continue
        if char == "\\":
            escaped = True
            i += 1
            continue
        if quote:
            if char == quote:
                quote = None
            i += 1
            continue
        if char in {"'", '"'}:
            quote = char
            i += 1
            continue
        if char == "<":
            return True
        if char == ">":
            j = i + 1
            if j < len(command) and command[j] == ">":
                j += 1
            while j < len(command) and command[j].isspace():
                j += 1
            if j < len(command) and command[j] == "&":
                i = j + 1
                continue
            target = []
            while j < len(command) and not command[j].isspace() and command[j] not in {";", "|", "&"}:
                target.append(command[j])
                j += 1
            if "".join(target) != "/dev/null":
                return True
            i = j
            continue
        i += 1
    return quote is not None


def looks_like_absolute_path(token: str) -> bool:
    stripped = token.strip("'\"")
    if stripped == "/dev/null":
        return False
    converted = convert_msys_path(stripped)
    if converted is None:
        return False
    path = Path(converted)
    return path.is_absolute()


def looks_like_path_token(token: str) -> bool:
    if not token or token in {"{}", ";", "+", "-", "--"}:
        return False
    if token.startswith("-"):
        return False
    if token.startswith(("http://", "https://")):
        return False
    if token in {"(", ")", "!", "not"}:
        return False
    if any(ch in token for ch in ("/", "\\")):
        return True
    if token in {".", ".."}:
        return True
    if any(ch in token for ch in ("*", "?", "[")):
        return "/" in token or "\\" in token
    return False


def path_prefix_before_glob(token: str) -> str:
    for glob_char in ("*", "?", "["):
        if glob_char in token:
            before = token.split(glob_char, 1)[0]
            parent = str(Path(before).parent)
            return "." if parent in {"", "."} else parent
    return token


def should_skip_token(
    tokens: list[str],
    index: int,
    *,
    find_mode: bool,
    find_exec_mode: bool,
) -> bool:
    token = tokens[index]
    if index == 0:
        return True
    if token in {"{}", ";", "+", "(", ")", "!", "not"}:
        return True
    if token.startswith("-"):
        return True
    previous = tokens[index - 1] if index > 0 else ""
    if previous in {
        "-name",
        "-iname",
        "-regex",
        "-iregex",
        "-path",
        "-ipath",
        "-printf",
        "-exec",
        "-ok",
        "-maxdepth",
        "-mindepth",
        "-type",
        "-mtime",
        "-mmin",
        "-size",
    }:
        return True
    if find_exec_mode and token == "{}":
        return True
    if token.startswith(("http://", "https://")):
        return True
    return False


if __name__ == "__main__":
    raise SystemExit(main())
