from docker_layer_rank.sizes import format_bytes, parse_docker_size


def test_parse_docker_size_valid_values() -> None:
    assert parse_docker_size("0B") == 0
    assert parse_docker_size("0 B") == 0
    assert parse_docker_size("1B") == 1
    assert parse_docker_size("1kB") == 1000
    assert parse_docker_size("1.5kB") == 1500
    assert parse_docker_size("12.4MB") == 12400000
    assert parse_docker_size("1.2GB") == 1200000000
    assert parse_docker_size("2 TB") == 2000000000000


def test_parse_docker_size_invalid_values() -> None:
    invalid_values = ["", " ", "N/A", "-", "--", "unknown", "0", "12", "12MiB", "abc"]
    for value in invalid_values:
        try:
            parse_docker_size(value)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Expected ValueError for {value!r}")


def test_format_bytes() -> None:
    assert format_bytes(0) == "0 B"
    assert format_bytes(999) == "999 B"
    assert format_bytes(1000) == "1.00 kB"
    assert format_bytes(1000000) == "1.00 MB"
