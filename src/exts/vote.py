import dbl
import os
import discord

from discord.ext import commands, tasks

from src.common import SupportServer


class Vote(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.support_server = self.bot.get_guild(SupportServer.ID)

		if os.getenv("DBL_TOKEN") not in (None, "TOKEN", "VALUE", "", " "):
			self.dbl = dbl.DBLClient(self.bot, os.getenv("DBL_TOKEN"), autopost=True)

		self.refresh_support_server.start()

	@tasks.loop(minutes=30.0)
	async def refresh_support_server(self):
		self.support_server = self.bot.get_guild(SupportServer.ID)

	@commands.Cog.listener(name="on_dbl_vote")
	async def on_dbl_vote(self, data):
		if data["type"] == "upvote" and data["bot"] == self.bot.user.id:
			user_id = data["user"]

			num_votes = 1 if not data["isWeekend"] else 2

			user = self.bot.get_user(user_id)

			await self.bot.mongo.increment_one("players", {"_id": user_id}, {"votes": num_votes})

			if user is not None:
				try:
					await user.send("Thank you for voting for me! :heart:")

					member = self.support_server.get_member(user_id)

					if member is None:
						await user.send("psst...you can join our support server here https://discord.gg/QExQuvE")

				except (discord.Forbidden, discord.HTTPException):
					""" Failed """

	@commands.command(name="vote")
	async def vote(self, ctx):
		""" Link to the vote site. """

		await ctx.send(
			"https://discord.boats/bot/666616515436478473"
			"https://top-bots.xyz/bot/666616515436478473"
		)


def setup(bot):
	if not bot.debug:
		bot.add_cog(Vote(bot))
