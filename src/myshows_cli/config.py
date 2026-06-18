"""Configuration helpers for MyShows CLI."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CLIENT_ID = "apidoc"
DEFAULT_CLIENT_SECRET = "apidoc"


class ConfigurationError(ValueError):
    """Raised when required settings are missing."""


@dataclass(slots=True)
class Settings:
    client_id: str
    client_secret: str
    username: str
    password: str
    language: str = "en"

    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables."""
        env_file_values = _load_config_values()
        values = {
            "client_id": _first_value("MYSHOWS_CLIENT_ID", env_file_values) or DEFAULT_CLIENT_ID,
            "client_secret": _first_value("MYSHOWS_CLIENT_SECRET", env_file_values) or DEFAULT_CLIENT_SECRET,
            "username": _first_value(
                "MYSHOWS_USERNAME",
                env_file_values,
                aliases=("MYSHOWS_CLI_EMAIL", "email", "EMAIL"),
            ),
            "password": _first_value(
                "MYSHOWS_PASSWORD",
                env_file_values,
                aliases=("MYSHOWS_CLI_PASSWORD", "password", "PASSWORD"),
            ),
            "language": _first_value("MYSHOWS_LANGUAGE", env_file_values) or "en",
        }
        missing = [name.upper() for name, value in values.items() if name != "language" and not value]
        if missing:
            names = ", ".join(f"MYSHOWS_{name}" for name in missing)
            raise ConfigurationError(f"Missing required environment variables: {names}")
        return cls(**values)


def _load_config_values() -> dict[str, str]:
    values: dict[str, str] = {}
    for path in _config_paths():
        values.update(_load_dotenv(path))
    return values


def _config_paths() -> list[Path]:
    paths: list[Path] = []

    xdg_config_home = os.getenv("XDG_CONFIG_HOME", "").strip()
    if xdg_config_home:
        paths.append(Path(xdg_config_home) / "myshows-cli" / ".env")
    else:
        home = os.getenv("HOME", "").strip()
        if home:
            paths.append(Path(home) / ".config" / "myshows-cli" / ".env")

    paths.append(Path.cwd() / ".env")
    return paths


def _first_value(primary: str, dotenv_values: dict[str, str], aliases: tuple[str, ...] = ()) -> str:
    for key in (primary, *aliases):
        value = os.getenv(key)
        if value and value.strip():
            return value.strip()
        file_value = dotenv_values.get(key)
        if file_value and file_value.strip():
            return file_value.strip()
    return ""


def _load_dotenv(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values
