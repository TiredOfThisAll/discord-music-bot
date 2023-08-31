from typing import Any
from discord.ext import commands
import os
import json

from bot.bot import queue_info, parsers_dict, config
from .play import play


@commands.hybrid_command(
    name="load_queue",
    description="Import queue from dump file"
)
async def command_load_queue(ctx):

    await ctx.defer()

    queue = queue_info[f"{ctx.guild.id}"]
    if not ctx.author.voice:
        return await ctx.send('You are not connected to a voice channel')

    try:
        def json_decode(dict):
            if "parser" in dict:
                parser_name = dict["parser"]["name"]
                dict["parser"] = parsers_dict[parser_name] if parser_name in \
                    parsers_dict else None
            return dict

        with open(os.path.join(
            config.QUEUE_DUMPS_PATH,
            f"{ctx.guild.id}_queue_dump.txt"),
            "r",
            encoding="utf-8"
        ) as dump_file:
            queue_dump = json.loads(dump_file.read(), object_hook=json_decode)

        if queue_dump:
            if "song_info" in queue_dump:
                queue["song_info"] += queue_dump["song_info"]

            if queue["song_info"]:
                last_song = queue["song_info"].pop()
                if "url" in last_song["info"]["params"]:
                    query = last_song["info"]["params"]["url"]
                else:
                    query = last_song["info"]["name"]
                await play(
                    ctx,
                    query=query,
                    queue_imported=True,
                    already_defered=True,
                    imported_songs_amount=len(queue_dump["song_info"]) - 1
                )
            else:
                return await ctx.send("No songs were saved")

    except FileNotFoundError:
        await ctx.send("No queue was saved for this server")


async def setup(bot):
    bot.add_command(command_load_queue)
