import discord
from math import ceil


class PaginationButtons(discord.ui.View):
    def __init__(self, queue_info, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.music = queue_info["extracted_video_info"]
        self.urls = queue_info['video_urls']
        self.page_number = 1

    @discord.ui.button(label="<", style=discord.ButtonStyle.blurple, disabled=True, custom_id="left_page_button")
    async def left_page_button_callback(self, interaction, button):
        self.page_number -= 1
        button.disabled = False if self.page_number > 1 else True
        for button in self.children:
            if button.custom_id == "page_button":
                button.label = f"{self.page_number}"
            if button.custom_id == "right_page_button":
                button.disabled = True if self.page_number == ceil(len(self.urls) / 10) else False
        await interaction.response.edit_message(view=self, embed=await queue_embed(self.music, self.urls, self.page_number))

    @discord.ui.button(label=f"1", style=discord.ButtonStyle.blurple, disabled=True, custom_id="page_button")
    async def page_button_callback(self, interaction, button):
        await interaction.send_message("How the F")

    @discord.ui.button(label=">", style=discord.ButtonStyle.blurple, custom_id="right_page_button")
    async def right_page_button_callback(self, interaction, button):
        self.page_number += 1
        button.disabled = True if self.page_number == ceil(len(self.urls) / 10) else False
        for button in self.children:
            if button.custom_id == "page_button":
                button.label = f"{self.page_number}"
            if button.custom_id == "left_page_button":
                button.disabled = False if self.page_number > 1 else True
        await interaction.response.edit_message(view=self, embed=await queue_embed(self.music, self.urls, self.page_number))


async def queue_embed(music, urls, page_number=1, time_string='0:0', estimated_time='0:0'):
    page_count = ceil(len(urls) / 10)
    embed = discord.Embed(title=f"Queue page {page_number} of {max(1, page_count)}",
                          colour=discord.Colour.blurple())

    if music:
        None if "image" not in list(music[0]) else embed.set_thumbnail(url=music[0]["image"])
        embed.add_field(name="Current song", value=f"{music[0]['title']}", inline=False)
        embed.add_field(name="Timebar", value=time_string)
        embed.add_field(name="Estimated time playing: ", value=estimated_time)
        None if len(music) <= 1 else embed.add_field(name="Next song", value=f"{music[1]['title']}", inline=False)

    None if not urls else embed.add_field(name="", value=f"```{get_queue_page(page_number, urls)}```", inline=False)
    return embed


def get_queue_page(page_number, urls):
    return "".join(list(map(lambda x: f"♫ {x['title']} \n", urls[(page_number-1)*10:10*page_number])))
