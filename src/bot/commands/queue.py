import discord
from discord.ext import commands

from bot.bot import bot, queue_info
from bot.queue_embed import PaginationButtons, queue_embed


@commands.hybrid_command(name="queue", description="show queue")
async def command_queue(ctx):
    queue = queue_info[f"{ctx.guild.id}"]

    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        await ctx.send("Nothing is playing right now")
        return

    view = PaginationButtons(queue)

    if len(queue['song_info']) < 12:
        view = None

    await ctx.send(
        view=view,
        embed=await queue_embed(queue)
    )


async def setup(bot):
    bot.add_command(command_queue)
