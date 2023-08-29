from discord.ext import commands

from bot.bot import bot, CONFIG


@commands.command(name='sync')
async def sync(ctx):
    # You should sync only when adding new commands or editing existing ones
    # or you can be ratelimited by discord for unnecessary syncing
    if ctx.author.id not in CONFIG["admins"]:
        await ctx.channel.send("You are not my father")
        return
    await bot.tree.sync()
    await ctx.channel.send(f'synced slash commands for {bot.user}')
    print(f'synced slash commands for {bot.user}')


async def setup(bot):
    bot.add_command(sync)
