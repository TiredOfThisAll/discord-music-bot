import yt_dlp as youtube_dl
from requests import get


async def extract_full_info(urls, music):
    # download webpage to get direct url of video
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'ignoreerrors': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        if urls:
            info = ''
            # Searching for the first available video to extract info
            while not info and urls:
                info = ydl.extract_info(urls[0]["url"], download=False)
                urls.pop(0)
            music.append({"title": info["title"], "link": info['url'], "image": info["thumbnail"]})
        return music, urls


async def search_youtube(query, urls):
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'ignoreerrors': True,
        # Allows to get list of urls from playlist without downloading webpage
        'extract_flat': 'in_playlist',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        entries = []
        try:
            get(query)
        except:
            # Search video on youtube by user query
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            if info.get('_type') == 'playlist':
                info = info['entries'][0]
        else:
            # Extract video info by url
            info = ydl.extract_info(query, download=False)
            if info.get('_type') == 'playlist':
                entries = [entry for entry in info.get('entries') if entry is not None]
            else:
                info["url"] = info["webpage_url"]

        if entries:
            for entry in entries:
                urls.append({"url": entry["url"], "title": entry["title"]})
        else:
            urls.append({"url": info["url"], "title": info["title"]})
        return urls