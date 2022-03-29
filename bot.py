# bot.py
import os
import requests
from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.environ['DISCORD_TOKEN']

client = commands.Bot(command_prefix='?')

@client.event
async def on_ready():
    
    print(f'{client.user} is connected to the following guilds:\n')
    for guild in client.guilds:
        print(f'{guild}\n')


@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'{member.name}, bem-vindo ao {guild.name}!')

@client.command()
async def quarta(ctx):
    if datetime.now().strftime('%A') != 'Wednesday':
        await ctx.send('Hoje definitivamente não é quarta-feira meus bacanos')
    else:
        await ctx.send('Hoje é quarta-feira meus bacanos!!')


@client.command()
async def waifu(ctx):
    image = requests.get(('https://api.waifu.pics/sfw/waifu'))
    await ctx.send(f'{image.json()["url"]}')


@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

client.run(TOKEN)
