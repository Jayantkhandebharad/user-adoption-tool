#!/usr/bin/env python3
"""Fail if a blocked term appears in the repository, a staged change, or a commit message.

Terms are stored only as (length, SHA-256 of the lower-cased term), so this file does not
contain them. Each line is lower-cased and stripped of everything but letters and digits, then
every window of each blocked length is hashed and compared; this also catches the term inside
identifiers, URLs or with separators ("Foo-Bar", "foo.bar.com").

Usage:
  check-blocked-terms.py --all              tracked files (contents and paths)
  check-blocked-terms.py --staged           lines added in the staged diff, and staged paths
  check-blocked-terms.py --message FILE     a commit message file
  check-blocked-terms.py --commits RANGE    messages of commits in a git range (e.g. a..b)
"""

import hashlib
import re
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path

BLOCKED = {(7, "56ffd8dfe53379d68bf858a661cd397058b750cbc0c021adf736272fb920f6a0")}
LENGTHS = sorted({length for length, _ in BLOCKED})
NON_ALNUM = re.compile(r"[^a-z0-9]+")


def contains_blocked(text: str) -> bool:
    squashed = NON_ALNUM.sub("", text.lower())
    for length in LENGTHS:
        for i in range(len(squashed) - length + 1):
            digest = hashlib.sha256(squashed[i : i + length].encode()).hexdigest()
            if (length, digest) in BLOCKED:
                return True
    return False


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def scan(lines: Iterable[tuple[str, str]]) -> list[str]:
    """lines: (location, text) pairs. Returns the locations that contain a blocked term."""
    return [where for where, text in lines if contains_blocked(text)]


def tracked_files() -> Iterable[tuple[str, str]]:
    for path in git("ls-files", "-z").split("\0"):
        if not path:
            continue
        yield f"{path} (path)", path
        try:
            data = Path(path).read_bytes()
        except (FileNotFoundError, IsADirectoryError):
            continue
        if b"\0" in data[:8192]:
            continue  # binary
        for number, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
            yield f"{path}:{number}", line


def staged_changes() -> Iterable[tuple[str, str]]:
    for path in git("diff", "--cached", "--name-only", "-z").split("\0"):
        if path:
            yield f"{path} (path)", path
    current, number = "?", 0
    for line in git("diff", "--cached", "--unified=0", "--no-color").splitlines():
        if line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else line[4:]
        elif line.startswith("@@"):
            match = re.search(r"\+(\d+)", line)
            number = int(match.group(1)) if match else 0
        elif line.startswith("+"):
            yield f"{current}:{number}", line[1:]
            number += 1


def message_lines(text: str, label: str) -> Iterable[tuple[str, str]]:
    for number, line in enumerate(text.splitlines(), 1):
        if not line.startswith("#"):  # git strips comment lines from messages
            yield f"{label}:{number}", line


def commit_messages(rev_range: str) -> Iterable[tuple[str, str]]:
    for sha in git("rev-list", rev_range).split():
        yield from message_lines(git("log", "-1", "--format=%B", sha), f"commit {sha[:10]}")


def main(argv: list[str]) -> int:
    if len(argv) == 1 and argv[0] == "--all":
        hits = scan(tracked_files())
    elif len(argv) == 1 and argv[0] == "--staged":
        hits = scan(staged_changes())
    elif len(argv) == 2 and argv[0] == "--message":
        hits = scan(message_lines(Path(argv[1]).read_text(), "commit message"))
    elif len(argv) == 2 and argv[0] == "--commits":
        hits = scan(commit_messages(argv[1]))
    else:
        print(__doc__, file=sys.stderr)
        return 2
    for where in hits:
        print(f"blocked term found: {where}", file=sys.stderr)
    if hits:
        print("Remove it before committing (see CLAUDE.md, ground rules).", file=sys.stderr)
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
