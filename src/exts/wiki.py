import httpx
import discord
import itertools

from discord.ext import commands

from src.menus.pagemenu import PageMenu


def chunk_list(ls, n):
    for i in range(0, len(ls), n):
        yield ls[i: i + n]


class Wiki(commands.Cog):
    """ Commands for autobattlesonline.fandom.com/ """

    BASE_URL = "https://autobattlesonline.fandom.com"

    def __init__(self, bot):
        self._cache = {}

        self.bot = bot

    @commands.command(name="wiki")
    async def wiki(self, ctx):
        """ Alphabetical list of Wiki articles. """

        # Cache the Wiki to avoid sending a request every command invoked
        if self._cache.get("wiki") is None:
            self._cache["wiki"] = await self.get_wiki_links()

        data = self._cache["wiki"]

        embeds, chunks = [], list(chunk_list(data, 5))

        # Pages
        for i, chunk in enumerate(chunks, start=1):
            embed = discord.Embed(title="Auto Battle Online Wiki", url=Wiki.BASE_URL)

            # A, [Links...]
            for letter, links in chunk:
                rows = [f"{item['title']}\n{Wiki.BASE_URL}{item['url']}" for item in links]

                embed.add_field(name=letter, value="\n".join(rows), inline=False)

            embed.set_footer(text=f"{ctx.bot.user.name} | Page {i}/{len(chunks)}", icon_url=ctx.bot.user.avatar_url)

            embeds.append(embed)

        await PageMenu(ctx.bot, embeds, timeout=60.0).send(ctx)

    @staticmethod
    async def get_wiki_links() -> list:
        def valid_secton(section):
            title = section["title"]

            return not title.startswith(("V0", "V1", "Main Page", "Auto Battles Online Wiki"))

        async with httpx.AsyncClient() as client:
            r = await client.get(f"{Wiki.BASE_URL}/api/v1/Articles/List?limit=50")

        data_ = r.json()
        data_ = [item_ for item_ in data_["items"] if valid_secton(item_)]

        # Group each link by the character it starts with
        return [(k, list(items)) for k, items in itertools.groupby(data_, lambda ele: ele["title"][0])]


def setup(bot):
    bot.add_cog(Wiki(bot))
