import discord

from discord.ext import commands

from datetime import datetime

from bot.common import checks
from bot.common import AboSQL

from bot.common._leaderboard import ABOLeaderboard

from bot.structures import Leaderboard
from bot.common.database import DBConnection


class ABO(commands.Cog, name="abo"):
	def __init__(self, bot):
		self.bot = bot

		self._leaderboard = Leaderboard(
			title="Trophy Leaderboard",
			file="game_stats.json",
			columns=[1, 2, 3],
			members_only=True,
			size=100,
			bot=self.bot,
			sort_func=lambda kv: kv[1][2]
		)

		self._leaderboard.update_column(1, "Lvl")
		self._leaderboard.update_column(2, "")
		self._leaderboard.update_column(3, "Updated", lambda data: ABO.get_days_since_update(data))

	async def cog_check(self, ctx):
		return (
				await checks.channel_has_tag(ctx, "abo", self.bot.svr_cache) and
				await checks.author_has_role(ctx, "member", self.bot.svr_cache)
		)

	@staticmethod
	def get_days_since_update(data: dict):
		days = (datetime.today() - datetime.strptime(data[0], "%d/%m/%Y %H:%M:%S")).days

		return f"{days} days" if days >= 7 else ""

	@commands.command(name="me", help="Display your own stats")
	async def get_stats(self, ctx: commands.Context):
		with DBConnection() as con:
			con.cur.execute(AboSQL.SELECT_USER, (ctx.author.id,))

			user = con.cur.fetchone()

		if user is None:
			return await ctx.send(f":x: **{ctx.author.display_name}**, I found no stats for you")

		date = user.dateset.strftime("%d/%m/%Y")
		embed = self.bot.create_embed(title=ctx.author.display_name, desc=f":alarm_clock: **{date}**")
		text = f":joystick: **{user.lvl}**\n:trophy: **{user.trophies:,}**"

		embed.add_field(name="ABO Stats", value=text)

		return await ctx.send(embed=embed)

	@commands.command(name="set", aliases=["s"], help="Set your game stats")
	async def set_stats(self, ctx, level: int, trophies: int):
		with DBConnection() as con:
			params = (ctx.author.id, level, trophies, datetime.now())

			con.cur.execute(AboSQL.UPDATE, params)

		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@commands.is_owner()
	@commands.command(name="setuser", hidden=True)
	async def set_user(self, ctx, user: discord.Member, level: int, trophies: int):
		with DBConnection() as con:
			params = (user.id, level, trophies, datetime.now())

			con.cur.execute(AboSQL.UPDATE, (user.id, level, trophies, datetime.now()))

		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@commands.command(name="alb", help="Display trophy leaderboard")
	async def leaderboard(self, ctx: commands.Context):
		lb = ABOLeaderboard()

		return await ctx.send(lb.get(ctx.author))


def setup(bot):
	bot.add_cog(ABO(bot))