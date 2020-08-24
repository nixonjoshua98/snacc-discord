import random

from src.common import SupportServer

from src.structs.reactioncollection import ReactionCollection


class Giveaway:
	def __init__(self, bot):
		self.bot = bot

		self.destination = None

	async def send(self):
		support_server = self.bot.get_guild(SupportServer.ID)

		self.destination = chnl = support_server.get_channel(SupportServer.GIVEAWAY_CHANNEL)

		embed = self.bot.embed(title="Giveaway!", description=f"React :white_check_mark: to enter")

		members = await ReactionCollection(self.bot, embed, duration=5, max_reacts=None).prompt(chnl)

		if members >= 2:
			await self.on_giveaway_end(members)

	async def on_giveaway_end(self, members):
		money = random.randint(5_000, 7_500)

		winner = random.choice(members)

		await self.bot.mongo.increment_one("bank", {"_id": winner.id}, {"usd": money})

		await self.destination.send(f"Congratulations **{winner.mention}** for winning **${money:,}!**")


