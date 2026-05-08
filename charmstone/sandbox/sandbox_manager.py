"""
Phase 3.2 – 3.5: Docker-based sandbox manager.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import docker
from docker.models.containers import Container

from sandbox.harness_builder import HarnessBuilder

_IMAGE_TAG = "charmstone-sandbox:latest"
_WORKSPACE_MOUNT = "/workspace"


class SandboxManager:
    """
    Manages a single Docker container that bind-mounts a local workspace directory.
    """

    def __init__(self) -> None:
        self._client: docker.DockerClient = docker.from_env()
        self._container: Container | None = None
        self._harness: HarnessBuilder | None = None

    # ── Image ─────────────────────────────────────────────────────────────────

    def build_image(self, dockerfile_dir: Path | None = None) -> None:
        """Build the sandbox image from the bundled Dockerfile."""
        if dockerfile_dir is None:
            dockerfile_dir = Path(__file__).parent
        self._client.images.build(
            path=str(dockerfile_dir),
            tag=_IMAGE_TAG,
            rm=True,
        )

    # ── Container lifecycle ───────────────────────────────────────────────────

    def start(self, workspace_path: Path) -> None:
        """
        Phase 3.3: Start a background container with workspace_path
        bind-mounted to /workspace in read-write mode.
        """
        workspace_path = workspace_path.resolve()
        self._container = self._client.containers.run(
            _IMAGE_TAG,
            command="sleep infinity",
            detach=True,
            remove=True,
            volumes={
                str(workspace_path): {
                    "bind": _WORKSPACE_MOUNT,
                    "mode": "rw",
                }
            },
        )
        self._harness = HarnessBuilder(workspace_path)

    def stop(self) -> None:
        if self._container is not None:
            try:
                self._container.stop(timeout=5)
            except Exception:
                pass
            self._container = None
            self._harness = None

    # ── Execution ─────────────────────────────────────────────────────────────

    def exec_run(
        self,
        command: str | list[str],
        workdir: str = _WORKSPACE_MOUNT,
    ) -> tuple[int, str]:
        """
        Phase 3.5: Run a command inside the running container.
        Returns (exit_code, combined_output).
        """
        if self._container is None:
            raise RuntimeError("Sandbox is not running. Call start() first.")
        result = self._container.exec_run(
            command,
            workdir=workdir,
            demux=False,
        )
        output = (result.output or b"").decode("utf-8", errors="replace")
        return result.exit_code, output

    # ── Harness access ────────────────────────────────────────────────────────

    @property
    def harness(self) -> HarnessBuilder:
        if self._harness is None:
            raise RuntimeError("Sandbox is not running. Call start() first.")
        return self._harness

    def __enter__(self) -> "SandboxManager":
        return self

    def __exit__(self, *_: Any) -> None:
        self.stop()
