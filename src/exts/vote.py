import dbl
import os
import discord

from discord.ext import commands

from src import inputs
from src.common.models import BankM, PlayerM


class Vote(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.topgg = dbl.DBLClient(self.bot, os.getenv("TOPGG_TOKEN"), autopost=True)

	@commands.Cog.listener(name="on_dbl_vote")
	async def on_dbl_vote(self, data):
		if data["type"] == "upvote" and data["bot"] == self.bot.user.id:
			user_id = data["user"]

			num_votes = 1 if not data["isWeekend"] else 2

			user = self.bot.get_user(user_id)

			async with self.bot.pool.acquire() as con:
				_ = await BankM.fetchrow(con, user_id)
				_ = await PlayerM.fetchrow(con, user_id)

				await PlayerM.increment(con, user_id, field="votes", amount=num_votes)

			if user is not None:
				try:
					await user.send("Thank you for voting for me! :heart:")
				except (discord.Forbidden, discord.HTTPException):
					""" Failed """

	@commands.command(name="vote")
	async def vote(self, ctx):
		""" Link to the vote sites. """

		await ctx.send(
			"\n".join(
				(
					"**Voting for me is super helpful and greatly appreciated!** :heart:",

					"https://discord.boats/bot/666616515436478473",
					"https://top-bots.xyz/bot/666616515436478473"
				)
			)
		)

	@commands.command(name="voters")
	async def show_voters(self, ctx):
		""" Show the top voters (love you all) """

		async def query():
			return await ctx.bot.pool.fetch(PlayerM.SELECT_TOP_VOTERS)

		await inputs.show_leaderboard(ctx, "Top Voters", columns=["votes"], order_by="votes", query_func=query)


def setup(bot):
	if not bot.debug and os.getenv("TOPGG_TOKEN") is not None:
		bot.add_cog(Vote(bot))
