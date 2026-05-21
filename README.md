# docker-layer-rank

## What it does

`docker-layer-rank` analyzes a locally available Docker image and generates a Markdown report ranking image history entries by size contribution.

The report includes every Docker history entry, including `0B` metadata-only entries.

## Requirements

- Python 3.10+
- Docker CLI
- Access to a local Docker daemon

## Installation

```bash
pip install .
```

For development dependencies:

```bash
pip install .[dev]
```

## Usage

```bash
docker-layer-rank nginx:latest
docker-layer-rank my-app:dev --output reports
docker-layer-rank my-app:dev --inspect --output reports
python -m docker_layer_rank nginx:latest
```

The image must already exist locally. This tool does not pull images for you.

CLI shape:

```text
docker-layer-rank IMAGE [--output DIR] [--inspect]
```

## Private images

This tool does not authenticate to registries and does not pull images.
For private images, use Docker normally first:

```bash
docker login private-registry.example.com
docker pull private-registry.example.com/team/app:latest
```

Then run:

```bash
docker-layer-rank private-registry.example.com/team/app:latest
```

## Generated reports

Reports are written as Markdown files using the `report-ddMMyyyy-hhmmss.md` filename pattern.

Examples:

```text
report-21052026-153012.md
report-21052026-153012-1.md
```

The report includes these sections:

- `Image Summary`
- `Report Summary`
- `Ranked Layers by Size Contribution`
- `Layer Details`
- `Notes`

When `--inspect` is used, the report also includes:

- `Raw Docker Image Inspect JSON`

## Inspect mode

Use `--inspect` to append raw `docker image inspect` JSON to the Markdown report.

This can expose environment variables, labels, entrypoints, commands, and other image metadata.

Example:

```bash
docker-layer-rank alpine:latest --inspect --output reports
```

## Security notes

Reports may contain image metadata, environment variables, labels, and build commands. Treat generated reports as potentially sensitive, especially for private images.

## Development

The project uses only the Python standard library at runtime.

Tests use `pytest`.

Useful commands:

```bash
python -m compileall docker_layer_rank tests
python -m pytest -q
```

`pytest` is declared in the `dev` extra but may need to be installed in your local environment before running the test suite.

## License

MIT
