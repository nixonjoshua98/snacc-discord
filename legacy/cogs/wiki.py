import discord
import itertools

from discord.ext import commands

from bot import utils

from bot.structures.wiki import Wiki


def chunks(ls, n):
    for i in range(0, len(ls), n):
        yield ls[i: i + n]


class WikiCog(commands.Cog, name="Wiki"):
    BASE_URL = "https://autobattlesonline.fandom.com"

    def __init__(self, bot):
        """ Wiki Cog """

        self.__cache = {}

        self.bot = bot

    @commands.command(name="wiki")
    async def wiki(self, ctx):
        """ Alphabetical list of Wiki articles. """

        async def get_wiki():
            r = await utils.requests.get(f"{WikiCog.BASE_URL}/api/v1/Articles/List?limit=50")

            data_ = [
                item_ for item_ in r.json()["items"]
                if item_["title"] != "Auto Battles Online Wiki" and not item_["title"].startswith(("V0.", "Main Page"))
            ]

            return [(k, list(items)) for k, items in itertools.groupby(data_, lambda ele: ele["title"][0])]

        if self.__cache.get("wiki", None) is None:
            self.__cache["wiki"] = await get_wiki()

        data = [(k, list(items)) for k, items in self.__cache["wiki"]]

        embeds = []

        for chunk in chunks(data, 7):
            embed = discord.Embed(title="Auto Battle Online Wiki", url=WikiCog.BASE_URL)

            for k, items in chunk:
                rows = [f"{item['title']}\n{WikiCog.BASE_URL}{item['url']}" for item in items]

                embed.add_field(name=k, value="\n".join(rows), inline=False)

            embeds.append(embed)

        await utils.embeds.create(ctx, embeds)

    @commands.command(name="abilities", aliases=["skills"])
    async def abilities(self, ctx):
        """ Sends the abilities and skills Wiki article. """

        wiki = Wiki("Abilities_and_Skills")

        pages = wiki.get()

        await utils.embeds.create(ctx, pages)


def setup(bot):
    bot.add_cog(WikiCog(bot))
