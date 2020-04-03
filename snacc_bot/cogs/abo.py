import discord

from discord.ext import commands

from src.common.database import DBConnection
from snacc_bot.common.leaderboards import ABOLeaderboard


class ABO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.lb = ABOLeaderboard()

    @commands.command(name="set", aliases=["s"], help="Set your stats")
    async def set_stats(self, ctx, level: int, trophies: int):
        with DBConnection() as con:
            params = (ctx.author.id, level, trophies)
            con.cur.execute(con.get_query("update-user-abo.sql"), params)

        await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

    @commands.command(name="me", help="Display your stats")
    async def get_stats(self, ctx: commands.Context):
        with DBConnection() as con:
            params = (ctx.author.id, )
            con.cur.execute(con.get_query("select-user-abo-stats.sql"), params)

            user = con.cur.fetchone()

        if user is None:
            return await ctx.send(f":x: **{ctx.author.display_name}**, I found no stats for you")

        embed = self.bot.create_embed(title=ctx.author.display_name, thumbnail=ctx.author.avatar_url)

        embed.add_field(name="ABO Stats", value=f":joystick: **{user.lvl}**\n:trophy: **{user.trophies:,}**")

        return await ctx.send(embed=embed)

    @commands.command(name="setuser", help="Set another user stats")
    async def set_user(self, ctx, user: discord.Member, level: int, trophies: int):
        with DBConnection() as con:
            params = (user.id, level, trophies)
            con.cur.execute(con.get_query("update-user-abo.sql"), params)

        await ctx.send(f"**{user.display_name}** :thumbsup:")

    @commands.command(name="alb", help="Display the ABO leaderboard")
    async def leaderboard(self, ctx: commands.Context):
        await ctx.send(self.lb.get(ctx.author))


def setup(bot):
    bot.add_cog(ABO(bot))
