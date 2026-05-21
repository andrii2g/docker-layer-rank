from docker_layer_rank.cli import build_parser


def test_cli_args_parsing() -> None:
    parser = build_parser()
    args = parser.parse_args(["image:latest", "--output", "reports", "--inspect"])

    assert args.image == "image:latest"
    assert args.output == "reports"
    assert args.inspect is True


def test_cli_requires_image() -> None:
    parser = build_parser()
    try:
        parser.parse_args([])
    except SystemExit:
        pass
    else:
        raise AssertionError("Expected SystemExit when IMAGE is missing")
