import discord

from discord.ext import commands

from bot.common import utils, checks


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def _send_system_channel(guild: discord.Guild, message: str):
        if guild.system_channel:
            try:
                await guild.system_channel.send(message)
            except discord.Forbidden:
                """ Bot doesn't have access to the system channel """

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        with open(utils.resource("on_guild_join.txt"), "r") as fh:
            template = fh.read()

        bot_info = await self.bot.application_info()

        welc_msg = template.format(guild=guild, bot=self.bot, bot_info=bot_info)
        owner_dm = f"I joined the server **{guild.name}** owned by **{guild.owner}**"

        await bot_info.owner.send(owner_dm)
        await self._send_system_channel(guild, welc_msg)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        join_msg = f"Welcome {member.mention} to {member.guild.name}!"

        await self._send_system_channel(member.guild, join_msg)

        try:
            role = utils.get_tagged_role(self.bot.svr_cache, member.guild, "default", ignore_exception=True)

            await member.add_roles(role, atomic=True)

        except AttributeError:
            """ Simply hasn't been set yet """

        except discord.Forbidden as e:
            await self._send_system_channel(member.guild, f":x: **{e.args[0]}**")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        msg = f"**{str(member)}** " + (f"({member.nick}) " if member.nick is not None else "") + "has left the server"

        await self._send_system_channel(member.guild, msg)


class VListeners(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.hidden = True

    async def cog_check(self, ctx: commands.Context):
        return await self.bot.is_owner(ctx.author) or checks.author_is_server_owner(ctx)

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
    bot.add_cog(Listeners(bot))
    bot.add_cog(VListeners(bot))
