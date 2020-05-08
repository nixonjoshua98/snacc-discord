import discord

from discord.ext import commands

from datetime import datetime

from bot.structures.leaderboard import TrophyLeaderboard

from bot.common import checks
from bot.common.queries import AboSQL
from bot.common.converters import Range


class ABO(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.leaderboards = dict()

	async def cog_check(self, ctx):
		return await checks.server_has_member_role(ctx)

	@commands.command(name="set", aliases=["s"], usage="<level> <trophies>")
	async def set_stats(self, ctx, level: Range(0, 150), trophies: Range(0, 6_000)):
		""" Set your ABO stats, which are visible on the leaderboard. """

		await self.bot.pool.execute(AboSQL.UPDATE_USER, ctx.author.id, level, trophies, datetime.now())

		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@commands.has_permissions(administrator=True)
	@commands.command(name="setuser", aliases=["su"], usage="<user> <level> <trophies>")
	async def set_user(self, ctx, user: discord.Member, level: Range(0, 150), trophies: Range(0, 7_500)):
		""" [Admin] Set another users ABO stats. """

		await self.bot.pool.execute(AboSQL.UPDATE_USER, user.id, level, trophies, datetime.now())

		await ctx.send(f"**{user.display_name}** :thumbsup:")

	@commands.has_permissions(administrator=True)
	@commands.command(name="shame", help="Shame others")
	async def shame(self, ctx: commands.Context):
		""" [Admin] Mention the members who are missing or lacking stat updates.  """

		svr_config = await self.bot.get_server(ctx.guild)

		role = ctx.guild.get_role(svr_config["memberrole"])

		all_data = await self.bot.pool.fetch(AboSQL.SELECT_ALL)

		data_table = {row["userid"]: row for row in all_data}

		lacking, missing = [], []

		for member in role.members:
			user_data = data_table.get(member.id, None)

			if user_data is None:
				missing.append(member)
				continue

			if (datetime.now() - user_data["dateset"]).days >= 7:
				lacking.append(member)

		msg = f"**Members: {len(role.members)}**\n"

		if len(lacking) > 0:
			msg += "\n" + "**__Lacking__** - Members who have not updated their stats in the past 7 days\n"
			msg += " | ".join(map(lambda ele: ele.mention, lacking)) + "\n"

		if len(missing) > 0:
			msg += "\n" + "**__Missing__** - Set your stats using `!set <level> <trophies>`\n"
			msg += " | ".join(map(lambda ele: ele.mention, missing))

		await ctx.message.delete()

		await ctx.send(msg)

	@commands.command(name="alb", help="Leaderboard")
	async def leaderboard(self, ctx: commands.Context):
		""" Show the trophy leaderboard for the ABO game. """

		return await ctx.send(await TrophyLeaderboard(ctx).create())


def setup(bot):
	bot.add_cog(ABO(bot))
