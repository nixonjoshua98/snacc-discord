import discord
import typing

from src.common import data_reader


class PlayerCoins:
	def __init__(self, member: typing.Union[discord.User, discord.Member]):
		self.user = member

		self.balance = 0

		self._load("coins.json")

	def set(self, amount: int):
		self.balance = amount

		self._save("coins.json")

	def add(self, amount: int):
		self.balance = max(0, self.balance + amount)

		self._save("coins.json")

	def deduct(self, amount: int):
		if amount > self.balance:
			return False

		self.balance = max(0, self.balance - amount)

		self._save("coins.json")

		return True

	def _load(self, file: str):
		data = data_reader.read_json(file)

		self.balance = data.get(str(self.user.id), 0)

	def _save(self, file: str):
		data = data_reader.read_json(file)

		data[str(self.user.id)] = self.balance

		data_reader.write_json(file, data)