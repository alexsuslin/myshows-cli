# Changelog

All notable changes to this project should be documented in this file.

## Unreleased

## v0.2.0 - 2026-06-25

Title-based episode marking release for agent workflows.

### Added

- Added `mark-title` to mark a watched episode by title or title context instead of requiring an `sXXeYY` code.
- Added safe ambiguous episode handling with JSON `candidates` so agents can ask for clarification instead of guessing.

## v0.1.1 - 2026-06-18

Configuration quality-of-life release for agent and VPS usage.

### Added

- Added XDG-style config loading from `$XDG_CONFIG_HOME/myshows-cli/.env`.
- Added fallback config loading from `~/.config/myshows-cli/.env`.
- Added `MYSHOWS_CLI_EMAIL` and `MYSHOWS_CLI_PASSWORD` as aliases for login credentials.

## v0.1.0 - 2026-06-18

First public release of `myshows-cli`.

### Highlights

- Added an agent-friendly Python CLI around the official MyShows API v2.
- Added stable JSON output for low-context agent usage.
- Published the first GitHub Actions CI workflow for syntax, lint, tests, and build checks.
- Added maintainer and agent documentation for long-term project upkeep.

### Added

- `start` command to mark a show as currently watched.
- `progress` command to inspect last watched, next episode, and remaining episodes.
- `mark` command to mark an episode as watched and optionally rate it.
- `watching` command to list currently watched shows sorted by popularity or title.
- `remaining` command to count regular episodes left to watch.
- `.env` support with compact `email/password` credentials.
- Fallback OAuth app credentials via `apidoc/apidoc` when explicit app credentials are not provided.
- Fuzzy show-name handling for small user typos.
- Safe `Show not found` behavior for weak matches instead of arbitrary selection.

### Testing

- Added TDD coverage for CLI output, config loading, API client headers, show resolution, and service behavior.
- Added PR CI checks for:
  - Python syntax compilation
  - Ruff linting
  - pytest
  - package build

### Documentation

- Added `AGENTS.md` with project conventions and maintenance rules.
- Added `docs/agent-cli.md` as the canonical agent usage guide.
- Added `docs/skill.md` as a lightweight agent-facing pointer.
- Updated `README.md` with badges, install/dev guidance, and command examples.

### Notes

- MyShows writes may be visible with a short delay on immediate follow-up reads.
- The first public GitHub release is tagged as `v0.1.0`.
