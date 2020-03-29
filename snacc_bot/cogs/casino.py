from discord.ext import commands


class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return True

    @commands.cooldown(1, 60 * 30, commands.BucketType.user)
    @commands.command(name="flip", aliases=["fl"], help="Flip a coin [30m]")
    async def flip(self, ctx: commands.Context):
        return ctx.send("56")


def setup(bot):
    bot.add_cog(Casino(bot))