from myshows_cli.service import EpisodeNotFoundError, MyShowsService, ShowNotFoundError


class StubClient:
    def __init__(self, *, search_results, show_details, watched_map):
        self.search_results = search_results
        self.show_details = show_details
        self.watched_map = watched_map
        self.calls = []

    def call(self, method, params=None, auth=True):
        self.calls.append((method, params, auth))
        if method == "shows.Search":
            query = params["query"]
            return self.search_results.get(query, [])
        if method == "shows.GetById":
            return self.show_details[params["showId"]]
        if method == "profile.Episodes":
            return self.watched_map[params["showId"]]
        if method == "profile.Shows":
            return self.watched_map["profile_shows"]
        if method == "manage.CheckEpisode":
            return True
        if method == "manage.SetShowStatus":
            return True
        raise AssertionError(f"Unexpected method: {method}")


def make_service():
    return MyShowsService(
        StubClient(
            search_results={
                "South Park": [
                    {"id": 101, "title": "Южный парк", "titleOriginal": "South Park", "watching": 5000},
                ],
                "Wild Wild West": [
                    {"id": 202, "title": "Wild Wild West", "titleOriginal": "Wild Wild West", "watching": 400},
                ],
                "Friends": [
                    {"id": 303, "title": "Друзья", "titleOriginal": "Friends", "watching": 9000},
                ],
                "x filez": [
                    {"id": 404, "title": "Секретные материалы", "titleOriginal": "The X-Files", "watching": 11000},
                ],
                "x-files": [],
                "x files": [
                    {"id": 404, "title": "Секретные материалы", "titleOriginal": "The X-Files", "watching": 11000},
                ],
                "zzzznotfound": [
                    {"id": 303, "title": "Друзья", "titleOriginal": "Friends", "watching": 9000},
                ],
            },
            show_details={
                101: {
                    "id": 101,
                    "title": "Южный парк",
                    "titleOriginal": "South Park",
                    "episodes": [
                        {"id": 1001, "seasonNumber": 1, "episodeNumber": 1, "shortName": "s01e01", "title": "Cartman Gets an Anal Probe", "isSpecial": 0},
                        {"id": 1002, "seasonNumber": 1, "episodeNumber": 2, "shortName": "s01e02", "title": "Weight Gain 4000", "isSpecial": 0},
                        {"id": 1003, "seasonNumber": 1, "episodeNumber": 3, "shortName": "s01e03", "title": "Volcano", "isSpecial": 0},
                    ],
                },
                202: {
                    "id": 202,
                    "title": "Wild Wild West",
                    "titleOriginal": "Wild Wild West",
                    "episodes": [
                        {"id": 2001, "seasonNumber": 2, "episodeNumber": 13, "shortName": "s02e13", "title": "Prev", "isSpecial": 0},
                        {"id": 2014, "seasonNumber": 2, "episodeNumber": 14, "shortName": "s02e14", "title": "Target", "isSpecial": 0},
                    ],
                },
                303: {
                    "id": 303,
                    "title": "Друзья",
                    "titleOriginal": "Friends",
                    "episodes": [
                        {"id": 3001, "seasonNumber": 1, "episodeNumber": 1, "shortName": "s01e01", "title": "Pilot", "isSpecial": 0},
                        {"id": 3002, "seasonNumber": 1, "episodeNumber": 2, "shortName": "s01e02", "title": "The Sonogram at the End", "isSpecial": 0},
                        {"id": 3003, "seasonNumber": 1, "episodeNumber": 3, "shortName": "s01e03", "title": "The Thumb", "isSpecial": 0},
                        {"id": 3999, "seasonNumber": 0, "episodeNumber": 1, "shortName": "s00e01", "title": "Special", "isSpecial": 1},
                    ],
                },
                404: {
                    "id": 404,
                    "title": "Секретные материалы",
                    "titleOriginal": "The X-Files",
                    "watching": 11000,
                    "episodes": [
                        {"id": 4001, "seasonNumber": 1, "episodeNumber": 1, "shortName": "s01e01", "title": "Pilot", "isSpecial": 0},
                    ],
                },
            },
            watched_map={
                101: [{"id": 1001, "rating": 0}, {"id": 1002, "rating": 4}],
                202: [],
                303: [{"id": 3001, "rating": 0}],
                404: [],
                "profile_shows": [
                    {
                        "show": {"id": 1, "title": "Loki", "titleOriginal": "Loki", "watching": 9500},
                        "watchStatus": "watching",
                        "totalEpisodes": 12,
                        "watchedEpisodes": 6,
                    },
                    {
                        "show": {"id": 2, "title": "Andor", "titleOriginal": "Andor", "watching": 12000},
                        "watchStatus": "watching",
                        "totalEpisodes": 24,
                        "watchedEpisodes": 12,
                    },
                    {
                        "show": {"id": 3, "title": "Lost", "titleOriginal": "Lost", "watching": 15000},
                        "watchStatus": "finished",
                        "totalEpisodes": 121,
                        "watchedEpisodes": 121,
                    },
                ],
            },
        )
    )


def test_progress_returns_last_and_next_episode():
    service = make_service()

    result = service.progress("South Park")

    assert result["show"]["title_original"] == "South Park"
    assert result["last_watched"]["code"] == "s01e02"
    assert result["next_episode"]["code"] == "s01e03"
    assert result["remaining_episodes"] == 1


def test_mark_episode_checks_target_episode_with_rating():
    service = make_service()

    result = service.mark_episode("Wild Wild West", "s02e14", rating=4)

    assert result["episode"]["id"] == 2014
    assert service.client.calls[-2] == (
        "manage.SetShowStatus",
        {"id": 202, "status": "watching"},
        True,
    )
    assert service.client.calls[-1] == (
        "manage.CheckEpisode",
        {"id": 2014, "rating": 4},
        True,
    )


def test_mark_episode_raises_for_missing_episode():
    service = make_service()

    try:
        service.mark_episode("Wild Wild West", "s02e99")
    except EpisodeNotFoundError as error:
        assert "s02e99" in str(error)
    else:
        raise AssertionError("Expected EpisodeNotFoundError")


def test_watching_sorts_by_popularity():
    service = make_service()

    result = service.list_watching(sort_by="popularity")

    assert [item["show"]["title_original"] for item in result] == ["Andor", "Loki"]


def test_remaining_excludes_specials():
    service = make_service()

    result = service.remaining("Friends")

    assert result["remaining_episodes"] == 2
    assert result["total_episodes"] == 3


def test_start_watching_sets_show_status_with_fuzzy_name():
    service = make_service()

    result = service.start_watching("x filez")

    assert result["show"]["title_original"] == "The X-Files"
    assert result["watch_status"] == "watching"
    assert service.client.calls[-1] == (
        "manage.SetShowStatus",
        {"id": 404, "status": "watching"},
        True,
    )


def test_start_watching_uses_query_fallback_for_hyphenated_name():
    service = make_service()

    result = service.start_watching("x-files")

    assert result["show"]["title_original"] == "The X-Files"


def test_start_watching_raises_when_match_is_too_weak():
    service = make_service()

    try:
        service.start_watching("zzzznotfound")
    except ShowNotFoundError as error:
        assert "zzzznotfound" in str(error)
    else:
        raise AssertionError("Expected ShowNotFoundError")
