#!/usr/bin/env python3
"""Auto-approve Bash requests that respect the current project boundary.

Exit 0 approves the request. Exit 1 falls through to Claude Code's normal
permission prompt. The hook never denies a command.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_MARKERS = (
    ".git",
    ".claude",
    "AGENTS.md",
    "ProjectSettings/ProjectVersion.txt",
    "Packages/manifest.json",
    "package.json",
)

READ_COMMANDS = {
    "rg",
    "grep",
    "findstr",
    "select-string",
    "cat",
    "type",
    "get-content",
    "head",
    "tail",
    "sed",
    "awk",
    "nl",
    "wc",
    "sort",
    "uniq",
    "cut",
    "tr",
    "comm",
    "cmp",
    "column",
    "jq",
    "yq",
    "file",
    "strings",
    "basename",
    "dirname",
    "realpath",
    "readlink",
    "md5sum",
    "sha1sum",
    "sha256sum",
    "sha512sum",
    "ls",
    "dir",
    "get-childitem",
    "resolve-path",
    "test-path",
    "select-object",
    "measure-object",
    "sort-object",
    "group-object",
    "compare-object",
    "format-table",
    "format-list",
    "convertfrom-json",
    "convertto-json",
    "tree",
    "du",
    "stat",
    "xxd",
    "pwd",
    "where",
    "which",
    "test",
    "[",
    "printf",
    "echo",
}

MUTATING_COMMANDS = {
    "rm",
    "rmdir",
    "del",
    "erase",
    "unlink",
    "shred",
    "remove-item",
    "mv",
    "move",
    "move-item",
    "rename",
    "rename-item",
    "cp",
    "copy",
    "copy-item",
    "touch",
    "mkdir",
    "md",
    "new-item",
    "set-content",
    "add-content",
    "out-file",
    "tee",
    "install",
    "chmod",
    "chown",
    "icacls",
    "takeown",
    "npm",
    "npx",
    "pnpm",
    "yarn",
    "dotnet",
    "msbuild",
    "unity",
    "unity.exe",
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
    "rev-parse",
    "branch",
    "remote",
    "tag",
}

SCRIPT_COMMANDS = {
    "python",
    "python3",
    "py",
    "node",
    "bash",
    "sh",
    "pwsh",
    "powershell",
    "cmd",
}

WRAPPERS = {"time", "timeout", "nice", "nohup", "stdbuf", "command", "env"}
SHELL_KEYWORDS = {
    "do",
    "done",
    "then",
    "else",
    "elif",
    "fi",
    "while",
    "until",
    "if",
}


@dataclass(frozen=True)
class Redirection:
    target: str
    writes: bool


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 1

    command = extract_command(payload)
    if not command:
        return 1

    start_cwd = extract_cwd(payload)
    project_root = find_project_root(start_cwd) or find_project_root(Path.cwd())
    if project_root is None:
        return 1

    policy = ProjectBoundaryPolicy(project_root, start_cwd)
    return 0 if policy.approves(command) else 1


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
        candidates: list[object] = []
        if isinstance(tool_input, dict):
            candidates.extend((tool_input.get("cwd"), tool_input.get("workdir")))
        candidates.extend((payload.get("cwd"), payload.get("workdir")))
        for candidate in candidates:
            if isinstance(candidate, str) and candidate.strip():
                path = normalize_path(candidate, Path.cwd())
                if path is not None:
                    return path
    return Path.cwd().resolve()


def find_project_root(start: Path) -> Path | None:
    start = start.resolve()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(start),
            capture_output=True,
            text=True,
            timeout=3,
        )
        if result.returncode == 0 and result.stdout.strip():
            root = normalize_path(result.stdout.strip(), start)
            if root is not None:
                return root.resolve()
    except (OSError, subprocess.SubprocessError):
        pass

    for current in (start, *start.parents):
        if any((current / marker).exists() for marker in PROJECT_MARKERS):
            return current.resolve()
    return None


class ProjectBoundaryPolicy:
    def __init__(self, project_root: Path, start_cwd: Path) -> None:
        self.project_root = project_root.resolve()
        self.cwd = start_cwd.resolve()

    def approves(self, command: str) -> bool:
        if has_unsupported_dynamic_syntax(command):
            return self.is_in_project(self.cwd) and not self.raw_command_has_outside_mutation(command)
        try:
            segments = split_compound(command)
        except ValueError:
            return self.is_in_project(self.cwd) and not self.raw_command_has_outside_mutation(command)
        if not segments:
            return False

        for segment in segments:
            if not self.approves_segment(segment):
                return False
        return True

    def approves_segment(self, segment: str) -> bool:
        grouped = unwrap_shell_group(segment)
        if grouped is not None:
            nested = ProjectBoundaryPolicy(self.project_root, self.cwd)
            return nested.approves(grouped)

        substitutions, outer = extract_substitutions(segment)
        for inner in substitutions:
            nested = ProjectBoundaryPolicy(self.project_root, self.cwd)
            if not nested.approves(inner):
                return False

        try:
            command_text, redirections = strip_redirections(outer)
            tokens = tokenize(command_text)
        except ValueError:
            return False

        if not self.redirections_are_safe(redirections):
            return False

        tokens = strip_prefixes(tokens)
        if not tokens:
            return not any(redirection.writes for redirection in redirections)

        command = command_name(tokens[0])
        if command == "cd":
            return self.apply_cd(tokens)
        if command in SCRIPT_COMMANDS:
            return self.approves_script(tokens)
        if command == "git":
            return self.approves_git(tokens)
        if command == "find":
            return self.approves_find(tokens)
        if command == "xargs":
            return self.approves_xargs(tokens)
        if command == "curl":
            return self.approves_curl(tokens)
        if command in READ_COMMANDS:
            if command == "sed" and any(flag == "-i" or flag.startswith("-i") for flag in tokens[1:]):
                return self.mutation_stays_in_project(tokens[1:])
            return True
        if command in MUTATING_COMMANDS:
            return self.mutation_stays_in_project(tokens[1:])

        # Unknown tools are trusted only when launched from inside the project
        # and do not name an explicit outside path.
        return self.is_in_project(self.cwd) and not self.has_explicit_outside_path(tokens[1:])

    def apply_cd(self, tokens: list[str]) -> bool:
        if len(tokens) != 2 or tokens[1] in {"-", "~"}:
            return False
        target = normalize_path(tokens[1], self.cwd)
        if target is None:
            return False
        self.cwd = target.resolve()
        return True

    def approves_script(self, tokens: list[str]) -> bool:
        command = command_name(tokens[0])
        inline = inline_script_command(command, tokens)
        if inline is not None:
            if command in {"powershell", "pwsh", "cmd", "bash", "sh"}:
                nested = ProjectBoundaryPolicy(self.project_root, self.cwd)
                return nested.approves(inline)
            if self.is_in_project(self.cwd):
                return not self.raw_command_has_outside_mutation(inline)
            return False

        if is_version_query(tokens[1:]):
            return True

        # Complete-auto mode trusts scripts launched from the project. Script
        # internals cannot be reliably inspected by a PermissionRequest hook.
        if self.is_in_project(self.cwd):
            return not self.has_explicit_outside_path(tokens[1:])
        return False

    def approves_git(self, tokens: list[str]) -> bool:
        git_cwd = self.cwd
        subcommand_index = 1
        index = 1
        while index < len(tokens):
            token = tokens[index]
            if token == "-C" and index + 1 < len(tokens):
                target = normalize_path(tokens[index + 1], git_cwd)
                if target is None:
                    return False
                git_cwd = target
                index += 2
                continue
            if token.startswith("-C") and len(token) > 2:
                target = normalize_path(token[2:], git_cwd)
                if target is None:
                    return False
                git_cwd = target
                index += 1
                continue
            if token.startswith("-"):
                index += 1
                continue
            subcommand_index = index
            break
        else:
            return True

        subcommand = tokens[subcommand_index].lower()
        if subcommand in GIT_READ_SUBCOMMANDS:
            return True
        return self.is_in_project(git_cwd) and not self.has_explicit_outside_path(
            tokens[subcommand_index + 1:],
            base=git_cwd,
        )

    def approves_find(self, tokens: list[str]) -> bool:
        mutation = "-delete" in tokens
        roots = find_roots(tokens)

        index = 1
        while index < len(tokens):
            if tokens[index] in {"-exec", "-execdir", "-ok", "-okdir"}:
                nested_tokens: list[str] = []
                index += 1
                while index < len(tokens) and tokens[index] not in {";", "+"}:
                    nested_tokens.append(tokens[index])
                    index += 1
                if not nested_tokens:
                    return False
                nested_command = command_name(nested_tokens[0])
                if nested_command in SCRIPT_COMMANDS:
                    nested_policy = ProjectBoundaryPolicy(self.project_root, self.cwd)
                    if not nested_policy.approves_segment(" ".join(nested_tokens)):
                        return False
                if nested_command not in READ_COMMANDS:
                    mutation = True
                    if not self.mutation_stays_in_project(nested_tokens[1:]):
                        return False
            index += 1

        if not mutation:
            return True
        return all(self.path_is_in_project(root) for root in roots)

    def approves_xargs(self, tokens: list[str]) -> bool:
        nested = [token for token in tokens[1:] if not token.startswith("-")]
        if not nested:
            return False
        nested_command = command_name(nested[0])
        if nested_command in READ_COMMANDS:
            return True
        if nested_command in SCRIPT_COMMANDS:
            nested_policy = ProjectBoundaryPolicy(self.project_root, self.cwd)
            return nested_policy.approves_segment(" ".join(nested))
        return self.is_in_project(self.cwd) and not self.has_explicit_outside_path(nested[1:])

    def approves_curl(self, tokens: list[str]) -> bool:
        output_flags = {"-o", "--output", "-O", "--remote-name", "--output-dir"}
        writes = any(
            token in output_flags
            or token.startswith("--output=")
            or token.startswith("--output-dir=")
            for token in tokens[1:]
        )
        if not writes:
            return True
        return self.mutation_stays_in_project(tokens[1:])

    def redirections_are_safe(self, redirections: list[Redirection]) -> bool:
        for redirection in redirections:
            if not redirection.writes or redirection.target in {"/dev/null", "NUL", "nul"}:
                continue
            if not self.path_is_in_project(redirection.target):
                return False
        return True

    def mutation_stays_in_project(self, args: list[str]) -> bool:
        if not self.is_in_project(self.cwd):
            return False
        return not self.has_explicit_outside_path(args)

    def raw_command_has_outside_mutation(self, command: str) -> bool:
        if not contains_mutation_signal(command):
            return False
        return self.has_explicit_outside_path(extract_path_candidates(command))

    def has_explicit_outside_path(self, args: list[str], *, base: Path | None = None) -> bool:
        base = base or self.cwd
        for raw in args:
            for candidate in option_path_candidates(raw):
                if candidate in {"/dev/null", "NUL", "nul", "{}", ";", "+"}:
                    continue
                if contains_unresolved_path_expansion(candidate):
                    if self.is_in_project(base):
                        continue
                    return True
                if not looks_like_explicit_path(candidate):
                    continue
                path = normalize_path(path_prefix_before_glob(candidate), base)
                if path is not None and not self.is_in_project(path):
                    return True
        return False

    def path_is_in_project(self, raw: str) -> bool:
        if contains_unresolved_path_expansion(raw):
            return False
        path = normalize_path(path_prefix_before_glob(raw), self.cwd)
        return path is not None and self.is_in_project(path)

    def is_in_project(self, path: Path) -> bool:
        try:
            common = os.path.commonpath(
                (os.path.normcase(str(self.project_root)), os.path.normcase(str(path.resolve())))
            )
        except (OSError, ValueError):
            return False
        return common == os.path.normcase(str(self.project_root))


def split_compound(command: str) -> list[str]:
    segments: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escaped = False
    substitution_depth = 0
    group_depth = 0
    index = 0

    while index < len(command):
        char = command[index]
        if escaped:
            current.extend(("\\", char))
            escaped = False
            index += 1
            continue
        if char == "\\":
            escaped = True
            index += 1
            continue
        if quote:
            current.append(char)
            if char == quote:
                quote = None
            index += 1
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            index += 1
            continue
        if command.startswith("$(", index):
            substitution_depth += 1
            current.append("$(")
            index += 2
            continue
        if char == ")" and substitution_depth:
            substitution_depth -= 1
            current.append(char)
            index += 1
            continue
        if substitution_depth:
            current.append(char)
            index += 1
            continue
        if char == "(":
            group_depth += 1
            current.append(char)
            index += 1
            continue
        if char == ")" and group_depth:
            group_depth -= 1
            current.append(char)
            index += 1
            continue
        if group_depth:
            current.append(char)
            index += 1
            continue
        if command.startswith(("&&", "||"), index):
            add_segment(segments, current)
            current = []
            index += 2
            continue
        if char in {";", "|"}:
            add_segment(segments, current)
            current = []
            index += 1
            continue
        current.append(char)
        index += 1

    if quote or escaped or substitution_depth or group_depth:
        raise ValueError("unterminated shell expression")
    add_segment(segments, current)
    return segments


def add_segment(segments: list[str], chars: list[str]) -> None:
    segment = "".join(chars).strip()
    if segment:
        segments.append(segment)


def extract_substitutions(command: str) -> tuple[list[str], str]:
    substitutions: list[str] = []
    output: list[str] = []
    index = 0

    while index < len(command):
        if not command.startswith("$(", index):
            output.append(command[index])
            index += 1
            continue
        depth = 1
        cursor = index + 2
        quote: str | None = None
        while cursor < len(command) and depth:
            char = command[cursor]
            if quote:
                if char == quote:
                    quote = None
            elif char in {"'", '"'}:
                quote = char
            elif command.startswith("$(", cursor):
                depth += 1
                cursor += 1
            elif char == ")":
                depth -= 1
            cursor += 1
        if depth:
            raise ValueError("unterminated command substitution")
        substitutions.append(command[index + 2:cursor - 1])
        output.append("_SUBSTITUTION_")
        index = cursor
    return substitutions, "".join(output)


def strip_redirections(segment: str) -> tuple[str, list[Redirection]]:
    lexer = shlex.shlex(segment, posix=False, punctuation_chars="<>")
    lexer.whitespace_split = True
    lexer.commenters = ""
    raw_tokens = list(lexer)
    output: list[str] = []
    redirections: list[Redirection] = []
    index = 0

    while index < len(raw_tokens):
        token = raw_tokens[index]
        operator = token
        if re.fullmatch(r"\d+", token) and index + 1 < len(raw_tokens):
            if raw_tokens[index + 1] in {">", ">>", "<"}:
                operator = raw_tokens[index + 1]
                index += 1
            else:
                output.append(token)
                index += 1
                continue
        if operator not in {">", ">>", "<"}:
            output.append(token)
            index += 1
            continue
        if index + 1 >= len(raw_tokens):
            raise ValueError("redirection without target")
        target = strip_quotes(raw_tokens[index + 1])
        if target.startswith("&") or target in {"1", "2"}:
            index += 2
            continue
        redirections.append(Redirection(target=target, writes=operator != "<"))
        index += 2

    return " ".join(output), redirections


def tokenize(command: str) -> list[str]:
    lexer = shlex.shlex(command, posix=False)
    lexer.whitespace_split = True
    lexer.commenters = ""
    return [";" if token == r"\;" else strip_quotes(token) for token in lexer]


def strip_prefixes(tokens: list[str]) -> list[str]:
    result = list(tokens)
    while result and result[0].lower() in SHELL_KEYWORDS:
        result.pop(0)
    while result and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", result[0]):
        result.pop(0)
    while result and command_name(result[0]) in WRAPPERS:
        wrapper = command_name(result.pop(0))
        if wrapper == "timeout" and result and re.fullmatch(r"[0-9.]+[smhd]?", result[0]):
            result.pop(0)
        while result and result[0].startswith("-"):
            result.pop(0)
    return result


def command_name(raw: str) -> str:
    return Path(raw.replace("\\", "/")).name.lower()


def unwrap_shell_group(segment: str) -> str | None:
    value = segment.strip()
    if len(value) < 2 or value[0] != "(" or value[-1] != ")":
        return None
    depth = 0
    quote: str | None = None
    escaped = False
    for index, char in enumerate(value):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if quote:
            if char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            continue
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0 and index != len(value) - 1:
                return None
    return value[1:-1].strip() if depth == 0 else None


def find_roots(tokens: list[str]) -> list[str]:
    roots: list[str] = []
    for token in tokens[1:]:
        if token == "--":
            continue
        if token.startswith("-") or token in {"(", ")", "!", "not"}:
            break
        roots.append(token)
    return roots or ["."]


def inline_script_command(command: str, tokens: list[str]) -> str | None:
    flags_by_command = {
        "powershell": {"-command", "-c"},
        "pwsh": {"-command", "-c"},
        "cmd": {"/c", "/k"},
        "bash": {"-c"},
        "sh": {"-c"},
        "python": {"-c"},
        "python3": {"-c"},
        "py": {"-c"},
        "node": {"-e", "--eval"},
    }
    flags = flags_by_command.get(command, set())
    for index, token in enumerate(tokens[1:], 1):
        lowered = token.lower()
        if lowered in flags and index + 1 < len(tokens):
            return tokens[index + 1]
        for flag in flags:
            if lowered.startswith(flag + ":") or lowered.startswith(flag + "="):
                return token[len(flag) + 1:]
    return None


def is_version_query(args: list[str]) -> bool:
    return bool(args) and all(
        token.lower() in {"--version", "-v", "-version", "/version"}
        for token in args
    )


def contains_mutation_signal(command: str) -> bool:
    lowered = command.lower()
    command_signals = MUTATING_COMMANDS | {
        "writealltext",
        "writeallbytes",
        "write_text",
        "write_bytes",
        "write",
        "delete",
        "unlink",
        "rmtree",
        "remove",
        "replace",
        "rename",
    }
    if any(
        re.search(rf"(?<![a-z0-9_-]){re.escape(signal)}(?![a-z0-9_-])", lowered)
        for signal in command_signals
    ):
        return True
    return bool(re.search(r"(?:^|[^<])>{1,2}(?![>&])", command))


def extract_path_candidates(command: str) -> list[str]:
    candidates = re.findall(
        r"""(?ix)
        (?:
            [a-z]:[\\/][^\s"'`;|)]+
            | /(?:mnt/[a-z]/)?[^\s"'`;|)]+
            | \\\\[^\s"'`;|)]+
            | \$\{?[a-z_][a-z0-9_]*\}?[\\/][^\s"'`;|)]+
            | %[a-z_][a-z0-9_]*%[\\/][^\s"'`;|)]+
        )
        """,
        command,
    )
    return [candidate.rstrip(".,") for candidate in candidates]


def option_path_candidates(token: str) -> list[str]:
    token = strip_quotes(token)
    if token.startswith(("http://", "https://")):
        return []
    if "=" in token and token.startswith("-"):
        return [token.split("=", 1)[1]]
    return [token]


def looks_like_explicit_path(token: str) -> bool:
    if not token or token.startswith(("http://", "https://")):
        return False
    if token in {".", "..", "~"}:
        return True
    if re.match(r"^[A-Za-z]:[\\/]", token):
        return True
    if token.startswith(("/", "\\")):
        return True
    return "/" in token or "\\" in token


def contains_unresolved_path_expansion(token: str) -> bool:
    return token.startswith("~") or bool(re.search(r"\$[{A-Za-z_]|\%[^%]+\%", token))


def path_prefix_before_glob(token: str) -> str:
    for marker in ("*", "?", "["):
        if marker in token:
            prefix = token.split(marker, 1)[0]
            parent = str(Path(prefix).parent)
            return "." if parent in {"", "."} else parent
    return token


def normalize_path(raw: str, cwd: Path) -> Path | None:
    value = strip_quotes(raw).strip()
    if not value:
        return None
    converted = convert_shell_path(value)
    path = Path(converted)
    if not path.is_absolute():
        path = cwd / path
    try:
        return path.resolve()
    except OSError:
        return path.absolute()


def convert_shell_path(raw: str) -> str:
    value = raw.replace("\\", "/")
    if re.match(r"^[A-Za-z]:/", value):
        return value
    match = re.match(r"^/([A-Za-z])/(.*)$", value)
    if match:
        return f"{match.group(1).upper()}:/{match.group(2)}"
    match = re.match(r"^/mnt/([A-Za-z])/(.*)$", value)
    if match:
        return f"{match.group(1).upper()}:/{match.group(2)}"
    return value


def strip_quotes(token: str) -> str:
    if len(token) >= 2 and token[0] == token[-1] and token[0] in {"'", '"'}:
        return token[1:-1]
    return token


def has_unsupported_dynamic_syntax(command: str) -> bool:
    return any(marker in command for marker in ("`", "<(", ">(", "<<", "<<<"))


if __name__ == "__main__":
    raise SystemExit(main())
