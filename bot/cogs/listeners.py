import discord

from discord.ext import commands

from bot.common import checks


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

    @commands.Cog.listener("on_guild_join")
    async def on_guild_join(self, guild: discord.Guild):
        bot_info = await self.bot.application_info()

        with open("./bot/data/on_guild_join.txt") as fh:
            template = fh.read()

        welc_msg = template.format(guild=guild, bot=self.bot, bot_info=bot_info)
        owner_dm = f"I joined the server **{guild.name}** owned by **{guild.owner}**"

        await bot_info.owner.send(owner_dm)
        await self._send_system_channel(guild, welc_msg)

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: discord.Member):
        join_msg = f"Welcome {member.mention} to {member.guild.name}!"

        await self._send_system_channel(member.guild, join_msg)

        try:
            svr = await self.bot.get_cog("Settings").get_server_settings(member.guild)

            role = member.guild.get_role(svr["entryrole"])

            if role is not None:
                await member.add_roles(role)

        except discord.Forbidden:
            """ We cannot add the role """

    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(self, member: discord.Member):
        msg = f"**{str(member)}** " + (f"({member.nick}) " if member.nick is not None else "") + "has left the server"

        await self._send_system_channel(member.guild, msg)


class VListeners(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.hidden = True  # Hides Cog from the Help section

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
