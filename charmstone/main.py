"""
Charmstone entry point.

Starts the PyQt6 application, registers the global hotkey, and wires all
subsystems together.
"""

import sys

from PyQt6.QtCore import QMetaObject, Qt, Q_ARG
from PyQt6.QtWidgets import QApplication

from agent.api_client import AgentAPIClient
from agent.state_machine import AgentStateMachine
from context_extractor import get_finder_folder, validate_directory
from hotkey_listener import HotkeyListener
from overlay import RadialMenuWindow
from sandbox.sandbox_manager import SandboxManager


def main() -> None:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    sandbox = SandboxManager()
    api_client = AgentAPIClient()

    def on_init_sandbox() -> None:
        raw = get_finder_folder()
        workspace = validate_directory(raw)
        if workspace is None:
            return
        try:
            sandbox.build_image()
            sandbox.start(workspace)
        except Exception as exc:
            print(f"[charmstone] sandbox start failed: {exc}", file=sys.stderr)

    def on_prompt(text: str) -> None:
        raw = get_finder_folder()
        workspace = validate_directory(raw)
        if workspace is None:
            return
        state_machine.submit_user_input(text)

    overlay = RadialMenuWindow(
        on_init_sandbox=on_init_sandbox,
        on_prompt=on_prompt,
    )
    state_machine = AgentStateMachine(overlay, sandbox, api_client)

    def on_hotkey() -> None:
        """Called from pynput's background thread — marshal to the Qt main thread."""
        raw = get_finder_folder()
        workspace = validate_directory(raw)

        def _show() -> None:
            if workspace is not None:
                state_machine.begin_interview(workspace)
            overlay.show_at_cursor()

        # Qt requires UI mutations on the main thread
        QMetaObject.invokeMethod(overlay, "show_at_cursor", Qt.ConnectionType.QueuedConnection)
        if workspace is not None:
            QMetaObject.invokeMethod(
                overlay,
                "set_prompt_placeholder",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, "Describe what you want…"),
            )

    listener = HotkeyListener(on_hotkey)
    listener.start()

    exit_code = app.exec()
    listener.stop()
    sandbox.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
