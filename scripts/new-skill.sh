#!/usr/bin/env bash
# Scaffold a new skill: ./scripts/new-skill.sh <skill-name>
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
name="${1:-}"

[ -n "$name" ] || { echo "usage: $0 <skill-name>" >&2; exit 1; }
echo "$name" | grep -Eq '^[a-z0-9]+(-[a-z0-9]+)*$' \
  || { echo "error: name must be lowercase letters/digits separated by hyphens" >&2; exit 1; }

dir="$REPO_ROOT/skills/$name"
[ ! -e "$dir" ] || { echo "error: skills/$name already exists" >&2; exit 1; }

mkdir -p "$dir"
sed "s/{{name}}/$name/g" "$REPO_ROOT/scripts/templates/SKILL.md" > "$dir/SKILL.md"
echo "created skills/$name/SKILL.md"
