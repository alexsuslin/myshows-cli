"""Thin MyShows API client."""

from __future__ import annotations

from typing import Any

import requests

from myshows_cli.config import Settings


class MyShowsApiError(RuntimeError):
    """Raised when MyShows returns an API-level error."""


class MyShowsClient:
    """Small JSON-RPC client for MyShows."""

    USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )

    def __init__(
        self,
        settings: Settings,
        *,
        session: requests.Session | None = None,
        rpc_url: str = "https://api.myshows.me/v2/rpc/",
        token_url: str = "https://myshows.me/oauth/token",
    ) -> None:
        self.settings = settings
        self.session = session or requests.Session()
        self.rpc_url = rpc_url
        self.token_url = token_url
        self._access_token: str | None = None
        self._request_id = 0

    def call(self, method: str, params: dict[str, Any] | None = None, auth: bool = True) -> Any:
        """Call a MyShows JSON-RPC method and return its result."""
        self._request_id += 1
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Language": self.settings.language,
            "User-Agent": self.USER_AGENT,
        }
        if auth:
            headers["Authorization"] = f"Bearer {self._get_access_token()}"
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self._request_id,
        }
        response = self.session.post(self.rpc_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        body = response.json()
        if "error" in body:
            error = body["error"]
            raise MyShowsApiError(f"{error.get('message', 'Unknown API error')} ({error.get('code')})")
        return body.get("result")

    def _get_access_token(self) -> str:
        if self._access_token:
            return self._access_token

        response = self.session.post(
            self.token_url,
            data={
                "grant_type": "password",
                "client_id": self.settings.client_id,
                "client_secret": self.settings.client_secret,
                "username": self.settings.username,
                "password": self.settings.password,
            },
            headers={
                "Accept": "application/json",
                "Accept-Language": self.settings.language,
                "User-Agent": self.USER_AGENT,
            },
            timeout=30,
        )
        response.raise_for_status()
        body = response.json()
        token = body.get("access_token")
        if not token:
            raise MyShowsApiError("OAuth token response did not include access_token")
        self._access_token = token
        return token
