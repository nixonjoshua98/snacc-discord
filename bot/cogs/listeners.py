import discord

from discord.ext import commands

from bot.common import checks

GUILD_JOIN_TEXT = """
The infamous **{bot.user.name}** has graced your ~~lowly~~ server! [{guild.owner.mention}]

My default prefix is **{bot.default_prefix}**...obviously

**__Help__**
- **{bot.default_prefix}help**...durp
- Contact my almighty creator **{bot_info.owner}**

**__Invite Me__**
https://discordapp.com/oauth2/authorize?client_id=666616515436478473&scope=bot&permissions=8
"""


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
        bot_info = await self.bot.application_info()

        welc_msg = GUILD_JOIN_TEXT.format(guild=guild, bot=self.bot, bot_info=bot_info)
        owner_dm = f"I joined the server **{guild.name}** owned by **{guild.owner}**"

        await bot_info.owner.send(owner_dm)
        await self._send_system_channel(guild, welc_msg)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        join_msg = f"Welcome {member.mention} to {member.guild.name}!"

        await self._send_system_channel(member.guild, join_msg)

        try:
            svr = await self.bot.get_cog("Settings").get_server(member.guild)

            role = member.guild.get_role(svr["entryrole"])

            if role is not None:
                await member.add_roles(role)

        except discord.Forbidden:
            """ We cannot add the role """

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
