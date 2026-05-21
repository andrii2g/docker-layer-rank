from datetime import datetime
from pathlib import Path

from docker_layer_rank.errors import OutputPathError
from docker_layer_rank.output_paths import create_report_path, prepare_output_dir, write_report_file


def test_prepare_output_dir_creates_missing_directory(tmp_path: Path) -> None:
    output_dir = tmp_path / "reports"
    prepared = prepare_output_dir(output_dir)
    assert prepared.exists()
    assert prepared.is_dir()
    assert not list(prepared.glob(".docker-layer-rank-write-probe-*.tmp"))


def test_prepare_output_dir_rejects_file_path(tmp_path: Path) -> None:
    file_path = tmp_path / "not-a-dir"
    file_path.write_text("x", encoding="utf-8")
    try:
        prepare_output_dir(file_path)
    except OutputPathError:
        pass
    else:
        raise AssertionError("Expected OutputPathError")


def test_create_report_path_adds_suffixes(tmp_path: Path) -> None:
    now = datetime(2026, 5, 21, 15, 30, 12)
    base = tmp_path / "report-21052026-153012.md"
    base.write_text("", encoding="utf-8")
    next_path = create_report_path(tmp_path, now)
    assert next_path.name == "report-21052026-153012-1.md"


def test_write_report_file_writes_markdown(tmp_path: Path) -> None:
    report_path = tmp_path / "report.md"
    write_report_file(report_path, "# test\n")
    assert report_path.read_text(encoding="utf-8") == "# test\n"
