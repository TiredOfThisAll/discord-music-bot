import discord
from discord.ext import commands

from bot.bot import bot, queue_info


@commands.hybrid_command(name="pause", description="pause current song")
async def command_pause(ctx):
    queue = queue_info[f"{ctx.guild.id}"]
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        await ctx.send("Nothing is playing right now")
        return
    voice_client.pause()
    await ctx.send(f"Paused {queue['song_info'][0]['info']['name']}")


async def setup(bot):
    bot.add_command(command_pause)
