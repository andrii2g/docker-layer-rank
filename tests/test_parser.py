from docker_layer_rank.errors import DockerHistoryError
from docker_layer_rank.parser import (
    build_image_summary,
    build_layer_records,
    build_layer_report,
    detect_instruction_type,
    normalize_created_by,
)


def test_build_image_summary() -> None:
    summary = build_image_summary(
        "alpine:latest",
        {
            "Id": "sha256:abc",
            "RepoTags": ["alpine:latest"],
            "RepoDigests": ["alpine@sha256:def"],
            "Created": "2026-05-21T10:14:00Z",
            "Os": "linux",
            "Architecture": "amd64",
            "Size": 1234,
            "VirtualSize": 5678,
            "RootFS": {"Layers": ["a", "b"]},
        },
    )

    assert summary.reference == "alpine:latest"
    assert summary.image_id == "sha256:abc"
    assert summary.rootfs_layer_count == 2


def test_build_layer_records_and_report() -> None:
    entries = [
        {
            "ID": "sha256:a",
            "CreatedSince": "1 hour ago",
            "CreatedAt": "2026-05-21T10:00:00Z",
            "CreatedBy": '/bin/sh -c #(nop)  CMD ["python"]',
            "Size": "0B",
            "Comment": "",
        },
        {
            "ID": "sha256:b",
            "CreatedSince": "1 hour ago",
            "CreatedAt": "2026-05-21T09:59:00Z",
            "CreatedBy": "/bin/sh -c pip install -r requirements.txt",
            "Size": "120MB",
            "Comment": "",
        },
        {
            "ID": "<missing>",
            "CreatedSince": "1 hour ago",
            "CreatedAt": "2026-05-21T09:58:00Z",
            "CreatedBy": "COPY . /app # buildkit",
            "Size": "80MB",
            "Comment": "buildkit.dockerfile.v0",
        },
    ]
    layers = build_layer_records(entries)
    report = build_layer_report(image=build_image_summary("img", {}), layers=layers, raw_inspect_json=None)

    assert layers[0].history_index == 1
    assert layers[0].is_empty is True
    assert layers[1].instruction_type == "RUN"
    assert layers[2].normalized_instruction == "COPY . /app"
    assert report.ranked_layers[0].size_bytes == 120000000


def test_invalid_size_raises_docker_history_error() -> None:
    try:
        build_layer_records(
            [
                {
                    "ID": "sha256:a",
                    "CreatedSince": "1 hour ago",
                    "CreatedAt": "2026-05-21T10:00:00Z",
                    "CreatedBy": "RUN bad",
                    "Size": "abc",
                    "Comment": "",
                }
            ]
        )
    except DockerHistoryError:
        pass
    else:
        raise AssertionError("Expected DockerHistoryError")


def test_normalize_and_detect() -> None:
    assert normalize_created_by("/bin/sh -c #(nop)  ENV NODE_VERSION=20.11.1") == "ENV NODE_VERSION=20.11.1"
    assert normalize_created_by("RUN /bin/sh -c pip install -r requirements.txt # buildkit") == "RUN pip install -r requirements.txt"
    assert detect_instruction_type("COPY . /app", "COPY . /app # buildkit") == "COPY"
    assert detect_instruction_type("", "/bin/sh -c echo hi") == "RUN"
