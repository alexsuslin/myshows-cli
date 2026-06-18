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


def test_settings_accept_cli_env_aliases(monkeypatch):
    monkeypatch.delenv("MYSHOWS_CLIENT_ID", raising=False)
    monkeypatch.delenv("MYSHOWS_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("MYSHOWS_USERNAME", raising=False)
    monkeypatch.delenv("MYSHOWS_PASSWORD", raising=False)
    monkeypatch.delenv("email", raising=False)
    monkeypatch.delenv("password", raising=False)
    monkeypatch.setenv("MYSHOWS_CLI_EMAIL", "cli@example.com")
    monkeypatch.setenv("MYSHOWS_CLI_PASSWORD", "cli-secret")

    settings = Settings.from_env()

    assert settings.username == "cli@example.com"
    assert settings.password == "cli-secret"


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


def test_settings_load_from_xdg_config_dotenv(tmp_path: Path, monkeypatch):
    config_home = tmp_path / "config-home"
    dotenv = config_home / "myshows-cli" / ".env"
    dotenv.parent.mkdir(parents=True)
    dotenv.write_text(
        "MYSHOWS_CLI_EMAIL=xdg@example.com\nMYSHOWS_CLI_PASSWORD=xdg-secret\n",
        encoding="utf-8",
    )
    workdir = tmp_path / "workspace"
    workdir.mkdir()

    monkeypatch.chdir(workdir)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_home))
    monkeypatch.delenv("HOME", raising=False)
    monkeypatch.delenv("MYSHOWS_USERNAME", raising=False)
    monkeypatch.delenv("MYSHOWS_PASSWORD", raising=False)
    monkeypatch.delenv("MYSHOWS_CLI_EMAIL", raising=False)
    monkeypatch.delenv("MYSHOWS_CLI_PASSWORD", raising=False)
    monkeypatch.delenv("email", raising=False)
    monkeypatch.delenv("password", raising=False)

    settings = Settings.from_env()

    assert settings.username == "xdg@example.com"
    assert settings.password == "xdg-secret"


def test_cwd_dotenv_overrides_xdg_config(tmp_path: Path, monkeypatch):
    config_home = tmp_path / "config-home"
    xdg_dotenv = config_home / "myshows-cli" / ".env"
    xdg_dotenv.parent.mkdir(parents=True)
    xdg_dotenv.write_text("email=xdg@example.com\npassword=xdg-secret\n", encoding="utf-8")

    workdir = tmp_path / "workspace"
    workdir.mkdir()
    (workdir / ".env").write_text("email=local@example.com\npassword=local-secret\n", encoding="utf-8")

    monkeypatch.chdir(workdir)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_home))
    monkeypatch.delenv("HOME", raising=False)
    monkeypatch.delenv("MYSHOWS_USERNAME", raising=False)
    monkeypatch.delenv("MYSHOWS_PASSWORD", raising=False)
    monkeypatch.delenv("MYSHOWS_CLI_EMAIL", raising=False)
    monkeypatch.delenv("MYSHOWS_CLI_PASSWORD", raising=False)
    monkeypatch.delenv("email", raising=False)
    monkeypatch.delenv("password", raising=False)

    settings = Settings.from_env()

    assert settings.username == "local@example.com"
    assert settings.password == "local-secret"
