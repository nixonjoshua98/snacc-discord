import random
import typing

from discord.ext import commands

from src.common.converters import Range, CoinSide

from src.common.models import BankM


class Gambling(commands.Cog):

	async def cog_before_invoke(self, ctx):
		ctx.bank_data["author_bank"] = await BankM.fetchrow(ctx.bot.pool, ctx.author.id)

	@commands.command(name="flip")
	@commands.max_concurrency(1, commands.BucketType.user)
	async def flip(self, ctx, side: typing.Optional[CoinSide] = "heads", bet: Range(0, 50_000) = 0):
		""" Flip a coin and bet on which side it lands on. """

		if ctx.bank_data["author_bank"]["money"] < bet:
			raise commands.CommandError("You do not have enough money.")

		side_landed = random.choice(["heads", "tails"])

		correct_side = side_landed == side

		winnings = bet if correct_side else bet * -1

		await BankM.increment(ctx.bot.pool, ctx.author.id, field="money", amount=winnings)

		await ctx.send(f"It's **{side_landed}**! You {'won' if correct_side else 'lost'} **${abs(winnings):,}**!")

	@commands.command(name="bet")
	@commands.max_concurrency(1, commands.BucketType.user)
	async def bet(self, ctx, bet: Range(0, 50_000) = 0, sides: Range(6, 100) = 6, side: Range(1, 100) = 6):
		""" Roll a dice and bet on which side the die lands on. """

		if ctx.bank_data["author_bank"]["money"] < bet:
			raise commands.CommandError("You do not have enough money.")

		# User made an impossible to win bet.
		elif side > sides:
			raise commands.CommandError(f"You bet on side **{side}** but your dice only has **{sides}** sides.")

		side_landed = random.randint(1, sides)

		correct_side = side_landed == side

		winnings = bet * (sides - 1) if correct_side else bet * -1

		await BankM.increment(ctx.bot.pool, ctx.author.id, field="money", amount=winnings)

		await ctx.send(
			f":1234: You {'won' if correct_side else 'lost'} **${abs(winnings):,}**! "
			f"The dice landed on `{side_landed}`"
		)


def setup(bot):
	bot.add_cog(Gambling())

