from __future__ import annotations

import re

_SIZE_RE = re.compile(r"^\s*(?P<num>\d+(?:\.\d+)?)\s*(?P<unit>B|kB|KB|MB|GB|TB)\s*$")

_MULTIPLIERS = {
    "B": 1,
    "kB": 1000,
    "KB": 1000,
    "MB": 1000**2,
    "GB": 1000**3,
    "TB": 1000**4,
}

_FORMAT_UNITS = (
    ("TB", 1000**4),
    ("GB", 1000**3),
    ("MB", 1000**2),
    ("kB", 1000),
)


def parse_docker_size(value: str) -> int:
    match = _SIZE_RE.match(value)
    if match is None:
        raise ValueError(f"Unsupported Docker size value: {value!r}")

    number = float(match.group("num"))
    unit = match.group("unit")
    return int(number * _MULTIPLIERS[unit])


def format_bytes(value: int) -> str:
    if value < 1000:
        return f"{value} B"

    for unit, divisor in _FORMAT_UNITS:
        if value >= divisor:
            return f"{value / divisor:.2f} {unit}"

    return f"{value} B"
