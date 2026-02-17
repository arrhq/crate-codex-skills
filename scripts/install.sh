#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILLS_DIR="${CODEX_HOME}/skills"
TARGET_SKILL_DIR="${SKILLS_DIR}/crate"
SNIPPET_SOURCE="${REPO_ROOT}/templates/AGENTS.crate.md"
AGENTS_FILE="${CODEX_HOME}/AGENTS.md"

append_agents=false

usage() {
  cat <<USAGE
Usage:
  ./scripts/install.sh [--append-agents]

Options:
  --append-agents   Append templates/AGENTS.crate.md to ~/.codex/AGENTS.md (idempotent).
USAGE
}

for arg in "$@"; do
  case "$arg" in
    --append-agents)
      append_agents=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      usage
      exit 1
      ;;
  esac
done

mkdir -p "$SKILLS_DIR"
rm -rf "$TARGET_SKILL_DIR"
cp -R "${REPO_ROOT}/codex/skills/crate" "$TARGET_SKILL_DIR"

echo "Installed skill: ${TARGET_SKILL_DIR}"

if [[ "$append_agents" == true ]]; then
  mkdir -p "$CODEX_HOME"
  touch "$AGENTS_FILE"

  begin_marker="<!-- crate-codex-skills:begin -->"
  end_marker="<!-- crate-codex-skills:end -->"

  if grep -q "$begin_marker" "$AGENTS_FILE"; then
    echo "AGENTS snippet already exists: ${AGENTS_FILE}"
  else
    {
      echo
      echo "$begin_marker"
      cat "$SNIPPET_SOURCE"
      echo "$end_marker"
    } >> "$AGENTS_FILE"
    echo "Appended AGENTS snippet: ${AGENTS_FILE}"
  fi
fi

cat <<NEXT

Next steps:
1. Update ~/.codex/config.json with examples/mcp-config.json
2. Restart Codex
3. Verify MCP calls: list_project_tasks, get_session_continuity, upsert_session_continuity
NEXT
