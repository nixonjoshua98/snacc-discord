import discord

from snacc import utils

from discord.ext import commands


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_guild_join")
    async def on_guild_join(self, guild):
        """ Called when the legacy joins a new server (guild). """

        bot_info = await self.bot.application_info()

        with open(".\\snacc\\data\\on_guild_join.txt") as fh:
            template = fh.read()

        msg = template.format(guild=guild, bot=self.bot, bot_info=bot_info)

        await utils.dis.send_system_channel(guild, msg)

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member):
        """ Called when a member joins a server. """

        msg = f"Welcome {member.mention} to {member.guild.name}!"

        try:
            svr = await self.bot.get_server(member.guild)

            role = member.guild.get_role(svr["defaultrole"])

            if role is not None:
                await member.add_roles(role)

        except (discord.Forbidden, discord.HTTPException) as e:
            """ We failed to add the role """

        await utils.dis.send_system_channel(member.guild, msg)

    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(self, member):
        """ Called when a member leaves (or kicked) from a server. """

        msg = f"**{str(member)}** " + (f"({member.nick}) " if member.nick else "") + "has left the server"

        await utils.dis.send_system_channel(member.guild, msg)


def setup(bot):
    import os

    if not os.getenv("DEBUG", False):
        bot.add_cog(Listeners(bot))
