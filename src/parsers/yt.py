import yt_dlp as youtube_dl

from .base_parser import BaseParser

import asyncio


class YT(BaseParser):
    ydl_opts_flat = {
            'format': 'bestaudio',
            'quiet': True,
            'ignoreerrors': True,
            # Allows to get list of urls from playlist without downloading webpage
            'extract_flat': 'in_playlist',
        }
    ydl_opts = {
            'format': 'bestaudio',
            'quiet': True,
            'ignoreerrors': True,
        }
    domains = [
        "youtube.com",
        "youtu.be",
        "www.youtube.com",
        "www.youtu.be"
    ]
    name = "YT"

    def __init__(self):
        super().__init__(self.__class__.name, self.__class__.domains)
    
    async def search(self, query:str, callback:callable)->dict:
        with youtube_dl.YoutubeDL(self.ydl_opts_flat) as ydl:

            loop = asyncio.get_running_loop()

            url = f"ytsearch:{query}"
            download = False

            args = (url, download)
            info = await loop.run_in_executor(None, ydl.extract_info, *args)
          
            if not info:
                return
            if info.get('_type') == 'playlist':
                if not info['entries']:
                    return
                entry = info['entries'][0]
        
        params = {"url": entry["url"]}

        if callback:
            callback({
                "name": entry["title"],
                "duration": int(entry["duration"]),
                "params": params
                },
            self
            )
        return {
            "name": entry["title"],
            "duration": int(entry["duration"]),
            "params": params
        }

    
    async def process_url(self, url:str)->list:
        with youtube_dl.YoutubeDL(self.ydl_opts_flat) as ydl:

            loop = asyncio.get_running_loop()
            download = False
            args = (url, download)
            info = await loop.run_in_executor(None, ydl.extract_info, *args)

            if not info:
                return
            
            if info.get('_type') != 'playlist':
                params = {"url": info["webpage_url"]}
                return [{"name": info["title"], "duration": int(info["duration"]),"params": params}]
            
            songs = []
            if info['entries']:
                entries = [entry for entry in info.get('entries') if entry is not None]
                for entry in entries:
                    params = {"url": entry["url"]}
                    songs.append({
                        "name": entry["title"],
                        "duration": int(entry["duration"]),
                        "params": params
                    })
            return songs


    async def get_song(self, song_info:dict)->dict:
        # download webpage to get direct url of video
        ydl_opts = {
            'format': 'bestaudio',
            'quiet': True,
            'ignoreerrors': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # Searching for the first available video to extract info
            loop = asyncio.get_running_loop()

            url = song_info["params"]["url"]
            download = False

            args = (url, download)
            info = await loop.run_in_executor(None, ydl.extract_info, *args)
            if not info:
                return
            return {"link": info['url'], "image": info["thumbnail"]}
