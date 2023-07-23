# bot.py
import os
import requests
from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv
import pytz
load_dotenv()

TOKEN = os.environ['DISCORD_TOKEN']
API_KEY = os.environ['API_KEY']

client = commands.Bot(command_prefix='?')


@client.event
async def on_ready():

    print(f'{client.user} is connected to the following guilds:\n')
    for guild in client.guilds:
        print(f'{guild}\n')


@client.command()
async def quarta(ctx):
    sao_paulo_tz = pytz.timezone("America/Sao_Paulo")
    now = datetime.now(sao_paulo_tz)
    if now.strftime('%A') != 'Wednesday':
        await ctx.send('Hoje definitivamente não é quarta-feira meus bacanos')
    else:
        await ctx.send('Hoje é quarta-feira meus bacanos!!')


@client.command()
async def random(ctx):
    image = requests.get(
        url=f'https://api.unsplash.com/photos/random/?client_id={API_KEY}')
    await ctx.send(image.json()["urls"]["raw"])


@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

client.run(TOKEN)
