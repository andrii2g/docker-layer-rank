from __future__ import annotations

from .errors import DockerHistoryError
from .models import ImageSummary, LayerRecord, LayerReport
from .sizes import parse_docker_size

_KNOWN_INSTRUCTIONS = {
    "RUN",
    "COPY",
    "ADD",
    "ENV",
    "CMD",
    "ENTRYPOINT",
    "WORKDIR",
    "EXPOSE",
    "LABEL",
    "USER",
    "VOLUME",
    "ARG",
    "ONBUILD",
    "HEALTHCHECK",
    "SHELL",
    "STOPSIGNAL",
}


def build_image_summary(image_ref: str, inspect_item: dict) -> ImageSummary:
    rootfs = inspect_item.get("RootFS")
    rootfs_layers = rootfs.get("Layers") if isinstance(rootfs, dict) else None

    return ImageSummary(
        reference=image_ref,
        image_id=str(inspect_item.get("Id") or ""),
        repo_tags=_as_string_list(inspect_item.get("RepoTags")),
        repo_digests=_as_string_list(inspect_item.get("RepoDigests")),
        created=_as_optional_string(inspect_item.get("Created")),
        os=_as_optional_string(inspect_item.get("Os")),
        architecture=_as_optional_string(inspect_item.get("Architecture")),
        size_bytes=_as_optional_int(inspect_item.get("Size")),
        virtual_size_bytes=_as_optional_int(inspect_item.get("VirtualSize")),
        rootfs_layer_count=len(rootfs_layers) if isinstance(rootfs_layers, list) else 0,
    )


def build_layer_records(history_entries: list[dict]) -> list[LayerRecord]:
    records: list[LayerRecord] = []
    for index, entry in enumerate(history_entries, start=1):
        size_raw = str(entry.get("Size", ""))
        try:
            size_bytes = parse_docker_size(size_raw)
        except ValueError as exc:
            raise DockerHistoryError("failed to parse Docker image history output") from exc

        created_by = str(entry.get("CreatedBy") or "")
        normalized = normalize_created_by(created_by)

        records.append(
            LayerRecord(
                history_index=index,
                layer_id=str(entry.get("ID") or "<missing>"),
                created_since=str(entry.get("CreatedSince") or ""),
                created_at=str(entry.get("CreatedAt") or ""),
                created_by=created_by,
                normalized_instruction=normalized,
                instruction_type=detect_instruction_type(normalized, created_by),
                size_raw=size_raw,
                size_bytes=size_bytes,
                comment=str(entry.get("Comment") or ""),
                is_empty=size_bytes == 0,
            )
        )
    return records


def build_layer_report(
    *,
    image: ImageSummary,
    layers: list[LayerRecord],
    raw_inspect_json: list[dict] | None,
) -> LayerReport:
    history_size_total_bytes = sum(layer.size_bytes for layer in layers)
    ranked_layers = sorted(layers, key=lambda layer: (-layer.size_bytes, layer.history_index))
    return LayerReport(
        image=image,
        layers=layers,
        ranked_layers=ranked_layers,
        generated_at="",
        history_size_total_bytes=history_size_total_bytes,
        non_empty_count=sum(1 for layer in layers if not layer.is_empty),
        empty_count=sum(1 for layer in layers if layer.is_empty),
        include_raw_inspect=raw_inspect_json is not None,
        raw_inspect_json=raw_inspect_json,
    )


def normalize_created_by(created_by: str) -> str:
    text = " ".join(created_by.replace("\n", " ").split())
    if text.endswith("# buildkit"):
        text = text[: -len("# buildkit")].rstrip()

    if text.startswith("/bin/sh -c #(nop) "):
        return text[len("/bin/sh -c #(nop) ") :].strip()

    if text.startswith("/bin/sh -c "):
        command = text[len("/bin/sh -c ") :].strip()
        return f"RUN {command}"

    if text.startswith("RUN /bin/sh -c "):
        command = text[len("RUN /bin/sh -c ") :].strip()
        return f"RUN {command}"

    return text


def detect_instruction_type(normalized_instruction: str, created_by: str) -> str:
    first_token = normalized_instruction.split(" ", 1)[0] if normalized_instruction else ""
    if first_token in _KNOWN_INSTRUCTIONS:
        return first_token
    if "/bin/sh -c" in created_by:
        return "RUN"
    return "UNKNOWN"


def _as_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _as_optional_string(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _as_optional_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
