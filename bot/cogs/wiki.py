import discord
import requests

from discord.ext import commands


from bs4 import BeautifulSoup


class Wiki(commands.Cog):
    def __init__(self, bot):
        """ Wiki Cog """

        self.bot = bot

        self.cache = {}

    @commands.command(name="abilities", aliases=["skills"])
    async def abilities(self, ctx):
        if self.cache.get("abilities", None) is None:
            r = requests.get("https://autobattlesonline.fandom.com/wiki/Abilities_and_Skills")

            self.cache["abilities"] = r.content

        content = self.cache["abilities"]

        soup = BeautifulSoup(content, "html.parser")

        data = soup.find_all(lambda tag: tag.name in {"p", "h1", "h2", "h3", "h4", "h5"})
        data = data[:-8]

        title, desc = data[0], data[1]

        embed = discord.Embed(title=title.text, description=desc.text)

        vals = []

        for i, ele in enumerate(data[3:]):
            text = ele.text.strip()
            text = text.replace("[edit | edit source]", "")
            text = text.replace("Base Description:", "")

            if text.lower() in {"\n", "contents", ""}:
                continue

            if ele.name == "h2":
                vals.append(f"\n\n**{text}**\n")

            elif ele.name == "h3":
                vals.append(f"\n\n**{text}**")

            elif ele.name == "h4":
                vals.append(f"__{text}__\n" if data[i - 1].tag == "p" else f"\n__{text}__\n")

            else:
                vals.append(text + " ")

        msg = ''.join(vals)

        embed.add_field(name=title.text, value=msg)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Wiki(bot))
