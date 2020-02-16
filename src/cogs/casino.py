import random
import asyncio

from num2words import num2words
from discord.ext import commands
from src.common import checks

from src.structures import PlayerCoins


class Casino(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		return await checks.in_game_room(ctx) and commands.guild_only()

	@checks.has_minimum_coins("coins.json", 10)
	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(name="spin", aliases=["sp"])
	async def spin(self, ctx):
		def num2emoji(num):
			return "".join([f":{num2words(digit)}:" for digit in f"{num:05d}"])

		coins = PlayerCoins(ctx.author)
		winnings = amount = coins.balance
		coins.deduct(amount)

		lower_bound = max(int(amount * 0.75), amount - 50)
		upper_bound = min(int(amount * 1.50), amount + 50)

		message = await ctx.send(f"-> {num2emoji(winnings)} <-")

		# Spin animation
		for i in range(2):
			await asyncio.sleep(1.0)
			winnings = max(0, random.randint(lower_bound, upper_bound))
			winnings = winnings + 1 if winnings == amount else winnings  # Cannot gain nothing
			await message.edit(content=f" -> {num2emoji(winnings)} <-")

		text = 'won' if winnings-amount > 0 else 'lost'

		PlayerCoins(ctx.author).add(winnings)

		await ctx.send(f"**{ctx.author.display_name}** has {text} **{abs(winnings-amount)}** coins!")
