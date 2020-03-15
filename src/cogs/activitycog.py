import discord

from discord.ext import commands

from src.common import FileReader


class ActivityCog(commands.Cog):
	@staticmethod
	async def create_leaderboard(author: discord.Member, leaderboard_config: dict) -> str:
		with FileReader(leaderboard_config["file"]) as stats, FileReader("server_settings.json") as server_settings:
			data = stats.data()

			# Sort the data if needed
			if leaderboard_config.get("sort_func", None) is not None:
				data = sorted(data.items(), key=leaderboard_config["sort_func"], reverse=True)

			member_role_id = server_settings.get_inner_key(author.guild.id, "roles", {}).get("member", None)

		max_column_width = 15
		leaderboard_size = leaderboard_config.get("leaderboard_size", 10)
		show_members_only = leaderboard_config.get("members_only", False)

		rows, column_lengths = [], []

		author_row = None

		# Column headers
		rows.append(
			["#", "MEMBER"] + [leaderboard_config.get("headers", {}).get(col, col).upper() for col in leaderboard_config.get("columns", [])])

		# Initial column widths
		for i, col in enumerate(rows[0]):
			column_lengths.append(len(col))

		rank = 0

		member_role = discord.utils.get(author.guild.roles, id=member_role_id)

		for user_id, user_data in data:
			member = author.guild.get_member(int(user_id))

			# If member is invalid, a bot, or not a member when it is members only
			if member is None or member.bot or (member_role and member_role not in member.roles and show_members_only):
				continue

			rank += 1

			# Rank
			rank_string = f"#{rank:02d}"

			# Get username to show on the row
			username = member.display_name[0:max_column_width]

			current_row = [rank_string, username]

			# Additional columns
			for extra_col in leaderboard_config.get("columns", []):
				try:
					col_val = user_data[extra_col]
				except (IndexError, KeyError):
					col_val = "N/A"

				func = leaderboard_config.get("column_funcs", {}).get(extra_col, None)

				# Does a function need to be called?
				if func is not None:
					col_val = func(user_data)

				current_row.append(str(col_val)[0:max_column_width])

			rows.append(current_row)

			# If author
			if member.id == author.id:
				author_row = current_row

			# Update columns lengths
			for i, col in enumerate(current_row):
				column_lengths[i] = max(column_lengths[i], len(col))

		leaderboard_string = f"{leaderboard_config['title']}\n"

		leaderboard_string += "-" * (sum(column_lengths) + len(column_lengths)) + "\n"

		# Build the leaderboard
		for row in rows[0:leaderboard_size + 1]:
			for j, col in enumerate(row):
				leaderboard_string += f"{col}{' ' * (column_lengths[j] - len(col))}" + " "

			leaderboard_string += "\n"

		# Author rank (if data present)
		if author_row is not None:
			leaderboard_string += "-" * (sum(column_lengths) + len(column_lengths)) + "\n"
			for j, col in enumerate(author_row):
				leaderboard_string += f"{col}{' ' * (column_lengths[j] - len(col))}" + " "

		return "```c++\n" + leaderboard_string + "```"
