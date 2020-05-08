import random

from discord.ext import commands

from bot import utils

from bot.common.queries import BankSQL
from bot.structures.leaderboard import MoneyLeaderboard
from bot.common.converters import DiscordUser, Range


class Money(commands.Cog, command_attrs=(dict(cooldown_after_parsing=True))):
    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.bals = await utils.bank.get_ctx_users_bals(ctx)

    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    @commands.command(name="daily")
    async def daily(self, ctx):
        """ Get some free coins! """

        initial_author_bal = ctx.bals["author"]["money"]

        daily_money = random.randint(250, 2_500)

        await self.bot.pool.execute(BankSQL.SET_MONEY, ctx.author.id, initial_author_bal + daily_money)

        await ctx.send(f"You gained **${daily_money}**!")

    @commands.command(name="balance", aliases=["bal", "money"])
    async def balance(self, ctx, target: DiscordUser(author_ok=True) = None):
        """ Show the bank balances of the user, or supply an optional target user. """

        bal = ctx.bals["target" if target is not None else "author"]["money"]

        target = target if target is not None else ctx.author

        await ctx.send(f":moneybag: **{target.display_name}** has **${bal:,}**.")

    @commands.cooldown(1, 60 * 60, commands.BucketType.user)
    @commands.command(name="steal")
    async def steal_coins(self, ctx, target: DiscordUser()):
        """ Attempt to steal from another user. """

        if random.randint(0, 2) != 0:
            return await ctx.send(f"You stole nothing from **{target.display_name}**")

        initial_author_bal = ctx.bals["author"]["money"]
        initial_target_bal = ctx.bals["target"]["money"]

        max_amount = random.randint(1, int(min(initial_author_bal, initial_target_bal) * 0.05))

        stolen_amount = min(10_000, max_amount)

        await self.bot.pool.execute(BankSQL.SET_MONEY, ctx.author.id, initial_author_bal + stolen_amount)
        await self.bot.pool.execute(BankSQL.SET_MONEY, target.id,     initial_author_bal - stolen_amount)

        await ctx.send(f"You stole **${stolen_amount:,}** from **{target.display_name}**")

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(name="gift", aliases=["give"])
    async def gift(self, ctx, target: DiscordUser(), amount: Range(1, 1_000_000)):
        """ Gift some money to another user. """

        initial_author_bal = ctx.bals["author"]["money"]

        if initial_author_bal < amount:
            return await ctx.send(f"{ctx.author.mention}, you are too poor to do that.")

        await self.bot.pool.execute(BankSQL.SET_MONEY, ctx.author.id, initial_author_bal - amount)
        await self.bot.pool.execute(BankSQL.SET_MONEY, target.id,     initial_author_bal + amount)

        await ctx.send(f"You gave **${amount:,}** to **{target.display_name}**")

    @commands.command(name="moneylb", aliases=["richest", "mlb"])
    async def leaderboard(self, ctx: commands.Context):
        """ Show the richest players. """

        return await ctx.send(await MoneyLeaderboard(ctx).create())


def setup(bot):
    bot.add_cog(Money(bot))
