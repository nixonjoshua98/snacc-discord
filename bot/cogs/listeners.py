import discord

from discord.ext import commands


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

            except discord.HTTPException:
                """ Failed for some other reason """

    @commands.Cog.listener("on_guild_join")
    async def on_guild_join(self, guild: discord.Guild):
        bot_info = await self.bot.application_info()

        with open("./bot/data/on_guild_join.txt") as fh:
            template = fh.read()

        welc_msg = template.format(guild=guild, bot=self.bot, bot_info=bot_info)
        owner_dm = f"I joined the server **{guild.name}** owned by **{guild.owner}**"

        await self._send_system_channel(guild, welc_msg)
        await bot_info.owner.send(owner_dm)

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: discord.Member):
        join_msg = f"Welcome {member.mention} to {member.guild.name}!"

        await self._send_system_channel(member.guild, join_msg)

        try:
            svr = await self.bot.get_server(member.guild)

            role = member.guild.get_role(svr["entryrole"])

            if role is not None:
                await member.add_roles(role)

        except discord.Forbidden:
            """ We cannot add the role """

    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(self, member: discord.Member):
        msg = f"**{str(member)}** " + (f"({member.nick}) " if member.nick is not None else "") + "has left the server"

        await self._send_system_channel(member.guild, msg)


def setup(bot):
    bot.add_cog(Listeners(bot))
