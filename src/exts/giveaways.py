import random
import asyncio

from discord.ext import commands, tasks

from src.common import SupportServer

from src.common import checks

from src.structs.reactioncollection import ReactionCollection


class Giveaways(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def start_giveaway_loop(self):
		async def start():
			print("Starting loop: Giveaways")

			await asyncio.sleep(3.0 * 3_600)

			self.giveaway_loop.start()

		if not self.bot.debug:
			asyncio.create_task(start())

	@tasks.loop(hours=3.0)
	async def giveaway_loop(self):
		await self.giveaway()

		self.giveaway_loop.change_interval(hours=random.randint(6, 12))

	@checks.snaccman_only()
	@commands.command(name="giveaway")
	async def giveaway_command(self, ctx):
		""" Start a giveaway in the support server. """

		await ctx.send("I have started a giveaway in the support server!")

		await self.giveaway()

	async def giveaway(self):
		support_server = self.bot.get_guild(SupportServer.ID)

		chnl = support_server.get_channel(693550889956540502)

		giveaway = random.choice(("giveaway_bitcoin", "giveaway_money"))

		await getattr(self, giveaway)(chnl)

	async def giveaway_bitcoin(self, chnl):
		bitcoins = random.randint(1, 1)

		embed = self.bot.embed(
			title="Giveaway!",
			description=f"React :white_check_mark: to enter. Winner will win **${bitcoins:,}** BTC."
		)

		members = await self.get_members(embed, chnl)

		if len(members) > 0:
			winner = random.choice(members)

			await self.bot.mongo.increment_one("bank", {"_id": winner.id}, {"btc": bitcoins})

			await chnl.send(f"Congratulations **{str(winner)}** for winning **{bitcoins:,}** BTC!")

	async def giveaway_money(self, chnl):
		money = random.randint(5_000, 7_500)

		embed = self.bot.embed(
			title="Giveaway!",
			description=f"React :white_check_mark: to enter. Winner will win **${money:,}**."
		)

		members = await self.get_members(embed, chnl)

		if len(members) > 0:
			winner = random.choice(members)

			await self.bot.mongo.increment_one("bank", {"_id": winner.id}, {"usd": money})

			await chnl.send(f"Congratulations **{str(members[0])}** for winning **${money:,}!**")

	async def get_members(self, embed, chnl) -> list:
		return await ReactionCollection(self.bot, embed, duration=1_800, max_reacts=None).prompt(chnl)


def setup(bot):
	bot.add_cog(Giveaways(bot))
