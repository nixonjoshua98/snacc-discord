import discord

from discord.ext import commands

from datetime import datetime

from bot.structures.leaderboard import TrophyLeaderboard

from bot.common.queries import AboSQL
from bot.common.converters import IntegerRange

MEMBER_ROLE = 666615010579054614
DARKNESS_GUILD = 666613802657382435


class ABO(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.leaderboards = dict()

	async def cog_check(self, ctx):
		return ctx.guild.id == DARKNESS_GUILD and await self.get_member_role(ctx.guild) in ctx.author.roles

	async def get_member_role(self, guild):
		return guild.get_role(MEMBER_ROLE)

	@commands.command(name="ad")
	async def ad(self, ctx):
		""" Show the guild Ad currently stored. """

		with open("./bot/data/ad.txt") as fh:
			ad = fh.read()

		await ctx.send(ad)

	@commands.command(name="set", aliases=["s"], usage="<level> <trophies>")
	async def set_stats(self, ctx, level: IntegerRange(0, 150), trophies: IntegerRange(0, 6_000)):
		""" Set your ABO stats, which are visible on the leaderboard. """

		await self.bot.pool.execute(AboSQL.UPDATE_USER, ctx.author.id, level, trophies, datetime.now())

		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@commands.has_permissions(administrator=True)
	@commands.command(name="setuser", aliases=["su"], usage="<user> <level> <trophies>")
	async def set_user(self, ctx, user: discord.Member, level: IntegerRange(0, 150), trophies: IntegerRange(0, 7_500)):
		""" Set another members ABO stats. """

		await self.bot.pool.execute(AboSQL.UPDATE_USER, user.id, level, trophies, datetime.now())

		await ctx.send(f"**{user.display_name}** :thumbsup:")

	@commands.has_permissions(administrator=True)
	@commands.command(name="shame", help="Shame others")
	async def shame(self, ctx: commands.Context):
		""" Mention the members who are missing or lacking stat updates.  """

		role = await self.get_member_role(ctx.guild)

		all_data = await self.bot.pool.fetch(AboSQL.SELECT_ALL)

		data_table = {row["userid"]: row for row in all_data}

		lacking = []
		missing = []

		for member in role.members:
			user_data = data_table.get(member.id, None)

			if user_data is None:
				missing.append(member)
				continue

			delta_update = (datetime.now() - user_data["dateset"]).days

			if delta_update >= 7:
				lacking.append(member)

		msg = f"**Members: {len(role.members)}**\n"

		if len(lacking) > 0:
			msg += "\n" + "**__Lacking__** - Members who have not updated their stats in the past 7 days\n"
			msg += " | ".join(map(lambda ele: ele.mention, lacking)) + "\n"

		if len(missing) > 0:
			msg += "\n" + "**__Missing__** - Set your stats using `!set <level> <trophies>`\n"
			msg += " | ".join(map(lambda ele: ele.mention, missing))

		await ctx.send(msg)
		await ctx.message.delete()

	@commands.command(name="alb", help="Leaderboard")
	async def leaderboard(self, ctx: commands.Context):
		""" Show the trophy leaderboard for the ABO game. """

		return await ctx.send(await TrophyLeaderboard(ctx).create())


def setup(bot):
	bot.add_cog(ABO(bot))
