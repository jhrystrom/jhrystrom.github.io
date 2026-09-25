# Dependencies live in pyproject.toml; uv.lock keeps a local run and a CI run identical.

# List available commands.
default:
    @just --list

# Install the pre-commit hook that runs `just check` before each commit.
install-hooks:
    uv run pre-commit install

# Build the site into _site/. Pass --future to include scheduled posts.
build *flags:
    uv run build.py {{flags}}

# Build, serve on :8000, and rebuild on change. `just dev --future` previews scheduled posts.
dev *flags: (build flags)
    #!/usr/bin/env bash
    set -euo pipefail
    trap 'kill 0' EXIT
    uvx watchfiles "uv run build.py {{flags}}" content templates static &
    python3 -m http.server 8000 --directory _site

# Format everything in place.
fmt:
    uv run ruff format .
    uv run mdformat content/

# Fail on anything malformed. CI runs exactly this.
check:
    uv run build.py --out .check-site --strict
    uv run ruff format --check .
    uv run ruff check .
    uv run mdformat --check content/
