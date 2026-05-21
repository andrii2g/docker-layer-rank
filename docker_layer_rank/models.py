from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImageSummary:
    reference: str
    image_id: str
    repo_tags: list[str]
    repo_digests: list[str]
    created: str | None
    os: str | None
    architecture: str | None
    size_bytes: int | None
    virtual_size_bytes: int | None
    rootfs_layer_count: int


@dataclass(frozen=True)
class LayerRecord:
    history_index: int
    layer_id: str
    created_since: str
    created_at: str
    created_by: str
    normalized_instruction: str
    instruction_type: str
    size_raw: str
    size_bytes: int
    comment: str
    is_empty: bool


@dataclass(frozen=True)
class LayerReport:
    image: ImageSummary
    layers: list[LayerRecord]
    ranked_layers: list[LayerRecord]
    generated_at: str
    history_size_total_bytes: int
    non_empty_count: int
    empty_count: int
    include_raw_inspect: bool
    raw_inspect_json: list[dict] | None
