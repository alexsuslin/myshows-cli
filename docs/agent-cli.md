# Agent CLI Guide

This is the canonical guide for agents that use `myshows-agent-cli`.

## Purpose

Use the CLI instead of embedding raw MyShows API details into prompts. The CLI keeps calls short, responses structured, and context usage low.

## Execution mode

Always prefer JSON mode:

```bash
myshows <command> ... --json
```

Treat the JSON payload as the source of truth. Use exit code `0` as success and `1` as failure.

## Credentials

The CLI reads configuration from environment variables or a local `.env` file.

Configuration sources are checked in this order:

1. environment variables
2. `./.env` in the current working directory
3. `$XDG_CONFIG_HOME/myshows-cli/.env`
4. `~/.config/myshows-cli/.env`

Smallest practical `.env`:

```dotenv
email=your-login-or-email
password=your-password
```

Explicit CLI aliases are also supported:

```dotenv
MYSHOWS_CLI_EMAIL=your-login-or-email
MYSHOWS_CLI_PASSWORD=your-password
```

Optional explicit OAuth app credentials:

```dotenv
MYSHOWS_CLIENT_ID=...
MYSHOWS_CLIENT_SECRET=...
MYSHOWS_USERNAME=...
MYSHOWS_PASSWORD=...
MYSHOWS_LANGUAGE=en
```

If `MYSHOWS_CLIENT_ID` and `MYSHOWS_CLIENT_SECRET` are missing, the CLI falls back to `apidoc/apidoc`.

## Supported commands

### `start`

Use when the agent needs to say that the user has started watching a show.

```bash
myshows start "X-Files" --json
```

Behavior notes:

- small naming mistakes are acceptable, for example `x filez`
- if the best match is too weak, the CLI returns `ok: false` instead of picking a random show
- the CLI sets the show status to `watching`

Expected success shape:

```json
{
  "ok": true,
  "data": {
    "show": {
      "id": 404,
      "title": "Секретные материалы",
      "title_original": "The X-Files",
      "popularity": 11000
    },
    "watch_status": "watching"
  }
}
```

### `progress`

Use when the agent needs the latest watched episode, next episode, or remaining count for a show.

```bash
myshows progress "South Park" --json
```

Expected response shape:

```json
{
  "ok": true,
  "data": {
    "show": {
      "id": 34,
      "title": "South Park",
      "title_original": "South Park",
      "popularity": 97074
    },
    "last_watched": {
      "id": 2277,
      "title": "Weight Gain 4000",
      "season": 1,
      "episode": 2,
      "code": "s01e02"
    },
    "next_episode": {
      "id": 2278,
      "title": "Volcano",
      "season": 1,
      "episode": 3,
      "code": "s01e03"
    },
    "watched_episodes": 2,
    "total_episodes": 335,
    "remaining_episodes": 333
  }
}
```

### `mark`

Use when the agent needs to mark an episode as watched and optionally set an episode rating.

```bash
myshows mark "South Park" s01e02 --rating 4 --json
```

Behavior notes:

- episode codes must use the `sXXeYY` format
- the CLI attempts to set the show status to `watching`
- MyShows may reflect writes with a short delay on immediate follow-up reads

Expected success shape:

```json
{
  "ok": true,
  "data": {
    "show": {
      "id": 34,
      "title": "South Park",
      "title_original": "South Park",
      "popularity": 97074
    },
    "episode": {
      "id": 2277,
      "title": "Weight Gain 4000",
      "season": 1,
      "episode": 2,
      "code": "s01e02"
    },
    "rating": 4,
    "checked": true
  }
}
```

### `watching`

Use when the agent needs the shows currently being watched.

```bash
myshows watching --sort popularity --json
```

Current supported sort values:

- `popularity`
- `title`

Expected success shape:

```json
{
  "ok": true,
  "data": [
    {
      "show": {
        "id": 34,
        "title": "Южный Парк",
        "title_original": "South Park",
        "popularity": 97074
      },
      "popularity": 97074,
      "watched_episodes": 2,
      "total_episodes": 329,
      "watch_status": "watching"
    }
  ]
}
```

### `remaining`

Use when the agent only needs how many regular episodes are left.

```bash
myshows remaining "Friends" --json
```

Expected success shape:

```json
{
  "ok": true,
  "data": {
    "show": {
      "id": 20,
      "title": "Friends",
      "title_original": "Friends",
      "popularity": 233255
    },
    "watched_episodes": 0,
    "total_episodes": 236,
    "remaining_episodes": 236
  }
}
```

## Error format

On failure:

```json
{
  "ok": false,
  "error": "human readable message"
}
```

Example for a weak or missing show match:

```json
{
  "ok": false,
  "error": "Show not found: zzzznotfound"
}
```

## Recommended agent behavior

- Prefer exact show names when available.
- Small typos are usually fine, but the CLI may reject very weak matches on purpose.
- Prefer `--json` in every automated call.
- After `mark`, tolerate a short delay before assuming a read mismatch is a bug.
- Do not scrape MyShows HTML if the CLI can answer the question.
- If a needed operation does not exist yet, add it to the CLI instead of teaching the agent raw API calls.

## Documentation maintenance rule

When a new CLI command, flag, or response field is added, update this file in the same change.

Also review:

- `README.md`
- `docs/skill.md`
- `AGENTS.md`
