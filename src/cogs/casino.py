import random

from discord.ext import commands

from src.common import checks
from src.common import FileReader

from src.structures.casino import SpinMachine


class Casino(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		return await checks.in_game_room(ctx)

	@checks.has_minimum_coins("coins.json", 10)
	@commands.cooldown(25, 60 * 60 * 24, commands.BucketType.user)
	@commands.command(name="spin", aliases=["sp"], help="Slot machine [LOW RISK]")
	async def spin(self, ctx):
		machine = SpinMachine(ctx)

		winnings = await machine.spin()

		text = 'won' if winnings > 0 else 'lost'

		await ctx.send(f"**{ctx.author.display_name}** has {text} **{abs(winnings):,}** coins!")

	@checks.has_minimum_coins("coins.json", 10)
	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="flip", aliases=["fl"], help="Flip a coin [HIGH RISK]")
	async def flip(self, ctx):
		with FileReader("coins.json") as file:
			# Initial player balance
			start_balance = file.get(str(ctx.author.id), default_val=0)

			win_amount = int(min(750, start_balance * 0.5))

			if random.randint(0, 1) == 0:
				file.increment(str(ctx.author.id), win_amount)
			else:
				file.decrement(str(ctx.author.id), win_amount)

			# Balance after the flip
			end_balance = file.get(str(ctx.author.id), default_val=0)

		winnings = end_balance - start_balance

		text = 'won' if winnings > 0 else 'lost'

		await ctx.send(f"**{ctx.author.display_name}** has {text} **{abs(winnings):,}** coins by flipping a coin!")

