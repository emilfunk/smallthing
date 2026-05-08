"""
Phase 1.2: Global hotkey listener using pynput.
Fires a callback when <cmd>+<alt> is pressed.
"""

from collections.abc import Callable

from pynput import keyboard


# Modifier combination: Command + Alt (Option) on macOS.
_HOTKEY_COMBO = "<cmd>+<alt>"


class HotkeyListener:
    """Runs a pynput GlobalHotKeys listener in a background daemon thread."""

    def __init__(self, on_trigger: Callable[[], None]) -> None:
        self._on_trigger = on_trigger
        self._listener: keyboard.GlobalHotKeys | None = None

    def start(self) -> None:
        self._listener = keyboard.GlobalHotKeys(
            {_HOTKEY_COMBO: self._on_trigger}
        )
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
