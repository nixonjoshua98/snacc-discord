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
            con.cur.execute("SELECT * FROM coins;")

            results = con.cur.fetchall()

        print(results)


def setup(bot):
    bot.add_cog(Coins(bot))
