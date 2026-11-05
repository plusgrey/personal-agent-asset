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
for lang in en zh_cn; do
  [ -d "$REPO_ROOT/skills/$lang" ] || { err "missing locale directory: skills/$lang"; continue; }
  for dir in "$REPO_ROOT"/skills/$lang/*/; do
    [ -d "$dir" ] || continue
    name="$(basename "$dir")"
    file="$dir/SKILL.md"
    if [ ! -f "$file" ]; then err "$lang/$name: missing SKILL.md"; continue; fi
    [ "$(head -n1 "$file")" = "---" ] || { err "$lang/$name: SKILL.md must start with YAML frontmatter"; continue; }
    fm_name="$(fm_get "$file" name)"
    [ "$fm_name" = "$name" ] || err "$lang/$name: frontmatter name '$fm_name' must match directory name"
    [ -n "$(fm_get "$file" description)" ] || err "$lang/$name: missing description"
    echo "  ✓ $lang/$name"
  done
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

echo "python"
if command -v python3 >/dev/null 2>&1; then
  if ! python3 -m compileall -q "$REPO_ROOT/automations" "$REPO_ROOT/tests"; then
    err "Python syntax check failed"
  else
    echo "  ✓ syntax"
  fi
else
  err "python3 is required for Python syntax checks"
fi

echo "workflow/config"
workflow="$REPO_ROOT/.github/workflows/automations.yml"
[ -f "$workflow" ] || err "missing .github/workflows/automations.yml"
if [ -f "$workflow" ]; then
  grep -q '^name:' "$workflow" || err "workflow missing name"
  grep -q '^on:' "$workflow" || err "workflow missing triggers"
  grep -q 'workflow_dispatch:' "$workflow" || err "workflow missing manual trigger"
  grep -q 'schedule:' "$workflow" || err "workflow missing schedule"
fi
[ -f "$REPO_ROOT/.env.example" ] || err "missing .env.example"
[ -f "$REPO_ROOT/requirements.txt" ] || err "missing requirements.txt"
if command -v ruby >/dev/null 2>&1; then
  ruby -e 'require "yaml"; YAML.load_file(ARGV[0])' "$workflow" >/dev/null 2>&1 || err "invalid workflow YAML"
else
  echo "  - ruby unavailable; skipped YAML parser"
fi
echo "  ✓ files"

if [ "$errors" -gt 0 ]; then
  echo "$errors error(s)" >&2
  exit 1
fi
echo "all good"
