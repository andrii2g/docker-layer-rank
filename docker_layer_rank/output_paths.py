from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path

from .errors import OutputPathError


def prepare_output_dir(output_dir: Path) -> Path:
    directory = Path(output_dir).resolve()
    if directory.exists() and not directory.is_dir():
        raise OutputPathError(f"invalid output directory: {directory}")

    if not directory.exists():
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise OutputPathError(f"invalid output directory: {directory}") from exc

    probe_output_dir_writable(directory)
    return directory


def probe_output_dir_writable(directory: Path) -> None:
    probe_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix=".docker-layer-rank-write-probe-",
            suffix=".tmp",
            dir=directory,
            delete=False,
        ) as probe:
            probe_path = Path(probe.name)
            probe.write("ok")
            probe.flush()
    except OSError as exc:
        if probe_path is not None:
            try:
                probe_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise OutputPathError(f"directory is not writable: {directory}") from exc

    try:
        probe_path.unlink(missing_ok=True)
    except OSError as exc:
        raise OutputPathError(f"could not remove temporary write probe: {probe_path}") from exc


def create_report_path(output_dir: Path, now: datetime | None = None) -> Path:
    timestamp = now or datetime.now()
    filename = f"report-{timestamp:%d%m%Y-%H%M%S}.md"
    base_path = output_dir / filename
    if not base_path.exists():
        return base_path

    suffix = 1
    while True:
        candidate = output_dir / f"report-{timestamp:%d%m%Y-%H%M%S}-{suffix}.md"
        if not candidate.exists():
            return candidate
        suffix += 1


def write_report_file(report_path: Path, markdown: str) -> None:
    try:
        with report_path.open("x", encoding="utf-8") as report_file:
            report_file.write(markdown)
    except OSError as exc:
        raise OutputPathError(f"failed to write report: {report_path}") from exc
