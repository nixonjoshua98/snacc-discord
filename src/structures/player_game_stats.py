import discord

from src.common import data_reader
from src.common.constants import MAX_DAYS_NO_UPDATE
from datetime import datetime


class PlayerGameStats:
	def __init__(self, user: discord.Member):
		self.user = user

		""" Stats found in the game Auto Battles Online """
		self.date_set, self.level, self.trophies = None, None, None

		self._load("game_stats.json")

	def update(self, *, level: int, trophies: int):
		self.level, self.trophies, self.date_set = level, trophies, datetime.today()
		self._save("game_stats.json")

	def serialize(self) -> list:
		return [self.date_set.strftime("%d/%m/%Y %H:%M:%S"), self.level, self.trophies]

	def has_stats(self) -> bool:
		return self.date_set is not None and self.level is not None and self.trophies is not None

	def slacking(self) -> bool:
		return True if (not self.has_stats() or self.days_since_set() >= MAX_DAYS_NO_UPDATE) else False

	def days_since_set(self) -> int:
		return (datetime.today() - self.date_set).days if self.has_stats() else -1

	def create_embed(self) -> discord.Embed:
		embed = discord.Embed(title=f"Member: {self.user.display_name}", description=f"Member Stats", color=0xff8000)

		stats_list = self.serialize()

		for i, txt in enumerate(("Date Recorded", "Level", "Trophies")):
			embed.add_field(name=txt, value=stats_list[i])

		return embed

	def _load(self, file: str):
		all_stats = data_reader.read_json(file)

		stats = self.trophies = all_stats.get(str(self.user.id), None)

		if stats:
			date, self.level, self.trophies = stats

			self.date_set = datetime.strptime(date, "%d/%m/%Y %H:%M:%S")

	def _save(self, file: str):
		data = data_reader.read_json(file)

		data[str(self.user.id)] = self.serialize()

		data_reader.write_json(file, data)