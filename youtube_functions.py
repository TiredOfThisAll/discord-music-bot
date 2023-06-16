import yt_dlp as youtube_dl
from requests import get


async def extract_full_info(queue_info):
    # download webpage to get direct url of video
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'ignoreerrors': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        if queue_info["video_urls"]:
            info = ''
            # Searching for the first available video to extract info
            while not info and queue_info["video_urls"]:
                info = ydl.extract_info(queue_info["video_urls"][0]["url"], download=False)
                queue_info["video_urls"].pop(0)
            queue_info["extracted_video_info"].append({"title": info["title"], "link": info['url'], "image": info["thumbnail"]})
        return queue_info


async def search_youtube(query, queue_info):
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
                queue_info["video_urls"].append({"url": entry["url"], "title": entry["title"]})
        else:
            queue_info["video_urls"].append({"url": info["url"], "title": info["title"]})
        return queue_info