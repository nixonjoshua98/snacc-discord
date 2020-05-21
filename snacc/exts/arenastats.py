import discord
from discord.ext import commands

from datetime import datetime

from snacc import utils

from snacc.common import checks
from snacc.common.queries import ArenaStatsSQL

from snacc.classes.menus import EmbedMenu
from snacc.classes.converters import UserMember
from snacc.classes.leaderboards import TrophyLeaderboard


class ArenaStats(commands.Cog, name="Arena Stats"):
	""" Commands related to the Arena mode in the `Auto Battles Online` mobile game. """

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

				if len(results) > 14:
					for result in results[14:]:
						await con.execute(ArenaStatsSQL.DELETE_ROW, target.id, result["date_set"])

	@commands.cooldown(1, 60 * 60 * 12, commands.BucketType.user)
	@commands.command(name="set", aliases=["s"], cooldown_after_parsing=True)
	async def set_stats(self, ctx, level: int, trophies: int):
		""" Update your ABO stats, which are visible on the leaderboard. """

		await self.set_users_stats(ctx, ctx.author, level, trophies)

		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@commands.cooldown(1, 60, commands.BucketType.user)
	@commands.has_permissions(administrator=True)
	@commands.command(name="setuser", aliases=["su"], cooldown_after_parsing=True)
	async def set_user_stats_command(self, ctx, target: UserMember(), level: int, trophies: int):
		""" [Admin] Set another users ABO stats. """

		await self.set_users_stats(ctx, target, level, trophies)

		await ctx.send(f"**{target.display_name}** :thumbsup:")

	@commands.has_permissions(administrator=True)
	@commands.command(name="shame", help="Shame others")
	async def shame(self, ctx: commands.Context):
		""" [Admin] Mention the members who are missing or lacking stat updates.  """

		svr_config = await ctx.bot.get_server(ctx.guild)

		role = ctx.guild.get_role(svr_config["member_role"])

		all_data = await ctx.bot.pool.fetch(ArenaStatsSQL.SELECT_ALL_USERS_LATEST)

		data_table = {row["user_id"]: row for row in all_data}

		lacking, missing = [], []

		for member in role.members:
			user_data = data_table.get(member.id, None)

			if user_data is None:
				missing.append(member)
				continue

			days = (datetime.now() - user_data["date_set"]).days

			if days >= 7:
				lacking.append((member, days))

		msg = f"**Members: {len(role.members)}**\n"

		if len(lacking) > 0:
			msg += "\n" + "**__Lacking__** - Members who have not updated their stats in the past 7 days\n"
			msg += " | ".join(map(lambda ele: f"{ele[0].mention} **({ele[1]})**", lacking)) + "\n"

		if len(missing) > 0:
			msg += "\n" + "**__Missing__** - Set your stats using `!set <level> <trophies>`\n"
			msg += " | ".join(map(lambda ele: ele.mention, missing))

		await ctx.send(msg)

	@commands.command(name="stats")
	async def get_stats(self, ctx, target: UserMember() = None):
		"""
		View yours, or an optional users stats.
		"""

		target = ctx.author if target is None else target

		results = await ctx.bot.pool.fetch(ArenaStatsSQL.SELECT_USER, target.id)

		if results is None:
			return await ctx.send("I found not stats for you.")

		embeds = []

		today = datetime.today().strftime('%d/%m/%Y %H:%M:%S')

		for page in utils.chunk_list(results, 7):
			embed = discord.Embed(title=f"{target.display_name}'s Arena Stats", colour=discord.Color.orange())

			embed.set_thumbnail(url=target.avatar_url)

			embed.set_footer(text=f"{ctx.bot.user.name} | {today}", icon_url=ctx.bot.user.avatar_url)

			for row in page:
				name = row["date_set"].strftime("%d/%m/%Y")
				value = f"Level: {row['level']:,}\nTrophies: {row['trophies']:,}"

				embed.add_field(name=name, value=value)

			embeds.append(embed)

		await EmbedMenu(embeds).send(ctx) if len(embeds) > 1 else await ctx.send(embed=embeds[0])

	@commands.cooldown(1, 60, commands.BucketType.guild)
	@commands.command(name="trophies")
	async def show_leaderboard(self, ctx: commands.Context):
		""" Show the server trophy leader-statsboard. """

		await TrophyLeaderboard().send(ctx)

	@commands.command(name="alb")
	async def alb(self, ctx: commands.Context):
		await ctx.send("`!alb` will soon disappear and has moved to `!trophies`")


def setup(bot):
	bot.add_cog(ArenaStats())
