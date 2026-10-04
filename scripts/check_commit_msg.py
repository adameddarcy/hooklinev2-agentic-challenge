"""Commit-msg hook: require every commit message to start with a ticket prefix.

The first line must look like ``HL07: Short description``. Run by pre-commit with the
path to the commit message file.
"""

import re
import sys
from pathlib import Path

PATTERN = re.compile(r"^HL\d{2}: \S")


def subject_line(message: str) -> str:
    """Return the first line of ``message`` that isn't a git comment."""
    for line in message.splitlines():
        if not line.startswith("#"):
            return line
    return ""


def is_valid(message: str) -> bool:
    """Return ``True`` if the commit subject starts with ``HL[num][num]: ``."""
    return PATTERN.match(subject_line(message)) is not None


def main(argv: list[str]) -> int:
    message = Path(argv[1]).read_text(encoding="utf-8")
    if is_valid(message):
        return 0
    print(
        "Commit message must start with a ticket prefix, e.g. 'HL07: Add secret rotation'.\n"
        f"Got: {subject_line(message)!r}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
