import discord
import random
import os

from configparser import ConfigParser


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
	def open(self):
		weights = [hero.weight for hero in ChestHeroes.ALL_HEROES]

		return random.choices(ChestHeroes.ALL_HEROES, weights=weights, k=1)[0]


class HeroChests:
	_ALL = (
		NormalHeroChest(0, name="Normal Hero Chest", cost=7_500),
	)

	@classmethod
	def get(cls, **kwargs): return discord.utils.get(cls._ALL, **kwargs)


class Hero:
	__ids = set()

	def __init__(self, _id, *, name, weight, atk, hp):
		self.id = _id

		self.name = name
		self.weight = weight

		self.base_attack = atk
		self.base_health = hp

		self.rating = 0

		self.icon = self._get_icon()
		self.grade = self._get_grade()

		if self.id in Hero.__ids:
			raise KeyError(f"Hero ID '{self.id}' is not unique.")

		Hero.__ids.add(self.id)

	def _get_icon(self):
		config = ConfigParser()

		config.read(os.path.join(os.getcwd(), "data", "heroes.ini"))

		return config.get("icons", self.name, fallback=None)

	def _get_grade(self):
		grades = {"Z": 999 + 999, "S": 700, "A": 600, "B": 500, "C": 400, "D": 300, "E": 200, "F": 100}

		self.rating = rating = self.base_attack + self.base_health

		for k, v in grades.items():
			if rating >= v:
				return k

		return "F"


class ChestHeroes:
	ALL_HEROES = (
		# - Z
		Hero(0, 	name="Snaccman", 			weight=1,	atk=999.0, 	hp=999.0),

		# - F
		Hero(16, 	name="Happy", 				weight=50,	atk=10.0, 	hp=150.0),

		# - E
		Hero(17, 	name="Mumen Rider",			weight=45, 	atk=25.0, 	hp=200.0),
		Hero(20, 	name="Sakura Haruno", 		weight=45, 	atk=60.0, 	hp=175.0),

		# - D
		Hero(1, 	name="Light Yagami", 		weight=40, 	atk=40.0, 	hp=260.0),
		Hero(2, 	name="Kirigaya Kazuto", 	weight=40, 	atk=50.0, 	hp=300.0),
		Hero(3, 	name="Edward Elric", 		weight=40, 	atk=50.0, 	hp=340.0),
		Hero(4, 	name="Levi Ackerman", 		weight=40, 	atk=45.0, 	hp=330.0),

		# - C
		Hero(5, 	name="Rias Gremory", 		weight=35, 	atk=70.0, 	hp=330.0),
		Hero(6, 	name="Death The Kid", 		weight=35, 	atk=80.0, 	hp=350.0),
		Hero(7, 	name="Natsu Dragneel", 		weight=35, 	atk=85.0, 	hp=375.0),

		# - B
		Hero(8, 	name="Killua Zoldyck", 		weight=25, 	atk=95.0, 	hp=430.0),
		Hero(9, 	name="Itachi Uchiha", 		weight=25, 	atk=100.0, 	hp=410.0),
		Hero(10, 	name="Yato", 				weight=25, 	atk=80.0, 	hp=450.0),
		Hero(11, 	name="Saitama", 			weight=25, 	atk=125.0, 	hp=425.0),
		Hero(12, 	name="Shoto Todoroki", 		weight=25, 	atk=75.0, 	hp=500.0),

		# - A
		Hero(13, 	name="Ichigo Kurosaki",		weight=15, 	atk=125.0, 	hp=550.0),
		Hero(14, 	name="Naruto", 				weight=15, 	atk=130.0, 	hp=530.0),
		Hero(15, 	name="Monkey D. Luffy", 	weight=15, 	atk=120.0, 	hp=560.0),

		# - S
		Hero(18, 	name="Mob", 				weight=10, 	atk=200.0, 	hp=500.0),
		Hero(19, 	name="Gon Freecss", 		weight=10, 	atk=150.0, 	hp=550.0),
	)

	ALL_HEROES = sorted(ALL_HEROES, key=lambda h: h.rating, reverse=True)

	@classmethod
	def get(cls, **kwargs): return discord.utils.get(cls.ALL_HEROES, **kwargs)


weights = sum([hero.weight for hero in ChestHeroes.ALL_HEROES])

for hero in ChestHeroes.ALL_HEROES:
	print(
		f"[{hero.grade}] {hero.name: <16} "
		f"{str(round((hero.weight / weights) * 100, 2)) + '%': <6} "
	)
