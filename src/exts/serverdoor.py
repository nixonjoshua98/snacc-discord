import discord
from discord.ext import commands

from src.common.models import ServersM


class ServerDoor(commands.Cog, name="Server Door"):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def send_message(guild, message):
        channels = [guild.system_channel] + guild.text_channels

        for c in channels:
            try:
                await c.send(message)

            except (discord.Forbidden, discord.HTTPException):
                continue

            break

    @commands.has_permissions(administrator=True)
    @commands.command(name="toggledoor")
    async def toggle_door(self, ctx):
        """ [Admin] Toggle the messages posted when a member joins or leaves the server. """

        config = await ctx.bot.get_server_config(ctx.guild, refresh=True)

        display_joins = config.get("display_joins", True)

        await ServersM.set(ctx.bot.pool, ctx.guild.id, display_joins=not display_joins)

        await ctx.send(f"Server door: {'`Hidden`' if display_joins else '`Shown`'}")

    @commands.Cog.listener("on_guild_join")
    async def on_guild_join(self, guild):
        """ Called when the bot joins a new server. """

        msg = (
            f"The infamous **{self.bot.user.name}** has graced your ~~lowly~~ server! [{guild.owner.mention}]"
            f"\n"
            f"Commands can be found at `!help`"
            f"\n"
            f"Some commands will need a role to be set. For example, the ArenaStats commands need a `member` role."
            f"Find out how to assign roles by looking at settings (last page of `!help` or `!help Settings`)"
        )

        await self.send_message(guild, msg)

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member):
        """ Called when a member joins a server. """

        svr = await self.bot.get_server_config(member.guild)

        try:
            role = member.guild.get_role(svr["default_role"])

            if role is not None:
                await member.add_roles(role)

        except (discord.Forbidden, discord.HTTPException):
            """ We failed to add the role. """

        if svr.get("display_joins"):
            await self.send_message(member.guild, f"Welcome {member.mention} to {member.guild.name}!")

    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(self, member):
        """ Called when a member leaves a server. """

        svr = await self.bot.get_server_config(member.guild)

        if svr.get("display_joins"):
            msg = f"**{str(member)}** " + (f"({member.nick}) " if member.nick else "") + "has left the server"

            await self.send_message(member.guild, msg)


def setup(bot):
    if not bot.debug:
        bot.add_cog(ServerDoor(bot))
