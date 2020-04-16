import discord
import random

from discord.ext import commands

from bot.common.queries import BankSQL

from bot.structures.leaderboard import RichestPlayers

from bot.common.converters import DiscordUser


class Bank(commands.Cog):
    DEFAULT_ROW = [500]

    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx):
        ctx.user_balance = await self.get_user_balance(ctx.author)

    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    @commands.command(name="daily")
    async def daily(self, ctx: commands.Context):
        """ Get some free stuff daily! """

        bal_diff = random.randint(250, 1000)

        await self.update_coins(ctx.author, bal_diff)

        await ctx.send(f"**{ctx.author.display_name}** gained **{bal_diff}** coins!")

    @commands.command(name="balance", usage="<user=None>", aliases=["money", "coins", "bal"])
    async def balance(self, ctx, user: DiscordUser(author_ok=True) = None):
        """ Show the bank balances of the user, or supply an optional user paramater. """
        user = user if user is not None else ctx.author

        bal = await self.get_user_balance(user)

        coins = bal["coins"]

        await ctx.send(f":moneybag: **{user.display_name}** has a total of **{coins:,}** coins")

    async def get_user_balance(self, author: discord.Member):
        async with self.bot.pool.acquire() as con:
            async with con.transaction():
                user = await con.fetchrow(BankSQL.SELECT_USER, author.id)

                if user is None:
                    await con.execute(BankSQL.INSERT_USER, author.id, self.DEFAULT_ROW)

                    user = await con.fetchrow(BankSQL.SELECT_USER, author.id)

        return user

    async def update_coins(self, author, amount):
        q = BankSQL.ADD_COINS if amount > 0 else BankSQL.SUB_COINS

        await self.bot.pool.execute(q, author.id, abs(amount))

    @commands.command(name="coinlb", aliases=["richest", "clb"])
    async def leaderboard(self, ctx: commands.Context):
        """ Show the richest players """

        return await ctx.send(await RichestPlayers(ctx).create())


def setup(bot):
    bot.add_cog(Bank(bot))