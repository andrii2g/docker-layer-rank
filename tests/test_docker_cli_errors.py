import subprocess

from docker_layer_rank.docker_cli import get_image_history, inspect_image, run_docker
from docker_layer_rank.errors import (
    DockerHistoryError,
    DockerInspectError,
    DockerUnavailableError,
    ImageNotFoundError,
)


def test_run_docker_missing_executable(monkeypatch) -> None:
    def fake_run(*args, **kwargs):
        raise FileNotFoundError()

    monkeypatch.setattr(subprocess, "run", fake_run)

    try:
        run_docker(["docker"], command_kind="inspect", image="img")
    except DockerUnavailableError as exc:
        assert exc.reason == "cli_missing"
    else:
        raise AssertionError("Expected DockerUnavailableError")


def test_inspect_missing_image(monkeypatch) -> None:
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 1, "", "Error: No such image: img")

    monkeypatch.setattr(subprocess, "run", fake_run)

    try:
        inspect_image("img")
    except ImageNotFoundError:
        pass
    else:
        raise AssertionError("Expected ImageNotFoundError")


def test_inspect_invalid_reference(monkeypatch) -> None:
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 1, "", "invalid reference format")

    monkeypatch.setattr(subprocess, "run", fake_run)

    try:
        inspect_image("bad ref")
    except DockerInspectError:
        pass
    else:
        raise AssertionError("Expected DockerInspectError")


def test_history_parse_failure(monkeypatch) -> None:
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 0, "not-json", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    try:
        get_image_history("img")
    except DockerHistoryError:
        pass
    else:
        raise AssertionError("Expected DockerHistoryError")
