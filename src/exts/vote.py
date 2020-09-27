import dbl
import os
import discord

from discord.ext import commands

from src import utils

from src.common import SupportServer


class Vote(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener("on_startup")
	async def on_startup(self):
		if (token := os.getenv("DBL_TOKEN")) not in (None, "TOKEN", "VALUE", "", " "):

			auth = os.environ["VOTE_AUTH"]

			dbl.DBLClient(
				self.bot,
				token,
				autopost=True,
				webhook_port=4999,
				webhook_path="/topgghook",
				webhook_auth=auth
			)

			print("Created vote clients")

	@commands.Cog.listener(name="on_dbl_test")
	async def on_dbl_test(self, data):
		print(data)

		await self.on_dbl_vote(data)

	@commands.Cog.listener(name="on_dbl_vote")
	async def on_dbl_vote(self, data):
		user_id = int(data["user"])

		user = self.bot.get_user(user_id)

		empire = await self.bot.db["empires"].find_one({"_id": user_id}) or dict()

		multiplier = 1.25 if data["isWeekend"] else 1.0

		reward = int(min(50_000, max(utils.net_income(empire) * 5, 5_000)) * multiplier)

		await self.bot.db["bank"].update_one({"_id": user_id}, {"$inc": {"usd": reward}}, upsert=True)

		if user is not None:
			support_server = self.bot.get_guild(SupportServer.ID)

			try:
				await user.send(f"Thank you for voting for me! You have received **${reward:,}** :heart:")

				member = support_server.get_member(user_id)

				if member is None:
					await user.send(f"psst...you can join our support server here {SupportServer.LINK}")

			except (discord.Forbidden, discord.HTTPException):
				""" Failed """


def setup(bot):
	if not bot.debug:
		bot.add_cog(Vote(bot))
