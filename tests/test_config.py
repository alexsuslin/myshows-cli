from pathlib import Path

from myshows_cli.config import Settings


def test_settings_accept_legacy_env_aliases(monkeypatch):
    monkeypatch.delenv("MYSHOWS_CLIENT_ID", raising=False)
    monkeypatch.delenv("MYSHOWS_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("MYSHOWS_USERNAME", raising=False)
    monkeypatch.delenv("MYSHOWS_PASSWORD", raising=False)
    monkeypatch.setenv("email", "test@example.com")
    monkeypatch.setenv("password", "secret")

    settings = Settings.from_env()

    assert settings.client_id == "apidoc"
    assert settings.client_secret == "apidoc"
    assert settings.username == "test@example.com"
    assert settings.password == "secret"


def test_settings_load_from_dotenv_file(tmp_path: Path, monkeypatch):
    dotenv = tmp_path / ".env"
    dotenv.write_text("email=dotenv@example.com\npassword=dotenv-secret\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("email", raising=False)
    monkeypatch.delenv("password", raising=False)
    monkeypatch.delenv("MYSHOWS_USERNAME", raising=False)
    monkeypatch.delenv("MYSHOWS_PASSWORD", raising=False)

    settings = Settings.from_env()

    assert settings.username == "dotenv@example.com"
    assert settings.password == "dotenv-secret"
