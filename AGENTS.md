# AGENTS.md

This repository contains a minimal Python CLI wrapper around the official MyShows API.

The primary consumer is an external agent running on a VPS, such as Hermes or OpenClaw. The project should stay small, predictable, and easy for an agent to call with low prompt/context cost.

## Core goals

- Keep the CLI contract stable.
- Prefer machine-readable output over rich terminal UX.
- Add the smallest amount of code needed for each new user-facing capability.
- Keep MyShows API details inside the codebase and docs, not in agent prompts.

## Source of truth

- Human-facing project overview: `README.md`
- Agent-facing CLI contract: `docs/agent-cli.md`
- Historical skill notes / lightweight summary: `docs/skill.md`

When these documents disagree, treat `docs/agent-cli.md` as the canonical agent contract and update the others to match.

## Architecture guidelines

- `src/myshows_cli/cli.py`: argument parsing, output formatting, exit codes
- `src/myshows_cli/service.py`: use-case logic
- `src/myshows_cli/client.py`: API transport and JSON-RPC/OAuth interaction
- `src/myshows_cli/config.py`: env and `.env` loading

Keep responsibilities narrow. Avoid adding heavy abstractions until there is a clear second use case that needs them.

## CLI rules

- Prefer `--json` for agent usage.
- Preserve output shape compatibility where practical.
- Return exit code `0` on success and `1` on operational errors.
- Do not require HTML scraping if the official API can answer the request.
- If the API is eventually consistent after a write, document that behavior instead of hiding it with surprising retries.
- Favor safe fuzzy resolution for show names: accept small typos, reject weak matches.

## Testing rules

- Use TDD for user-facing functionality.
- Add or update tests before or alongside behavior changes.
- Cover both service behavior and CLI behavior for every new command.
- Keep tests deterministic and small.

## Dependency rules

- Prefer the standard library unless a dependency clearly reduces complexity.
- New dependencies must have a narrow purpose.
- Avoid adding frameworks or rich terminal libraries unless they materially improve the agent workflow.

## Documentation update policy

When adding or changing user-facing functionality, review and update these files as needed in the same change:

- `README.md`
- `CHANGELOG.md` for release-worthy user-visible changes
- `docs/agent-cli.md`
- `docs/skill.md`
- `AGENTS.md` if project conventions or maintenance rules changed

At minimum, every new CLI command or flag should be reflected in:

- command examples
- expected JSON shape or behavior notes
- any new operational caveats

## Operational notes

- The CLI supports `.env` with `email` and `password`.
- If explicit `MYSHOWS_CLIENT_ID` and `MYSHOWS_CLIENT_SECRET` are missing, the code falls back to `apidoc/apidoc`.
- MyShows may show short write-to-read delays after mutation calls. Treat this as an API consistency nuance, not necessarily a local bug.

## Change checklist

Before considering work complete:

- run tests
- run lint
- verify package build
- update docs for any CLI/API contract changes
- update `CHANGELOG.md` and GitHub Release notes when preparing a release
- avoid committing secrets or `.env`
