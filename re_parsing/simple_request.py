import asyncio
import aiohttp


class Request:
    HEADERS = {'User-Agent' : "Magic Browser"}

    def __init__(self, url: str) -> None:
        self.url = url
        self.event_loop = asyncio.get_event_loop()


    def parse_url(self) -> str:
        return self.event_loop.run_until_complete(self.request())

    async def request(self) -> str:
        async with aiohttp.ClientSession(headers = self.HEADERS) as session:
            try:
                async with session.get(self.url) as response:

                    if response.status == 200:
                        return await response.text()
                    
                    elif response.status == 404: 
                        print('Трек или альбом не найден, проверьте вышу ссылку '
                              'на правильность')
                        exit()

            except aiohttp.ClientConnectionError: 

                return print('Error request!')
            
            except Exception as e:

                return print('Unknown error, send her to author', e)
