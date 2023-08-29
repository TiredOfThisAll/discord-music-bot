from random import random
from math import floor
import urllib
import aiohttp
import html
import re
from lxml import html
from datetime import datetime, timedelta

from .base_parser import BaseParser


class VK(BaseParser):
    domains = [
        "vk.com",
        "vk.ru",
        "www.vk.com",
        "www.vk.ru"
    ]

    searchFMT = "https://i{server_id}.kissvk.com/api/song/search/do?origin=kissvk.com&query={query}"  # nopep8
    downloadFMT = "https://i{server_id}.kissvk.com/api/song/download/get/10/{artist}-{title}-kissvk.com.mp3?origin=kissvk.com&url={url}&artist={artist}&title={title}&index={song_id}"  # nopep8
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36 OPR/55.0.2994.44',  # nopep8
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Content-Type': 'application/json'
    }

    vk_song_xpath = '//div[@class=\'audio_row__inner\']/div[@class=\'audio_row__performer_title\']'  # nopep8
    vk_song_xpath_performer = 'div[@class=\'audio_row__performers\']/*'
    vk_song_xpath_title = 'div[@class=\'audio_row__title _audio_row__title\']/a[@class=\'audio_row__title_inner _audio_row__title_inner\']'  # nopep8
    vk_song_xpath_duration = "../div[@class=\'audio_row__info _audio_row__info\']/div[@class=\'audio_row__duration audio_row__duration-s _audio_row__duration\']"  # nopep8

    name = "VK"

    def __init__(self):
        super().__init__(self.__class__.name, self.__class__.domains)

    async def search(self, query: str, callback: callable) -> dict:
        server = floor(random() * 29) + 100

        query = urllib.parse.quote(query, encoding="utf-8")

        url = self.searchFMT.format(server_id=server, query=query)

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:

                data = await response.json()

                if data["songs"]:
                    song = data["songs"][0]

                    image = song["vkAlbumPictureUrl"] \
                        if "vkAlbumPictureUrl" in song else None

                    params = {
                        "server": server,
                        "artist": song["artist"],
                        "title": song["title"],
                        "url": song["url"],
                        "index": song["index"],
                        "image": image
                    }

                    if callback:
                        callback({
                            "name": song["artist"] + " - " + song["title"],
                            "duration": int(song["duration"]),
                            "params": params
                            },
                            self
                        )
                    return {
                        "name": song["artist"] + " - " + song["title"],
                        "duration": int(song["duration"]),
                        "params": params
                    }

    async def process_url(self, url: str) -> list:
        # Retrieve playlist id to create valid link
        if "playlist" not in url:
            return
        # nopep8
        check = re.search("audio_playlist(?P<playlist_id>\d+\D{1}\d+)", url)  # nopep8

        if check:
            playlist_id = check.groupdict()['playlist_id']
            url = f"https://vk.com/music/playlist/{playlist_id}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36 OPR/55.0.2994.44',  # nopep8
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'identity'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:

                tree = html.fromstring(await response.text())

                songs = []

                for entry in tree.xpath(self.vk_song_xpath):
                    title = "".join(entry.xpath(
                        self.vk_song_xpath_title + "/text()"
                    ))

                    artist = ", ".join(entry.xpath(
                        self.vk_song_xpath_performer + "/text()"
                    ))

                    duration = datetime.strptime(
                        "".join(entry.xpath(
                            self.vk_song_xpath_duration + "/text()"
                        )),
                        "%M:%S"
                    )
                    duration = timedelta(
                        hours=duration.hour,
                        minutes=duration.minute,
                        seconds=duration.second
                    )

                    params = {"title": title, "artist": artist}
                    songs.append({
                        "name": artist + " - " + title,
                        "duration": duration.seconds,
                        "params": params
                    })

                return songs

    async def get_song(self, song_info: dict) -> dict:
        params = song_info["params"]
        encartist = urllib.parse.quote(params["artist"])
        enctitle = urllib.parse.quote(params["title"])
        encurl = urllib.parse.quote(params["url"])

        download_url = self.downloadFMT.format(
            server_id=params["server"],
            artist=encartist,
            title=enctitle,
            url=encurl,
            song_id=params["index"]
        )

        return {"link": download_url}
