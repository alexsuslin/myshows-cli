# Agent Skill Notes

Use [docs/agent-cli.md](agent-cli.md) as the canonical guide for agent usage.

This file stays as a short pointer for skill-level discovery:

- use `myshows start "Show Name" --json` when the user says they started a show
- use `myshows mark-title "Show Name" "Episode title" --json` when the user names an episode but not an episode code
- prefer `myshows ... --json`
- keep MyShows API details inside the CLI, not in prompts
- update `docs/agent-cli.md`, `README.md`, and `AGENTS.md` whenever agent-facing behavior changes
