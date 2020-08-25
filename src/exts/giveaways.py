import random
import asyncio

from discord.ext import commands, tasks

from src.common import checks

from src.structs.giveaway import Giveaway


class Giveaways(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.start_giveaway_loop()

	def start_giveaway_loop(self):
		async def start():
			print("Starting loop: Giveaways")

			await asyncio.sleep(3.0 * 3_600)

			self.giveaway_loop.start()

		if not self.bot.debug:
			asyncio.create_task(start())

	@tasks.loop(hours=6.0)
	async def giveaway_loop(self):
		self.giveaway_loop.change_interval(hours=random.randint(6, 12))

		asyncio.create_task(Giveaway(self.bot).send())

	@checks.snaccman_only()
	@commands.command(name="giveaway")
	async def giveaway_command(self, ctx):
		""" Start a giveaway in the support server. """

		await ctx.send("I have started a giveaway in the support server!")

		asyncio.create_task(Giveaway(self.bot).send())


def setup(bot):
	bot.add_cog(Giveaways(bot))
