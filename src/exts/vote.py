import dbl
import os
import discord

from discord.ext import commands, tasks

from src import inputs
from src.common import SupportServer
from src.common.models import PlayerM


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

			async with self.bot.pool.acquire() as con:
				_ = await PlayerM.fetchrow(con, user_id)

				await PlayerM.increment(con, user_id, field="votes", amount=num_votes)

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
		""" Link to the vote sites. """

		await ctx.send(
			"**Vote for me! You will be rewarded shortly after!** :heart:"
			"\n"
			"https://top.gg/bot/666616515436478473 (not verified yet)"
			"\n"
			"\n"
			"https://discord.boats/bot/666616515436478473"
			"\n"
			"https://top-bots.xyz/bot/666616515436478473"
		)

	@commands.command(name="voters")
	async def show_voters(self, ctx):
		""" Show the top voters (love you all) """

		async def query():
			return await ctx.bot.pool.fetch(PlayerM.SELECT_TOP_VOTERS)

		await inputs.show_leaderboard(ctx, "Top Voters", columns=["votes"], order_by="votes", query_func=query)


def setup(bot):
	if not bot.debug:
		bot.add_cog(Vote(bot))
