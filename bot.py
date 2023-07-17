import discord
from discord.ext import commands
import asyncio
import random
import time
from datetime import timedelta

import youtube_functions
from queue_embed import PaginationButtons, queue_embed
from vk_music import parse_vk_url

queue_info = {}
current_number_of_songs = 0
ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


with open("discord_id.txt") as discord_id:
    DISCORD_ID = discord_id.read()


async def join(context):
    channel = context.author.voice.channel
    voice_client = await channel.connect()
    return voice_client


async def leave(context):
    await context.disconnect()


@bot.event
async def on_ready():
    try:
        with open("guilds.txt") as guilds_file:
            guilds = guilds_file.read().split(";")[:-1]
        for guild in guilds:
            queue_info[guild] = {"extracted_video_info": [], "video_urls": [], "repeat_current_song": False, "queries": []}
    except FileNotFoundError:
        open("guilds.txt", "x")
    print(f'Bot connected as {bot.user}')


@bot.event
async def on_guild_join(guild):
    with open("guilds.txt", "r+") as guilds_file:
        guilds = guilds_file.read()
        if str(guild.id) not in guilds:
            guilds_file.write(f"{guild.id};")
    queue_info[f"{guild.id}"] = {"extracted_video_info": [], "video_urls": []}


@bot.command(name='sync')
async def sync(ctx):
    # You should sync only when adding new commands or editing existing ones
    # or you can be ratelimited by discord for unnecessary syncing
    if ctx.author.id != int(DISCORD_ID):
        await ctx.channel.send("You are not my father")
        return
    await bot.tree.sync()
    await ctx.channel.send(f'synced slash commands for {bot.user}')
    print(f'synced slash commands for {bot.user}')


@bot.hybrid_command(name="play", description="play some stuff, you can use urls or search on youtube by video title")
async def play(ctx, *, url, queue_imported=False, already_defered=False):
    global current_number_of_songs, queue_info
    new_queue_created = False

    queue = queue_info[f"{ctx.guild.id}"]

    # Begging discord to continue interaction of slash command if we are too slow
    if not already_defered:
        await ctx.defer()

    if not ctx.author.voice:
        return await ctx.send('You are not connected to a voice channel')
    
    queue_size = len(queue["extracted_video_info"]) + len(queue["video_urls"])

    await youtube_functions.search_youtube(url, queue)

    if not queue["video_urls"]:
        await ctx.send("No available videos with this url")
        return

    if not queue["extracted_video_info"] and queue["video_urls"]:
        await youtube_functions.extract_full_info(queue)
        if queue["extracted_video_info"]:
            new_queue_created = True
        else:
            await ctx.send("No available videos with this url")
            return

    if queue["extracted_video_info"]:
        # connect the bot if it has not been connected to voice channel
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if not voice_client:
            voice_client = await join(ctx)
        
        new_queue_size = len(queue["extracted_video_info"]) + len(queue["video_urls"])
        
        if new_queue_created:
            await ctx.send(f'{new_queue_size} song(s) in queue')
        else:
            await ctx.send(f"{new_queue_size - queue_size} song(s) were added to the queue")
        
        if voice_client.is_playing():
            return
        
        while queue["extracted_video_info"]:
            response = f'Playing {queue["extracted_video_info"][0]["title"]}'
            response = response if not queue_imported else "Queue was succesfully imported\n" + response
            queue_imported = False
            await ctx.send(response)

            voice_client.play(discord.FFmpegPCMAudio(queue["extracted_video_info"][0]["link"], **ffmpeg_options))

            queue["extracted_video_info"][0]["start_time"] = time.time()

            while voice_client.is_playing() or voice_client.is_paused():
                if queue["queries"]:
                    if not queue["video_urls"]:
                        while not queue["video_urls"] and queue["queries"]:
                            await youtube_functions.search_youtube(queue["queries"][0], queue)
                            queue["queries"].pop(0)
                    else:
                        await youtube_functions.search_youtube(queue["queries"][0], queue)
                        queue["queries"].pop(0)
                if len(queue["extracted_video_info"]) < 2 and queue["video_urls"]:
                    await youtube_functions.extract_full_info(queue)
                await asyncio.sleep(1)
            if queue["extracted_video_info"] and not queue["repeat_current_song"]:
                queue["extracted_video_info"].pop(0)

        await leave(voice_client)


