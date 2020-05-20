import httpx


async def get(url):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)

    return r