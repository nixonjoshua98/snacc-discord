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
		amount = coins.balance

		coins.deduct(amount)

		lower_bound = max(int(amount * 0.75), amount - 75)
		upper_bound = min(int(amount * 1.50), amount + 100)

		# Add winnings before the actual spin to avoid issues
		winnings = max(0, random.randint(lower_bound, upper_bound))
		winnings = winnings + 1 if winnings == amount else winnings

		coins.add(winnings)

		message = await ctx.send(f"-> {num2emoji(amount)} <-")

		# Spin animation
		for i in range(2):
			await asyncio.sleep(1.0)
			temp_num = max(0, random.randint(lower_bound, upper_bound))

			temp_num = temp_num + 1 if temp_num == amount else temp_num

			await message.edit(content=f"-> {num2emoji(temp_num)} <-")
		await message.edit(content=f"-> {num2emoji(winnings)} <-")

		text = 'won' if winnings-amount > 0 else 'lost'

		await ctx.send(f"**{ctx.author.display_name}** has {text} **{abs(winnings-amount)}** coins!")
