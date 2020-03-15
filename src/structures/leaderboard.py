import discord

from src.common import FileReader


class Leaderboard:
	MAX_COLUMN_WIDTH = 15

	def __init__(self, *, title: str, file: str, columns: list, members_only: bool = False, size: int = 10, sort_func=None):
		self._title = title
		self._file = file
		self._columns = columns
		self._col_headers = {}
		self._col_funcs = {}
		self._show_members_only = members_only
		self._size = size
		self._sort_func = sort_func

	def update_column(self, col: str, name: str, func=None):
		if col not in self._columns:
			raise Exception(f"Column '{col}' is not present in the leaderboard")

		self._col_headers[col] = name
		self._col_funcs[col] = func

	async def create(self, author: discord.Member):
		guild = author.guild
		data = self._get_data()
		rows = [["#", "MEMBER"] + [self._col_headers.get(col, col).upper() for col in self._columns]]
		member_role = Leaderboard._get_member_role(guild) if self._show_members_only else None
		column_lengths = list(map(len, rows[0]))
		current_rank = 0

		author_row = None

		for member_id, member_data in data:
			member = guild.get_member(int(member_id))

			if member is None or member.bot or (member_role not in member.roles and self._show_members_only):
				continue

			current_rank += 1

			row = self._create_row(current_rank, member, member_data)

			rows.append(row)

			if member.id == author.id:
				author_row = row

			column_lengths = [max(column_lengths[i], len(col)) for i, col in enumerate(row)]

		return self._create_leaderboard_string(rows, author_row, column_lengths)

	def _create_row(self, member_rank: int, member: discord.Member, member_data: dict):
		username = member.display_name[0:self.MAX_COLUMN_WIDTH]
		current_row = [f"#{member_rank:02d}", username]

		for col in self._columns:
			# TODO: This part only exists cos game_stats.json is not a JSON yet
			try:
				col_val = member_data[col]
			except (IndexError, KeyError):
				col_val = "N/A"

			func = self._col_funcs.get(col, None)

			col_val = func(member_data) if func is not None else col_val

			current_row.append(str(col_val)[0:self.MAX_COLUMN_WIDTH])

		return current_row

	def _create_leaderboard_string(self, rows, author_row, column_lengths):
		leaderboard_string = f"{self._title}\n"

		leaderboard_string += "-" * (sum(column_lengths) + len(column_lengths)) + "\n"

		# Build the leaderboard
		for row in rows[0:self._size + 1]:
			for j, col in enumerate(row):
				leaderboard_string += f"{col}{' ' * (column_lengths[j] - len(col))}" + " "

			leaderboard_string += "\n"

		self._add_author_rank(leaderboard_string, author_row, column_lengths)

		return "```c++\n" + leaderboard_string + "```"

	@staticmethod
	def _add_author_rank(leaderboard: str, author_row: str, column_lengths: list):
		if author_row is not None:
			leaderboard += "-" * (sum(column_lengths) + len(column_lengths)) + "\n"
			for j, col in enumerate(author_row):
				leaderboard += f"{col}{' ' * (column_lengths[j] - len(col))}" + " "

		return leaderboard

	def _get_data(self):
		with FileReader(self._file) as stats:
			data = stats.data()

		if self._sort_func is not None:
			data = sorted(data.items(), key=self._sort_func, reverse=True)

		return data

	@staticmethod
	def _get_member_role(guild: discord.Guild):
		with FileReader("server_settings.json") as server_settings:
			roles = server_settings.get_inner_key(guild.id, "roles", {})

		return guild.get_role(roles.get("member", None))



