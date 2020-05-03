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

		await self.bot.pool.execute(AboSQL.UPDATE, ctx.author.id, level, trophies, datetime.now())

		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@commands.has_permissions(administrator=True)
	@commands.command(name="setuser", aliases=["su"], usage="<user> <level> <trophies>")
	async def set_user(self, ctx, user: discord.Member, level: IntegerRange(0, 150), trophies: IntegerRange(0, 7_500)):
		""" Set another members ABO stats. """

		await self.bot.pool.execute(AboSQL.UPDATE, user.id, level, trophies, datetime.now())

		await ctx.send(f"**{user.display_name}** :thumbsup:")

	@commands.has_permissions(administrator=True)
	@commands.command(name="shame", help="Shame others")
	async def shame(self, ctx: commands.Context):
		""" Mention everyone who has not updated their stats in the last 7 days. """

		member_role = await self.get_member_role(ctx.guild)

		all_data = await self.bot.pool.fetch(AboSQL.SELECT_ALL)

		msg = "**__Lacking Activity__**\n"

		for user in all_data:
			member = ctx.guild.get_member(user["userid"])

			days_since_update = (datetime.now() - user["dateset"]).days

			if member is not None and days_since_update >= 7 and member_role in member.roles:
				msg += f"{member.mention} ({days_since_update}) | "

		return await ctx.send(msg)

	@commands.command(name="alb", help="Leaderboard")
	async def leaderboard(self, ctx: commands.Context):
		""" Show the trophy leaderboard for the ABO game. """

		return await ctx.send(await TrophyLeaderboard(ctx).create())


def setup(bot):
	bot.add_cog(ABO(bot))
