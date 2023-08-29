import asyncio

from urllib.parse import urlparse


class QueryProcessor():
    def __init__(self, parsers: tuple) -> None:
        if not isinstance(parsers, tuple):
            raise TypeError("parsers type should be tuple")
        self.parsers = parsers

        if not self.parsers:
            raise ValueError("parsers count should be above 0")

        self.domains_dict = {}

        for parser in self.parsers:
            for domain in parser.domains:
                self.domains_dict[domain] = parser

    async def process_query(self, query: str) -> list:
        res = urlparse(query)
        if res.netloc:
            if res.netloc in self.domains_dict:
                parser = self.domains_dict[res.netloc]
                info = await parser.process_url(query)

                if not isinstance(info, list):
                    return [{"parser": parser, "info": info}]

                songs = []
                for song in info:
                    songs.append({"parser": parser, "info": song})

                return songs
        else:
            search_results = []

            def parser_callback(data: dict, parser):
                search_results.append((parser, data, self.compare(
                    query, data["name"]
                )))

            tasks = []
            for parser in self.parsers:
                tasks.append(asyncio.create_task(parser.search(
                    query, parser_callback
                )))

            await asyncio.gather(*tasks)

            parser, info, weight = max(search_results, key=lambda x: x[2])
            return [{"parser": parser, "info": info}]

    def compare(self, query: str, title: str) -> int:
        query = query.lower()
        title = title.lower()
        q = query.split()
        count = 0
        matches = []
        for word in q:
            if word in title:
                matches.append(word)
                count += 1
        return count
