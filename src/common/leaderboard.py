import enum
import discord

from src.common import FileReader

from src.cogs.pet import Pet


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
		"column_funcs": {"xp": lambda xp: Pet.level_from_xp(xp)},
		"headers": {"xp": "lvl"}
	},

	Type.ABO: {
		"title": "Auto Battles Online",
		"file": "game_stats.json",
		"sort_func": lambda kv: kv[1][2],
		"columns": [1, 2],
		"headers": {1: "Level", 2: "Trophies"}
	}
}


async def create_leaderboard(author: discord.Member, lb_type: Type) -> str:
	lookup = LOOKUP_TABLE[lb_type]

	with FileReader(lookup["file"]) as f:
		data = f.data()

		# Sort the data if needed
		if lookup.get("sort_func", None) is not None:
			data = sorted(data.items(), key=lookup["sort_func"], reverse=True)


	MAX_COLUMN_SIZE = 15
	LEADERBOARD_SIZE = 10

	rows, column_lengths = [], []

	author_row = None

	# Column headers
	rows.append(["#", "MEMBER"] + [lookup.get("headers", {}).get(col, col).upper() for col in lookup.get("columns", [])])

	rank = 0

	for user_id, user_data in data:
		member = author.guild.get_member(int(user_id))

		if member is None or member.bot:
			continue

		rank += 1

		# Rank
		rank_string = f"#{rank:02d}"

		# Get username to show on the row
		username = member.display_name[0:MAX_COLUMN_SIZE]

		current_row = [rank_string, username]

		# Additional columns
		for extra_col in lookup.get("columns", []):
			col_val = user_data[extra_col]

			# Does a function need to be called?
			if lookup.get("column_funcs", None) is not None:
				# Get the function for the column, otherwise create a lambda which does nothing
				func = lookup.get("column_funcs", dict).get(extra_col, lambda col: col)

				col_val = func(col_val)

			current_row.append(str(col_val)[0:MAX_COLUMN_SIZE])

		rows.append(current_row)

		if member and member.id == author.id:
			author_row = current_row

		# Update columns lengths
		for i, col in enumerate(current_row):
			if i == len(column_lengths):
				column_lengths.append(0)

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

	return "```c++\n" + leaderboard_string + "```"



