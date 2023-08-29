import discord
from discord.ext import commands
import asyncio
from datetime import datetime

from bot.bot import bot, queue_info, join, leave, ffmpeg_options, \
    query_processor


@commands.hybrid_command(
    name="play",
    description="play some stuff, available music platforms: vk, youtube"
)
async def command_play(ctx, *, query):
    await play(ctx, query=query)


async def play(
        ctx,
        *,
        query: str,
        queue_imported: bool = False,
        already_defered: bool = False,
        imported_songs_amount: int = 0
) -> None:

    queue = queue_info[f"{ctx.guild.id}"]

    # Begging discord to continue interaction of slash command
    # if we are too slow
    if not already_defered:
        await ctx.defer()

    if not ctx.author.voice:
        return await ctx.send('You are not connected to a voice channel')

    queue_size = len(queue["song_info"])

    info = await query_processor.process_query(query)

    if not info:
        return await ctx.send("no available songs with this query")

    for song in info:
        queue["song_info"].append(song)

    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if voice_client:
        new_songs = len(queue['song_info']) - queue_size + \
            imported_songs_amount
        return await ctx.send(f"{new_songs} song(s) were added to the queue")
    else:
        await prepare_new_song(queue, 0)

        if not queue["song_info"]:
            return await ctx.send("no availble songs with this query")

        # connect the bot if it has not been connected to voice channel
        voice_client = await join(ctx)

        await ctx.send(f'{len(queue["song_info"])} song(s) in queue')

    while queue["song_info"]:
        curr_song = queue["song_info"][0]
        parser_name = curr_song["parser"].name
        response = f'{parser_name} Playing {curr_song["info"]["name"]}'
        response = response if not queue_imported \
            else "Queue was succesfully imported\n" + response
        queue_imported = False
        await ctx.send(response)

        voice_client.play(discord.FFmpegPCMAudio(
            curr_song["info"]["params"]["link"],
            **ffmpeg_options
        ))

        curr_time = datetime.now().replace(microsecond=0).timestamp()
        curr_song["info"]["start_time"] = curr_time

        while voice_client.is_playing() or voice_client.is_paused():
            if not queue["repeat_current_song"]:
                if len(queue["song_info"]) > 1:
                    params = queue["song_info"][1]["info"]["params"]
                    if "link" not in params:
                        await prepare_new_song(queue, 1)

            await asyncio.sleep(1)

        if queue["song_info"] and not queue["repeat_current_song"]:
            queue["song_info"].pop(0)

    await leave(voice_client)


async def prepare_new_song(queue: str, index: int) -> None:
    songs = queue["song_info"]

    while queue["song_info"] and "url" not in songs[index]["info"]["params"]:
        song = queue["song_info"][index]
        info = await queue["song_info"][index]["parser"].search(
            song["info"]["name"],
            None
        )
        if not info:
            queue["song_info"].pop(index)
        else:
            queue["song_info"][index]["info"].update(info)

    while queue["song_info"] and "link" not in songs[index]["info"]["params"]:
        info = await queue["song_info"][index]["parser"].get_song(
            queue["song_info"][index]["info"]
        )
        if info:
            queue["song_info"][index]["info"]["params"].update(info)
        else:
            queue["song_info"].pop(index)


async def setup(bot):
    bot.add_command(command_play)
