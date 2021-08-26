# bot.py
import os
import discord
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'{member.name}, bem-vindo ao {guild.name}!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if 'dia' and 'hj' in message.content.lower():
        if datetime.now().strftime('%A') != 'Wednesday':
            await message.channel.send('Hoje definitivamente não é quarta-feira')
        else:
            await message.channel.send('Hoje é quarta-feira meus bacanos!!')

@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

client.run(TOKEN)
