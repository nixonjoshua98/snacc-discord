from src.common import data_reader
from datetime import datetime


class MemberGameStats:
	DATA_FILE = "game_stats.json"

	def __init__(self, *, _id: int):
		self._id = _id

		self.date_set = None
		self.level = None
		self.trophies = None

		self._load_stats()

	def update(self, *, level: int, trophies: int) -> bool:
		self.level = level
		self.trophies = trophies

		return self._save_stats()

	def days_since_set(self) -> int:
		return (datetime.today() - self.date_set).days

	def _load_stats(self):
		all_stats = data_reader.read_json(self.DATA_FILE)

		player_stats = all_stats.get(str(self._id), [])

		if player_stats:
			date, self.level, self.trophies = player_stats

			self.date_set = datetime.strptime(date, "%d/%m/%Y %H:%M:%S")

	def _save_stats(self) -> bool:
		data = data_reader.read_json(self.DATA_FILE)

		try:
			data[str(self._id)] = [self.date_set.strftime("%d/%m/%Y"), self.level, self.trophies]
		except AttributeError:
			return False

		data_reader.write_json(self.DATA_FILE, data)

		return True
