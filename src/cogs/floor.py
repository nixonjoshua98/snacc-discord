import random

from discord.ext import commands
from src.common import checks

from src.common import asycio_schedule
from src.structures import PlayerCoins


class Floor(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self._coins_on_floor = 50

		asycio_schedule.add_task(60 * 60, self.drop_coins)

	async def cog_check(self, ctx):
		return await checks.in_game_room(ctx) and commands.guild_only()

	async def drop_coins(self):
		self._coins_on_floor += random.randint(15, 35)

	@commands.command(name="floor", help="See whats on the floor")
	async def floor(self, ctx):
		await ctx.send(f"There are **{self._coins_on_floor}** coins on the floor")

	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="pickup", help="Pick up something from the floor")
	async def pickup(self, ctx):
		if self._coins_on_floor > 0:
			coins = PlayerCoins(ctx.author)
			amount = self._coins_on_floor
			self._coins_on_floor = 0

			coins.add(amount)

			return await ctx.send(f"**{ctx.author.display_name}** picked up **{amount}** coins!")

		await ctx.send(f"**{ctx.author.display_name}** found no coins :cry:")