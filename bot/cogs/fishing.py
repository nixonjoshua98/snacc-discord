from discord.ext import commands

from bot.common import (
    checks,
)

from bot.common import (
    ChannelTags,
)


class Fishing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        return checks.channel_has_tag(ctx, ChannelTags.GAME)

    @commands.cooldown(10, 60 * 60, commands.BucketType.user)
    @commands.command(name="f", help="Fishing!")
    async def fish(self, ctx: commands.Context):
        return await ctx.send(":fish: Work in Progress! :fish:")

    @commands.command(name="flb", help="Leaderboard")
    async def leaderboard(self, ctx: commands.Context):
        return await ctx.send(":fish: Work in Progress! :fish:")


def setup(bot):
    bot.add_cog(Fishing(bot))
