import asyncio
import aiohttp


class Request:
    HEADERS = {'User-Agent' : "Magic Browser"}

    def __init__(self, link: str) -> None:
        self.link = link
        self.event_loop = asyncio.get_event_loop()

    def parse_url(self) -> str:
        return self.event_loop.run_until_complete(self.request())

    async def request(self) -> str:
        async with aiohttp.ClientSession(headers=self.HEADERS) as session:
            async with session.get(self.link) as response:

                if response.status != 200:
                    print('Error request!')

                return await response.text()