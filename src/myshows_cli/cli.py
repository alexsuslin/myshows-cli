"""CLI entry point."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from myshows_cli.client import MyShowsClient
from myshows_cli.config import ConfigurationError, Settings
from myshows_cli.service import AmbiguousEpisodeTitleError, MyShowsService, MyShowsServiceError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="myshows", description="Minimal MyShows CLI for agents.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    progress = subparsers.add_parser("progress", help="Show progress for a series.")
    progress.add_argument("show_name")
    progress.add_argument("--json", action="store_true", dest="as_json")

    start = subparsers.add_parser("start", help="Mark a show as currently watching.")
    start.add_argument("show_name")
    start.add_argument("--json", action="store_true", dest="as_json")

    mark = subparsers.add_parser("mark", help="Mark an episode as watched.")
    mark.add_argument("show_name")
    mark.add_argument("episode_code")
    mark.add_argument("--rating", type=int, choices=range(0, 6))
    mark.add_argument("--json", action="store_true", dest="as_json")

    mark_title = subparsers.add_parser("mark-title", help="Mark an episode as watched by title.")
    mark_title.add_argument("show_name")
    mark_title.add_argument("episode_title")
    mark_title.add_argument("--rating", type=int, choices=range(0, 6))
    mark_title.add_argument("--json", action="store_true", dest="as_json")

    watching = subparsers.add_parser("watching", help="List currently watched shows.")
    watching.add_argument("--sort", choices=("popularity", "title"), default="popularity")
    watching.add_argument("--json", action="store_true", dest="as_json")

    remaining = subparsers.add_parser("remaining", help="Count remaining episodes.")
    remaining.add_argument("show_name")
    remaining.add_argument("--json", action="store_true", dest="as_json")

    return parser


def run(argv: list[str] | None = None, *, service: MyShowsService | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    as_json = getattr(args, "as_json", False)

    try:
        active_service = service or MyShowsService(MyShowsClient(Settings.from_env()))
        if args.command == "start":
            data = active_service.start_watching(args.show_name)
            return _emit_result(data, as_json, _format_start(data))
        if args.command == "progress":
            data = active_service.progress(args.show_name)
            return _emit_result(data, as_json, _format_progress(data))
        if args.command == "mark":
            data = active_service.mark_episode(args.show_name, args.episode_code, rating=args.rating)
            return _emit_result(data, as_json, _format_mark(data))
        if args.command == "mark-title":
            data = active_service.mark_episode_by_title(args.show_name, args.episode_title, rating=args.rating)
            return _emit_result(data, as_json, _format_mark(data))
        if args.command == "watching":
            data = active_service.list_watching(sort_by=args.sort)
            return _emit_result(data, as_json, _format_watching(data))
        if args.command == "remaining":
            data = active_service.remaining(args.show_name)
            return _emit_result(data, as_json, _format_remaining(data))
        parser.error(f"Unsupported command: {args.command}")
    except AmbiguousEpisodeTitleError as error:
        return _emit_error(str(error), as_json, candidates=error.candidates)
    except (ConfigurationError, MyShowsServiceError) as error:
        return _emit_error(str(error), as_json)
    except Exception as error:  # pragma: no cover - safety net for agent usage
        return _emit_error(f"Unexpected error: {error}", as_json)
    return 0


def main() -> int:
    """Run the CLI."""
    return run()


def _emit_result(data: Any, as_json: bool, text: str) -> int:
    if as_json:
        print(json.dumps({"ok": True, "data": data}, ensure_ascii=False))
    else:
        print(text)
    return 0


def _emit_error(message: str, as_json: bool, **extra: Any) -> int:
    if as_json:
        payload = {"ok": False, "error": message}
        payload.update(extra)
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(message, file=sys.stderr)
    return 1


def _format_progress(data: dict[str, Any]) -> str:
    show_data = data.get("show", {})
    show = show_data.get("title_original") or show_data.get("title") or "unknown"
    last_watched = data.get("last_watched")
    next_episode = data.get("next_episode")
    last_code = last_watched.get("code") if last_watched else "n/a"
    next_code = next_episode.get("code") if next_episode else "done"
    return f"{show}: last={last_code}, next={next_code}, remaining={data.get('remaining_episodes', '?')}"


def _format_start(data: dict[str, Any]) -> str:
    show_data = data.get("show", {})
    show = show_data.get("title_original") or show_data.get("title") or "unknown"
    return f"{show}: status={data.get('watch_status', 'watching')}"


def _format_mark(data: dict[str, Any]) -> str:
    show_data = data.get("show", {})
    show = show_data.get("title_original") or show_data.get("title") or "unknown"
    rating = f", rating={data['rating']}" if data["rating"] is not None else ""
    return f"{show}: marked {data['episode']['code']}{rating}"


def _format_watching(data: list[dict[str, Any]]) -> str:
    if not data:
        return "No watching shows."
    lines = []
    for item in data:
        show_data = item.get("show", {})
        show = show_data.get("title_original") or show_data.get("title") or "unknown"
        lines.append(
            f"{show}: popularity={item.get('popularity', 0)}, watched={item.get('watched_episodes', 0)}/{item.get('total_episodes', 0)}"
        )
    return "\n".join(lines)


def _format_remaining(data: dict[str, Any]) -> str:
    show_data = data.get("show", {})
    show = show_data.get("title_original") or show_data.get("title") or "unknown"
    return f"{show}: remaining={data['remaining_episodes']} of {data.get('total_episodes', '?')}"
