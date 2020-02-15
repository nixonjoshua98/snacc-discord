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
		return await checks.in_bot_channel(ctx) and await checks.has_member_role(ctx) and commands.guild_only()

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(name="spin")
	async def spin(self, ctx):
		def num2emoji(num):
			return "".join([f":{num2words(digit)}:" for digit in f"{num:05d}"])

		coins = PlayerCoins(ctx.author)

		amount = coins.balance

		if amount < 10:
			return await ctx.send(f"Minimum bet: **10**")

		if coins.deduct(amount):
			winnings = amount
			message = await ctx.send(f"-> {num2emoji(winnings)} <-")

			for i in range(3):
				await asyncio.sleep(1.0)
				winnings = max(0, random.randint(int(amount * 0.75), int(amount * 1.5)))
				await message.edit(content=f"-> {num2emoji(winnings)} <-")

			PlayerCoins(ctx.author).add(winnings)  # Reload

			await ctx.send(f"**{ctx.author.display_name}** has won **{winnings} ({winnings-amount})** coins!")

		else:
			await ctx.send(f"**{ctx.author.display_name}** you have less than **{amount}** coins")