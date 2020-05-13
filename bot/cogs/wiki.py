import discord

from discord.ext import commands

from bot.structures.wiki import Wiki


class WikiCog(commands.Cog, name="Wiki"):
    def __init__(self, bot):
        """ Wiki Cog """

        self.bot = bot

    @commands.command(name="abilities", aliases=["skills"])
    async def abilities(self, ctx):
        wiki = Wiki("Abilities_and_Skills")

        page = wiki.get()

        embed = discord.Embed(title=page.title, description=page.desc, url=wiki.url)

        embed.add_field(name=page.title, value=page.pages[-1][0:1024])

        embed.set_footer(text=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(WikiCog(bot))
