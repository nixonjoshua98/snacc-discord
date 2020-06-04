import discord
from discord.ext import commands

from snacc.common import MAIN_SERVER


async def send_system_channel(guild, message):
    try:
        await guild.system_channel.send(message)

    except (AttributeError, discord.Forbidden, discord.HTTPException):
        """ Failed """


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_guild_join")
    async def on_guild_join(self, guild):
        """ Called when the bot joins a new server. """

        msg = f"The infamous **{self.bot.user.name}** has graced your ~~lowly~~ server! [{guild.owner.mention}]"

        await send_system_channel(guild, msg)

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member):
        """ Called when a member joins a server. """

        msg = f"Welcome {member.mention} to {member.guild.name}!"

        try:
            svr = await self.bot.get_server(member.guild)

            role = member.guild.get_role(svr["default_role"])

            if role is not None:
                await member.add_roles(role)

            if member.guild.id == MAIN_SERVER:
                await member.send(f"Welcome to {member.guild.name}! Introduce yourself to the server!")

        except (discord.Forbidden, discord.HTTPException):
            """ We failed to add the role or send the DM. """

        await send_system_channel(member.guild, msg)

    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(self, member):
        """ Called when a member leaves a server. """

        msg = f"**{str(member)}** " + (f"({member.nick}) " if member.nick else "") + "has left the server"

        await send_system_channel(member.guild, msg)


def setup(bot):
    import os

    if not os.getenv("DEBUG", False):
        bot.add_cog(Listeners(bot))
