import random

from discord.ext import commands

from bot.common.converters import IntegerRange


class Gambling(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.cooldown(25, 60 * 60 * 3, commands.BucketType.user)
	@commands.command(name="spin", aliases=["sp"], help="Spin machine")
	async def spin(self, ctx):
		""" Use a spin machine. """

		def get_winning(amount) -> int:
			low, high = max(amount * -0.75, -750), min(amount * 2.0, 1000)

			return random.randint(int(low), int(high))

		bank = self.bot.get_cog("Bank")

		user_balance = await bank.get_user_balance(ctx.author)

		bet = user_balance["money"]

		winnings = get_winning(bet)

		await bank.update_money(ctx.author, winnings)

		if winnings > 0:
			await ctx.send(f"You won **${abs(winnings):,}** on the spin machine!")

		else:
			await ctx.send(f"You lost **${abs(winnings):,}** on the spin machine.")

	@commands.cooldown(1, 3, commands.BucketType.user)
	@commands.command(name="flip", aliases=["fl"], usage="<bet=10> <side=heads>")
	async def flip(self, ctx, bet: IntegerRange(1, 50_000) = 10, side: str = "heads"):
		""" Flip a coin and bet on which side it lands on. """

		side = side.lower()
		bank = self.bot.get_cog("Bank")

		user_balance = await bank.get_user_balance(ctx.author)

		# User has less than what they want to bet
		if user_balance["money"] < bet:
			return await ctx.send("You do not have enough money.")

		elif side not in ["tails", "heads"]:
			return await ctx.send("Invalid side.")

		side_landed = random.choice(["heads", "tails"])

		winnings = bet if side_landed == side else bet * -1

		await bank.update_money(ctx.author, winnings)

		if winnings > 0:
			await ctx.send(f"It's **{side_landed.title()}**. You won **${abs(winnings):,}**!")

		else:
			await ctx.send(f"It's **{side_landed.title()}**. You lost **${abs(winnings):,}**.")

	@commands.cooldown(1, 3, commands.BucketType.user)
	@commands.command(name="bet", aliases=["roll"], usage="<bet=10> <sides=6> <side=6>")
	async def bet(self, ctx, bet: IntegerRange(1, 50_000) = 10, sides: IntegerRange(6, 100) = 6, side: int = 6):
		"""
		Roll a die and bet on which side the die lands on.
		"""

		bank = self.bot.get_cog("Bank")

		user_balance = await bank.get_user_balance(ctx.author)

		# User has less than what they want to bet
		if user_balance["money"] < bet:
			return await ctx.send("You do not have enough money.")

		# The user made a bet which they can not win
		elif side > sides:
			return await ctx.send(f"You made an impossible to win bet. `{sides}` sides but you bet on side `{side}`")

		landed_side = random.randint(1, sides)

		winnings = bet * (sides - 1) if side == landed_side else bet * -1

		await bank.update_money(ctx.author, winnings)

		if winnings > 0:
			await ctx.send(f":1234: You won **${abs(winnings):,}**! The dice landed on `{landed_side}`")

		else:
			await ctx.send(f":1234: You lost **${abs(winnings):,}**. The dice landed on `{landed_side}`")

def setup(bot):
	bot.add_cog(Gambling(bot))
