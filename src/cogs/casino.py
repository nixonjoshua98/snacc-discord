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
		return await checks.in_game_channel(ctx)

	@checks.has_minimum_coins("coins.json", 10)
	@commands.cooldown(25, 60 * 60 * 24, commands.BucketType.user)
	@commands.command(name="spin", aliases=["sp"], help="Slot machine [LOW RISK]")
	async def spin(self, ctx):
		def get_win_bounds(amount) -> tuple:
			low = max([amount * 0.75, amount - (25 + (7.50 * amount / 1000))])
			upp = min([amount * 2.00, amount + (50 + (10.0 * amount / 1000))])
			return int(low), int(upp)

		def create_message(amount):
			number_emoji = "".join([f":{num2words(digit)}:" for digit in f"{amount:05d}"])
			return f":arrow_right:{number_emoji}:arrow_left:\n"

		# Add the winnings before the animation
		with FileReader("coins.json") as file:
			balance = file.get(str(ctx.author.id), default_val={})

			bet_amount = balance["coins"]

			balance["coins"] -= bet_amount

			lower, upper = get_win_bounds(bet_amount)
			winnings = max(0, random.randint(lower, upper))

			balance["coins"] = winnings

			file.set(str(ctx.author.id), balance)

		# Initial animation message
		message = await ctx.send(create_message(bet_amount))

		# Animation
		for i in range(2):
			await asyncio.sleep(1.0)
			temp_num = max(0, random.randint(lower, upper))
			temp_num = temp_num + 1 if temp_num == bet_amount else temp_num
			await message.edit(content=create_message(temp_num))

		await asyncio.sleep(1.0)
		await message.edit(content=create_message(winnings))

		balance_change = winnings - bet_amount
		text = 'won' if balance_change > 0 else 'lost'
		await ctx.send(f"**{ctx.author.display_name}** has {text} **{abs(balance_change):,}** coins!")

	@checks.has_minimum_coins("coins.json", 10)
	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="flip", aliases=["fl"], help="Flip a coin [HIGH RISK]")
	async def flip(self, ctx):
		with FileReader("coins.json") as file:
			# Initial player balance
			data = file.get(str(ctx.author.id), default_val={})

			start = data["coins"]

			win_amount = int(min(2500, data["coins"] * 0.5))

			if random.randint(0, 1) == 0:
				data["coins"] += win_amount
			else:
				data["coins"] -= win_amount

			file.set(str(ctx.author.id), data)

		winnings = data["coins"] - start

		text = 'won' if winnings > 0 else 'lost'

		await ctx.send(f"**{ctx.author.display_name}** has {text} **{abs(winnings):,}** coins by flipping a coin!")

