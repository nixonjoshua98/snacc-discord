from discord.ext import commands


class Fishing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(10, 60 * 60, commands.BucketType.user)
    @commands.command(name="f", help="Fishing!")
    async def fish(self, ctx: commands.Context):
        return await ctx.send(":fish: Work in Progress! :fish:")

    @commands.command(name="flb", help="Leaderboard")
    async def leaderboard(self, ctx: commands.Context):
        return await ctx.send(":fish: Work in Progress! :fish:")


def setup(bot):
    bot.add_cog(Fishing(bot))
