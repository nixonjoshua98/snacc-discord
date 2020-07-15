import random
import typing

from discord.ext import commands

from src.common.converters import Range, CoinSide

from src.common.queries import BankSQL


class Gambling(commands.Cog):

	@commands.cooldown(1, 3, commands.BucketType.user)
	@commands.command(name="flip", cooldown_after_parsing=True)
	async def flip(self, ctx, side: typing.Optional[CoinSide] = "heads", bet: Range(0, 50_000) = 0):
		""" Flip a coin and bet on which side it lands on. """

		async with ctx.bot.pool.acquire() as con:
			bal = await ctx.bot.get_cog("Money").get_user_balance(con, ctx.author)

			if bal["money"] < bet:
				raise commands.CommandError("You do not have enough money.")

			side_landed = random.choice(["heads", "tails"])

			correct_side = side_landed == side

			winnings = bet if correct_side else bet * -1

			# No point updating the database if we bet nothing
			if winnings != 0:
				query = BankSQL.ADD_MONEY if winnings > 0 else BankSQL.SUB_MONEY

				await con.execute(query, ctx.author.id, winnings)

		await ctx.send(f"It's **{side_landed}**! You {'won' if correct_side else 'lost'} **${abs(winnings):,}**!")


def setup(bot):
	bot.add_cog(Gambling())

