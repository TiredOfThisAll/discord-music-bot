import discord
from discord.ext import commands
import asyncio
import random

import youtube_functions
from queue_embed import PaginationButtons, queue_embed

music = []
urls = []
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
    print(f'Bot connected as {bot.user}')


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
async def play(ctx, *, url):
    global current_number_of_songs, urls, music
    new_queue_created = False

    # Begging discord to continue interaction of slash command if we are too slow
    await ctx.defer()

    if not ctx.author.voice:
        return await ctx.send('You are not connected to a voice channel')
    
    current_number_of_songs = len(urls) + len(music)

    await youtube_functions.search_youtube(url, urls)

    if not music and urls:
        await youtube_functions.extract_full_info(urls, music)
        if music:
            new_queue_created = True
        else:
            ctx.send("No available videos with this url")
            return

    if music:
        # connect the bot if it has not been connected to voice channel
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if not voice_client:
            voice_client = await join(ctx)
        if new_queue_created:
            await ctx.send(f"{len(music) + len(urls)} song(s) in queue")
        else:
            await ctx.send(f"{abs(current_number_of_songs - len(urls) - len(music))} song(s) were added to the queue")
            return
        while music:
            await ctx.send(f"Playing {music[0]['title']}")

            voice_client.play(discord.FFmpegPCMAudio(music[0]["link"], **ffmpeg_options))
            await youtube_functions.extract_full_info(urls, music)

            while voice_client.is_playing() or voice_client.is_paused():
                await asyncio.sleep(1)
            if music:
                music.pop(0)

        await leave(voice_client)


@bot.hybrid_command(name="skip", description="skip current song")
async def skip(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        await ctx.send("Nothing is playing right now")
        return
    await ctx.send(f"Skipped {music[0]['title']}")
    voice_client.stop()


@bot.hybrid_command(name="stop", description="clear the queue and stop playing")
async def stop(ctx):
    urls.clear()
    music.clear()
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        await ctx.send("Nothing is playing right now")
        return
    voice_client.stop()
    await voice_client.disconnect()
    await ctx.send("Successfully stopped the music")


@bot.hybrid_command(name="pause", description="pause current song")
async def pause(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        await ctx.send("Nothing is playing right now")
        return
    voice_client.pause()
    await ctx.send(f"Paused {music[0]['title']}")


@bot.hybrid_command(name="resume", description="resume current song")
async def resume(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        await ctx.send("Nothing is playing right now")
        return
    voice_client.resume()
    await ctx.send(f"Resumed {music[0]['title']}")


@bot.hybrid_command(name="queue", description="show queue")
async def queue(ctx):
    view = PaginationButtons(music, urls)
    if not music and not urls:
        await ctx.send("Nothing is playing right now")
        return
    if len(urls) < 11:
        view = None
    await ctx.send(view=view, embed=await queue_embed(music, urls))


@bot.hybrid_command(name="shuffle", with_app_command=True, description="shuffle the queue")
async def shuffle(ctx):
    if not music and not urls:
        await ctx.send("Queue is empty right now")
        return
    random.shuffle(urls)
    await ctx.send("Successfully shuffled the queue")


# block all DMs
@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


def run_bot(token):
    bot.run(token)
