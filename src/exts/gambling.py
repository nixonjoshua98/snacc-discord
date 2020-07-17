import random
import typing

from discord.ext import commands

from src.common.converters import Range, CoinSide

from src.common.models import BankM


class Gambling(commands.Cog):

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(name="flip", cooldown_after_parsing=True)
	async def flip(self, ctx, side: typing.Optional[CoinSide] = "heads", bet: Range(0, 50_000) = 0):
		""" Flip a coin and bet on which side it lands on. """

		async with ctx.bot.pool.acquire() as con:
			row = await BankM.get_row(con, ctx.author.id)

			if row["money"] < bet:
				raise commands.CommandError("You do not have enough money.")

			side_landed = random.choice(["heads", "tails"])

			correct_side = side_landed == side

			winnings = bet if correct_side else bet * -1

			if winnings != 0:
				await con.execute(BankM.ADD_MONEY, ctx.author.id, winnings)

		await ctx.send(f"It's **{side_landed}**! You {'won' if correct_side else 'lost'} **${abs(winnings):,}**!")

	@commands.command(name="bet")
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def bet(self, ctx, bet: Range(0, 50_000) = 0, sides: Range(6, 100) = 6, side: Range(1, 100) = 6):
		""" Roll a dice and bet on which side the die lands on. """

		async with ctx.bot.pool.acquire() as con:
			bank = await BankM.get_row(con, ctx.author.id)

			money = bank[BankM.MONEY]

			if money < bet:
				raise commands.CommandError("You do not have enough money.")

			elif side > sides:
				raise commands.CommandError(f"You bet on side **{side}** but the dice only has **{sides}** sides.")

			side_landed = random.randint(1, sides)

			correct_side = side_landed == side

			winnings = bet * (sides - 1) if correct_side else bet * -1

			if winnings != 0:
				await con.execute(BankM.ADD_MONEY, ctx.author.id, winnings)

		await ctx.send(
			f":1234: You {'won' if correct_side else 'lost'} **${abs(winnings):,}**! "
			f"The dice landed on `{side_landed}`"
		)


def setup(bot):
	bot.add_cog(Gambling())

