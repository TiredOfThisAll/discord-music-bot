import discord
from discord.ext import commands
import json
import os

from bot.bot import bot, queue_info, config


@commands.hybrid_command(
    name="save_queue",
    description="Create a dump file of current queue"
)
async def command_save_queue(ctx):
    queue = queue_info[f"{ctx.guild.id}"]

    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        await ctx.send("Queue is empty right now")
        return

    with open(
        os.path.join(
            config.QUEUE_DUMPS_PATH,
            f"{ctx.guild.id}_queue_dump.txt"
            ),
        "w+",
        encoding="utf-8"
    ) as queue_dump_file:
        queue_dump_file.write(json.dumps(
            queue,
            default=vars,
            ensure_ascii=True
        ))

    await ctx.send("Queue dump file was successfully created")


async def setup(bot):
    bot.add_command(command_save_queue)
