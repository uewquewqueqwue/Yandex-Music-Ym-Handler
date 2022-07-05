import asyncio

import aiohttp


class RequestUrls:
    """gets page requests"""

    HEADERS: dict = {"User-Agent": "Magic Browser"}

    def __init__(self, url: str) -> None:
        self.__url = url
        self.event_loop = asyncio.get_event_loop()
        self.status = None

    def parse_url(self) -> str | None:
        """return html page"""
        # print(self.__url)

        return self.event_loop.run_until_complete(self.request())

    def parse_img(self) -> None:
        """return picture"""

        return self.event_loop.run_until_complete(self.download_image())

    async def request(self) -> str | None:
        """request wrapper"""

        async with aiohttp.ClientSession(headers=self.HEADERS) as session:
            async with session.get(self.__url) as response:
                # print(response.status)
                if response.status == 200:
                    self.status = 200
                    return await response.text()

                if response.status == 400:
                    self.status = 400
                    raise TypeError(
                        "Track or album not found, check your link for correctness"
                    )
                if response.status == 404:
                    self.status = 404
                    raise TypeError("Incorrect URL")

    async def download_image(self) -> None:
        """return the downloaded image"""

        async with aiohttp.ClientSession() as session:
            async with session.get(self.__url) as response:
                if response.status == 200:
                    response_bytes = await response.read()
                    with open("image.jpg", "wb") as file:
                        file.write(response_bytes)
