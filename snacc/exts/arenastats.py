import discord

from discord.ext import commands

from datetime import datetime

from snacc.common import checks
from snacc.common.queries import ArenaStatsSQL
from snacc.classes.leaderboard import TrophyLeaderboard


class ArenaStats(commands.Cog):
	def __init__(self):
		self.leaderboards = dict()

	async def cog_check(self, ctx):
		return await checks.user_has_member_role(ctx)

	@commands.command(name="set", aliases=["s"])
	async def set_stats(self, ctx, level: int, trophies: int):
		"""
		Set your ABO stats, which are visible on the leaderboard.
		Setting your stats regularly also stops you from appearing in the [shame] list.
		"""

		async with ctx.bot.pool.acquire() as con:
			async with con.transaction():
				await ctx.bot.pool.execute(ArenaStatsSQL.INSERT_ROW, ctx.author.id, datetime.now(), level, trophies)

		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@commands.has_permissions(administrator=True)
	@commands.command(name="setuser", aliases=["su"])
	async def set_user_stats(self, ctx, target: discord.Member, level: int, trophies: int):
		""" [Admin] Set another users ABO stats. """

		async with ctx.bot.pool.acquire() as con:
			async with con.transaction():
				await ctx.bot.pool.execute(ArenaStatsSQL.INSERT_ROW, target.id, datetime.now(), level, trophies)

		await ctx.send(f"**{target.display_name}** :thumbsup:")

	@commands.command(name="me")
	async def get_stats(self, ctx):
		"""
		View your stat history which is stored (older stats may have been deleted).
		"""

		results = await ctx.bot.pool.fetch(ArenaStatsSQL.SELECT_USER, ctx.author.id)

		if results is None:
			return await ctx.send("I found not stats for you.")

		embed = discord.Embed(title=f"{ctx.author.display_name}'s Arena Stats", colour=discord.Color.orange())

		for row in results:
			name = row["date_set"].strftime("%d-%m-%Y")
			value = f"Level: {row['level']:,}\nTrophies: {row['trophies']:,}"

			embed.add_field(name=name, value=value)

		await ctx.send(embed=embed)

	@commands.command(name="alb")
	async def leaderboard(self, ctx: commands.Context):
		""" Show the server trophy leaderboard. """

		return await ctx.send(await TrophyLeaderboard(ctx).create())


def setup(bot):
	bot.add_cog(ArenaStats())
