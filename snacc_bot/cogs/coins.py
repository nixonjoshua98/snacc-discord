import random

from discord.ext import commands

from snacc_bot.common.database import DBConnection


class Coins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return True

    @commands.cooldown(1, 60 * 30, commands.BucketType.user)
    @commands.command(name="balance", aliases=["bal"], help="Display coin balance")
    async def balance(self, ctx: commands.Context):
        with DBConnection() as con:
            con.cur.execute(con.get_query("select-user-coins.sql"), (ctx.author.id,))

            bal = con.cur.fetchone()

            bal = 0 if bal is None else bal.balance

        await ctx.send(f":moneybag: **{ctx.author.display_name}** has a total of **{bal:,}** coins")

    @commands.cooldown(1, 60 * 15, commands.BucketType.user)
    @commands.command(name="free", aliases=["pickup"], help="Get free coins [15m]")
    async def free(self, ctx: commands.Context):
        amount = random.randint(15, 50)

        with DBConnection() as con:
            con.cur.execute(con.get_query("select-user-coins.sql"), (ctx.author.id,))

            bal = con.cur.fetchone()

            query = con.get_query("insert-user-coins.sql" if bal is None else "update-user-coins.sql")

            con.cur.execute(query, (ctx.author.id, amount))

        await ctx.send(f"**{ctx.author.display_name}** gained **{amount}** coins!")


def setup(bot):
    bot.add_cog(Coins(bot))
