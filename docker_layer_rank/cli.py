from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .app import generate_report_for_image
from .errors import (
    DockerHistoryError,
    DockerInspectError,
    DockerUnavailableError,
    ImageNotFoundError,
    OutputPathError,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docker-layer-rank",
        description=(
            "Analyze a locally available Docker image and generate a Markdown report "
            "ranking all image history entries by size contribution."
        ),
    )
    parser.add_argument(
        "image",
        metavar="IMAGE",
        help="Docker image name, tag, ID, or digest. The image must already exist locally.",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="DIR",
        default=".",
        help="Directory where the Markdown report will be generated. Defaults to current directory.",
    )
    parser.add_argument(
        "--inspect",
        action="store_true",
        help="Append raw docker image inspect JSON to the Markdown report.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        report_path = generate_report_for_image(
            image=args.image,
            output_dir=Path(args.output),
            include_inspect=args.inspect,
        )
    except DockerUnavailableError as exc:
        if exc.reason == "cli_missing":
            print("Error: Docker CLI was not found.", file=sys.stderr)
            print("Install Docker and make sure the `docker` command is available in PATH.", file=sys.stderr)
        else:
            print("Error: Docker daemon is not available.", file=sys.stderr)
            print("Start Docker and try again.", file=sys.stderr)
        return 1
    except ImageNotFoundError as exc:
        print(f"Error: image not found locally: {exc.image}", file=sys.stderr)
        print("", file=sys.stderr)
        print("This tool analyzes local Docker images only.", file=sys.stderr)
        print("Pull the image first.", file=sys.stderr)
        return 2
    except OutputPathError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 3
    except DockerHistoryError:
        print("Error: failed to read or parse Docker image history output.", file=sys.stderr)
        return 4
    except DockerInspectError as exc:
        print("Error: Docker image inspect failed.", file=sys.stderr)
        if str(exc):
            print(f"Reason: {exc}", file=sys.stderr)
        return 1

    print(f"Report generated: {report_path}")
    return 0
