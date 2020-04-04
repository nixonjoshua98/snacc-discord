from discord.ext import commands

from bot.common import checks


class VListeners(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return await self.bot.is_owner(ctx.author) or await checks.author_is_server_owner(ctx)

    @commands.command(name="gjoin", aliases=["gj"])
    async def on_guild_join_command(self, ctx: commands.Context):
        listener_cog = self.bot.get_cog("Listeners")

        return await listener_cog.on_guild_join(ctx.guild)

    @commands.command(name="mjoin", aliases=["mj"])
    async def on_member_join_command(self, ctx: commands.Context):
        listener_cog = self.bot.get_cog("Listeners")

        return await listener_cog.on_member_join(ctx.author)

    @commands.command(name="mremove", aliases=["mr"])
    async def on_member_remove_command(self, ctx: commands.Context):
        listener_cog = self.bot.get_cog("Listeners")

        return await listener_cog.on_member_remove(ctx.author)


def setup(bot):
    bot.add_cog(VListeners(bot))
