import asyncio
import logging
import os

import discord
from discord import app_commands
from dotenv import load_dotenv

from songport import ResolveError, resolve

log = logging.getLogger("songlink")

PLATFORM_NAMES = {
    "spotify": "Spotify",
    "appleMusic": "Apple Music",
    "deezer": "Deezer",
    "youtubeMusic": "YouTube Music",
    "tidal": "Tidal",
    "soundcloud": "SoundCloud",
}


def format_reply(track):
    header = f"**{track.title}** by {track.artist}"
    if not track.links:
        return f"{header}\nSongPort found no link on the other platforms."

    lines = [header]
    for link in track.links:
        name = PLATFORM_NAMES.get(link.platform, link.platform)
        note = " (search page, not an exact match)" if link.is_search_fallback else ""
        lines.append(f"{name}: {link.url}{note}")
    return "\n".join(lines)


class SongLinkClient(discord.Client):
    def __init__(self, api_key, guild_id=None):
        super().__init__(intents=discord.Intents.none())
        self.api_key = api_key
        self.guild_id = guild_id
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        if self.guild_id is None:
            await self.tree.sync()
            return
        guild = discord.Object(id=self.guild_id)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

    async def on_ready(self):
        log.info("connected as %s", self.user)


def build_client(api_key, guild_id=None):
    client = SongLinkClient(api_key, guild_id)

    @client.tree.command(
        name="sl",
        description="Turn a music link into the links for the other platforms.",
    )
    @app_commands.describe(link="A Spotify, Apple Music, Deezer or YouTube Music link")
    async def sl(interaction: discord.Interaction, link: str):
        await interaction.response.defer()
        try:
            track = await asyncio.to_thread(resolve, link, client.api_key)
        except ResolveError as error:
            await interaction.followup.send(str(error))
            return
        except Exception:
            log.exception("resolve failed for %s", link)
            await interaction.followup.send(
                "The bot hit an unexpected error. The server log has the detail."
            )
            return
        await interaction.followup.send(format_reply(track))

    return client


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    load_dotenv()
    try:
        token = os.environ["DISCORD_TOKEN"]
        api_key = os.environ["SONGPORT_API_KEY"]
    except KeyError as missing:
        raise SystemExit(f"Set {missing.args[0]} in the environment or in a .env file.")

    guild_id = os.environ.get("DISCORD_GUILD_ID")
    build_client(api_key, int(guild_id) if guild_id else None).run(token)


if __name__ == "__main__":
    main()
