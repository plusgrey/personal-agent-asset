# shellcheck shell=bash
# Claude Code adapter. Sourced by install.sh.
CLAUDE_HOME="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"

adapter_name()   { echo "Claude Code ($(pretty "$CLAUDE_HOME"))"; }
adapter_detect() { command -v claude >/dev/null 2>&1 || [ -d "$CLAUDE_HOME" ]; }

adapter_apply() {
  info "skills";   sync_children "$REPO_ROOT/skills"   "$CLAUDE_HOME/skills"
  info "commands"; sync_children "$REPO_ROOT/commands" "$CLAUDE_HOME/commands" '*.md'
  info "agents";   sync_children "$REPO_ROOT/agents"   "$CLAUDE_HOME/agents"   '*.md'
  info "rules";    sync_item     "$REPO_ROOT/rules/AGENTS.md" "$CLAUDE_HOME/CLAUDE.md"
  info "mcp";      todo "merge mcp/servers.json via 'claude mcp add' / ~/.claude.json"
  info "hooks";    todo "merge hooks/ into $(pretty "$CLAUDE_HOME")/settings.json"
}
