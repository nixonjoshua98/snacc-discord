import asyncio
import random

from discord.ext import commands, tasks

from src import utils

from src.common import SupportServer, checks

from src.structs.reactioncollection import ReactionCollection


class Support(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener("on_startup")
	async def on_startup(self):
		if not self.bot.debug:
			print("Starting loop: Giveaways")

			await asyncio.sleep(6.0 * 3_600)

			self.giveaway_loop.start()

	@tasks.loop(hours=12.0)
	async def giveaway_loop(self):
		await Giveaway(self.bot).send()

	@checks.snaccman_only()
	@commands.command(name="giveaway")
	async def giveaway_command(self, ctx):
		""" Start a giveaway in the support server. """

		await ctx.send("I have started a giveaway in the support server!")

		asyncio.create_task(Giveaway(self.bot).send())

	@commands.command(name="support")
	async def support(self, ctx):
		""" Link to the support server. """

		await ctx.send("https://discord.gg/QExQuvE")


class Giveaway:
	def __init__(self, bot):
		self.bot = bot

		self.destination = None

	async def send(self):
		support_server = self.bot.get_guild(SupportServer.ID)

		giveaway_role = support_server.get_role(SupportServer.GIVEAWAY_ROLE)

		self.destination = chnl = support_server.get_channel(SupportServer.GIVEAWAY_CHANNEL)

		embed = self.bot.embed(title="Giveaway!", description=f"React :tada: to enter")

		await chnl.send(giveaway_role.mention, delete_after=300.0)

		members = await ReactionCollection(self.bot, embed, duration=3_600, max_reacts=None).prompt(chnl)

		if len(members) >= 2:
			await self.on_giveaway_end(members)

	async def on_giveaway_end(self, members):
		name = utils.get_random_name()
		value = random.randint(5_000, 10_000)

		winner = random.choice(members)

		await self.bot.mongo.snacc["loot"].insert_one({"user": winner.id, "name": name, "value": value})

		await self.destination.send(
			f"Congratulations **{winner.mention}** for winning **- {name} -** worth **${value:,}!**"
		)


def setup(bot):
	bot.add_cog(Support(bot))
