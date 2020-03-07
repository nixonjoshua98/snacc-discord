import random

from discord.ext import commands
from src.common import checks

from src.common import asycio_schedule
from src.common import FileReader


class Floor(commands.Cog, name="floor"):
	def __init__(self, bot):
		self.bot = bot

		self._coins_on_floor = 0

		asycio_schedule.add_task(60 * 30, self.drop_coins)

	async def cog_check(self, ctx):
		return await checks.in_game_room(ctx)

	async def drop_coins(self):
		self._coins_on_floor += random.randint(10, 25)

	@commands.command(name="floor", help="See whats on the floor")
	async def floor(self, ctx):
		await ctx.send(f"There are **{self._coins_on_floor}** coins on the floor")

	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="pickup", help="Pick up something")
	async def pickup(self, ctx):
		if self._coins_on_floor > 0:
			with FileReader("coins.json") as file:
				amount = self._coins_on_floor

				data = file.get(str(ctx.author.id), default_val={})

				data["coins"] = data.get("coins", 0) + amount

				file.set(str(ctx.author.id), data)

				self._coins_on_floor = 0

			return await ctx.send(f"**{ctx.author.display_name}** picked up **{amount}** coins!")

		return await ctx.send(f"**{ctx.author.display_name}** found no coins :cry:")