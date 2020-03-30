import random
import asyncio

from num2words import num2words

from discord.ext import commands

from src.common import checks
from src.common import FileReader


class Casino(commands.Cog, name="casino"):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		return await checks.requires_channel_tag("game")(ctx)

	@checks.has_minimum_coins("coins.json", 10)
	@commands.cooldown(25, 60 * 60 * 12, commands.BucketType.user)
	@commands.command(name="spin", aliases=["sp"], help="Slot machine [25/12hrs]")
	async def spin(self, ctx):
		def get_win_bounds(amount) -> tuple:
			low = max([amount * 0.75, amount - (25 + (7.50 * amount / 1000))])
			upp = min([amount * 2.00, amount + (50 + (10.0 * amount / 1000))])
			return int(low), int(upp)

		def create_message(amount):
			return f":arrow_right:{''.join([f':{num2words(digit)}:' for digit in f'{amount:05d}'])}:arrow_left:\n"

		# Add the winnings before the animation
		with FileReader("coins.json") as coins_file:
			initial_balance = coins_file.get_inner_key(str(ctx.author.id), "coins", 0)

			lower, upper = get_win_bounds(initial_balance)

			final_balance = max(0, random.randint(lower, upper))

			coins_file.set_inner_key(str(ctx.author.id), "coins", final_balance)

		message = await ctx.send(create_message(initial_balance))

		await asyncio.sleep(1.0)

		for i in range(2):
			await message.edit(content=create_message(max(0, random.randint(lower, upper))))
			await asyncio.sleep(1.0)

		await message.edit(content=create_message(final_balance))

		balance_change = final_balance - initial_balance

		text = 'won' if balance_change > 0 else 'lost'

		await ctx.send(f"**{ctx.author.display_name}** has {text} **{abs(balance_change):,}** coins!")
	@checks.has_minimum_coins("coins.json", 10)
	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="flip", aliases=["fl"], help="Flip a coin [1hr]")
	async def flip(self, ctx):
		with FileReader("coins.json") as coins_file:
			initial_balance = coins_file.get_inner_key(str(ctx.author.id), "coins", 0)

			win_amount = int(min(2500, initial_balance * 0.5))

			if random.randint(0, 1) == 0:
				final_balance = initial_balance + win_amount
			else:
				final_balance = initial_balance - win_amount

			coins_file.set_inner_key(str(ctx.author.id), "coins", final_balance)

		text = 'won' if final_balance > initial_balance else 'lost'

		await ctx.send(f"**{ctx.author.display_name}** has {text} **{abs(win_amount):,}** coins by flipping a coin!")

