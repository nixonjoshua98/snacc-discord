import discord

from discord.ext import commands

from bot.common.converters import DiscordUser


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ban")
    async def ban(self, ctx: commands.Context, user: DiscordUser()):
        """ Totally ban a user from this server. """

        try:
            await user.edit(nick=f"[BANNED] {user.display_name[0:20]}")

            await ctx.send("I have banned them successfully.")

        except discord.Forbidden:
            await ctx.send("I failed. The user is too powerful for me to ban!")

        except discord.HTTPException:
            await ctx.send("I have failed to ban this user")

    @commands.command(name="unban")
    async def unban(self, ctx: commands.Context, user: DiscordUser()):
        """ Unban a user from this server. """

        try:
            await user.edit(nick=user.display_name.replace("[BANNED]", ""))

            await ctx.send("I have unbanned them successfully.")

        except discord.Forbidden:
            await ctx.send("I failed. The user is too powerful for me to unban!")

        except discord.HTTPException:
            await ctx.send("I have failed to unban this user")


def setup(bot):
    bot.add_cog(Misc(bot))
