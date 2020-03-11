import enum

import discord

from src.common import FileReader

from src.common import functions


class Type(enum.IntEnum):
	COIN = 0,
	PET = 1,
	ABO = 2


LOOKUP_TABLE = {
	Type.COIN: {
		"title": "Coin Leaderboard",
		"file": "coins.json",
		"sort_func": lambda kv: kv[1]["coins"],
		"columns": ["coins"]
	},

	Type.PET: {
		"title": "Pet Leaderboard",
		"file": "pet_stats.json",
		"sort_func": lambda kv: kv[1]["xp"],
		"columns": ["name", "xp"],
		"column_funcs": {"xp": lambda data: functions.pet_level_from_xp(data)},
		"headers": {"xp": "lvl"}
	},

	Type.ABO: {
		"title": "Auto Battles Online",
		"file": "game_stats.json",
		"sort_func": lambda kv: kv[1][2],  # Sort the data with this function
		"columns": [1, 2, 3],  # Either indexes for lists for keys for dicts
		# Optional column headers: replaces the column values with these
		"headers": {1: "Lvl", 2: "", 3: "Updated"},
		# Functions whose result becomes the value for that column
		"column_funcs": {3: lambda data: functions.abo_days_since_column(data)},
		"leaderboard_size": 30,
		"members_only": True  # Only display members who have the allocated member role
	}
}

import time

async def create_leaderboard(author: discord.Member, lb_type: Type) -> str:
	now = time.time()

	lookup = LOOKUP_TABLE[lb_type]

	with FileReader(lookup["file"]) as stats, FileReader("server_settings.json") as server_settings:
		data = stats.data()

		# Sort the data if needed
		if lookup.get("sort_func", None) is not None:
			data = sorted(data.items(), key=lookup["sort_func"], reverse=True)

		member_role_id = server_settings.get(author.guild.id, default_val={}).get("member_role", None)


	MAX_COLUMN_SIZE = 15
	LEADERBOARD_SIZE = lookup.get("leaderboard_size", 10)
	MEMBERS_ONLY = lookup.get("members_only", False)

	rows, column_lengths = [], []

	author_row = None

	# Column headers
	rows.append(["#", "MEMBER"] + [lookup.get("headers", {}).get(col, col).upper() for col in lookup.get("columns", [])])

	# Initial column widths
	for i, col in enumerate(rows[0]):
		column_lengths.append(len(col))

	rank = 0

	member_role = discord.utils.get(author.guild.roles, id=member_role_id)

	for user_id, user_data in data:
		member = author.guild.get_member(int(user_id))

		# If member is invalid, a bot, or not a member when it is members only
		if member is None or member.bot or (member_role and member_role not in member.roles and MEMBERS_ONLY):
			continue

		rank += 1

		# Rank
		rank_string = f"#{rank:02d}"

		# Get username to show on the row
		username = member.display_name[0:MAX_COLUMN_SIZE]

		current_row = [rank_string, username]

		# Additional columns
		for extra_col in lookup.get("columns", []):
			try:
				col_val = user_data[extra_col]
			except (IndexError, KeyError):
				col_val = "N/A"

			func = lookup.get("column_funcs", {}).get(extra_col, None)

			# Does a function need to be called?
			if func is not None:
				col_val = func(user_data)

			current_row.append(str(col_val)[0:MAX_COLUMN_SIZE])

		rows.append(current_row)

		# If author
		if member.id == author.id:
			author_row = current_row

		# Update columns lengths
		for i, col in enumerate(current_row):
			column_lengths[i] = max(column_lengths[i], len(col))

	leaderboard_string = f"{lookup['title']}\n"

	leaderboard_string += "-" * (sum(column_lengths) + len(column_lengths)) + "\n"

	# Build the leaderboard
	for row in rows[0:LEADERBOARD_SIZE + 1]:
		for j, col in enumerate(row):
			leaderboard_string += f"{col}{' ' * (column_lengths[j] - len(col))}" + " "

		leaderboard_string += "\n"

	# Author rank (if data present)
	if author_row is not None:
		leaderboard_string += "-" * (sum(column_lengths) + len(column_lengths)) + "\n"
		for j, col in enumerate(author_row):
			leaderboard_string += f"{col}{' ' * (column_lengths[j] - len(col))}" + " "

	print(f"Time taken to build leaderboard ({lb_type.name}):", round(time.time() - now, 5), sep=" ")

	return "```c++\n" + leaderboard_string + "```"



