"""
Phase 1.3 & 1.4: macOS Finder context extraction and path validation.
"""

import subprocess
from pathlib import Path


# AppleScript that returns the POSIX path of the first selected folder in Finder.
# If no folder is selected, falls back to the frontmost Finder window's target.
_APPLESCRIPT = """
tell application "Finder"
    try
        set sel to selection
        if (count of sel) > 0 then
            set item1 to item 1 of sel
            if class of item1 is folder then
                return POSIX path of (item1 as alias)
            end if
            return POSIX path of ((container of item1) as alias)
        else
            return POSIX path of (target of front Finder window as alias)
        end if
    on error
        return ""
    end try
end tell
"""


def get_finder_folder() -> str:
    """
    Execute AppleScript via osascript and return the POSIX path of the
    currently selected (or open) folder in Finder.

    Returns an empty string when Finder is not available or nothing is selected.
    """
    try:
        result = subprocess.run(
            ["osascript", "-e", _APPLESCRIPT],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def validate_directory(path_str: str) -> Path | None:
    """
    Return a resolved pathlib.Path when path_str is a valid existing directory,
    otherwise return None.
    """
    if not path_str:
        return None
    p = Path(path_str).expanduser().resolve()
    return p if p.is_dir() else None
