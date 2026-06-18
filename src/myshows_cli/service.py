"""Service layer for agent-friendly MyShows use cases."""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any


class MyShowsServiceError(RuntimeError):
    """Base service error."""


class ShowNotFoundError(MyShowsServiceError):
    """Raised when a show could not be resolved."""


class EpisodeNotFoundError(MyShowsServiceError):
    """Raised when an episode code does not exist for a show."""


EPISODE_CODE_RE = re.compile(r"^s(?P<season>\d{1,2})e(?P<episode>\d{1,3})$", re.IGNORECASE)


@dataclass(slots=True)
class MyShowsService:
    """High-level use cases on top of MyShows RPC."""

    client: Any
    minimum_show_match_score: float = 60.0

    def progress(self, show_name: str) -> dict[str, Any]:
        show = self._resolve_show(show_name)
        episodes = self._sorted_regular_episodes(show["episodes"])
        watched_ids = self._watched_ids(show["id"])
        last_watched = self._last_watched(episodes, watched_ids)
        next_episode = self._next_unwatched(episodes, watched_ids)
        watched_regular = sum(1 for episode in episodes if episode["id"] in watched_ids)
        return {
            "show": self._show_payload(show),
            "last_watched": self._episode_payload(last_watched),
            "next_episode": self._episode_payload(next_episode),
            "watched_episodes": watched_regular,
            "total_episodes": len(episodes),
            "remaining_episodes": len(episodes) - watched_regular,
        }

    def mark_episode(self, show_name: str, episode_code: str, rating: int | None = None) -> dict[str, Any]:
        show = self._resolve_show(show_name)
        episode = self._find_episode(show["episodes"], episode_code)
        self.client.call("manage.SetShowStatus", {"id": show["id"], "status": "watching"})
        params = {"id": episode["id"]}
        if rating is not None:
            params["rating"] = rating
        self.client.call("manage.CheckEpisode", params)
        return {
            "show": self._show_payload(show),
            "episode": self._episode_payload(episode),
            "rating": rating,
            "checked": True,
        }

    def start_watching(self, show_name: str) -> dict[str, Any]:
        show = self._resolve_show(show_name)
        self.client.call("manage.SetShowStatus", {"id": show["id"], "status": "watching"})
        return {
            "show": self._show_payload(show),
            "watch_status": "watching",
        }

    def list_watching(self, sort_by: str = "popularity") -> list[dict[str, Any]]:
        result = self.client.call("profile.Shows")
        shows = [item for item in result if item.get("watchStatus") == "watching"]
        if sort_by == "popularity":
            shows.sort(key=lambda item: item.get("show", {}).get("watching", 0), reverse=True)
        elif sort_by == "title":
            shows.sort(key=lambda item: item.get("show", {}).get("titleOriginal") or item.get("show", {}).get("title", ""))

        payload = []
        for item in shows:
            show = item["show"]
            payload.append(
                {
                    "show": self._show_payload(show),
                    "popularity": show.get("watching", 0),
                    "watched_episodes": item.get("watchedEpisodes", 0),
                    "total_episodes": item.get("totalEpisodes", 0),
                    "watch_status": item.get("watchStatus"),
                }
            )
        return payload

    def remaining(self, show_name: str) -> dict[str, Any]:
        show = self._resolve_show(show_name)
        episodes = self._sorted_regular_episodes(show["episodes"])
        watched_ids = self._watched_ids(show["id"])
        watched_regular = sum(1 for episode in episodes if episode["id"] in watched_ids)
        return {
            "show": self._show_payload(show),
            "watched_episodes": watched_regular,
            "total_episodes": len(episodes),
            "remaining_episodes": len(episodes) - watched_regular,
        }

    def _resolve_show(self, show_name: str) -> dict[str, Any]:
        candidates = self._search_candidates(show_name)
        if not candidates:
            raise ShowNotFoundError(f"Show not found: {show_name}")

        ranked = [
            (candidate, self._show_score(show_name, candidate))
            for candidate in candidates
        ]
        chosen, score = max(ranked, key=lambda item: item[1])
        if score < self.minimum_show_match_score:
            raise ShowNotFoundError(f"Show not found: {show_name}")
        return self.client.call("shows.GetById", {"showId": chosen["id"], "withEpisodes": True}, auth=False)

    def _search_candidates(self, show_name: str) -> list[dict[str, Any]]:
        variants = self._search_variants(show_name)
        deduped: dict[int, dict[str, Any]] = {}
        for query in variants:
            for candidate in self.client.call("shows.Search", {"query": query}, auth=False):
                deduped[candidate["id"]] = candidate
        return list(deduped.values())

    def _watched_ids(self, show_id: int) -> set[int]:
        watched = self.client.call("profile.Episodes", {"showId": show_id})
        return {episode["id"] for episode in watched}

    def _find_episode(self, episodes: list[dict[str, Any]], episode_code: str) -> dict[str, Any]:
        match = EPISODE_CODE_RE.match(episode_code.strip())
        if not match:
            raise EpisodeNotFoundError(f"Invalid episode code: {episode_code}")
        season = int(match.group("season"))
        episode_number = int(match.group("episode"))
        for episode in self._sorted_regular_episodes(episodes):
            if (
                episode.get("seasonNumber") == season
                and episode.get("episodeNumber") == episode_number
            ):
                return episode
        raise EpisodeNotFoundError(f"Episode not found: {episode_code}")

    @staticmethod
    def _sorted_regular_episodes(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        regular = [episode for episode in episodes if not episode.get("isSpecial")]
        return sorted(regular, key=lambda item: (item.get("seasonNumber", 0), item.get("episodeNumber", 0)))

    @staticmethod
    def _last_watched(episodes: list[dict[str, Any]], watched_ids: set[int]) -> dict[str, Any] | None:
        watched = [episode for episode in episodes if episode["id"] in watched_ids]
        return watched[-1] if watched else None

    @staticmethod
    def _next_unwatched(episodes: list[dict[str, Any]], watched_ids: set[int]) -> dict[str, Any] | None:
        for episode in episodes:
            if episode["id"] not in watched_ids:
                return episode
        return None

    @staticmethod
    def _normalize(text: str | None) -> str:
        return re.sub(r"[^a-z0-9а-я]+", "", (text or "").lower())

    @staticmethod
    def _search_variants(show_name: str) -> list[str]:
        variants: list[str] = []

        def add(value: str) -> None:
            cleaned = re.sub(r"\s+", " ", value).strip()
            if cleaned and cleaned not in variants:
                variants.append(cleaned)

        add(show_name)
        add(re.sub(r"[-_/]+", " ", show_name))
        add(re.sub(r"[^a-zA-Z0-9а-яА-Я]+", " ", show_name))

        words = re.findall(r"[a-zA-Z0-9а-яА-Я]+", show_name.lower())
        softened_words = [word[:-1] if len(word) >= 5 else word for word in words]
        if softened_words and softened_words != words:
            add(" ".join(softened_words))

        return variants

    def _show_score(self, query: str, item: dict[str, Any]) -> float:
        query_normalized = self._normalize(query)
        titles = [item.get("title"), item.get("titleOriginal")]
        title_scores = []
        for title in titles:
            normalized = self._normalize(title)
            if not normalized:
                continue
            if normalized == query_normalized:
                title_scores.append(1000.0)
                continue
            if normalized.startswith(query_normalized):
                title_scores.append(700.0)
                continue
            if query_normalized in normalized:
                title_scores.append(500.0)
                continue
            title_scores.append(SequenceMatcher(None, query_normalized, normalized).ratio() * 100)
        return max(title_scores or [0.0]) + min(item.get("watching", 0) / 1000, 25)

    @staticmethod
    def _show_payload(show: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": show["id"],
            "title": show.get("title"),
            "title_original": show.get("titleOriginal"),
            "popularity": show.get("watching", 0),
        }

    @staticmethod
    def _episode_payload(episode: dict[str, Any] | None) -> dict[str, Any] | None:
        if episode is None:
            return None
        return {
            "id": episode["id"],
            "title": episode.get("title"),
            "season": episode.get("seasonNumber"),
            "episode": episode.get("episodeNumber"),
            "code": episode.get("shortName")
            or f"s{episode.get('seasonNumber', 0):02d}e{episode.get('episodeNumber', 0):02d}",
        }
