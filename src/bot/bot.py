import discord
from discord.ext import commands

import json
import os

from query_processor.query_processor import QueryProcessor
from parsers.yt import YT
from parsers.vk import VK

parsers = (YT(), VK())
query_processor = QueryProcessor(parsers)
parsers_dict = {}

queue_info = {}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


for parser in parsers:
    parsers_dict[parser.name] = parser
        

with open(os.path.join("configs", "config.json")) as file:
    CONFIG = json.loads(file.read())

if not CONFIG:
    raise ValueError("Incorrect config")

ffmpeg_options = CONFIG["ffmpeg_options"]

async def join(context):
    channel = context.author.voice.channel
    voice_client = await channel.connect()
    return voice_client


async def leave(context):
    await context.disconnect()


@bot.event
async def on_ready():
    curr_dir = os.getcwd()
    commands_path = os.path.join(curr_dir, "src", "bot", "commands")
    for command_file in os.listdir(commands_path):
        if command_file != "__pycache__":
            await bot.load_extension(f"bot.commands.{command_file[:-3]}")
    try:
        with open("guilds.txt") as guilds_file:
            guilds = guilds_file.read().split(";")[:-1]
        for guild in guilds:
            queue_info[guild] = {"song_info": [], "repeat_current_song": False}
    except FileNotFoundError:
        open("guilds.txt", "x")
    
    print(f'Bot connected as {bot.user}')


@bot.event
async def on_guild_join(guild):
    with open("guilds.txt", "r+") as guilds_file:
        guilds = guilds_file.read()
        if str(guild.id) not in guilds:
            guilds_file.write(f"{guild.id};")
    queue_info[f"{guild.id}"] = {"song_info": [], "repeat_current_song": False}


# block all DMs
@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


def run_bot():
    bot.run(CONFIG["token"])
