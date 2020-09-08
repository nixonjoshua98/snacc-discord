import dbl
import os
import discord

from discord.ext import commands

from src.common import SupportServer


class Vote(commands.Cog):
	__can_disable__ = False

	def __init__(self, bot):
		self.bot = bot

		if os.getenv("DBL_TOKEN") not in (None, "TOKEN", "VALUE", "", " "):
			self.dbl = dbl.DBLClient(self.bot, os.getenv("DBL_TOKEN"), autopost=True)

	@commands.Cog.listener(name="on_dbl_vote")
	async def on_dbl_vote(self, data):
		if data["type"] == "upvote" and data["bot"] == self.bot.user.id:
			user_id = data["user"]

			# - isWeekend or is_weekend?
			num_votes = 1 if not data.get("isWeekend", data.get("is_weekend")) else 2

			user = self.bot.get_user(user_id)

			await self.bot.db["players"].update_one({"_id": user_id}, {"$inc": {"votes": num_votes}}, upsert=True)

			if user is not None:
				support_server = self.bot.get_guild(SupportServer.ID)

				try:
					await user.send("Thank you for voting for me! :heart:")

					member = support_server.get_member(user_id)

					if member is None:
						await user.send("psst...you can join our support server here https://discord.gg/QExQuvE")

				except (discord.Forbidden, discord.HTTPException):
					""" Failed """

	@commands.command(name="vote")
	async def vote(self, ctx):
		""" Link to the vote site. """

		await ctx.send(
			"https://discord.boats/bot/666616515436478473\n"
			"https://top-bots.xyz/bot/666616515436478473"
		)


def setup(bot):
	if not bot.debug:
		bot.add_cog(Vote(bot))
