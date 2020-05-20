import os

from discord.ext import commands


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="lines")
    async def lines(self, ctx):
        """ Count the number of lines within the legacy. """
        lines = 0

        for root, dirs, files in os.walk("./legacy/"):
            for f in files:
                if f.endswith(".py"):
                    path = os.path.join(root, f)

                    with open(path, "r") as fh:
                        for line in fh.read().splitlines():
                            if line:
                                lines += 1

        await ctx.send(f"I am made up of **{lines:,}** lines of code.")


def setup(bot):
    bot.add_cog(Stats(bot))
