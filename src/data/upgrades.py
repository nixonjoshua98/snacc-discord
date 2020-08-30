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

		self.display_name = kwargs.get("display_name", self.key.title().replace("_", " "))

		Upgrade.__id += 1

	def calc_price(self, owned: int, buying: int):
		price = 0

		for i in range(owned, owned + buying):
			price += self._base_cost * pow(self._exponent, i)

		return math.ceil(price)


class EmpireUpgrades:
	groups = {
		"Quest Upgrades": [
			Upgrade(key="quicker_quests", 		base_cost=15_000),
			Upgrade(key="more_quest_money", 	base_cost=15_000)
		]
	}

	@classmethod
	def get(cls, **kwargs):
		upgrades = [upgrade for title, ls in cls.groups.items() for upgrade in ls]

		return discord.utils.get(upgrades, **kwargs)
