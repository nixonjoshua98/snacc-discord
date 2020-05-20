import random

from discord.ext import commands

from bot import utils

from bot.common.queries import BankSQL
from bot.common.converters import DiscordUser, Range

from bot.structures.leaderboard import MoneyLeaderboard


class Money(commands.Cog, command_attrs=(dict(cooldown_after_parsing=True))):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    @commands.command(name="daily")
    async def daily(self, ctx):
        """ Get some free coins! """

        daily_money = random.randint(250, 2_500)

        await self.bot.pool.execute(BankSQL.ADD_MONEY, ctx.author.id, daily_money)

        await ctx.send(f"You gained **${daily_money}**!")

    @commands.command(name="balance", aliases=["bal", "money"])
    async def balance(self, ctx, target: DiscordUser(author_ok=True) = None):
        """ Show the bank balances of the user, or supply an optional target user. """

        target = target if target is not None else ctx.author

        bal = await utils.bank.get_user_bal(ctx.bot.pool, target)

        await ctx.send(f":moneybag: **{target.display_name}** has **${bal['money']:,}**.")

    @commands.cooldown(1, 60 * 60, commands.BucketType.user)
    @commands.command(name="steal")
    async def steal_coins(self, ctx, target: DiscordUser()):
        """ Attempt to steal from another user. """

        if random.randint(0, 2) != 0:
            return await ctx.send(f"You stole nothing from **{target.display_name}**")

        bals = await utils.bank.get_users_bals(ctx.bot.pool, author=ctx.author, target=target)

        author_bal = bals["author"]
        target_bal = bals["target"]

        max_amount = random.randint(1, int(min(author_bal["money"], target_bal["money"]) * 0.05))

        stolen_amount = min(10_000, max_amount)

        await self.bot.pool.execute(BankSQL.ADD_MONEY, ctx.author.id, stolen_amount)
        await self.bot.pool.execute(BankSQL.SUB_MONEY, target.id,     stolen_amount)

        await ctx.send(f"You stole **${stolen_amount:,}** from **{target.display_name}**")

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(name="gift", aliases=["give"])
    async def gift(self, ctx, target: DiscordUser(), amount: Range(1, 1_000_000)):
        """ Gift some money to another user. """

        bal = await utils.bank.get_author_bal(ctx)

        if bal["money"] < amount:
            raise commands.CommandError("You do not have enough money.")

        await self.bot.pool.execute(BankSQL.SUB_MONEY, ctx.author.id, amount)
        await self.bot.pool.execute(BankSQL.ADD_MONEY, target.id,     amount)

        await ctx.send(f"You gave **${amount:,}** to **{target.display_name}**")

    @commands.command(name="moneylb", aliases=["richest", "mlb"])
    async def leaderboard(self, ctx: commands.Context):
        """ Show the richest players. """

        return await ctx.send(await MoneyLeaderboard(ctx).create())


def setup(bot):
    bot.add_cog(Money(bot))
