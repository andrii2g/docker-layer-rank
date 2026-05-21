from __future__ import annotations

from pathlib import Path

from .docker_cli import get_image_history, inspect_image
from .output_paths import create_report_path, prepare_output_dir, write_report_file


def generate_report_for_image(image: str, output_dir: Path, include_inspect: bool) -> Path:
    resolved_output_dir = prepare_output_dir(output_dir)

    inspect_data = inspect_image(image)
    history_data = get_image_history(image)

    del include_inspect
    del inspect_data
    del history_data

    report_path = create_report_path(resolved_output_dir)
    write_report_file(report_path, "")
    return report_path
