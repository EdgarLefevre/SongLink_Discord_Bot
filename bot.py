import os
import random
import requests

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

PLATFORMS=["appleMusic", 'spotify', "deezer", 'youtubeMusic']

def get_links(url):
    links=[]
    api_link = "https://api.song.link/v1-alpha.1/links?url="+url+"&userCountry=US"
    response = requests.get(api_link)
    try:
        for p in PLATFORMS:
            links.append(response.json()['linksByPlatform'][p]['url'])
        return links
    except Exception as e:
        print("Error get_links : " + e)
        return None


def create_response(links_list):
    if links_list == None:
        response = "Error in API call, try with another link."
        print(response)
    else:
        response = ""
        for p, l in zip(PLATFORMS, links_list):
            response += p+': '+l+"\n"
        print(response)
    return response

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name='sl', help='Give a music link and get all other plateform link')
async def sl(ctx, link):
    link_list = get_links(link)
    response = create_response(link_list)
    await ctx.send(response)


bot.run(TOKEN, bot=True, reconnect=True)
