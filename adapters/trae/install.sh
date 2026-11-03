# shellcheck shell=bash
# Trae adapter (stub). Sourced by install.sh.
TRAE_HOME="$HOME/.trae"

adapter_name()   { echo "Trae ($(pretty "$TRAE_HOME"))"; }
adapter_detect() { command -v trae >/dev/null 2>&1 || [ -d "$TRAE_HOME" ]; }

adapter_apply() {
  todo "confirm Trae's user-level skills/rules/MCP paths, then implement like adapters/cursor"
}
