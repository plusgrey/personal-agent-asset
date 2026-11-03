#!/usr/bin/env bash
# Validate repository assets. Exit non-zero on any error.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
errors=0
err() { echo "  ✗ $*" >&2; errors=$((errors + 1)); }

# Print the value of a top-level frontmatter key from a Markdown file.
fm_get() {
  awk -v key="$2" '
    NR == 1 && $0 != "---" { exit }
    NR > 1 && $0 == "---" { exit }
    NR > 1 && index($0, key ":") == 1 { sub("^" key ":[ ]*", ""); print; exit }
  ' "$1"
}

echo "skills/"
for dir in "$REPO_ROOT"/skills/*/; do
  [ -d "$dir" ] || continue
  name="$(basename "$dir")"
  file="$dir/SKILL.md"
  if [ ! -f "$file" ]; then err "$name: missing SKILL.md"; continue; fi
  [ "$(head -n1 "$file")" = "---" ] || { err "$name: SKILL.md must start with YAML frontmatter"; continue; }
  fm_name="$(fm_get "$file" name)"
  [ "$fm_name" = "$name" ] || err "$name: frontmatter name '$fm_name' must match directory name"
  [ -n "$(fm_get "$file" description)" ] || err "$name: missing description"
  echo "  ✓ $name"
done

echo "agents/"
for file in "$REPO_ROOT"/agents/*.md; do
  [ -f "$file" ] || continue
  base="$(basename "$file" .md)"
  [ -n "$(fm_get "$file" description)" ] || err "$base: missing description"
  echo "  ✓ $base"
done

echo "shell scripts"
for f in "$REPO_ROOT"/install.sh "$REPO_ROOT"/lib/*.sh "$REPO_ROOT"/adapters/*/install.sh "$REPO_ROOT"/scripts/*.sh; do
  [ -f "$f" ] || continue
  bash -n "$f" || err "syntax error: ${f#$REPO_ROOT/}"
done
echo "  ✓ syntax"

if [ "$errors" -gt 0 ]; then
  echo "$errors error(s)" >&2
  exit 1
fi
echo "all good"
