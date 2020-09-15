import discord
import random
import math
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

	@property
	def all(self): return ChestHeroes.ALL_HEROES

	def open(self, n): return Counter(random.choices(self.all, weights=[hero.weight for hero in self.all], k=n))


class WoodenHeroChest(HeroChest):

	@property
	def all(self): return [hero for hero in ChestHeroes.ALL_HEROES if hero.grade in "DEF"]


class BronzeHeroChest(HeroChest):

	@property
	def all(self): return [hero for hero in ChestHeroes.ALL_HEROES if hero.grade in "ABC"]


class IronHeroChest(HeroChest):

	@property
	def all(self): return [hero for hero in ChestHeroes.ALL_HEROES if hero.grade in "ZSA"]


class HeroChests:
	ALL = (
		WoodenHeroChest(1, name="Wooden Hero Chest", cost=5_000),
		BronzeHeroChest(2, name="Bronze Hero Chest", cost=10_000),
		IronHeroChest(3, name="Iron Hero Chest", cost=25_000),
	)

	@classmethod
	def get(cls, **kwargs): return discord.utils.get(cls.ALL, **kwargs)


class Hero:
	__ids = set()

	PRICES = {"Z": 50_000, "S": 27_500, "A": 17_500, "B": 12_500, "C": 7_500, "D": 5_500, "E": 3_000, "F": 1_500}
	WEIGHTS = {"Z": 2, "S": 10, "A": 15, "B": 25, "C": 35, "D": 45, "E": 40, "F": 50}

	def __init__(self, _id, *, name, grade, atk, hp, icon=None):
		self.id = int(_id)

		self.name = name
		self.grade = grade
		self.icon = icon

		self.atk = atk
		self.hp = hp

		if self.id in Hero.__ids:
			raise KeyError(f"Hero ID '{self.id}' is not unique.")

		Hero.__ids.add(self.id)

	def xp_to_level(self, xp):
		lvl = 1

		while xp > 0:
			if (xp := xp - (100 + (10 * lvl))) >= 0:
				lvl += 1

		return lvl

	def get_atk(self, hero_row):
		level = self.xp_to_level(hero_row.get("xp", 0)) - 1

		return math.floor(self.atk * (1.0 + (level * 0.01)))

	def get_hp(self, hero_row):
		level = self.xp_to_level(hero_row.get("xp", 0)) - 1

		return math.floor(self.hp * (1.0 + (level * 0.01)))

	@property
	def sell_price(self): return self.PRICES.get(self.grade, 0)

	@property
	def weight(self): return self.WEIGHTS.get(self.grade, 0)


class ChestHeroes:
	with open(os.path.join(os.getcwd(), "data", "heroes.json"), "r") as fh:
		data = json.load(fh)

		ALL_HEROES = tuple(Hero(_id, **kwargs) for _id, kwargs in data.items())

	ALL_HEROES = sorted(ALL_HEROES, key=lambda h: "Z S A B C D E F".index(h.grade))

	@classmethod
	def get(cls, **kwargs): return discord.utils.get(cls.ALL_HEROES, **kwargs)
