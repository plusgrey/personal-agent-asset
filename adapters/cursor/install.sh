# shellcheck shell=bash
# Cursor adapter. Sourced by install.sh.
# Note: ~/.cursor/skills-cursor is managed by Cursor itself — never write there.
CURSOR_HOME="$HOME/.cursor"

adapter_name()   { echo "Cursor ($(pretty "$CURSOR_HOME"))"; }
adapter_detect() { command -v cursor >/dev/null 2>&1 || [ -d "$CURSOR_HOME" ]; }

adapter_apply() {
  info "skills ($ASSET_LANG)"; sync_children "$SKILLS_ROOT" "$CURSOR_HOME/skills"
  info "commands"; sync_children "$REPO_ROOT/commands" "$CURSOR_HOME/commands" '*.md'
  info "agents";   sync_children "$REPO_ROOT/agents"   "$CURSOR_HOME/agents"   '*.md'
  info "rules";    todo "Cursor user rules live in Settings (not a file); paste rules/AGENTS.md manually or use project .cursor/rules/"
  info "mcp";      todo "render mcp/servers.json into $(pretty "$CURSOR_HOME")/mcp.json"
}
