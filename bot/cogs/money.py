import random

from discord.ext import commands

from bot.structures.leaderboard import MoneyLeaderboard

from bot.common.converters import DiscordUser, IntegerRange


class Money(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx: commands.Context):
        bank = self.bot.get_cog("Bank")

        ctx.balances_ = await bank.get_users_balances_in_args(ctx)

    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    @commands.command(name="daily")
    async def daily(self, ctx: commands.Context):
        """ Get some free stuff daily! """

        daily_money = random.randint(250, 1000)

        await self.bot.get_cog("Bank").update_money(ctx.author, daily_money)

        await ctx.send(f"You gained **${daily_money}**!")

    @commands.command(name="balance", aliases=["bal", "money"])
    async def balance(self, ctx, target: DiscordUser(author_ok=True) = None):
        """ Show the bank balances of the user, or supply an optional target user. """

        bal = ctx.balances_["target" if target is not None else "author"]["money"]

        target = target if target is not None else ctx.author

        await ctx.send(f":moneybag: **{target.display_name}** has **${bal:,}**.")

    @commands.cooldown(1, 60 * 60, commands.BucketType.user)
    @commands.command(name="steal", usage="<user>", cooldown_after_parsing=True)
    async def steal_coins(self, ctx, target: DiscordUser()):
        """ Attempt to steal from another user. """

        if random.randint(0, 2) != 0:
            return await ctx.send(f"You stole nothing from **{target.display_name}**")

        bank = self.bot.get_cog("Bank")

        author_bal, target_bal = ctx.balances_["author"]["money"], ctx.balances_["target"]["money"]

        max_amount = random.randint(0, int(min(author_bal, target_bal) * 0.05))

        stolen_amount = min(5000, max_amount)

        await bank.update_money(ctx.author, stolen_amount)

        await bank.update_money(target, -stolen_amount)

        await ctx.send(f"You stole **${stolen_amount:,}** from **{target.display_name}**")

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(name="gift", aliases=["give"], usage="<target> <amount>", cooldown_after_parsing=True)
    async def gift(self, ctx, target: DiscordUser(), amount: IntegerRange(1, 1_000_000)):
        """ Gift some money to another user. """

        author_bal = ctx.balances_["author"]["money"]

        if author_bal < amount:
            return await ctx.send(f"{ctx.author.mention}, you are too poor to do that.")

        bank = self.bot.get_cog("Bank")

        await bank.update_money(ctx.author, -amount)
        await bank.update_money(target, amount)

        await ctx.send(f"You gave **${amount:,}** to **{target.display_name}**")

    @commands.command(name="moneylb", aliases=["richest", "mlb"])
    async def leaderboard(self, ctx: commands.Context):
        """ Show the richest players. """

        return await ctx.send(await MoneyLeaderboard(ctx).create())


def setup(bot):
    bot.add_cog(Money(bot))
