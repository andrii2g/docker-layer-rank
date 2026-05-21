from __future__ import annotations


class DockerLayerRankError(Exception):
    """Base class for user-facing application errors."""


class DockerUnavailableError(DockerLayerRankError):
    """Docker CLI is missing, or Docker daemon cannot be reached."""

    def __init__(self, message: str, *, reason: str):
        super().__init__(message)
        self.reason = reason


class ImageNotFoundError(DockerLayerRankError):
    """Requested Docker image is not available locally."""

    def __init__(self, image: str, reason: str | None = None):
        super().__init__(reason or image)
        self.image = image
        self.reason = reason


class DockerInspectError(DockerLayerRankError):
    """Docker image inspect failed for a non-missing-image reason."""


class DockerHistoryError(DockerLayerRankError):
    """Docker image history failed or produced invalid output."""


class OutputPathError(DockerLayerRankError):
    """Output directory or report file path is invalid or unavailable."""
