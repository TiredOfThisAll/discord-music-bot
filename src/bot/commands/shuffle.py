import discord
from discord.ext import commands
import random

from bot.bot import bot, queue_info


@commands.hybrid_command(name="shuffle", with_app_command=True, description="shuffle the queue")
async def command_shuffle(ctx):
    queue = queue_info[f"{ctx.guild.id}"]
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_client:
        await ctx.send("Queue is empty right now")
        return
    
    curr_song = queue["song_info"].pop(0)
    random.shuffle(queue["song_info"])
    queue["song_info"].insert(0, curr_song)
    
    await ctx.send("Successfully shuffled the queue")


async def setup(bot):
    bot.add_command(command_shuffle)
