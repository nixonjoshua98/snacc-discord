import discord
from discord.ext import commands

import itertools

from snacc import utils
from snacc.structs.menus import Menu


def chunk_list(ls, n):
    for i in range(0, len(ls), n):
        yield ls[i: i + n]


class Wiki(commands.Cog):
    BASE_URL = "https://autobattlesonline.fandom.com"

    def __init__(self, bot):
        self.__cache = {}

        self.bot = bot

    @commands.command(name="wiki")
    async def wiki(self, ctx):
        """ Alphabetical list of Wiki articles. """

        async def get_wiki():
            def valid_secton(section):
                title = section["title"]

                return not title.startswith(("V0.", "Main Page", "Auto Battles Online Wiki"))

            r = await utils.get(f"{Wiki.BASE_URL}/api/v1/Articles/List?limit=50")

            data_ = r.json()
            data_ = [item_ for item_ in data_["items"] if valid_secton(item_)]

            return [(k, list(items)) for k, items in itertools.groupby(data_, lambda ele: ele["title"][0])]

        # Cache the Wiki to avoid sending a request every command invoked
        data = self.__cache["wiki"] = await get_wiki() if self.__cache.get("wiki") is None else self.__cache["wiki"]

        embeds, chunks = [], list(chunk_list(data, 5))

        # Pages
        for i, chunk in enumerate(chunks, start=1):
            embed = discord.Embed(title="Auto Battle Online Wiki", url=Wiki.BASE_URL)

            # A, [Sections...]
            for letter, links in chunk:
                rows = [f"{item['title']}\n{Wiki.BASE_URL}{item['url']}" for item in links]

                embed.add_field(name=letter, value="\n".join(rows), inline=False)

            embed.set_footer(text=f"{ctx.bot.user.name} | Page {i}/{len(chunks)}", icon_url=ctx.bot.user.avatar_url)

            embeds.append(embed)

        await Menu(embeds, timeout=60, delete_after=False).send(ctx)


def setup(bot):
    bot.add_cog(Wiki(bot))
