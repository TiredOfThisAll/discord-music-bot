import discord
from math import ceil
from datetime import datetime, timedelta

from bot.bot import CONFIG


class PaginationButtons(discord.ui.View):
    def __init__(self, queue: dict, timeout: float | None = 180) -> None:
        super().__init__(timeout=timeout)
        self.queue = queue
        self.page_number = 1

    @discord.ui.button(
        label="<",
        style=discord.ButtonStyle.blurple,
        disabled=True,
        custom_id="left_page_button"
        )
    async def left_page_button_callback(self, interaction, button):
        self.page_number -= 1
        button.disabled = not self.page_number > 1
        for button in self.children:
            if button.custom_id == "page_button":
                button.label = f"{self.page_number}"
            if button.custom_id == "right_page_button":
                last_page = ceil(len(self.queue["song_info"][1:]) / 10)
                button.disabled = self.page_number == last_page

        if self.queue["song_info"]:
            embed = await queue_embed(self.queue, self.page_number)
            await interaction.response.edit_message(view=self, embed=embed)
        else:
            await interaction.response.send_message("Queue is empty right now")

    @discord.ui.button(
        label=f"1",
        style=discord.ButtonStyle.blurple,
        disabled=True,
        custom_id="page_button"
    )
    async def page_button_callback(self, interaction, button):
        await interaction.send_message("How the F")

    @discord.ui.button(
            label=">",
            style=discord.ButtonStyle.blurple,
            custom_id="right_page_button"
        )
    async def right_page_button_callback(self, interaction, button):
        self.page_number += 1
        last_page = ceil(len(self.queue["song_info"][1:]) / 10)
        button.disabled = self.page_number == last_page
        for button in self.children:
            if button.custom_id == "page_button":
                button.label = f"{self.page_number}"
            if button.custom_id == "left_page_button":
                button.disabled = not self.page_number > 1

        if self.queue["song_info"]:
            embed = await queue_embed(self.queue, self.page_number)
            await interaction.response.edit_message(view=self, embed=embed)
        else:
            await interaction.response.send_message("Queue is empty right now")


async def queue_embed(queue: dict, page_number: int = 1) -> discord.Embed:
    page_count = ceil(len(queue["song_info"]) / 10)
    embed = discord.Embed(
        title=f"Queue page {page_number} of {max(1, page_count)}",
        colour=discord.Colour.blurple()
    )
    curr_song = queue["song_info"][0]
    song_start_time = datetime.fromtimestamp(curr_song["info"]["start_time"])

    song_cur_time = datetime.now().replace(microsecond=0) - song_start_time

    song_duration = timedelta(seconds=curr_song["info"]["duration"])

    time_string = f"[{song_cur_time}/{song_duration}]"

    estimated_time = sum(
        [song["info"]["duration"] for song in queue["song_info"]]
    )

    estimated_time = timedelta(seconds=estimated_time)

    if not queue["song_info"][0]["info"]["params"]["image"]:
        img = CONFIG["default_image"]
    else:
        img = queue["song_info"][0]["info"]["params"]["image"]
    embed.set_thumbnail(url=img)

    embed.add_field(
        name="Current song",
        value=f"{curr_song['info']['name']}",
        inline=False
    )
    embed.add_field(name="Timebar", value=time_string)
    embed.add_field(name="Estimated time playing: ", value=estimated_time)

    None if len(queue["song_info"]) < 2 else embed.add_field(
        name="",
        value=f"```{get_queue_page(page_number, queue['song_info'][1:])}```",
        inline=False
    )

    return embed


def get_queue_page(page_number, urls):
    return "".join(list(map(
        lambda x:
            f"{(page_number - 1) * 10 + x[0] + 1}. {x[1]['info']['name']} \n",
        enumerate(urls[(page_number-1)*10:10*page_number])
    )))
