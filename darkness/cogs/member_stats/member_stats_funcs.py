import discord
import typing

from datetime import datetime

from darkness.common import data_reader
from darkness.common import functions
from darkness.common.constants import (MAX_NUM_STAT_ENTRIES, MEMBER_ROLE_NAME)


def add_stat_entry(user_id: int, level: int, trophies: int) -> int:
	stats = get_member_stats(user_id)[1: MAX_NUM_STAT_ENTRIES]

	today = datetime.today().strftime("%d/%m/%Y %H:%M:%S")

	stats.append([today, level, trophies])

	data_reader.update_key("member_stats.json", key=str(user_id), value=stats)

	return True


def get_member_stats(user_id, recent_row_only: bool = False):
	member_stats_file = data_reader.read_json("member_stats.json")

	stats = member_stats_file.get(str(user_id), [])

	if not recent_row_only:
		return stats

	elif recent_row_only:
		return None if len(stats) == 0 else stats[-1]


def create_user_stat_embed(member: discord.Member) -> typing.Union[discord.Embed, None]:
	stats = get_member_stats(member.id, recent_row_only=True)

	if stats is None:
		return None

	embed = discord.Embed(title=f"Member: {member.display_name}", description=f"Member Stats", color=0xff8000)

	date = functions.to_date(stats[0])

	date = date.strftime("%d/%m/%Y")

	embed.add_field(name="Date Recorded", value=date)
	embed.add_field(name="Level", value=stats[1])
	embed.add_field(name="No. Trophies", value=stats[2])

	return embed


def create_leaderboard(ls, title):
	msg = f"```Guild Leaderboard (sorted by {title})\n"

	rank = 1

	for row in ls:
		username, days_ago, level, trophies = row

		msg += f"\n#{rank} {username} "

		if days_ago > 0:
			msg += f"({days_ago} day{'' if days_ago == 1 else 's'} ago)"

		msg += f"\n\tLvl: {level} Trophies: {trophies}"

		rank += 1

	msg += "```"

	return msg


def get_all_members_latest_stats(guild):
	member_stats_file = data_reader.read_json("member_stats.json")

	member_role = discord.utils.get(guild.roles, name=MEMBER_ROLE_NAME)

	data = []

	for k, v in member_stats_file.items():
		member = guild.get_member(int(k))

		if member is None or member_role not in member.roles or not v:
			continue

		date, level, trophies = v[-1]

		date = functions.to_date(date)

		hours_since_update = datetime.today() - date

		data.append((member.display_name, hours_since_update.days, level, trophies))

	return data


def get_inactive_members(guild: discord.Guild, days: int = 3) -> list:
	member_role = discord.utils.get(guild.roles, name=MEMBER_ROLE_NAME)

	inactive_members = []

	for member in guild.members:
		if member_role not in member.roles:
			continue

		stats = get_member_stats(member.id, recent_row_only=True)

		if stats is None:
			inactive_members.append(member)
			continue

		days_since_update = functions.days_since(stats[0])

		if days_since_update >= days:
			inactive_members.append(member)

	return inactive_members
