from myshows_cli.client import MyShowsClient
from myshows_cli.config import Settings


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self):
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if url.endswith("/oauth/token"):
            return FakeResponse({"access_token": "token-123"})
        return FakeResponse({"result": {"ok": True}})


def test_client_sends_browser_like_user_agent():
    session = FakeSession()
    client = MyShowsClient(
        Settings(
            client_id="apidoc",
            client_secret="apidoc",
            username="user@example.com",
            password="secret",
        ),
        session=session,
    )

    client.call("profile.Shows")

    _, oauth_kwargs = session.calls[0]
    _, rpc_kwargs = session.calls[1]
    assert "Mozilla/5.0" in oauth_kwargs["headers"]["User-Agent"]
    assert "Mozilla/5.0" in rpc_kwargs["headers"]["User-Agent"]
