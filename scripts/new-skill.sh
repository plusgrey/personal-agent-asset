#!/usr/bin/env bash
# Scaffold a new skill: ./scripts/new-skill.sh <skill-name> [en|zh_cn]
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
name="${1:-}"
lang="${2:-en}"

[ -n "$name" ] || { echo "usage: $0 <skill-name> [en|zh_cn]" >&2; exit 1; }
echo "$name" | grep -Eq '^[a-z0-9]+(-[a-z0-9]+)*$' \
  || { echo "error: name must be lowercase letters/digits separated by hyphens" >&2; exit 1; }
case "$lang" in
  en|zh_cn) ;;
  *) echo "error: language must be en or zh_cn" >&2; exit 1 ;;
esac

dir="$REPO_ROOT/skills/$lang/$name"
[ ! -e "$dir" ] || { echo "error: skills/$name already exists" >&2; exit 1; }

mkdir -p "$dir"
sed "s/{{name}}/$name/g" "$REPO_ROOT/scripts/templates/SKILL.md" > "$dir/SKILL.md"
echo "created skills/$lang/$name/SKILL.md"
