#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="${SCRIPT_DIR}/replay_outbox.py"

if [[ ! -f "${SCRIPT_PATH}" ]]; then
  echo "replay script not found: ${SCRIPT_PATH}" >&2
  exit 1
fi

if command -v python3.12 >/dev/null 2>&1; then
  exec python3.12 "${SCRIPT_PATH}" "$@"
fi

if command -v python3 >/dev/null 2>&1; then
  if python3 -c "import tomllib" >/dev/null 2>&1; then
    exec python3 "${SCRIPT_PATH}" "$@"
  fi
fi

if command -v uv >/dev/null 2>&1; then
  exec uv run --python 3.12 "${SCRIPT_PATH}" "$@"
fi

echo "python3.12 (or python3.11+) is required. Install it or install uv." >&2
exit 1
