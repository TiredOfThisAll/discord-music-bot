import discord
from discord.ext import commands

from bot.bot import bot, queue_info


@commands.hybrid_command(
    name="stop",
    description="clear the queue and stop playing"
)
async def command_stop(ctx):
    queue = queue_info[f"{ctx.guild.id}"]
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_client:
        await ctx.send("Nothing is playing right now")
        return

    queue["song_info"].clear()
    voice_client.stop()
    await voice_client.disconnect()
    await ctx.send("Successfully stopped the music")


async def setup(bot):
    bot.add_command(command_stop)
