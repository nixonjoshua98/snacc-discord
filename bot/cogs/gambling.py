import random
import secrets

from bot import utils

from discord.ext import commands

from bot.common import errors
from bot.common.queries import BankSQL
from bot.common.converters import Range, CoinSide


class Gambling(commands.Cog, command_attrs=(dict(cooldown_after_parsing=True))):
	def __init__(self, bot):
		self.bot = bot

	async def cog_before_invoke(self, ctx):
		ctx.bals = await utils.bank.get_ctx_users_bals(ctx)

	@commands.cooldown(25, 60 * 60 * 3, commands.BucketType.user)
	@commands.command(name="spin", aliases=["sp"])
	async def spin(self, ctx):
		""" Use a spin machine. """

		def get_winning(amount) -> int:
			low, high = max(amount * -0.75, -750), min(amount * 2.0, 1000)

			return random.randint(int(low), int(high))

		initial_author_bal = ctx.bals["author"]["money"]

		bet = initial_author_bal

		winnings = get_winning(bet)

		await self.bot.pool.execute(BankSQL.ADD_MONEY, ctx.author.id, winnings)

		await ctx.send(f"You {'won' if winnings > 0 else 'lost'} **${abs(winnings):,}** on the spin machine!")

	@commands.cooldown(1, 3, commands.BucketType.user)
	@commands.command(name="flip", aliases=["fl"])
	async def flip(self, ctx, bet: Range(1, 50_000) = 10, side: CoinSide = "heads"):
		""" Flip a coin and bet on which side it lands on. """

		initial_author_bal = ctx.bals["author"]["money"]

		if initial_author_bal < bet:
			raise errors.NotEnoughMoney()

		side_landed = secrets.choice(["heads", "tails"])
		correct_side = side_landed == side

		winnings = bet if correct_side else bet * -1

		await self.bot.pool.execute(BankSQL.ADD_MONEY, ctx.author.id, winnings)

		await ctx.send(f"It's **{side_landed}**! "
					   f"You {'won' if correct_side else 'lost'} **${abs(winnings):,}**!")

	@commands.cooldown(1, 3, commands.BucketType.user)
	@commands.command(name="bet", aliases=["roll"])
	async def bet(self, ctx, bet: Range(1, 50_000) = 10, sides: Range(6, 100) = 6, side: Range(6, 100) = 6):
		""" Roll a die and bet on which side the die lands on. """

		initial_author_bal = ctx.bals["author"]["money"]

		if initial_author_bal < bet:
			raise errors.NotEnoughMoney()

		side_landed = random.randint(1, sides)
		correct_side = side_landed == side

		winnings = bet * (sides - 1) if correct_side else bet * -1

		await self.bot.pool.execute(BankSQL.ADD_MONEY, ctx.author.id, winnings)

		await ctx.send(f":1234: You {'won' if correct_side else 'lost'} **${abs(winnings):,}**! "
					   f"The dice landed on `{side_landed}`")


def setup(bot):
	bot.add_cog(Gambling(bot))
