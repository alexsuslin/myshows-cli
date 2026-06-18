# myshows-agent-cli

[![CI](https://github.com/alexsuslin/myshows-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/alexsuslin/myshows-cli/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/alexsuslin/myshows-cli)](https://github.com/alexsuslin/myshows-cli/releases)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://github.com/alexsuslin/myshows-cli)
[![License](https://img.shields.io/github/license/alexsuslin/myshows-cli)](LICENSE)

Minimal Python CLI wrapper around the official MyShows API for agent workflows.

The project is intentionally small. The first release focuses on four stable commands that are cheap for an agent to call and cheap to parse:

- `start`
- `progress`
- `mark`
- `watching`
- `remaining`

## Why this shape

The main use case is a remote agent such as Hermes or OpenClaw running on Ubuntu on a VPS. Instead of giving the agent a lot of MyShows API context, we give it one short CLI with predictable JSON output.

Project guidance for maintainers lives in [AGENTS.md](AGENTS.md).
Canonical agent usage documentation lives in [docs/agent-cli.md](docs/agent-cli.md).
Project release history lives in [CHANGELOG.md](CHANGELOG.md).

## Current commands

```bash
myshows start "X-Files" --json
myshows progress "South Park" --json
myshows mark "Wild Wild West" s02e14 --rating 4 --json
myshows watching --sort popularity --json
myshows remaining "Friends" --json
```

## Environment

The CLI reads credentials from environment variables:

```bash
export MYSHOWS_CLIENT_ID="..."
export MYSHOWS_CLIENT_SECRET="..."
export MYSHOWS_USERNAME="..."
export MYSHOWS_PASSWORD="..."
export MYSHOWS_LANGUAGE="en"
```

`MYSHOWS_LANGUAGE` is optional and defaults to `en`.

The CLI also supports a local `.env` file. The smallest working variant is:

```dotenv
email=your-login-or-email
password=your-password
```

If `MYSHOWS_CLIENT_ID` and `MYSHOWS_CLIENT_SECRET` are omitted, the CLI falls back to the public API docs sandbox app credentials `apidoc/apidoc`. If you later request your own OAuth app from `api@myshows.me`, those explicit values will override the default.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Development

```bash
make test
make lint
make build
make check
```

If you do not want `make`, the direct commands are:

```bash
python -m compileall src tests
python -m pytest
python -m ruff check .
python -m build
```

## TDD scope for v0

The initial tests cover:

- starting a show as `watching`
- fuzzy show-name resolution for small typos
- rejecting weak matches with a `show not found` error
- finding progress for a show
- marking a specific episode as watched
- listing currently watched shows sorted by popularity
- counting remaining episodes while ignoring specials
- CLI JSON output for each command

## Project layout

```text
src/myshows_cli/
  cli.py
  client.py
  config.py
  service.py
tests/
docs/skill.md
docs/agent-cli.md
.github/workflows/ci.yml
```

## Notes

- This repository uses the official MyShows API v2 JSON-RPC endpoint.
- The implementation is intentionally thin and avoids overengineering.
- Token caching, richer fuzzy matching, and more commands can be added later in small PRs.
- When adding CLI functionality, update `README.md`, `docs/agent-cli.md`, and `docs/skill.md` in the same change.