@bot.hybrid_command(name="skip", description="skip current song")
async def skip(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        await ctx.send("Nothing is playing right now")
        return
    await ctx.send(f"Skipped {queue_info[f'{ctx.guild.id}']['extracted_video_info'][0]['title']}")
    voice_client.stop()


@bot.hybrid_command(name="stop", description="clear the queue and stop playing")
async def stop(ctx):
    queue = queue_info[f"{ctx.guild.id}"]
    queue["extracted_video_info"].clear()
    queue["video_urls"].clear()
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        await ctx.send("Nothing is playing right now")
        return
    voice_client.stop()
    await voice_client.disconnect()
    await ctx.send("Successfully stopped the music")


@bot.hybrid_command(name="pause", description="pause current song")
async def pause(ctx):
    queue = queue_info[f"{ctx.guild.id}"]
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        await ctx.send("Nothing is playing right now")
        return
    voice_client.pause()
    await ctx.send(f"Paused {queue['extracted_video_info'][0]['title']}")


@bot.hybrid_command(name="resume", description="resume current song")
async def resume(ctx):
    queue = queue_info[f"{ctx.guild.id}"]
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        await ctx.send("Nothing is playing right now")
        return
    voice_client.resume()
    await ctx.send(f"Resumed {queue['extracted_video_info'][0]['title']}")


@bot.hybrid_command(name="queue", description="show queue")
async def queue(ctx):
    queue = queue_info[f"{ctx.guild.id}"]

    if not queue['extracted_video_info'] and not queue['video_urls']:
        await ctx.send("Nothing is playing right now")
        return
    
    view = PaginationButtons(queue)

    song_cur_time = timedelta(seconds=int(time.time() - queue["extracted_video_info"][0]["start_time"]))

    song_duration = timedelta(seconds=int(queue["extracted_video_info"][0]["duration"]))

    time_string = f"[{song_cur_time}/{song_duration}]"

    estimated_time = sum([x["duration"] for x in queue["extracted_video_info"]])
    estimated_time += sum([x["duration"] for x in queue["video_urls"] if x["duration"]])
    estimated_time = timedelta(seconds=estimated_time)

    if len(queue['video_urls']) < 11:
        view = None
    await ctx.send(
        view=view,
        embed=await queue_embed(
        queue['extracted_video_info'],
        queue["video_urls"],
        time_string=time_string,
        estimated_time=estimated_time
        )
        )


@bot.hybrid_command(name="shuffle", with_app_command=True, description="shuffle the queue")
async def shuffle(ctx):
    queue = queue_info[f"{ctx.guild.id}"]
    if not queue["extracted_video_info"] and not queue["video_urls"]:
        await ctx.send("Queue is empty right now")
        return
    random.shuffle(queue["video_urls"])
    await ctx.send("Successfully shuffled the queue")


@bot.hybrid_command(name="save_queue", description="Create a dump file of current queue")
async def save_queue(ctx):
    queue = queue_info[f"{ctx.guild.id}"]

    if not queue["extracted_video_info"] and not queue["video_urls"]:
        await ctx.send("Queue is empty right now")
        return
    
    video_urls_list = [f'{video_info["webpage_url"]}\n{video_info["title"]}' for video_info in queue["extracted_video_info"]]
    if queue["video_urls"]:
        video_urls_list += [f'{video_info["url"]}\n{video_info["title"]}' for video_info in queue["video_urls"]]
    
    with open(f"{ctx.guild.id}_queue_dump.txt", "w", encoding="utf-8") as queue_dump_file:
        queue_dump_file.write("\n".join(video_urls_list))

    await ctx.send("Queue dump file was successfully created")


@bot.hybrid_command(name="load_queue", description="Import queue from dump file")
async def load_queue(ctx):
    global queue_info
    queue = queue_info[f"{ctx.guild.id}"]
    if not ctx.author.voice:
        return await ctx.send('You are not connected to a voice channel')
    
    try:
        with open(f"{ctx.guild.id}_queue_dump.txt", "r", encoding="utf-8") as queue_dump_file:
            queue_dump_list = queue_dump_file.read().split("\n")
        
        if len(queue_dump_list) > 1:
            for i in range(0, len(queue_dump_list)-2, 2):
                queue["video_urls"].append({"url": queue_dump_list[i], "title": queue_dump_list[i+1]})
        
        await play(ctx, url=queue_dump_list[-2], queue_imported=True)

    except FileNotFoundError:
        await ctx.send("No queue was saved for this server")


@bot.hybrid_command(name="repeat", description="Repeat current song\nuse the command again to stop the music from repeating")
async def repeat(ctx):
    global queue_info
    queue = queue_info[f"{ctx.guild.id}"]
    if not queue["extracted_video_info"]:
        await ctx.send("Nothing is playing right now")
        return
    if queue["repeat_current_song"]:
        queue["repeat_current_song"] = False
        await ctx.send(f'{queue["extracted_video_info"][0]["title"]} is no longer on repeat')
        return
    queue["repeat_current_song"] = True
    await ctx.send(f'{queue["extracted_video_info"][0]["title"]} is on repeat now')


@bot.hybrid_command(name="multiline_play", description="Play some song using one command")
async def multiline_play(ctx, *, urls, already_defered=False, already_in_queries=False):
    global queue_info

    if not already_defered:
        await ctx.defer()

    queue = queue_info[f"{ctx.guild.id}"]
    if not ctx.author.voice:
        return await ctx.send('You are not connected to a voice channel')
    urls = urls.split("\n")
    if not already_in_queries:
        queue["queries"] += urls[1:]

    await play(ctx, url=urls[0], already_defered=True)


@bot.hybrid_command(name="vk_play", description="Play playlist from vk")
async def vk_play(ctx, *, url):
    global queue_info

    await ctx.defer()

    queue = queue_info[f"{ctx.guild.id}"]
    if not ctx.author.voice:
        return await ctx.send('You are not connected to a voice channel')
    
    parse_vk_url(url, queue)

    if not queue["queries"]:
        return await ctx.send("No available songs with this url")
    
    await multiline_play(ctx, urls="\n".join(queue["queries"]), already_defered=True, already_in_queries=True)
    


# block all DMs
@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


def run_bot(token):
    bot.run(token)
