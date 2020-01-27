
import os
import discord
import operator

from datetime import datetime

from discord.ext import commands
from discord.ext.commands import CommandError

from darkness.common import (data_reader)
from darkness.common.backup import Backup
from darkness.common import functions
from darkness.common.constants import (SET_STATS_COOLDOWN, MAX_NUM_STAT_ENTRIES, MEMBER_ROLE_NAME, BOT_CHANNELS)


# - Checks
async def is_in_bot_channel(ctx):
	if ctx.channel.id not in BOT_CHANNELS:
		raise CommandError(f"**{ctx.author.display_name}**. Commands are disabled in this channel")

	return True

# -


def add_stat_entry(user_id, level, trophies):
	stats = get_member_stats(user_id)
	today = datetime.today().strftime("%d/%m/%Y %H:%M:%S")
	stats.append([today, level, trophies])
	data_reader.update_key("member_stats.json", key=str(user_id), value=stats)

	return {user_id: stats}


def get_member_stats(user_id):
	member_stats_file = data_reader.read_json("member_stats.json")
	stats = member_stats_file.get(str(user_id), [])[-(MAX_NUM_STAT_ENTRIES + 1):]

	return stats


def create_leaderboard(ls, title):
	msg = f"```Guild Leaderboard (sorted by {title})\n"

	rank = 1

	for row in ls:
		username, date, level, trophies = row

		msg += f"\n#{rank} {username} {date}"
		msg += f"\n\tLvl: {level} Trophies: {trophies}"

		rank += 1

	msg += "```"

	return msg


def get_all_members_latest_stat(guild):
	member_stats_file = data_reader.read_json("member_stats.json")

	member_role = discord.utils.get(guild.roles, name=MEMBER_ROLE_NAME)

	data = []

	for k, v in member_stats_file.items():
		member = guild.get_member(int(k))

		if member is None or member_role not in member.roles or not v:
			continue

		date, level, trophies = v[-1]

		date = functions.format_date_str(date)

		data.append((member.display_name, date, level, trophies))

	return data


class MemberStats(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		Backup.download_file("member_stats.json")

	@commands.has_role(MEMBER_ROLE_NAME)
	@commands.check(is_in_bot_channel)
	@commands.guild_only()
	@commands.cooldown(1, SET_STATS_COOLDOWN, commands.BucketType.member)
	@commands.command(name="stats", aliases=["s"], description="Set your stats ``!s <lvl> <trophies>``")
	async def set_stats(self, ctx, level: int, trophies: int):
		add_stat_entry(ctx.author.id, level, trophies)

		if not os.getenv("DEBUG", False):
			Backup.upload_file("member_stats.json")

		await ctx.send(f"``{ctx.author.display_name}`` :thumbsup:")

	@commands.has_role(MEMBER_ROLE_NAME)
	@commands.check(is_in_bot_channel)
	@commands.guild_only()
	@commands.command(name="me", description="Shows your latest stats")
	async def get_stats(self, ctx):
		stats = get_member_stats(ctx.author.id)
		username = ctx.author.display_name

		if not stats:
			await ctx.send(f"``{username}``, I could not find any stats for you")
			return

		last_row = stats[-1]

		embed = discord.Embed(title=f"Member: {username}", description=f"Most Recent Stat Update", color=0xff8000)

		date = functions.format_date_str(last_row[0])

		embed.add_field(name="Date Recorded", value=date)
		embed.add_field(name="Level", value=last_row[1])
		embed.add_field(name="No. Trophies", value=last_row[2])

		embed.set_footer(text=self.bot.user.display_name)

		await ctx.send(embed=embed)

	@commands.has_role(MEMBER_ROLE_NAME)
	@commands.check(is_in_bot_channel)
	@commands.guild_only()
	@commands.command(name="lbd", description="Show member stats sorted by last update date")
	async def get_date_lb(self, ctx):
		stats = get_all_members_latest_stat(ctx.guild)

		stats.sort(key=lambda row: datetime.strptime(row[1], "%d/%m/%Y"), reverse=True)

		msg = create_leaderboard(stats, "date")

		await ctx.send(msg)

	@commands.has_role(MEMBER_ROLE_NAME)
	@commands.check(is_in_bot_channel)
	@commands.guild_only()
	@commands.command(name="lbl", description="Show member stats sorted by level")
	async def get_level_lb(self, ctx):
		stats = get_all_members_latest_stat(ctx.guild)

		stats.sort(key=operator.itemgetter(2), reverse=True)

		msg = create_leaderboard(stats, "level")

		await ctx.send(msg)

	@commands.has_role(MEMBER_ROLE_NAME)
	@commands.check(is_in_bot_channel)
	@commands.guild_only()
	@commands.command(name="lbt", description="Show member stats sorted by trophies")
	async def get_trophy_lb(self, ctx):
		stats = get_all_members_latest_stat(ctx.guild)

		stats.sort(key=operator.itemgetter(3), reverse=True)

		msg = create_leaderboard(stats, "trophies")

		await ctx.send(msg)
