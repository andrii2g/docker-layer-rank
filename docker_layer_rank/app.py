from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .docker_cli import get_image_history, inspect_image
from .parser import build_image_summary, build_layer_records, build_layer_report
from .output_paths import create_report_path, prepare_output_dir, write_report_file
from .report import render_markdown_report


def generate_report_for_image(image: str, output_dir: Path, include_inspect: bool) -> Path:
    resolved_output_dir = prepare_output_dir(output_dir)

    inspect_data = inspect_image(image)
    history_data = get_image_history(image)
    image_summary = build_image_summary(image, inspect_data[0])
    layers = build_layer_records(history_data)
    report = build_layer_report(
        image=image_summary,
        layers=layers,
        raw_inspect_json=inspect_data if include_inspect else None,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    markdown = render_markdown_report(report)
    report_path = create_report_path(resolved_output_dir)
    write_report_file(report_path, markdown)
    return report_path
