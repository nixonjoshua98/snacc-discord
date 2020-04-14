import random

from discord.ext import commands

from bot.common import CoinsSQL

from bot.common.converters import NotAuthorOrBot, IntegerRange

from bot.common.database import DBConnection

from bot.structures import CoinLeaderboard


class Coins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.leaderboards = dict()

    @commands.command(name="bal", aliases=["balance", "coins"], help="Coin balance")
    async def balance(self, ctx: commands.Context):
        with DBConnection() as con:
            con.cur.execute(CoinsSQL.SELECT_USER, (ctx.author.id,))
            balance = getattr(con.cur.fetchone(), "balance", 0)

        await ctx.send(f":moneybag: **{ctx.author.display_name}** has a total of **{balance:,}** coins")

    @commands.cooldown(1, 60 * 60, commands.BucketType.user)
    @commands.command(name="free", aliases=["pickup"], help="Free coins!")
    async def free(self, ctx: commands.Context):
        with DBConnection() as con:
            con.cur.execute(CoinsSQL.SELECT_USER, (ctx.author.id,))

            balance = max(getattr(con.cur.fetchone(), "balance", 0), 0)
            amount = random.randint(10, min(int(max(balance * 0.1, 10)), 1000))

            con.cur.execute(CoinsSQL.INCREMENT, (ctx.author.id, amount))

        await ctx.send(f"**{ctx.author.display_name}** gained **{amount}** coins!")

    @commands.cooldown(1, 60 * 60, commands.BucketType.user)
    @commands.command(name="steal", usage="<user>")
    async def steal_coins(self, ctx: commands.Context, target: NotAuthorOrBot()):
        if random.randint(0, 2) != 0:
            return await ctx.send(f"**{ctx.author.display_name}** stole nothing from **{target.display_name}**")

        with DBConnection() as con:
            con.cur.execute(CoinsSQL.SELECT_USER, (ctx.author.id,))
            author_coins = getattr(con.cur.fetchone(), "balance", 0)

            con.cur.execute(CoinsSQL.SELECT_USER, (target.id,))
            target_coins = getattr(con.cur.fetchone(), "balance", 0)

            max_coins = int(min(author_coins * 0.05, target_coins * 0.05, 1000))

            amount = random.randint(0, max(0, max_coins))

            con.cur.execute(CoinsSQL.INCREMENT, (ctx.author.id, amount))
            con.cur.execute(CoinsSQL.DECREMENT, (target.id, amount))

        await ctx.send(f"**{ctx.author.display_name}** stole **{amount:,}** coins from **{target.display_name}**")

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(name="gift", usage="<user> <amount>")
    async def gift(self, ctx, target: NotAuthorOrBot(), amount: IntegerRange(1, 100_000)):
        with DBConnection() as con:
            con.cur.execute(CoinsSQL.SELECT_USER, (ctx.author.id,))
            author_coins = getattr(con.cur.fetchone(), "balance", 0)

            # Balance check
            if author_coins < amount:
                await ctx.send(f"**{ctx.author.display_name}, you do not have enough coins for that**")

            else:
                con.cur.execute(CoinsSQL.DECREMENT, (ctx.author.id, amount))
                con.cur.execute(CoinsSQL.INCREMENT, (target.id, amount))

                await ctx.send(f"You gifted **{amount:,}** coins to **{target.display_name}**")

    @commands.command(name="clb", aliases=["coinlb"], help="Leaderboard")
    async def leaderboard(self, ctx: commands.Context):
        if self.leaderboards.get(ctx.guild.id, None) is None:
            self.leaderboards[ctx.guild.id] = CoinLeaderboard(ctx.guild, self.bot)

        lb = self.leaderboards[ctx.guild.id]

        return await ctx.send(lb.get(ctx.author))


def setup(bot):
    bot.add_cog(Coins(bot))