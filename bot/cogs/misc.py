import discord

from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ban")
    async def ban(self, ctx: commands.Context, user: discord.Member):
        """ Ban a user from the server. """

        try:
            await user.edit(nick=f"[BANNED] {user.display_name.replace('[BANNED] ', '')}")

            await ctx.send("I have banned them successfully.")

        except discord.Forbidden:
            await ctx.send("I failed. The user is too powerful for me to ban!")

        except discord.HTTPException:
            await ctx.send("I have failed to ban this user")


def setup(bot):
    bot.add_cog(Misc(bot))
