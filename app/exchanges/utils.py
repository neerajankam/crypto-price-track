import aiohttp


async def make_request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response_json = await response.json()
    return response_json
