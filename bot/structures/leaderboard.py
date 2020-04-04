import discord

from bot.common import FileReader


class Leaderboard:
	MAX_COLUMN_WIDTH = 10

	def __init__(self, *, title: str, file: str, columns: list, bot, **options):
		self._title = title
		self._file = file
		self._columns = columns
		self._col_headers = {}
		self._col_funcs = {}
		self._bot = bot
		self._show_members_only = options.get("members_only", False)
		self._size = options.get("size", 10)
		self._sort_func = options.get("sort_func", None)

	def update_column(self, col: str, name: str, func=None):
		if col not in self._columns:
			raise Exception(f"Column '{col}' is not present in the leaderboard")

		self._col_headers[col] = name
		self._col_funcs[col] = func

	async def create(self, author: discord.Member, server_only: bool = True):
		guild = author.guild
		data = self._get_data()
		rows = [["#", "MEMBER"] + [self._col_headers.get(col, col).upper() for col in self._columns]]
		member_role = Leaderboard._get_member_role(guild) if self._show_members_only else None
		column_lengths = list(map(len, rows[0]))
		current_rank = 0

		author_row = None

		for member_id, member_data in data:
			member = guild.get_member(int(member_id))

			# Server only
			if server_only and member is None:
				continue

			# Ignore other bots
			if member and member.bot:
				continue

			# Members only
			if member and member_role not in member.roles and self._show_members_only:
				continue

			current_rank += 1

			# Only look for the author if we have reached the leaderboard size - could be replaced with a search
			if current_rank > self._size:
				if member_id == str(author.id):
					author_row = self._create_row(current_rank, author, member_data)
					break
				continue

			row = self._create_row(current_rank, member if member else member_id, member_data)

			rows.append(row)

			if member and member.id == author.id:
				author_row = row

			column_lengths = [max(column_lengths[i], len(col)) for i, col in enumerate(row)]

		return self._create_leaderboard_string(rows, author_row, column_lengths)

	def _create_row(self, member_rank: int, member, member_data: dict):
		username = f"ID: {member}"[0:self.MAX_COLUMN_WIDTH]

		if isinstance(member, discord.Member):
			username = member.display_name[0:self.MAX_COLUMN_WIDTH]
		else:
			user = self._bot.get_user(int(member))

			if user is not None:
				username = user.name[0:self.MAX_COLUMN_WIDTH]

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
		leaderboard_string = f"{self._title}\n\n"

		author_row_string = self._get_author_row(author_row, column_lengths) + "\n"

		# Build the leaderboard
		for i, row in enumerate(rows[0:self._size + 1]):
			temp = []
			for j, col in enumerate(row):
				temp.append(f"{col}{' ' * (column_lengths[j] - len(col))}" + " ")

			row_len = sum([len(r) for r in temp])

			if (row_len + len(leaderboard_string)) > 1950:
				return "```c++\n" + leaderboard_string + "```"

			leaderboard_string += "".join(temp) + "\n"

		leaderboard_string = "```c++\n" + leaderboard_string

		if len(leaderboard_string) + len(author_row_string) <= 1950:
			leaderboard_string += author_row_string
		else:
			leaderboard_string += "See this? Tell my creator"

		return leaderboard_string + "```"

	@staticmethod
	def _get_author_row(author_row: str, column_lengths: list):
		row_string = ""
		if author_row is not None:
			for j, col in enumerate(author_row):
				row_string += f"{col}{' ' * (column_lengths[j] - len(col))}" + " "

			row_string += "\n"

		return "- " * ((sum(column_lengths) + len(column_lengths)) // 2) + "\n" + row_string

	def _get_data(self):
		with FileReader(self._file) as stats:
			data = stats.data()

		if self._sort_func is not None:
			data = sorted(data.items(), key=self._sort_func, reverse=True)

		return data



