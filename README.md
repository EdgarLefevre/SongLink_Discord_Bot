# SongLink Discord Bot

Share music between friends who use different streaming services. Give the bot a link from one platform. The bot answers with the link for each other platform.

The bot resolves a link with the [SongPort API](https://songport.link/docs/api).

## Requirements

- Python 3.10 or later.
- A Discord bot token.
- A SongPort API key.

## Credentials

The bot needs two secrets and no others. You do not need a Spotify, Apple or Google account.

| Variable | Where you get it |
| --- | --- |
| `DISCORD_TOKEN` | The Discord developer portal, on the Bot page of your application. |
| `SONGPORT_API_KEY` | SongPort. Write to `hello@songport.link` to request a key. |

The bot uses a slash command, so it does not need the `MESSAGE_CONTENT` privileged intent. You do not enable any intent in the developer portal.

`DISCORD_GUILD_ID` is optional. Set it to one server id while you test, because the `/sl` command then appears in that server in seconds. Leave it empty in production, because Discord then registers the command in every server.

## Installation

Install the dependencies:

```shell
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

Copy the example environment file and add your two values:

```shell
cp .env.example .env
```

## Run the bot

```shell
./.venv/bin/python bot.py
```

The bot registers the `/sl` command when it connects. Discord can take up to one hour to show a new command in every server. Set `DISCORD_GUILD_ID` to test in one server without that wait.

The bot opens a connection to Discord from the machine that runs it. It does not listen on a port, so it needs no public address and no deployment. You can run it on your laptop and use `/sl` in Discord immediately.

Run one instance at a time for a given token. If the old bot still runs on your server, stop it first, or create a second Discord application with its own token for local tests.

## Usage

Type `/sl` and paste a link:

```
/sl https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT
```

The bot answers with the title, the artist, and one line for each platform. A line that ends with `(search page, not an exact match)` is a search result, because SongPort did not find the exact track on that platform.

## Add a platform

`PLATFORM_NAMES` in `bot.py` maps a SongPort platform key to the name that the bot prints. `DEFAULT_PLATFORMS` in `songport.py` lists the platforms that the bot asks for. Add a key to both lists to add a platform.

SongPort supports `spotify`, `appleMusic`, `deezer`, `youtubeMusic`, `tidal` and `soundcloud`.

## Tests

```shell
./.venv/bin/pip install -r requirements-dev.txt
./.venv/bin/python -m pytest
```

The tests run a local HTTP server that imitates the SongPort API, so they need no network access and no API key.

## Deployment

The bot opens a websocket to Discord and keeps it open, so it must run as a process that stays alive. A small virtual machine, a container, or a Raspberry Pi is sufficient. Set `DISCORD_TOKEN` and `SONGPORT_API_KEY` as environment variables, because the `.env` file is only a convenience for local work.

## Errors

The bot reports the cause of a failure instead of a missing link:

| Message | Cause |
| --- | --- |
| That is not a music link SongPort can read. | SongPort could not parse the link. |
| SongPort refused the API key. | The key is wrong, or it is not active. |
| SongPort could not match that track. | SongPort read the link but found no match. |
| SongPort got too many requests. | You reached a rate limit. Wait one minute. |
| SongPort did not answer in time. | The request timed out. |
