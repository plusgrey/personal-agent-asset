# shellcheck shell=bash
# OpenAI Codex CLI adapter. Sourced by install.sh.
CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"

adapter_name()   { echo "Codex ($(pretty "$CODEX_DIR"))"; }
adapter_detect() { command -v codex >/dev/null 2>&1 || [ -d "$CODEX_DIR" ]; }

adapter_apply() {
  info "skills";   sync_children "$REPO_ROOT/skills"   "$CODEX_DIR/skills"
  info "commands"; sync_children "$REPO_ROOT/commands" "$CODEX_DIR/prompts" '*.md'
  info "agents";   skip "subagents not supported by Codex"
  info "rules";    sync_item     "$REPO_ROOT/rules/AGENTS.md" "$CODEX_DIR/AGENTS.md"
  info "mcp";      todo "render mcp/servers.json into [mcp_servers] of $(pretty "$CODEX_DIR")/config.toml"
}
