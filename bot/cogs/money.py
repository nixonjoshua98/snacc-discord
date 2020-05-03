import random

from discord.ext import commands

from bot.structures.leaderboard import MoneyLeaderboard

from bot.common.converters import DiscordUser


class Money(commands.Cog):
    DEFAULT_ROW = [500, 0]

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    @commands.command(name="daily")
    async def daily(self, ctx: commands.Context):
        """ Get some free stuff daily! """

        daily_money = random.randint(250, 1000)

        bank = self.bot.get_cog("Bank")

        await bank.update_coins(ctx.author, daily_money)

        await ctx.send(f"You gained **${daily_money}**!")

    @commands.command(name="balance", usage="<user=None>", aliases=["bal", "money"])
    async def balance(self, ctx, user: DiscordUser(author_ok=True) = None):
        """ Show the bank balances of the user, or supply an optional user. """

        user = user if user is not None else ctx.author

        bank = self.bot.get_cog("Bank")

        target_balance = await bank.get_user_balance(ctx.author)

        coins = target_balance["money"]

        await ctx.send(f":moneybag: **{user.display_name}** has **${coins:,}**.")

    @commands.cooldown(1, 60 * 60, commands.BucketType.user)
    @commands.command(name="steal", usage="<user>", cooldown_after_parsing=True)
    async def steal_coins(self, ctx, user: DiscordUser()):
        """ Attempt to steal from another user. """

        if random.randint(0, 2) != 0:
            return await ctx.send(f"**{ctx.author.display_name}** stole nothing from **{user.display_name}**")

        bank = self.bot.get_cog("Bank")

        target_balance = await bank.get_user_balance(ctx.author)

        max_amount = random.randint(0, int(min(target_balance["money"], ctx.user_balance["money"]) * 0.05))

        stolen_amount = min(5000, max_amount)

        await bank.update_coins(ctx.author, stolen_amount)

        await bank.update_coins(user, -stolen_amount)

        await ctx.send(f"You stole **${stolen_amount:,}** from **{user.display_name}**")

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(name="gift", aliases=["give"], usage="<user> <amount>", cooldown_after_parsing=True)
    async def gift(self, ctx, user: DiscordUser(), amount: int):
        """ Gift some money to another user. """

        bank = self.bot.get_cog("Bank")

        user_balance = await bank.get_user_balance(ctx.author)

        if user_balance["money"] < amount:
            return await ctx.send(f"{ctx.author.mention}, you are too poor to do that.")

        await bank.update_coins(ctx.author, -amount)

        await bank.update_coins(user, amount)

        await ctx.send(f"{ctx.author.display_name} gifted **${amount:,}** to **{user.display_name}**")

    @commands.command(name="moneylb", aliases=["richest", "mlb"])
    async def leaderboard(self, ctx: commands.Context):
        """ Show the richest players. """

        return await ctx.send(await MoneyLeaderboard(ctx).create())


def setup(bot):
    bot.add_cog(Money(bot))
