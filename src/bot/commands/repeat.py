import discord
from discord.ext import commands

from bot.bot import bot, queue_info


command_description = """Repeat current song\n
use the command again to stop the music from repeating"""


@commands.hybrid_command(name="repeat", description=command_description)
async def command_repeat(ctx):
    queue = queue_info[f"{ctx.guild.id}"]
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        await ctx.send("Nothing is playing right now")
        return

    song_name = queue['song_info'][0]['info']['name']
    if queue["repeat_current_song"]:
        queue["repeat_current_song"] = False
        await ctx.send(f"{song_name} is no longer on repeat")
        return
    queue["repeat_current_song"] = True
    await ctx.send(f"{song_name} is on repeat now")


async def setup(bot):
    bot.add_command(command_repeat)
