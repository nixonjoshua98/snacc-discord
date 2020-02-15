from src.common import data_reader
from datetime import datetime

from src.common.constants import MAX_DAYS_NO_UPDATE


class GameStats:
	DATA_FILE = "game_stats.json"

	def __init__(self, *, _id: int):
		self._id = _id

		self.has_stats = False

		self.date_set = None
		self.level = None
		self.trophies = None

		self._load_stats()

	def update(self, *, level: int, trophies: int) -> bool:
		self.level = level
		self.trophies = trophies
		self.date_set = datetime.today()

		return self._save_stats()

	def slacking(self) -> bool:
		return True if (not self.has_stats or self.days_since_set() >= MAX_DAYS_NO_UPDATE) else False

	def serialize(self, date_format: str = "%d/%m/%Y %H:%M:%S") -> list:
		return [self.date_set.strftime(date_format), self.level, self.trophies]

	def days_since_set(self) -> int:
		try:
			return (datetime.today() - self.date_set).days
		except AttributeError:
			return -1

	def _load_stats(self):
		all_stats = data_reader.read_json(self.DATA_FILE)

		player_stats = all_stats.get(str(self._id), [])

		if player_stats:
			self.has_stats = True

			date, self.level, self.trophies = player_stats

			self.date_set = datetime.strptime(date, "%d/%m/%Y %H:%M:%S")

	def _save_stats(self) -> bool:
		data = data_reader.read_json(self.DATA_FILE)

		data[str(self._id)] = self.serialize()

		data_reader.write_json(self.DATA_FILE, data)

		return True
