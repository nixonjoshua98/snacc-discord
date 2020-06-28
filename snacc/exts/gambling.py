import random
import typing

from discord.ext import commands

from snacc.common.converters import Range, CoinSide

from snacc.common.queries import BankSQL


class Gambling(commands.Cog, command_attrs=(dict(cooldown_after_parsing=True))):
	@commands.cooldown(1, 3, commands.BucketType.user)
	@commands.command(name="flip")
	async def flip(self, ctx, side: typing.Optional[CoinSide] = "heads", bet: Range(0, 50_000) = 0):
		""" Flip a coin and bet on which side it lands on. """

		money_cog = ctx.bot.get_cog("Money")

		bal = await money_cog.get_balance(ctx.bot.pool, ctx.author)

		if bal["money"] < bet:
			raise commands.CommandError("You do not have enough money.")

		side_landed = random.choice(["heads", "tails"])

		correct_side = side_landed == side

		# Either +bet or -bet
		winnings = bet if correct_side else bet * -1

		await ctx.bot.pool.execute(BankSQL.ADD_MONEY, ctx.author.id, winnings)

		await ctx.send(f"It's **{side_landed}**! You {'won' if correct_side else 'lost'} **${abs(winnings):,}**!")


def setup(bot):
	bot.add_cog(Gambling())

