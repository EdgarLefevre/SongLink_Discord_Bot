import os
import requests

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

PLATFORMS = ["appleMusic", 'spotify', "deezer", 'youtubeMusic']


def get_links(url):
    links = []
    api_link = "https://api.song.link/v1-alpha.1/links?url=" + url + "&userCountry=US"
    response = requests.get(api_link)
    for p in PLATFORMS:
        try:
            links.append(response.json()['linksByPlatform'][p]['url'])
        except Exception:
            print("Error get_links for " + p)
            links.append("No link found")
    return links


def create_response(links_list):
    response = "".join(p + ': ' + l + "\n" for p, l in zip(PLATFORMS, links_list))
    print(response)
    return response


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name='sl', help='Give a music link and get all other platform link.\nType !sl <link> to get your links.')
async def sl(ctx, link):
    link_list = get_links(link)
    response = create_response(link_list)
    await ctx.send(response)


bot.run(TOKEN)
