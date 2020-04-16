import random

from discord.ext import commands

from bot.common.converters import Clamp


class Gambling(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.bank = self.bot.get_cog("Bank")

	async def cog_before_invoke(self, ctx):
		self.bank = self.bot.get_cog("Bank") if self.bank is None else self.bank

		ctx.user_balance = await self.bank.get_user_balance(ctx.author)

	@commands.cooldown(25, 60 * 60 * 3, commands.BucketType.user)
	@commands.command(name="spin", aliases=["sp"], help="Spin machine")
	async def spin(self, ctx):
		""" Use a spin machine. Winnings are within -750 - 1000. """

		def get_winning(amount) -> int:
			low, high = max(amount * -0.75, -750), min(amount * 2.0, 1000)

			return random.randint(int(low), int(high))

		bal_diff = get_winning(ctx.user_balance["coins"])

		await self.bank.update_coins(ctx.author, bal_diff)

		text = 'won' if bal_diff > 0 else 'lost'

		msg = f"**{ctx.author.display_name}** has {text} **{abs(bal_diff):,}** coins on the spin machine."

		await ctx.send(msg)

	@commands.cooldown(1, 3, commands.BucketType.user)
	@commands.command(name="fl", aliases=["flip"], usage="<bet=100>")
	async def flip(self, ctx, bet: Clamp(1, 5_000) = 100):
		""" Flip a coin and bet on what said it lands on """

		if ctx.user_balance["coins"] < bet:
			return await ctx.send("You do not have enough coins.")

		bal_diff = bet if random.randint(0, 1) == 0 else bet * -1

		await self.bank.update_coins(ctx.author, bal_diff)

		text = 'won' if bal_diff > 0 else 'lost'

		await ctx.send(f"**{ctx.author.display_name}** has {text} **{abs(bet):,}** coins by flipping a coin.")

	@commands.cooldown(1, 3, commands.BucketType.user)
	@commands.command(name="dice", aliases=["roll"], usage="<sides=6> <bet=100>")
	async def dice(self, ctx, sides: Clamp(6, 20) = 6, bet: Clamp(1, 5000) = 100):
		"""
		Roll a dice and bet on if the dice lands on a 6.
		Winnings are calculated by [bet] * [sides - 1]
		"""

		if ctx.user_balance["coins"] < bet:
			return await ctx.send("You do not have enough coins.")

		side = random.randint(1, sides)

		winnings = bet * (sides - 1) if side == 6 else bet * -1

		text = "won" if winnings > 0 else "lost"

		await ctx.send(f"You {text} **{abs(winnings):,}** coins! The dice landed on `{side}`")

		await self.bank.update_coins(ctx.author, bet * -1)





def setup(bot):
	bot.add_cog(Gambling(bot))
