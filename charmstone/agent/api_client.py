"""
Phase 4.1: Anthropic Claude API client for the Charmstone agent backend.
"""

from __future__ import annotations

import os
from pathlib import Path

import anthropic

_DEFAULT_MODEL = "claude-sonnet-4-6"

_SYSTEM_TEMPLATE = """\
You are Charmstone, an agentic assistant that automates tasks inside a local \
directory on behalf of the user.

Working directory: {workspace}
Files present:
{file_listing}

When the user describes an automation task:
1. Ask at most one clarifying question if essential details are missing.
2. Once you have enough context, output ONLY a valid Python script that \
   accomplishes the task when executed inside the working directory.
   Wrap the script in <automation> … </automation> tags.

Never explain the script outside of code comments. Never produce partial code.
"""


class AgentAPIClient:
    """Thin wrapper around the Anthropic SDK for the Charmstone agent loop."""

    def __init__(
        self,
        model: str = _DEFAULT_MODEL,
        api_key: str | None = None,
    ) -> None:
        self._model = model
        self._client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        )

    def ask(
        self,
        workspace: Path,
        user_query: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        """
        Send user_query with workspace context. Returns the model's text response.
        history is a list of {"role": "user"|"assistant", "content": "…"} dicts.
        """
        file_listing = _build_file_listing(workspace)
        system = _SYSTEM_TEMPLATE.format(
            workspace=str(workspace),
            file_listing=file_listing,
        )

        messages: list[dict[str, str]] = list(history or [])
        messages.append({"role": "user", "content": user_query})

        response = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=system,
            messages=messages,  # type: ignore[arg-type]
        )
        return response.content[0].text  # type: ignore[union-attr]


def _build_file_listing(workspace: Path, max_entries: int = 80) -> str:
    """Return a compact listing of the workspace's top-level files."""
    try:
        entries = sorted(workspace.iterdir(), key=lambda p: (p.is_file(), p.name))
        lines = [str(e.relative_to(workspace)) for e in entries[:max_entries]]
        if len(entries) > max_entries:
            lines.append(f"… and {len(entries) - max_entries} more")
        return "\n".join(lines) or "(empty)"
    except OSError:
        return "(unreadable)"
