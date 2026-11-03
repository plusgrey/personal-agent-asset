# shellcheck shell=bash
# Shared helpers for install.sh and adapters. Bash 3.2 compatible (macOS default).

: "${REPO_ROOT:?REPO_ROOT must be set before sourcing lib/common.sh}"
MODE="${MODE:-link}"        # link | copy
ACTION="${ACTION:-install}" # install | uninstall
DRY_RUN="${DRY_RUN:-0}"
TS="$(date +%Y%m%d%H%M%S)"

if [ -t 1 ]; then
  C_RESET=$'\033[0m'; C_DIM=$'\033[2m'; C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'; C_RED=$'\033[31m'; C_BOLD=$'\033[1m'
else
  C_RESET=; C_DIM=; C_GREEN=; C_YELLOW=; C_RED=; C_BOLD=
fi

info()    { printf '%s\n' "$*"; }
ok()      { printf '  %s✓%s %s\n' "$C_GREEN" "$C_RESET" "$*"; }
skip()    { printf '  %s-%s %s\n' "$C_DIM" "$C_RESET" "$*"; }
warn()    { printf '  %s!%s %s\n' "$C_YELLOW" "$C_RESET" "$*" >&2; }
die()     { printf '%serror:%s %s\n' "$C_RED" "$C_RESET" "$*" >&2; exit 1; }
section() { printf '\n%s==> %s%s\n' "$C_BOLD" "$*" "$C_RESET"; }

# Run a command, or just print it in dry-run mode.
run() {
  if [ "$DRY_RUN" = 1 ]; then
    printf '  %s[dry-run]%s %s\n' "$C_DIM" "$C_RESET" "$*"
  else
    "$@"
  fi
}

# Show paths relative to $HOME for readability.
pretty() {
  case "$1" in
    "$HOME"/*) printf '~/%s' "${1#"$HOME"/}" ;;
    *) printf '%s' "$1" ;;
  esac
}

# True if $1 is a symlink pointing somewhere inside this repo.
is_managed_link() {
  [ -L "$1" ] || return 1
  case "$(readlink "$1")" in
    "$REPO_ROOT"/*) return 0 ;;
    *) return 1 ;;
  esac
}

# install_item <src> <dest>
# Symlink (or copy) a single file/dir. Existing unmanaged files are backed up.
install_item() {
  local src="$1" dest="$2"
  [ -e "$src" ] || { skip "source missing: ${src#$REPO_ROOT/}"; return 0; }

  if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$src" ]; then
    skip "up to date: $(pretty "$dest")"
    return 0
  fi

  if is_managed_link "$dest"; then
    run rm "$dest"
  elif [ -e "$dest" ] || [ -L "$dest" ]; then
    warn "backup: $(pretty "$dest") -> $(pretty "$dest").bak.$TS"
    run mv "$dest" "$dest.bak.$TS"
  fi

  run mkdir -p "$(dirname "$dest")"
  if [ "$MODE" = copy ]; then
    run cp -R "$src" "$dest"
  else
    run ln -s "$src" "$dest"
  fi
  ok "$(pretty "$dest")"
}

# uninstall_item <src> <dest>
# Only removes symlinks that point into this repo; never touches other files.
uninstall_item() {
  local src="$1" dest="$2"
  if is_managed_link "$dest"; then
    run rm "$dest"
    ok "removed $(pretty "$dest")"
  elif [ -e "$dest" ]; then
    skip "not managed (left as is): $(pretty "$dest")"
  fi
}

# sync_item <src> <dest> — install or uninstall depending on $ACTION.
sync_item() {
  if [ "$ACTION" = uninstall ]; then uninstall_item "$@"; else install_item "$@"; fi
}

# sync_children <src_dir> <dest_dir> [glob]
# Sync each child of src_dir into dest_dir (hidden entries like .gitkeep are ignored).
sync_children() {
  local src_dir="$1" dest_dir="$2" glob="${3:-*}" entry name found=0
  [ -d "$src_dir" ] || return 0
  for entry in "$src_dir"/$glob; do
    [ -e "$entry" ] || continue
    name="$(basename "$entry")"
    case "$name" in .*|README.md) continue ;; esac
    found=1
    sync_item "$entry" "$dest_dir/$name"
  done
  [ "$found" = 1 ] || skip "nothing in ${src_dir#$REPO_ROOT/}/"
}

todo() { warn "TODO: $*"; }
