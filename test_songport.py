import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from songport import ResolveError, resolve

TRACK = {
    "isrc": "GBARL9300135",
    "title": "Never Gonna Give You Up",
    "artist": "Rick Astley",
    "platforms": {
        "spotify": {
            "url": "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT",
            "isSearchFallback": False,
        },
        "appleMusic": {
            "url": "https://music.apple.com/fr/album/never/1438556560?i=1438556832",
            "isSearchFallback": False,
        },
        "deezer": {
            "url": "https://www.deezer.com/track/15646529",
            "isSearchFallback": False,
        },
        "youtubeMusic": {
            "url": "https://music.youtube.com/search?q=rick+astley",
            "isSearchFallback": True,
        },
    },
}

LINK = "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT"


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        time.sleep(self.server.delay)
        length = int(self.headers.get("Content-Length", 0))
        self.server.last_body = json.loads(self.rfile.read(length) or b"{}")
        self.server.last_headers = dict(self.headers)
        status, payload = self.server.reply
        body = payload.encode() if isinstance(payload, str) else json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@pytest.fixture
def api():
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    server.reply = (200, TRACK)
    server.delay = 0
    server.last_body = None
    server.last_headers = {}
    threading.Thread(target=server.serve_forever, daemon=True).start()
    server.url = f"http://127.0.0.1:{server.server_port}/v1/convert"
    yield server
    server.shutdown()
    server.server_close()


def test_resolve_returns_the_track_title_and_artist(api):
    track = resolve(LINK, "sp_live_test", api_url=api.url)

    assert track.title == "Never Gonna Give You Up"
    assert track.artist == "Rick Astley"
    assert track.isrc == "GBARL9300135"


def test_resolve_returns_a_link_for_each_platform(api):
    track = resolve(LINK, "sp_live_test", api_url=api.url)

    assert {link.platform for link in track.links} == {
        "spotify",
        "appleMusic",
        "deezer",
        "youtubeMusic",
    }
    spotify = next(link for link in track.links if link.platform == "spotify")
    assert spotify.url == "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT"


def test_resolve_marks_a_search_fallback(api):
    track = resolve(LINK, "sp_live_test", api_url=api.url)

    youtube = next(link for link in track.links if link.platform == "youtubeMusic")
    deezer = next(link for link in track.links if link.platform == "deezer")
    assert youtube.is_search_fallback is True
    assert deezer.is_search_fallback is False


def test_resolve_sends_the_key_as_a_bearer_token(api):
    resolve(LINK, "sp_live_test", api_url=api.url)

    assert api.last_headers["Authorization"] == "Bearer sp_live_test"


def test_resolve_posts_the_link_in_the_body(api):
    resolve(LINK, "sp_live_test", api_url=api.url)

    assert api.last_body["url"] == LINK


def test_resolve_reports_an_unreadable_link(api):
    api.reply = (400, {"error": "Missing or invalid url"})

    with pytest.raises(ResolveError) as caught:
        resolve("not-a-link", "sp_live_test", api_url=api.url)

    assert "not a music link" in str(caught.value)


def test_resolve_reports_a_rejected_key(api):
    api.reply = (401, "Invalid or inactive API key.")

    with pytest.raises(ResolveError) as caught:
        resolve(LINK, "sp_live_wrong", api_url=api.url)

    assert "API key" in str(caught.value)


def test_resolve_reports_an_unmatched_track(api):
    api.reply = (422, {"error": "Couldn't resolve this link"})

    with pytest.raises(ResolveError) as caught:
        resolve(LINK, "sp_live_test", api_url=api.url)

    assert "could not match" in str(caught.value)


def test_resolve_reports_a_rate_limit(api):
    api.reply = (429, "Rate limited")

    with pytest.raises(ResolveError) as caught:
        resolve(LINK, "sp_live_test", api_url=api.url)

    assert "too many requests" in str(caught.value).lower()


def test_resolve_reports_a_slow_api(api):
    api.delay = 2

    with pytest.raises(ResolveError) as caught:
        resolve(LINK, "sp_live_test", api_url=api.url, timeout=0.2)

    assert "did not answer" in str(caught.value)


def test_resolve_keeps_the_platform_order_it_is_given(api):
    track = resolve(
        LINK,
        "sp_live_test",
        api_url=api.url,
        platforms=["deezer", "spotify", "appleMusic", "youtubeMusic"],
    )

    assert [link.platform for link in track.links] == [
        "deezer",
        "spotify",
        "appleMusic",
        "youtubeMusic",
    ]
    assert api.last_body["platforms"] == [
        "deezer",
        "spotify",
        "appleMusic",
        "youtubeMusic",
    ]


def test_resolve_skips_a_platform_the_api_omits(api):
    api.reply = (200, {**TRACK, "platforms": {"deezer": TRACK["platforms"]["deezer"]}})

    track = resolve(LINK, "sp_live_test", api_url=api.url, platforms=["spotify", "deezer"])

    assert [link.platform for link in track.links] == ["deezer"]
