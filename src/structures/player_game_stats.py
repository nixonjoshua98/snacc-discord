import discord
import dataclasses

from datetime import datetime
from src.common import data_reader


@dataclasses.dataclass
class GameStatsDC:
	set_date: datetime
	level: int
	trophies: int

	def serialize(self, date_format: str = "%d/%m/%Y %H:%M:%S"):
		return [self.set_date.strftime(date_format), self.level, self.trophies]


class PlayerGameStats:
	FILE = "game_stats.json"

	def __init__(self, guild: discord.Guild, _id: str):
		self._id = _id
		self._stats = None
		self._guild = guild

		self.member = guild.get_member(_id)

		self._load_game_stats()

	@property
	def trophies(self) -> int: return self._stats.trophies

	@property
	def level(self) -> int: return self._stats.level

	@property
	def display_name(self) -> str: return self.member.display_name

	def has_set_stats(self) -> bool: return self._stats is not None
	def days_since_set(self) -> int: return (datetime.today() - self._stats.set_date).days

	def create_embed(self):
		if self.has_set_stats() and self.member is not None:
			embed = discord.Embed(
				title=f"Member: {self.member.display_name}",
				description=f"Member Stats",
				color=0xff8000
			)

			stats_list = self._stats.serialize("%d/%m/%Y")

			for i, txt in enumerate(("Date Recorded", "Level", "Trophies")):
				embed.add_field(name=txt, value=stats_list[i])

			return embed

	def update_stats(self, level: int, trophies: int, *, write_file: bool):
		self._stats = GameStatsDC(datetime.today(), level, trophies)

		if write_file:
			self._save_stats_to_file()

	def _load_game_stats(self):
		all_stats = data_reader.read_json(self.FILE)

		player_stats = all_stats.get(str(self._id), [])

		if player_stats:
			date, level, trophies = player_stats

			date_obj = datetime.strptime(date, "%d/%m/%Y %H:%M:%S")

			self._stats = GameStatsDC(date_obj, level, trophies)

	def _save_stats_to_file(self):
		if self.has_set_stats():
			data = data_reader.read_json(self.FILE)

			data[str(self._id)] = self._stats.serialize()

			data_reader.write_json(self.FILE, data)
