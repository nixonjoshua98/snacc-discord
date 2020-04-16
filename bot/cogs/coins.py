import random

from discord.ext import commands

from bot.common.converters import DiscordUser, IntegerRange


class Coins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.bank = self.bot.get_cog("Bank")

    async def cog_before_invoke(self, ctx):
        ctx.user_balance = await self.bank.get_user_balance(ctx.author)

    @commands.cooldown(1, 60 * 60, commands.BucketType.user)
    @commands.command(name="steal", usage="<user>")
    async def steal_coins(self, ctx, user: DiscordUser()):
        """ Steal some coins from another user! """

        if random.randint(0, 2) != 0:
            return await ctx.send(f"**{ctx.author.display_name}** stole nothing from **{user.display_name}**")

        target_balances = await self.bank.get_user_balance(user)

        amount = random.randint(0, int(min(target_balances["coins"], ctx.user_balance["coins"]) * 0.05))

        await self.bank.update_coins(ctx.author, amount)
        await self.bank.update_coins(user, -amount)
        await ctx.send(f"**{ctx.author.mention}** stole **{amount:,}** coins from **{user.mention}**")

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(name="gift", aliases=["give"], usage="<user> <amount>")
    async def gift(self, ctx, user: DiscordUser(), amount: IntegerRange(1, 100_000)):
        """ Gift some coins to another user """

        if ctx.user_balance["coins"] < amount:
            return await ctx.send(f"{ctx.author.mention}, you do not have enough coins.")

        await self.bank.update_coins(ctx.author, -amount)
        await self.bank.update_coins(user, amount)
        await ctx.send(f"{ctx.author.mention} gifted **{amount:,}** coins to **{user.mention}**")


def setup(bot):
    bot.add_cog(Coins(bot))