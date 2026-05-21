from __future__ import annotations

import json
from datetime import datetime

from .models import LayerRecord, LayerReport
from .sizes import format_bytes


def layer_share_percent(layer: LayerRecord, history_size_total_bytes: int) -> float:
    if history_size_total_bytes <= 0:
        return 0.0
    return (layer.size_bytes / history_size_total_bytes) * 100


def render_markdown_report(report: LayerReport) -> str:
    generated_at = report.generated_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# Docker Image Layer Size Report",
        "",
        f"Generated at: {generated_at}",
        "",
        f"Image reference: `{_escape_inline(report.image.reference)}`",
        "",
        "## Image Summary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Image reference | `{_escape_inline(report.image.reference)}` |",
        f"| Image ID | `{_escape_inline(report.image.image_id)}` |",
        f"| OS / Architecture | `{_escape_inline(_join_os_arch(report.image.os, report.image.architecture))}` |",
        f"| Created | `{_escape_inline(report.image.created or '')}` |",
        f"| Repo tags | `{_escape_inline(', '.join(report.image.repo_tags))}` |",
        f"| Repo digests | `{_escape_inline(', '.join(report.image.repo_digests))}` |",
        f"| Inspect size | `{_escape_inline(_format_optional_bytes(report.image.size_bytes))}` |",
        f"| Virtual size | `{_escape_inline(_format_optional_bytes(report.image.virtual_size_bytes))}` |",
        f"| RootFS layer count | `{report.image.rootfs_layer_count}` |",
        "",
        "## Report Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Docker history entries | {len(report.layers)} |",
        f"| Non-empty entries | {report.non_empty_count} |",
        f"| Empty / metadata-only entries | {report.empty_count} |",
        f"| Parsed history size total | {format_bytes(report.history_size_total_bytes)} |",
        f"| Largest entry size | {_largest_size(report)} |",
        f"| Largest entry share | {_largest_share(report):.2f}% |",
        "",
        "## Ranked Layers by Size Contribution",
        "",
        "| Rank | History # | Layer ID | Size | Share | Empty | Instruction | Created |",
        "|---:|---:|---|---:|---:|---|---|---|",
    ]

    for rank, layer in enumerate(report.ranked_layers, start=1):
        lines.append(
            "| {rank} | {history} | `{layer_id}` | {size} | {share:.2f}% | {empty} | {instruction} | {created} |".format(
                rank=rank,
                history=layer.history_index,
                layer_id=_escape_inline(layer.layer_id),
                size=format_bytes(layer.size_bytes),
                share=layer_share_percent(layer, report.history_size_total_bytes),
                empty="yes" if layer.is_empty else "no",
                instruction=_escape_table_value(layer.normalized_instruction),
                created=_escape_table_value(layer.created_since),
            )
        )

    lines.extend(["", "## Layer Details", ""])

    for rank, layer in enumerate(report.ranked_layers, start=1):
        lines.extend(
            [
                f"### Rank {rank} - {format_bytes(layer.size_bytes)} - {layer_share_percent(layer, report.history_size_total_bytes):.2f}%",
                "",
                "| Field | Value |",
                "|---|---|",
                f"| History position | `{layer.history_index}` |",
                f"| Layer ID | `{_escape_inline(layer.layer_id)}` |",
                f"| Instruction type | `{_escape_inline(layer.instruction_type)}` |",
                f"| Empty layer | `{'yes' if layer.is_empty else 'no'}` |",
                f"| Created since | `{_escape_inline(layer.created_since)}` |",
                f"| Created at | `{_escape_inline(layer.created_at)}` |",
                f"| Comment | `{_escape_inline(layer.comment)}` |",
                "",
                "Created by:",
                "",
                "```text",
                layer.created_by,
                "```",
                "",
                "Normalized instruction:",
                "",
                "```text",
                layer.normalized_instruction,
                "```",
                "",
            ]
        )

    lines.extend(
        [
            "## Notes",
            "",
            "- This report uses local Docker CLI data only.",
            "- The image must already exist in the local Docker daemon.",
            "- No registry credentials are read, stored, or transmitted by this tool.",
            "- Size contribution is based on Docker history output and may be rounded by Docker CLI display behavior.",
            "- `0B` entries are usually metadata-only Dockerfile instructions such as `CMD`, `ENV`, `LABEL`, `WORKDIR`, or `ENTRYPOINT`.",
        ]
    )

    if report.include_raw_inspect and report.raw_inspect_json is not None:
        lines.extend(
            [
                "",
                "## Raw Docker Image Inspect JSON",
                "",
                "```json",
                json.dumps(report.raw_inspect_json, indent=2, sort_keys=True),
                "```",
            ]
        )

    return "\n".join(lines) + "\n"


def _escape_inline(value: str) -> str:
    return value.replace("`", "\\`")


def _escape_table_value(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _join_os_arch(os_name: str | None, architecture: str | None) -> str:
    if os_name and architecture:
        return f"{os_name}/{architecture}"
    return os_name or architecture or ""


def _format_optional_bytes(value: int | None) -> str:
    if value is None:
        return ""
    return format_bytes(value)


def _largest_size(report: LayerReport) -> str:
    if not report.ranked_layers:
        return "0 B"
    return format_bytes(report.ranked_layers[0].size_bytes)


def _largest_share(report: LayerReport) -> float:
    if not report.ranked_layers:
        return 0.0
    return layer_share_percent(report.ranked_layers[0], report.history_size_total_bytes)
