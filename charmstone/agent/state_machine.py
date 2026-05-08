"""
Phase 4.2 – 4.4: Interview-phase state machine connecting the API client,
the UI overlay, and the harness builder.
"""

from __future__ import annotations

import re
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING

from agent.api_client import AgentAPIClient
from sandbox.harness_builder import HarnessBuilder
from sandbox.sandbox_manager import SandboxManager

if TYPE_CHECKING:
    from overlay import RadialMenuWindow

_AUTOMATION_RE = re.compile(r"<automation>(.*?)</automation>", re.DOTALL)


class Phase(Enum):
    IDLE = auto()
    WAITING_FOR_INPUT = auto()
    WAITING_FOR_API = auto()


class AgentStateMachine:
    """
    Drives the agentic interview loop.

    States:
        IDLE              – nothing happening
        WAITING_FOR_INPUT – UI is visible, expecting the user to type
        WAITING_FOR_API   – API call in flight
    """

    def __init__(
        self,
        overlay: "RadialMenuWindow",
        sandbox: SandboxManager,
        api_client: AgentAPIClient | None = None,
    ) -> None:
        self._overlay = overlay
        self._sandbox = sandbox
        self._api = api_client or AgentAPIClient()
        self._phase = Phase.IDLE
        self._history: list[dict[str, str]] = []
        self._workspace: Path | None = None

    # ── Public interface ──────────────────────────────────────────────────────

    def begin_interview(self, workspace: Path) -> None:
        """Called when the user triggers 'Prompt' from the radial menu."""
        self._workspace = workspace
        self._history = []
        self._phase = Phase.WAITING_FOR_INPUT
        self._overlay.set_prompt_placeholder("Describe what you want…")

    def submit_user_input(self, text: str) -> None:
        """
        Phase 4.2/4.3: Called when the user presses Return in the prompt field.
        Fires an API request and transitions to WAITING_FOR_API.
        """
        if self._phase != Phase.WAITING_FOR_INPUT or not text.strip():
            return
        if self._workspace is None:
            return

        self._phase = Phase.WAITING_FOR_API
        self._history.append({"role": "user", "content": text})

        try:
            response = self._api.ask(
                workspace=self._workspace,
                user_query=text,
                history=self._history[:-1],  # history without the just-added entry
            )
        except Exception as exc:
            self._handle_error(str(exc))
            return

        self._history.append({"role": "assistant", "content": response})
        self._dispatch_response(response)

    # ── Response routing ──────────────────────────────────────────────────────

    def _dispatch_response(self, response: str) -> None:
        """
        Phase 4.3 & 4.4:
          - If response contains <automation>…</automation>, write it to harness.
          - Otherwise treat it as a clarifying question and update the placeholder.
        """
        match = _AUTOMATION_RE.search(response)
        if match:
            self._deploy_automation(match.group(1).strip())
        else:
            # Clarifying question — show it in the prompt placeholder
            question = response.strip()
            self._overlay.set_prompt_placeholder(question)
            self._phase = Phase.WAITING_FOR_INPUT

    def _deploy_automation(self, code: str) -> None:
        """Phase 4.4: Write the automation script to the harness directory."""
        if self._workspace is None:
            return
        harness = HarnessBuilder(self._workspace)
        script_path = harness.write_automation(code)
        # Optionally execute it immediately inside the sandbox
        try:
            exit_code, output = self._sandbox.exec_run(
                ["python", f"/workspace/.agent_harness/{script_path.name}"]
            )
            harness.write_log(
                f"=== automation run (exit {exit_code}) ===\n{output}\n"
            )
        except RuntimeError:
            # Sandbox not running — script written, execution deferred
            pass
        self._phase = Phase.IDLE

    def _handle_error(self, message: str) -> None:
        self._overlay.set_prompt_placeholder(f"Error: {message}")
        self._phase = Phase.WAITING_FOR_INPUT
