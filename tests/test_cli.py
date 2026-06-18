import json

from myshows_cli.cli import run


class StubService:
    def start_watching(self, show_name):
        return {"show": {"title_original": show_name}, "watch_status": "watching"}

    def progress(self, show_name):
        return {"show": {"title_original": show_name}, "next_episode": {"code": "s01e03"}}

    def mark_episode(self, show_name, episode_code, rating=None):
        return {
            "show": {"title_original": show_name},
            "episode": {"code": episode_code},
            "rating": rating,
        }

    def list_watching(self, sort_by):
        return [{"show": {"title_original": "Andor"}, "popularity": 12000, "sort_by": sort_by}]

    def remaining(self, show_name):
        return {"show": {"title_original": show_name}, "remaining_episodes": 2}


def test_progress_json_output(capsys):
    exit_code = run(["progress", "South Park", "--json"], service=StubService())

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["data"]["show"]["title_original"] == "South Park"


def test_start_json_output(capsys):
    exit_code = run(["start", "The X-Files", "--json"], service=StubService())

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["data"]["watch_status"] == "watching"


def test_mark_json_output(capsys):
    exit_code = run(
        ["mark", "Wild Wild West", "s02e14", "--rating", "4", "--json"],
        service=StubService(),
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["data"]["rating"] == 4


def test_watching_json_output(capsys):
    exit_code = run(["watching", "--sort", "popularity", "--json"], service=StubService())

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["data"][0]["show"]["title_original"] == "Andor"


def test_remaining_json_output(capsys):
    exit_code = run(["remaining", "Friends", "--json"], service=StubService())

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["data"]["remaining_episodes"] == 2
