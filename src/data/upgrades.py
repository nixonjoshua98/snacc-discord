import discord

import math


class Upgrade:
	__id = 1

	def __init__(self, *, key, base_cost, **kwargs):
		self.key = key
		self.id = Upgrade.__id

		self.max_amount = kwargs.get("max_amount", 10)

		self._base_cost = base_cost

		self._exponent = kwargs.get("exponent", 1.25)
		self._max_price = kwargs.get("max_price", None)

		self.display_name = kwargs.get("display_name", self.key.title().replace("_", " "))

		Upgrade.__id += 1

	def calc_price(self, owned: int, buying: int):
		price = 0

		for i in range(owned, owned + buying):
			p = self._base_cost * pow(self._exponent, i)

			if self._max_price is not None:
				p = min(self._max_price, p)

			price += p

		return math.ceil(price)


class EmpireUpgrades:
	upgrades = [
		Upgrade(key="quicker_quests", 	base_cost=15_000),
		Upgrade(key="more_quest_money", base_cost=15_000),
	]

	@classmethod
	def get(cls, **kwargs): return discord.utils.get(cls.upgrades, **kwargs)
