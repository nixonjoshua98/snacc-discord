import discord
from discord.ext import commands

from datetime import datetime

from snacc import utils

from snacc.common import checks
from snacc.common.queries import ArenaStatsSQL

from snacc.classes.menus import EmbedMenu
from snacc.classes.converters import UserMember
from snacc.classes.leaderboard import TrophyLeaderboard


class ArenaStats(commands.Cog, name="Arena Stats"):
	""" Arena stats for the Auto battles Online game. """

	def __init__(self):
		self.leaderboards = dict()

	async def cog_check(self, ctx):
		return await checks.user_has_member_role(ctx)

	@staticmethod
	async def set_users_stats(ctx, target: discord.Member, level: int, trophies: int):
		"""
		Add a new stat entry for the user and limit the number of stat entries for the user in the database.

		:param ctx: Discord context, we get the bot from it.
		:param target: The user whose stats we are updating
		:param level: The level of the user
		:param trophies: The amount of trophies they have
		"""

		async with ctx.bot.pool.acquire() as con:
			async with con.transaction():
				await con.execute(ArenaStatsSQL.INSERT_ROW, target.id, datetime.now(), level, trophies)

				results = await con.fetch(ArenaStatsSQL.SELECT_USER, target.id)

				if len(results) > 9:
					for result in results[9:]:
						await con.execute(ArenaStatsSQL.DELETE_ROW, target.id, result["date_set"])

	@commands.cooldown(1, 60 * 60 * 12, commands.BucketType.user)
	@commands.command(name="set", aliases=["s"], cooldown_after_parsing=True)
	async def set_stats(self, ctx, level: int, trophies: int):
		"""
		Set your ABO stats, which are visible on the leaderboard.
		Setting your stats regularly also stops you from appearing in the [shame] list.
		"""

		await self.set_users_stats(ctx, ctx.author, level, trophies)

		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@commands.cooldown(1, 60, commands.BucketType.user)
	@commands.has_permissions(administrator=True)
	@commands.command(name="setuser", aliases=["su"], cooldown_after_parsing=True)
	async def set_user_stats_command(self, ctx, target: UserMember(), level: int, trophies: int):
		""" [Admin] Set another users ABO stats. """

		await self.set_users_stats(ctx, target, level, trophies)

		await ctx.send(f"**{target.display_name}** :thumbsup:")

	@commands.command(name="me", aliases=["stats"])
	async def get_stats(self, ctx, target: UserMember() = None):
		"""
		View your stat history which is stored (older stats may have been deleted).
		"""

		target = ctx.author if target is None else target

		results = await ctx.bot.pool.fetch(ArenaStatsSQL.SELECT_USER, target.id)

		if results is None:
			return await ctx.send("I found not stats for you.")

		embeds = []

		for page in utils.chunk_list(results, 7):
			embed = discord.Embed(title=f"{target.display_name}'s Arena Stats", colour=discord.Color.orange())

			for row in page:
				name = row["date_set"].strftime("%d/%m/%Y")
				value = f"Level: {row['level']:,}\nTrophies: {row['trophies']:,}"

				embed.add_field(name=name, value=value)

			embeds.append(embed)

		await EmbedMenu(embeds).send(ctx) if len(embeds) > 1 else await ctx.send(embed=embeds[0])

	@commands.cooldown(1, 60, commands.BucketType.guild)
	@commands.command(name="alb")
	async def leaderboard(self, ctx: commands.Context):
		""" Show the server trophy leaderboard. """

		return await ctx.send(await TrophyLeaderboard(ctx).create())


def setup(bot):
	bot.add_cog(ArenaStats())
