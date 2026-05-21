from __future__ import annotations

import json
import subprocess
from typing import Literal

from .errors import (
    DockerHistoryError,
    DockerInspectError,
    DockerUnavailableError,
    ImageNotFoundError,
)

DockerCommandKind = Literal["inspect", "history"]

_DAEMON_ERROR_MARKERS = (
    "cannot connect to the docker daemon",
    "is the docker daemon running",
    "docker daemon is not running",
    "error during connect",
    "open //./pipe/docker_engine",
    "connect: connection refused",
    "connection refused",
    "permission denied while trying to connect to the docker daemon socket",
)

_MISSING_IMAGE_MARKERS = (
    "no such image",
    "no such object",
    "image not known",
    "reference does not exist",
)


def _combined_output(result: subprocess.CompletedProcess[str]) -> str:
    parts: list[str] = []
    if result.stderr:
        parts.append(result.stderr.strip())
    if result.stdout:
        parts.append(result.stdout.strip())
    return "\n".join(part for part in parts if part)


def _contains_marker(text: str, markers: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in markers)


def run_docker(args: list[str], *, command_kind: DockerCommandKind, image: str) -> str:
    try:
        result = subprocess.run(
            args,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
    except FileNotFoundError as exc:
        raise DockerUnavailableError(
            "Docker CLI was not found",
            reason="cli_missing",
        ) from exc

    if result.returncode == 0:
        return result.stdout

    message = _combined_output(result)

    if _contains_marker(message, _DAEMON_ERROR_MARKERS):
        raise DockerUnavailableError(
            "Docker daemon is not available",
            reason="daemon_unavailable",
        )

    if command_kind == "inspect":
        if _contains_marker(message, _MISSING_IMAGE_MARKERS):
            raise ImageNotFoundError(image=image, reason=message or None)
        raise DockerInspectError(message or "Docker image inspect command failed")

    if command_kind == "history":
        if _contains_marker(message, _MISSING_IMAGE_MARKERS):
            raise ImageNotFoundError(image=image, reason=message or None)
        raise DockerHistoryError(message or "Docker image history command failed")

    raise DockerInspectError(message or "Docker command failed")


def inspect_image(image: str) -> list[dict]:
    output = run_docker(
        ["docker", "image", "inspect", image],
        command_kind="inspect",
        image=image,
    )
    try:
        data = json.loads(output)
    except json.JSONDecodeError as exc:
        raise DockerInspectError("failed to parse Docker image inspect output") from exc

    if not isinstance(data, list) or not data:
        raise DockerInspectError("failed to parse Docker image inspect output")

    return data


def get_image_history(image: str) -> list[dict]:
    output = run_docker(
        [
            "docker",
            "image",
            "history",
            image,
            "--no-trunc",
            "--format",
            "{{json .}}",
        ],
        command_kind="history",
        image=image,
    )

    entries: list[dict] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise DockerHistoryError("failed to parse Docker image history output") from exc
        if not isinstance(item, dict):
            raise DockerHistoryError("failed to parse Docker image history output")
        entries.append(item)
    return entries
