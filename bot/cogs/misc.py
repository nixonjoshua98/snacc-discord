import discord

from discord.ext import commands

from bot.common.converters import DiscordUser


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ban")
    async def ban(self, ctx: commands.Context, user: DiscordUser()):
        """ Ban a user from the server (give it a go). """

        try:
            username = user.display_name.replace('[BANNED] ', '')

            await user.edit(nick=f"[BANNED] {username[0:20]}")

            await ctx.send("I have banned them successfully.")

        except discord.Forbidden:
            await ctx.send("I failed. The user is too powerful for me to ban!")

        except discord.HTTPException:
            await ctx.send("I have failed to ban this user")

    @commands.is_owner()
    @commands.command(name="execute", alises=["sql"])
    async def execute(self, ctx, query: str):
        """ [Owner Only] Execute an SQL query"""

        await ctx.message.delete()

        try:
            await self.bot.pool.execute(query)

        except Exception as e:
            await ctx.send(f"**Error:** {e.args[0]}")

        else:
            await ctx.send("Query executed.")


def setup(bot):
    bot.add_cog(Misc(bot))
