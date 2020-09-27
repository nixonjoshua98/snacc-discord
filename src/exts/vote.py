import dbl
import os
import discord

from discord.ext import commands

from src.common import SupportServer


class Vote(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

		self.dbl = None

	@commands.Cog.listener("on_startup")
	async def on_startup(self):
		if (token := os.getenv("DBL_TOKEN")) not in (None, "TOKEN", "VALUE", "", " "):
			self.dbl = dbl.DBLClient(self.bot, token, autopost=True, webhook_port=10010, webhook_auth="snacc")

			print("Created DBL webhook")

	@commands.Cog.listener("on_dbl_test")
	async def on_dbl_test(self, data):
		print(data)

	@commands.Cog.listener(name="on_dbl_vote")
	async def on_dbl_vote(self, data):
		print(data)

		user_id = data["user"]

		user = self.bot.get_user(user_id)

		if user is not None:
			support_server = self.bot.get_guild(SupportServer.ID)

			try:
				await user.send("Thank you for voting for me! :heart:")

				member = support_server.get_member(user_id)

				if member is None:
					await user.send(f"psst...you can join our support server here {SupportServer.LINK}")

			except (discord.Forbidden, discord.HTTPException):
				""" Failed """


def setup(bot):
	if not bot.debug:
		bot.add_cog(Vote(bot))
