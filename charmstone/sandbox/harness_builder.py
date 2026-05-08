"""
Phase 3.4 & 3.5: Harness builder — manages the .agent_harness directory
inside the mounted workspace and writes generated scripts.
"""

from __future__ import annotations

import stat
from pathlib import Path

_HARNESS_DIR = ".agent_harness"


class HarnessBuilder:
    """Creates and manages the .agent_harness subdirectory within workspace_path."""

    def __init__(self, workspace_path: Path) -> None:
        self.workspace_path = workspace_path
        self.harness_path = workspace_path / _HARNESS_DIR
        self.harness_path.mkdir(exist_ok=True)

    # ── Script management ─────────────────────────────────────────────────────

    def write_automation(self, code: str, filename: str = "automation.py") -> Path:
        """Write generated automation code and mark it executable."""
        dest = self.harness_path / filename
        dest.write_text(code, encoding="utf-8")
        dest.chmod(dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP)
        return dest

    def write_log(self, content: str, filename: str = "run.log") -> Path:
        dest = self.harness_path / filename
        with dest.open("a", encoding="utf-8") as f:
            f.write(content)
        return dest

    def harness_dir_path(self) -> Path:
        return self.harness_path
