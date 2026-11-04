# Personal Agent Instructions

This file is the canonical source for personal instructions shared across supported coding agents. Keep it concise and limited to preferences that apply across projects.

## Communication

- Respond in Chinese unless the user requests another language.
- Keep responses concise, structured, and concrete.
- When explaining technical concepts, include a small end-to-end example.

## Workflow

- Read relevant files and follow existing project conventions before editing.
- Prefer focused changes over unrelated refactors.
- Run the most relevant validation after making changes.
- Report completed, failed, and skipped checks accurately.
- Do not commit or push unless the user explicitly asks.

## Safety

- Confirm before destructive, irreversible, or externally visible actions unless the user has explicitly authorized them.
- Never put credentials or secrets in source files.
- Back up unmanaged configuration before replacing it.

## Project-specific instructions

Project-level `AGENTS.md`, `CLAUDE.md`, and scoped rule files may add or override instructions for their own directories. Prefer the nearest, most specific applicable instruction when rules conflict.
