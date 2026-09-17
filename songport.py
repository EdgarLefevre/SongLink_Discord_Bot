from dataclasses import dataclass

import requests

API_URL = "https://api.songport.link/v1/convert"

DEFAULT_PLATFORMS = ["spotify", "appleMusic", "deezer", "youtubeMusic"]

_STATUS_MESSAGES = {
    400: "That is not a music link SongPort can read.",
    401: "SongPort refused the API key. Check SONGPORT_API_KEY.",
    422: "SongPort could not match that track on the other platforms.",
    429: "SongPort got too many requests. Wait a minute and try again.",
}


class ResolveError(Exception):
    """An error with a message that the bot can show to a Discord user."""


@dataclass
class Link:
    platform: str
    url: str
    is_search_fallback: bool


@dataclass
class Track:
    title: str
    artist: str
    isrc: str | None
    links: list[Link]


def resolve(link, api_key, platforms=None, api_url=API_URL, timeout=10):
    wanted = list(platforms) if platforms else list(DEFAULT_PLATFORMS)

    try:
        response = requests.post(
            api_url,
            json={"url": link, "platforms": wanted},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )
    except requests.Timeout as error:
        raise ResolveError("SongPort did not answer in time. Try again.") from error
    except requests.RequestException as error:
        raise ResolveError(f"The bot could not reach SongPort: {error}") from error

    if response.status_code != 200:
        message = _STATUS_MESSAGES.get(
            response.status_code,
            f"SongPort answered with an unexpected status {response.status_code}.",
        )
        raise ResolveError(message)

    payload = response.json()
    found = payload.get("platforms") or {}
    links = [
        Link(
            platform=name,
            url=found[name]["url"],
            is_search_fallback=bool(found[name].get("isSearchFallback")),
        )
        for name in wanted
        if name in found
    ]
    return Track(
        title=payload.get("title", ""),
        artist=payload.get("artist", ""),
        isrc=payload.get("isrc"),
        links=links,
    )
