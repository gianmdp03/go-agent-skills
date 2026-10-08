#!/usr/bin/env bash
# Non-destructive installer for Antigravity, macOS/Linux/WSL. No existing skill is overwritten.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SCOPE="${1:-global}"
case "$SCOPE" in
  global) TARGET="${HOME}/.gemini/config/skills" ;;
  workspace) TARGET="${2:-$PWD}/.agents/skills" ;;
  *) echo 'Usage: ./install.sh [global | workspace /path/to/workspace]' >&2; exit 2 ;;
esac
for NAME in go-backend spring-to-go; do
  [[ -f "$ROOT/$NAME/SKILL.md" ]] || { echo "Missing $ROOT/$NAME/SKILL.md" >&2; exit 2; }
  [[ ! -e "$TARGET/$NAME" ]] || { echo "Already installed: $TARGET/$NAME; refusing to overwrite" >&2; exit 2; }
done
mkdir -p "$TARGET"
for NAME in go-backend spring-to-go; do
  cp -R -- "$ROOT/$NAME" "$TARGET/$NAME"
  echo "Installed: $TARGET/$NAME"
done
