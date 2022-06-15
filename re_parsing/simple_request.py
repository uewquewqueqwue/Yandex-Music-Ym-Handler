import asyncio
import sys

import aiohttp


class Request:
    """gets page requests"""

    HEADERS: dict = {"User-Agent": "Magic Browser"}

    def __init__(self, url: str):
        self.url: str = url
        self.event_loop = asyncio.get_event_loop()

    def parse_url(self) -> str | None:
        """return html page"""

        return self.event_loop.run_until_complete(self.request())

    async def request(self) -> str | None:
        """request wrapper"""

        async with aiohttp.ClientSession(headers=self.HEADERS) as session:
            try:
                async with session.get(self.url) as response:

                    if response.status == 200:
                        return await response.text()

                    if response.status == 404:
                        print(
                            "Track or album not found, check your link "
                            "for correctness"
                        )
                        return sys.exit()

            except aiohttp.ClientConnectionError:

                return "Error request!"

            except Exception as error:  # pylint: disable = broad-except

                return (
                    f"Unknown error, send her to author. Error: {error}\n"
                    "please contact me(qdissh@gmail.com)"
                )
