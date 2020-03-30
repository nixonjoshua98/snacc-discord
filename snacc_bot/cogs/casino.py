import random

from num2words import num2words

from discord.ext import commands

from snacc_bot.common.database import DBConnection


class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return True

    @commands.cooldown(1, 60 * 30, commands.BucketType.user)
    @commands.command(name="flip", aliases=["fl"], help="Flip a coin [30m]")
    async def flip(self, ctx: commands.Context):
        with DBConnection() as con:
            con.cur.execute(con.get_query("select-user-coins.sql"), (ctx.author.id,))

            user_coins = con.cur.fetchone()

            if user_coins is None or user_coins.balance < 10:
                await ctx.send(f":x: **{ctx.author.display_name}**, your balance is too low for this :slight_frown:")

            else:
                amount = int(min(2500, user_coins.balance * 0.5)) * random.choice([1, -1])

                con.cur.execute(con.get_query("update-user-coins.sql"), (amount, ctx.author.id))

                t = 'won' if amount > 0 else 'lost'

                await ctx.send(f"**{ctx.author.display_name}** has {t} **{abs(amount):,}** coins by flipping a coin!")

    @commands.cooldown(50, 60 * 60 * 24, commands.BucketType.user)
    @commands.command(name="spin", aliases=["sp"], help="Slot machine [50/24hrs]")
    async def spin(self, ctx):
        def get_win_bounds(amount) -> tuple:
            low = max([amount * 0.75, amount - (25 + (7.50 * amount / 1000))])
            upp = min([amount * 2.00, amount + (50 + (10.0 * amount / 1000))])
            return int(low), int(upp)

        def create_message(amount):
            return f":arrow_right:{''.join([f':{num2words(digit)}:' for digit in f'{amount:05d}'])}:arrow_left:\n"

        with DBConnection() as con:
            con.cur.execute(con.get_query("select-user-coins.sql"), (ctx.author.id,))

            user_coins = con.cur.fetchone()

            if user_coins is None or user_coins.balance < 10:
                return await ctx.send(f":x: **{ctx.author.display_name}**, your balance is too low for this :frowning:")

            final_balance = max(0, random.randint(*get_win_bounds(user_coins.balance)))

            # Set the new coin amount
            con.cur.execute(con.get_query("set-user-coins.sql"), (final_balance, ctx.author.id))

            balance_change = final_balance - user_coins.balance
            text = 'won' if balance_change > 0 else 'lost'

        return await ctx.send(f"{create_message(final_balance)}\n"
                              f"**{ctx.author.display_name}** has {text} **{abs(balance_change):,}** coins!")


def setup(bot):
    bot.add_cog(Casino(bot))
