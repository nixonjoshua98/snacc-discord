import discord

from discord.ext import commands

from bot.common import utils, checks


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.template_messages = {}

        path = utils.resource("on_guild_join.txt")

        with open(path, "r") as fh:
            self.template_messages["on_guild_join"] = fh.read()

    @staticmethod
    async def _send_system_channel(guild: discord.Guild, message: str):
        if guild.system_channel:
            await guild.system_channel.send(message)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        bot_info = await self.bot.application_info()

        welc_msg = self.template_messages["on_guild_join"].format(guild=guild, bot=self.bot, bot_info=bot_info)
        owner_dm = f"I joined the server **{guild.name}** owned by **{guild.owner}**"

        await bot_info.owner.send(owner_dm)
        await self._send_system_channel(guild, welc_msg)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        join_msg = f"Welcome {member.mention} to {member.guild.name}!"

        await self._send_system_channel(member.guild, join_msg)

        config = self.bot.svr_cache.get(member.guild.id)

        try:
            role = discord.utils.get(member.guild.roles, id=config.roles["default"])

            await member.add_roles(role, atomic=True)

        except (AttributeError, KeyError):
            pass

        except discord.Forbidden as e:
            await self._send_system_channel(member.guild, f":x: **{e.args[0]}**")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        remove_msg = f"{member.display_name} **({member.mention})** has left the server :frowning:"

        await self._send_system_channel(member.guild, remove_msg)


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
    bot.add_cog(Listeners(bot))
    bot.add_cog(VListeners(bot))