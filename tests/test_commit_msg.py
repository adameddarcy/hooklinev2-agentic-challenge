import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "check_commit_msg.py"


def run_hook(tmp_path: Path, message: str) -> subprocess.CompletedProcess[str]:
    message_file = tmp_path / "COMMIT_EDITMSG"
    message_file.write_text(message, encoding="utf-8")
    return subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPT), str(message_file)],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    "message",
    [
        "HL07: Add secret rotation",
        "HL02: Fix event matching\n\nRestore segment-based matching.",
        "# Please enter the commit message\nHL99: Tidy up",
    ],
)
def test_accepts_ticket_prefix(tmp_path: Path, message: str) -> None:
    assert run_hook(tmp_path, message).returncode == 0


@pytest.mark.parametrize(
    "message",
    [
        "Add secret rotation",
        "HL-07: Add secret rotation",
        "HL7: Add secret rotation",
        "hl07: Add secret rotation",
        "HL07 Add secret rotation",
        "HL07:",
        "HL007: Add secret rotation",
        'Revert "HL07: Add secret rotation"',
        "",
    ],
)
def test_rejects_missing_or_malformed_prefix(tmp_path: Path, message: str) -> None:
    result = run_hook(tmp_path, message)
    assert result.returncode == 1
    assert "HL07: Add secret rotation" in result.stderr
