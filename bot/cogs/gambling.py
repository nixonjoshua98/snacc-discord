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

		await bank.update_coins(ctx.author, winnings)

		if winnings > 0:
			await ctx.send(f"You won **${abs(winnings):,}** on the spin machine!")

		else:
			await ctx.send(f"You lost **${abs(winnings):,}** on the spin machine.")

	@commands.cooldown(1, 3, commands.BucketType.user)
	@commands.command(name="fl", aliases=["flip"], usage="<bet=10>")
	async def flip(self, ctx, bet: IntegerRange(1, 50_000) = 10):
		""" Flip a coin and bet on what said it lands on. """

		bank = self.bot.get_cog("Bank")

		user_balance = await bank.get_user_balance(ctx.author)

		# User has less than what they want to bet
		if user_balance["money"] < bet:
			return await ctx.send("You do not have enough money.")

		winnings = bet if random.choice([0, 1]) == 0 else bet * -1

		await bank.update_coins(ctx.author, winnings)

		if winnings > 0:
			await ctx.send(f"You won **${abs(winnings):,}** by flipping a coin!")

		else:
			await ctx.send(f"You lost **${abs(winnings):,}** by flipping a coin.")

	@commands.cooldown(1, 3, commands.BucketType.user)
	@commands.command(name="bet", aliases=["roll"], usage="<sides=6> <side=6> <bet=10>")
	async def bet(self, ctx, sides: IntegerRange(6, 100) = 6, side: int = 6, bet: IntegerRange(1, 50_000) = 10):
		"""
		Roll a die and bet on which [side] the die lands on.
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

		await bank.update_coins(ctx.author, winnings)

		if winnings > 0:
			await ctx.send(f":1234: You won **${abs(winnings):,}**! The dice landed on `{landed_side}`")

		else:
			await ctx.send(f":1234: You lost **${abs(winnings):,}**. The dice landed on `{landed_side}`")






def setup(bot):
	bot.add_cog(Gambling(bot))
