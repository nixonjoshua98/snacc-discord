import random

from discord.ext import commands

from snacc_bot.common.database import DBConnection


class Coins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return True

    @commands.command(name="bal", help="Display coin balance")
    async def balance(self, ctx: commands.Context):
        with DBConnection() as con:
            con.cur.execute(con.get_query("select-user-coins.sql"), (ctx.author.id,))
            user_coins = con.cur.fetchone()

        balance = 0 if user_coins is None else user_coins.balance

        await ctx.send(f":moneybag: **{ctx.author.display_name}** has a total of **{balance:,}** coins")

    @commands.cooldown(1, 60 * 15, commands.BucketType.user)
    @commands.command(name="free", help="Get free coins [15m]")
    async def free(self, ctx: commands.Context):
        amount = random.randint(15, 50)

        with DBConnection() as con:
            con.cur.execute(con.get_query("select-user-coins.sql"), (ctx.author.id,))

            if con.cur.fetchone() is None:
                query, params = con.get_query("insert-user-coins.sql"), (ctx.author.id, amount)
            else:
                query, params = con.get_query("update-user-coins.sql"), (amount, ctx.author.id)

            con.cur.execute(query, params)

        await ctx.send(f"**{ctx.author.display_name}** gained **{amount}** coins!")

    @commands.command(name="gift", help="Gift some coins")
    async def gift_coins(self, ctx: commands.Context):
        pass

    @commands.command(name="steal", help="Steal some coins")
    @commands.cooldown(1, 60 * 60, commands.BucketType.user)
    async def steal_coins(self, ctx: commands.Context):
        pass


def setup(bot):
    bot.add_cog(Coins(bot))
