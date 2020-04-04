import os
import discord

from discord.ext import commands

from bot.common import utils


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.template_messages = {}

        for f in ("on_guild_join",):
            path = utils.resource(f"{f}.txt")

            with open(path, "r") as fh:
                self.template_messages[f] = fh.read()

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


def setup(bot):
    bot.add_cog(Listeners(bot))