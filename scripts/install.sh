#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILLS_DIR="${CODEX_HOME}/skills"
SNIPPET_SOURCE="${REPO_ROOT}/templates/AGENTS.crate.md"
AGENTS_FILE="${CODEX_HOME}/AGENTS.md"

append_agents=false

SKILLS=(
  crate
  crate-dev-ops
  crate-pr-ops
  crate-continuity-ledger
  crate-create-context
  crate-create-snapshot
  crate-task-ops
  crate-session-ops
)

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

installed=()
for skill in "${SKILLS[@]}"; do
  src="${REPO_ROOT}/codex/skills/${skill}"
  dst="${SKILLS_DIR}/${skill}"

  if [[ ! -d "$src" ]]; then
    echo "Missing skill directory: ${src}" >&2
    exit 1
  fi

  rm -rf "$dst"
  cp -R "$src" "$dst"
  installed+=("$skill")
done

echo "Installed crate-related skills to ${SKILLS_DIR}:"
for skill in "${installed[@]}"; do
  echo "- ${skill}"
done

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
