from docker_layer_rank.models import ImageSummary, LayerRecord, LayerReport
from docker_layer_rank.report import render_markdown_report


def test_render_markdown_report_includes_required_sections() -> None:
    report = LayerReport(
        image=ImageSummary(
            reference="my-app:latest",
            image_id="sha256:abc123",
            repo_tags=["my-app:latest"],
            repo_digests=["my-app@sha256:def456"],
            created="2026-05-21T10:14:00Z",
            os="linux",
            architecture="amd64",
            size_bytes=423710000,
            virtual_size_bytes=423710000,
            rootfs_layer_count=2,
        ),
        layers=[
            LayerRecord(
                history_index=1,
                layer_id="sha256:b",
                created_since="2 days ago",
                created_at="2026-05-19T13:10:00Z",
                created_by="/bin/sh -c apt-get update && apt-get install -y curl",
                normalized_instruction="RUN apt-get update && apt-get install -y curl",
                instruction_type="RUN",
                size_raw="212MB",
                size_bytes=212000000,
                comment="",
                is_empty=False,
            ),
            LayerRecord(
                history_index=2,
                layer_id="<missing>",
                created_since="2 days ago",
                created_at="2026-05-19T13:11:00Z",
                created_by='CMD ["python", "app.py"]',
                normalized_instruction='CMD ["python", "app.py"]',
                instruction_type="CMD",
                size_raw="0B",
                size_bytes=0,
                comment="",
                is_empty=True,
            ),
        ],
        ranked_layers=[],
        generated_at="2026-05-21 15:30:12",
        history_size_total_bytes=212000000,
        non_empty_count=1,
        empty_count=1,
        include_raw_inspect=True,
        raw_inspect_json=[{"Id": "sha256:abc123"}],
    )
    report = LayerReport(
        image=report.image,
        layers=report.layers,
        ranked_layers=report.layers,
        generated_at=report.generated_at,
        history_size_total_bytes=report.history_size_total_bytes,
        non_empty_count=report.non_empty_count,
        empty_count=report.empty_count,
        include_raw_inspect=report.include_raw_inspect,
        raw_inspect_json=report.raw_inspect_json,
    )

    markdown = render_markdown_report(report)

    assert "# Docker Image Layer Size Report" in markdown
    assert "## Image Summary" in markdown
    assert "## Report Summary" in markdown
    assert "## Ranked Layers by Size Contribution" in markdown
    assert "## Layer Details" in markdown
    assert "## Notes" in markdown
    assert "## Raw Docker Image Inspect JSON" in markdown
    assert "0.00%" in markdown


def test_render_markdown_escapes_pipes() -> None:
    report = LayerReport(
        image=ImageSummary("img", "", [], [], None, None, None, None, None, 0),
        layers=[],
        ranked_layers=[
            LayerRecord(
                history_index=1,
                layer_id="id",
                created_since="now",
                created_at="",
                created_by="",
                normalized_instruction="RUN echo a|b",
                instruction_type="RUN",
                size_raw="1kB",
                size_bytes=1000,
                comment="",
                is_empty=False,
            )
        ],
        generated_at="2026-05-21 15:30:12",
        history_size_total_bytes=1000,
        non_empty_count=1,
        empty_count=0,
        include_raw_inspect=False,
        raw_inspect_json=None,
    )
    markdown = render_markdown_report(report)
    assert "a\\|b" in markdown
