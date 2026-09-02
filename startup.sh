#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

eval "$(rbenv init - zsh)"

exec bundle exec jekyll serve -l -H localhost --future
