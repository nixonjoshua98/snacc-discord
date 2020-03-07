import enum
import discord

from src.common import FileReader


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
	}
}


async def create_leaderboard(author: discord.Member, lb_type: Type):
	lookup = LOOKUP_TABLE[lb_type]

	with FileReader(lookup["file"]) as f:
		data = f.data()

		# Sort the data if needed
		if lookup.get("sort_func", None) is not None:
			data = sorted(data.items(), key=lookup["sort_func"], reverse=True)


	MAX_USERNAME_LENGTH = 20
	LEADERBOARD_SIZE = 10

	rows, column_lengths = [], []

	author_row = None

	rows.append(["#", "Member"] + [col.title() for col in lookup.get("columns", [])])

	for rank, (user_id, user_data) in enumerate(data, start=1):
		member = author.guild.get_member(int(user_id))

		# Rank
		rank_string = f"#{rank:02d}"

		# Get username to show on the row
		username = member.display_name[0:MAX_USERNAME_LENGTH] if member else ">> User Left <<"

		current_row = [rank_string, username]

		# Additional columns
		for extra_col in lookup.get("columns", []):
			current_row.append(str(user_data.get(extra_col, "ERROR")))

		rows.append(current_row)

		if member and member.id == author.id:
			author_row = current_row

		# Update columns lengths
		for i, col in enumerate(current_row):
			if i == len(column_lengths):
				column_lengths.append(0)

			column_lengths[i] = max(column_lengths[i], len(col))


	leaderboard_string = ""

	leaderboard_string += f"{lookup['title']}\n\n"

	# Build the leaderboard
	for row in rows[0:LEADERBOARD_SIZE]:
		for j, col in enumerate(row):
			leaderboard_string += f"{col}{' ' * (column_lengths[j] - len(col))}" + " "

		leaderboard_string += "\n"

	# Author rank (if data present)
	if author_row is not None:
		leaderboard_string += "-" * (sum(column_lengths) + len(column_lengths)) + "\n"
		for j, col in enumerate(author_row):
			leaderboard_string += f"{col}{' ' * (column_lengths[j] - len(col))}" + " "

	print(leaderboard_string)

	return "```c++\n" + leaderboard_string + "```"



