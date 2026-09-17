import asyncio

from bot import build_client, format_reply
from songport import Link, Track


def track(links):
    return Track(
        title="Never Gonna Give You Up",
        artist="Rick Astley",
        isrc="GBARL9300135",
        links=links,
    )


def test_reply_shows_the_title_and_artist():
    reply = format_reply(track([Link("deezer", "https://deezer.com/track/1", False)]))

    assert "Never Gonna Give You Up" in reply
    assert "Rick Astley" in reply


def test_reply_gives_one_line_per_platform():
    reply = format_reply(
        track(
            [
                Link("spotify", "https://open.spotify.com/track/1", False),
                Link("appleMusic", "https://music.apple.com/song/2", False),
            ]
        )
    )

    assert "Spotify: https://open.spotify.com/track/1" in reply
    assert "Apple Music: https://music.apple.com/song/2" in reply


def test_reply_uses_the_readable_platform_name():
    reply = format_reply(track([Link("youtubeMusic", "https://music.youtube.com/w/1", False)]))

    assert "YouTube Music:" in reply
    assert "youtubeMusic" not in reply


def test_reply_marks_a_search_link():
    reply = format_reply(
        track(
            [
                Link("deezer", "https://deezer.com/track/1", False),
                Link("youtubeMusic", "https://music.youtube.com/search?q=x", True),
            ]
        )
    )

    deezer_line = next(line for line in reply.splitlines() if "Deezer:" in line)
    youtube_line = next(line for line in reply.splitlines() if "YouTube Music:" in line)
    assert "search" in youtube_line
    assert "search" not in deezer_line


def test_reply_reports_when_no_platform_matched():
    reply = format_reply(track([]))

    assert "no link" in reply.lower()


class _TreeRecorder:
    def __init__(self):
        self.copied_to = []
        self.synced = []

    def copy_global_to(self, *, guild):
        self.copied_to.append(guild.id)

    async def sync(self, *, guild=None):
        self.synced.append(guild.id if guild else None)
        return []


def test_the_bot_registers_the_command_globally_without_a_guild_id():
    client = build_client("sp_live_test")
    recorder = _TreeRecorder()
    client.tree = recorder

    asyncio.run(client.setup_hook())

    assert recorder.synced == [None]
    assert recorder.copied_to == []


def test_the_bot_registers_the_command_in_one_guild_when_given_an_id():
    client = build_client("sp_live_test", guild_id=880123456789012345)
    recorder = _TreeRecorder()
    client.tree = recorder

    asyncio.run(client.setup_hook())

    assert recorder.copied_to == [880123456789012345]
    assert recorder.synced == [880123456789012345]
