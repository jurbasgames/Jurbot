# bot.py
import asyncio
import os
import requests
import openai
from datetime import datetime
import discord
from dotenv import load_dotenv
import pytz
import traceback
import base
from prompt import rpg_prompt
import dacite
import yaml


load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
API_KEY = os.getenv('API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

CONFIG: base.Config = dacite.from_dict(
    base.Config, yaml.safe_load(open(os.path.join("config.yaml"), "r"))
)
BOT_NAME = CONFIG.name
BOT_INSTRUCTIONS = CONFIG.instructions
EXAMPLE_CONVOS = CONFIG.example_conversations


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

openai.api_key = OPENAI_API_KEY

# Start bot
@client.event
async def on_ready():

    print(f'{client.user} is connected to the following guilds:\n')
    for guild in client.guilds:
        print(f'{guild}\n')
    await tree.sync()

# Bot commands

@tree.command(name="quarta",description='Verifica se é quarta-feira')
async def quarta(interaction: discord.Interaction):
    sao_paulo_tz = pytz.timezone("America/Sao_Paulo")
    now = datetime.now(sao_paulo_tz)
    if now.strftime('%A') != 'Wednesday':
        await interaction.response.send_message('Hoje definitivamente não é quarta-feira meus bacanos')
    else:
        await interaction.response.send_message('Hoje é quarta-feira meus bacanos!!')

@tree.command(name="random",description='Manda uma imagem aleatória')
async def random(interaction: discord.Interaction):
    image = requests.get(
        url=f'https://api.unsplash.com/photos/random/?client_id={API_KEY}')
    await interaction.response.send_message(image.json()["urls"]["raw"])

@tree.command(name="rpg", description="Inicia um jogo de RPG")
@discord.app_commands.checks.has_permissions(send_messages=True)
@discord.app_commands.checks.has_permissions(view_channel=True)
@discord.app_commands.checks.bot_has_permissions(send_messages=True)
@discord.app_commands.checks.bot_has_permissions(view_channel=True)
@discord.app_commands.checks.bot_has_permissions(manage_threads=True)
async def rpg(interaction: discord.Interaction):

    if not isinstance(interaction.channel, discord.TextChannel):
        return
    user = interaction.user
    embed = discord.Embed(
                description=f"{user.name} estamos iniciando seu RPG! Aguarde um momento...",
                color=discord.Color.green(),
            )
    embed.add_field(name=user.name, value="RPGzin", inline=False)
    embed = await interaction.response.send_message(embed=embed)
    response = await interaction.original_response()
    thread = await response.create_thread(
            name=f"{user.name[:20]} jogando RPG",
            slowmode_delay=1,
            reason="RPGzin",
            auto_archive_duration=60,
        )

    # Inicio do game
    try:
        async with thread.typing():
            prompt = rpg_prompt(user.name)
            messages = []
            messages.append({"role":"user","content": prompt})
            reply  = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=1,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            messages.append({"role":"system","content": str(reply['choices'][0]['message']['content'])})
            message = await thread.send(reply['choices'][0]['message']['content'])
            # Do for
            for i in ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟','❌']:
                await message.add_reaction(i)
            
            def check10(reaction, user):
                    return user == interaction.user and str(reaction.emoji) in ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟','❌']
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check10)
            def check3(reaction, user):
                    return user == interaction.user and str(reaction.emoji) in ['1️⃣','2️⃣','3️⃣','❌']
            if str(reaction.emoji) == '❌':
                await thread.send('Você encerrou o jogo.')
            while True:
                messages.append({"role":"user","content": str(reaction.emoji)})
                reply  = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=1,
                    max_tokens=256,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                messages.append({"role":"system","content": str(reply['choices'][0]['message']['content'])})
                message = await thread.send(reply['choices'][0]['message']['content'])
                # Check if has fim do jogo na mensagem em lower case
                if 'fim do jogo' in reply['choices'][0]['message']['content'].lower():
                    await thread.send('Você chegou ao fim do jogo.')
                    break
                # Do for
                for i in ['1️⃣','2️⃣','3️⃣','❌']:
                    await message.add_reaction(i)
                reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check3)
                if str(reaction.emoji) == '❌':
                    await thread.send('Você encerrou o jogo.')
                    break
    
    except asyncio.TimeoutError:
        await thread.send('Você demorou demais para reagir, o jogo foi encerrado.')
        await thread.delete()
    except Exception as e:
        # Delete thread
        await thread.delete()
        # Console log
        traceback.print_exc()

@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            f.write(f'Unhandled event: {event}\n')
            f.write(f'Time: {datetime.now()}\n')
            f.write(f'Args: {args}\n')
            f.write(f'Kwargs: {kwargs}\n')
            f.write(f'{traceback.format_exc()}\n')



client.run(TOKEN)
