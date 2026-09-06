# List available commands.
default:
    @just --list

# Build the site into _site/.
build:
    uv run build.py

# Build, serve on :8000, and rebuild whenever content or templates change.
dev: build
    #!/usr/bin/env bash
    set -euo pipefail
    trap 'kill 0' EXIT
    uvx watchfiles "uv run build.py" content templates static &
    python3 -m http.server 8000 --directory _site

# Format everything in place.
fmt:
    uvx ruff format .
    uvx --with mdformat-frontmatter mdformat content/

# Fail on anything malformed. CI runs exactly this.
check:
    uv run build.py --out .check-site --strict
    uvx ruff format --check .
    uvx ruff check .
    uvx --with mdformat-frontmatter mdformat --check content/

# Check that outbound links still resolve. Slow, network-dependent, not part of `check`.
check-links: build
    uvx --from lychee-bin lychee --no-progress _site
