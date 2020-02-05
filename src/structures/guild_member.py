import dataclasses
import discord

from datetime import datetime
from src.common import data_reader


@dataclasses.dataclass
class GuildMemberStats:
	set_date: datetime
	level: int
	trophies: int

	def serialize(self, date_format: str = "%d/%m/%Y %H:%M:%S"):
		return [self.set_date.strftime(date_format), self.level, self.trophies]


class GuildMember:
	def __init__(self, *, _id: int, display_name: str = None):
		self.id = _id
		self.display_name = display_name
		self.stats = None

		self.get_stats_from_file()

	def __str__(self):
		return self.display_name or str(self.id)

	def has_stats(self):
		return self.stats is not None

	def days_since_stat_set(self):
		return (datetime.today() - self.stats.set_date).days

	def create_embed(self):
		if self.has_stats():
			embed = discord.Embed(title=f"Member: {self.display_name}", description=f"Member Stats", color=0xff8000)

			stats_list = self.stats.serialize("%d/%m/%Y")

			for i, txt in enumerate(("Date Recorded", "Level", "Trophies")):
				embed.add_field(name=txt, value=stats_list[i])

			return embed

	def get_stats_from_file(self):
		data = data_reader.read_json("stats.json")

		member_stats = data.get(str(self.id), [])

		if member_stats:
			date, level, trophies = member_stats

			date = datetime.strptime(date, "%d/%m/%Y %H:%M:%S")

			self.stats = GuildMemberStats(date, level, trophies)

	def update_stats(self, *, level: int, trophies: int, write_file: bool):
		self.stats = GuildMemberStats(datetime.today(), level, trophies)

		if write_file:
			self.save_stats_to_file()

	def save_stats_to_file(self):
		if self.has_stats():
			data = data_reader.read_json("stats.json")

			data[str(self.id)] = self.stats.serialize()

			data_reader.write_json("stats.json", data)
