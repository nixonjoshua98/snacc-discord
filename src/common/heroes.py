import discord
import random
import itertools
import json
import os

from collections import Counter


class HeroChest:
	__ids = set()

	def __init__(self, _id, *, name, cost):
		self.id = _id

		self.name = name
		self.cost = cost

		if self.id in HeroChest.__ids:
			raise KeyError(f"Hero Chest ID '{self.id}' is not unique.")

		HeroChest.__ids.add(self.id)


class NormalHeroChest(HeroChest):
	def open(self, n):
		weights = [hero.weight for hero in ChestHeroes.ALL_HEROES]

		return Counter(random.choices(ChestHeroes.ALL_HEROES, weights=weights, k=n))


class HeroChests:
	_ALL = (
		NormalHeroChest(0, name="Normal Hero Chest", cost=7_500),
	)

	@classmethod
	def get(cls, **kwargs): return discord.utils.get(cls._ALL, **kwargs)


class Hero:
	__ids = set()

	def __init__(self, _id, *, name, grade, icon=None):
		self.id = int(_id)

		self.name = name
		self.grade = grade
		self.icon = icon

		if self.id in Hero.__ids:
			raise KeyError(f"Hero ID '{self.id}' is not unique.")

		Hero.__ids.add(self.id)

	@property
	def sell_price(self):
		return {
			"Z": 0, "S": 10_000, "A": 8_000, "B": 6_000, "C": 4_000, "D": 3_000, "E": 2_000, "F": 1_000
		}.get(self.grade, 0)

	@property
	def weight(self):
		return {
			"Z": 3, "S": 10, "A": 15, "B": 25, "C": 35, "D": 40, "E": 45, "F": 50
		}.get(self.grade, 0)


class ChestHeroes:
	with open(os.path.join(os.getcwd(), "data", "heroes.json"), "r") as fh:
		data = json.load(fh)

		ALL_HEROES = tuple(Hero(_id, **kwargs) for _id, kwargs in data.items())

	ALL_HEROES = sorted(ALL_HEROES, key=lambda h: "ZSABCDEF".index(h.grade))

	@classmethod
	def get(cls, **kwargs): return discord.utils.get(cls.ALL_HEROES, **kwargs)


weights = sum([hero.weight for hero in ChestHeroes.ALL_HEROES])


for grade, heroes in itertools.groupby(ChestHeroes.ALL_HEROES, lambda h: h.grade):
	heroes = list(heroes)

	total_weight = sum([h.weight for h in heroes])

	print(f"{grade} -> {str(round((total_weight / weights) * 100, 1)) + '%': <6}")


