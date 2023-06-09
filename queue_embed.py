import discord
from math import ceil


page_number = 1


class PaginationButtons(discord.ui.View):
    def __init__(self, music, urls, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.music = music
        self.urls = urls

    @discord.ui.button(label="<", style=discord.ButtonStyle.blurple, disabled=True, custom_id="left_page_button")
    async def left_page_button_callback(self, interaction, button):
        button.disabled = False if page_number > 2 else True
        for button in self.children:
            if button.custom_id == "page_button":
                button.label = f"{page_number - 1}"
            if button.custom_id == "right_page_button":
                button.disabled = True if page_number - 1 == ceil(len(self.urls) / 10) else False
        await interaction.response.edit_message(view=self, embed=await queue_embed(self.music, self.urls, -1))

    @discord.ui.button(label=f"{page_number}", style=discord.ButtonStyle.blurple, disabled=True, custom_id="page_button")
    async def page_button_callback(self, interaction, button):
        await interaction.send_message("How the F")

    @discord.ui.button(label=">", style=discord.ButtonStyle.blurple, custom_id="right_page_button")
    async def right_page_button_callback(self, interaction, button):
        button.disabled = True if page_number == ceil(len(self.urls) / 10) - 1 else False
        for button in self.children:
            if button.custom_id == "page_button":
                button.label = f"{page_number + 1}"
            if button.custom_id == "left_page_button":
                button.disabled = False if page_number + 1 > 1 else True
        await interaction.response.edit_message(view=self, embed=await queue_embed(self.music, self.urls, 1))


async def queue_embed(music, urls, page_change=0):
    page_count = ceil(len(urls) / 10)
    embed = discord.Embed(title=f"Queue page {page_number + page_change} of {max(1, page_count)}",
                          colour=discord.Colour.blurple())

    if music:
        None if "image" not in list(music[0]) else embed.set_thumbnail(url=music[0]["image"])
        embed.add_field(name="Current song", value=f"{music[0]['title']}", inline=False)
        None if len(music) <= 1 else embed.add_field(name="Next song", value=f"{music[1]['title']}", inline=False)

    None if not urls else embed.add_field(name="", value=f"```{get_queue_page(page_change, urls)}```", inline=False)
    return embed


def get_queue_page(page_change, urls):
    global page_number
    page_number += page_change
    return "".join(list(map(lambda x: f"♫ {x['title']} \n", urls[(page_number-1)*10:10*page_number])))