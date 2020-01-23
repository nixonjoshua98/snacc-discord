import discord
import os

from datetime import datetime
from discord.ext import commands

from darkness.common import data_reader
from darkness.common import myjson

"""
	?s 1 2: Set stats
	?lbt: get lb sorted by trophy count
"""

# Indexes
DATE_STAT = 0
LEVEL_STAT = 1
TROPHIES_STAT = 2


class MemberStats(commands.Cog):
	MAX_NUM_ROWS = 15
	DAYS_COOLDOWN = 1

	def __init__(self, bot):
		self.bot = bot

		myjson.get_json(file="member_stats.json")

	@commands.has_role("Darkness Employee")
	@commands.command(name="stats", aliases=["s"], description="Set your stats ``!s <lvl> <trophies>``")
	async def set_stats(self, ctx, level: int, trophies: int):
		author_id = ctx.author.id

		member_stats_file = data_reader.read_json("member_stats.json")

		author_stats = member_stats_file.get(str(author_id), [])[-(self.MAX_NUM_ROWS + 1):]
		ok_to_update = True

		if author_stats:
			date_object = datetime.strptime(author_stats[-1][DATE_STAT], "%d/%m/%Y")
			days_since = (datetime.today() - date_object).days

			ok_to_update = days_since >= self.DAYS_COOLDOWN

		if ok_to_update:
			today = datetime.today().strftime("%d/%m/%Y")

			author_stats.append([today, level, trophies])

			data_reader.update_key("member_stats.json", key=str(author_id), value=author_stats)

			if not os.getenv("DEBUG", False):
				myjson.upload_json(file="member_stats.json")

		emoji = ":thumbsup:" if ok_to_update else ":thumbsdown:"

		await ctx.send(f"``{ctx.author.display_name}`` {emoji}")

	@commands.is_owner()
	@commands.command(name="remove", hidden=True)
	async def remove_user(self, ctx, username: str):
		member = ctx.guild.get_member_named(username)

		if member is not None:
			data_reader.remove_key("member_stats.json", key=str(member.id))

			if not os.getenv("DEBUG", False):
				myjson.upload_json(file="member_stats.json")

			await ctx.send(f"``{member.display_name}`` has been removed")

	@commands.is_owner()
	@commands.command(name="rewind", hidden=True)
	async def rewind_user(self, ctx, username: str):
		member = ctx.guild.get_member_named(username)

		if member is not None:
			member_stats_file = data_reader.read_json("member_stats.json")

			rows = member_stats_file.get(str(member.id), [])
			rows = rows[:len(rows) - 1]

			data_reader.update_key("member_stats.json", key=str(member.id), value=rows)

			if not os.getenv("DEBUG", False):
				myjson.upload_json(file="member_stats.json")

			await ctx.send(f"``{member.display_name}`` has been rewinded")

		else:
			await ctx.send(f"Rewind on ``{member.display_name}`` has failed")

	@commands.command(name="lbt", description="Show member stats sorted by trophies")
	async def get_stats_sorted_by_trophies(self, ctx):
		msg = self.create_stat_leaderboard(lambda d: d[1][-1][TROPHIES_STAT], "sorted by trophies", server=ctx.guild)
		await ctx.send(msg)

	@commands.command(name="lbl", description="Show member stats sorted by level")
	async def get_stats_sorted_by_level(self, ctx):
		msg = self.create_stat_leaderboard(lambda d: d[1][-1][LEVEL_STAT], "sorted by level", server=ctx.guild)
		await ctx.send(msg)

	@commands.command(name="lbd", description="Show member stats sorted by last update date")
	async def get_stats_sorted_by_date(self, ctx):
		def sort_by_date(d):
			return datetime.strptime(d[1][-1][DATE_STAT], "%d/%m/%Y")

		msg = self.create_stat_leaderboard(sort_by_date, "sorted by date", server=ctx.guild)
		await ctx.send(msg)

	@commands.has_role("Darkness Employee")
	@commands.command(name="me", description="Shows your latest stats")
	async def get_user_own_stats(self, ctx):
		member_stats_file = data_reader.read_json("member_stats.json")

		user_stats = member_stats_file.get(str(ctx.author.id), [])

		display_name = ctx.guild.get_member(ctx.author.id).display_name

		if user_stats:
			recent_row = user_stats[-1]

			embed = discord.Embed(
				title=f"Member: {display_name}",
				description=f"Most Recent Stat Update",
				color=0xff8000,
			)

			embed.add_field(name="Date Recorded", value=recent_row[DATE_STAT])
			embed.add_field(name="Level", value=recent_row[LEVEL_STAT])
			embed.add_field(name="No. Trophies", value=recent_row[TROPHIES_STAT])

			embed.set_footer(text=self.bot.user.display_name)

			await ctx.send(embed=embed)

		else:
			await ctx.send(f"``{display_name}``, I could not find any stats for you")

	@staticmethod
	def create_stat_leaderboard(sort_func, sort_name: str, *, server: discord.Guild):
		member_stats_file = data_reader.read_json("member_stats.json")

		sorted_data = sorted(member_stats_file.items(), key=sort_func, reverse=True)

		msg = "```"

		msg += f"Member Stats ({sort_name})\n\n"

		rank = 0

		role = discord.utils.find(lambda r: r.name == "Darkness Employee", server.roles)

		for k, v in sorted_data:
			member = server.get_member(int(k))

			is_guild_member = role in member.roles

			if member is None or not is_guild_member:
				continue

			rank += 1

			username = member.display_name

			msg += f"#{rank} {username} ({v[-1][DATE_STAT]})\n"
			msg += f"\tLvl: {v[-1][LEVEL_STAT]} Trophies: {v[-1][TROPHIES_STAT]}\n"

		msg += "```"

		return msg

