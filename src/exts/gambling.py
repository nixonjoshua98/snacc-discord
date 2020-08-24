import random
import typing

from discord.ext import commands

from src.common.converters import Range, CoinSide


class Gambling(commands.Cog):

	@commands.command(name="flip")
	@commands.max_concurrency(1, commands.BucketType.user)
	async def flip(self, ctx, side: typing.Optional[CoinSide] = "heads", bet: Range(0, 50_000) = 0):
		""" Flip a coin and bet on which side it lands on. """

		bank = await ctx.bot.mongo.find_one("bank", {"_id": ctx.author.id})

		# - User cannot afford the bet
		if bank.get("usd", 0) < bet:
			raise commands.CommandError("You do not have enough money.")

		side_landed = random.choice(["heads", "tails"])

		correct_side = side_landed == side

		# - Bet was won and the bet is greater than 0
		if correct_side and bet > 0:
			await ctx.bot.mongo.increment_one("bank", {"_id": ctx.author.id}, {"usd": bet})

		# - User lost the bet and bet more than 0
		elif not correct_side and bet > 0:
			await ctx.bot.mongo.decrement_one("bank", {"_id": ctx.author.id}, {"usd": bet})

		await ctx.send(f"It's **{side_landed}**! You {'won' if correct_side else 'lost'} **${bet:,}**!")

	@commands.command(name="bet")
	@commands.max_concurrency(1, commands.BucketType.user)
	async def bet(self, ctx, bet: Range(0, 50_000) = 0, sides: Range(6, 100) = 6, side: Range(1, 100) = 6):
		""" Roll a dice and bet on which side the die lands on. """

		bank = await ctx.bot.mongo.select_one("bank", {"_id": ctx.author.id})

		# - User cannot afford the bet
		if bank.get("usd", 0) < bet:
			raise commands.CommandError("You do not have enough money.")

		# - User made an impossible to win bet.
		elif side > sides:
			raise commands.CommandError(f"You bet on side **{side}** but your dice only has **{sides}** sides.")

		side_landed = random.randint(1, sides)

		bet_won = side_landed == side

		# - Bet was won and the bet is greater than 0
		if bet_won and bet > 0:
			await ctx.bot.mongo.increment_one("bank", {"_id": ctx.author.id}, {"usd": bet})

		# - User lost the bet and bet more than 0
		elif not bet_won and bet > 0:
			await ctx.bot.mongo.decrement_one("bank", {"_id": ctx.author.id}, {"usd": bet})

		await ctx.send(f":1234: You {'won' if bet_won else 'lost'} **${bet:,}**! The dice landed on `{side_landed}`")


def setup(bot):
	bot.add_cog(Gambling())

