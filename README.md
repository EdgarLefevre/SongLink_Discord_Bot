# SongLink_Discord_Bot
Discord bot to share music links easily. Take a link from your favorite plateform and share it to your friends via this bot to get links from Spotify, YoutubeMusic, AppleMusic and Deezer.

## Installation 

Install requirements: 

```shell
pip install -r requirements.txt
```

Create a `.env` file containing: 

```shell
DISCORD_TOKEN=<your_bot_token>
```

Add your bot to your guild and then run the script: 

```shell
python bot.py
```

## Usage

`!sl <your_link_form_a_streaming_plateform>`

## Add plateforms

In `bot.py` you can find a list of platforms, just add the ones you want. 
> Check song_link api documentation to be sure that your platform is in the list.
