#!/usr/bin/env bash
# One-click installer for personal agent assets.
#   ./install.sh [options] [claude|codex|cursor|trae|all ...]
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
export REPO_ROOT

ALL_TOOLS="claude-code codex cursor trae"

usage() {
  cat <<EOF
Usage: ./install.sh [options] [target ...]

Targets:
  claude | claude-code    Claude Code
  codex                   OpenAI Codex CLI
  cursor                  Cursor
  trae                    Trae
  all                     every tool detected on this machine (default)

Options:
  --copy        copy files instead of symlinking
  --uninstall   remove symlinks created by this repo
  --dry-run     print actions without changing anything
  --force       install even if the tool is not detected
  -h, --help    show this help
EOF
}

MODE=link ACTION=install DRY_RUN=0 FORCE=0
targets=""
while [ $# -gt 0 ]; do
  case "$1" in
    --copy) MODE=copy ;;
    --uninstall) ACTION=uninstall ;;
    --dry-run|-n) DRY_RUN=1 ;;
    --force|-f) FORCE=1 ;;
    -h|--help) usage; exit 0 ;;
    all) targets="$targets all" ;;
    claude|claude-code) targets="$targets claude-code" ;;
    codex|cursor|trae) targets="$targets $1" ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
  shift
done
[ -n "$targets" ] || targets="all"
export MODE ACTION DRY_RUN FORCE

# shellcheck source=lib/common.sh
. "$REPO_ROOT/lib/common.sh"

explicit=1
case " $targets " in *" all "*) targets="$ALL_TOOLS"; explicit=0 ;; esac

info "${C_BOLD}personal-agent-asset${C_RESET}  action=$ACTION mode=$MODE$([ "$DRY_RUN" = 1 ] && echo ' (dry-run)')"

for tool in $targets; do
  adapter="$REPO_ROOT/adapters/$tool/install.sh"
  [ -f "$adapter" ] || { warn "no adapter for $tool"; continue; }
  (
    # Each adapter runs in a subshell and must define:
    #   adapter_name    human-readable name
    #   adapter_detect  return 0 if the tool is present on this machine
    #   adapter_apply   sync assets (uses sync_item / sync_children)
    # shellcheck source=/dev/null
    . "$adapter"
    if ! adapter_detect && [ "$FORCE" != 1 ]; then
      if [ "$explicit" = 1 ]; then
        warn "$(adapter_name) not detected, skipping (use --force to install anyway)"
      else
        skip "$(adapter_name) not detected"
      fi
      exit 0
    fi
    section "$(adapter_name)"
    adapter_apply
  )
done

info ""
info "Done."
