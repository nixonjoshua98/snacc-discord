import discord
import random
import os

from configparser import ConfigParser


class HeroChest:
	__hero_chest_id = 1

	def __init__(self, *, name, cost):
		self.id = HeroChest.__hero_chest_id

		self.name = name
		self.cost = cost

		HeroChest.__hero_chest_id += 1


class NormalHeroChest(HeroChest):
	def open(self):
		weights = [hero.weight for hero in ChestHeroes.ALL_HEROES]

		return random.choices(ChestHeroes.ALL_HEROES, weights=weights, k=1)[0]


class HeroChests:
	_ALL = (
		NormalHeroChest(name="Normal Hero Chest", cost=15_000),
	)

	@classmethod
	def get(cls, **kwargs): return discord.utils.get(cls._ALL, **kwargs)


class Hero:
	__hero_id = 1

	def __init__(self, *, name, weight, attack, health):
		self.id = Hero.__hero_id

		self.name = name
		self.weight = weight

		self.base_attack = attack
		self.base_health = health

		self.rating = 0

		self.icon = self._get_icon()
		self.grade = self._get_grade()

		Hero.__hero_id += 1

	def _get_icon(self):
		config = ConfigParser()

		config.read(os.path.join(os.getcwd(), "data", "heroes.ini"))

		return config.get("icons", self.name, fallback=None)

	def _get_grade(self):
		grades = {"A": 600, "B": 500, "C": 400, "D": 300}

		self.rating = rating = self.base_attack + self.base_health

		for k, v in grades.items():
			if rating >= v:
				return k

		return "F"


class ChestHeroes:
	ALL_HEROES = (
		Hero(name="Light Yagami", 		weight=45, 	attack=30.0, 	health=300.0),
		Hero(name="Kirigaya Kazuto", 	weight=45, 	attack=40.0, 	health=325.0),
		Hero(name="Edward Elric", 		weight=45, 	attack=40.0, 	health=350.0),
		Hero(name="Levi Ackerman", 		weight=45, 	attack=35.0, 	health=350.0),

		Hero(name="Rias Gremory", 		weight=35, 	attack=50.0, 	health=400.0),
		Hero(name="Death The Kid", 		weight=35, 	attack=45.0, 	health=375.0),
		Hero(name="Natsu Dragneel", 	weight=35, 	attack=50.0, 	health=425.0),

		Hero(name="Killua Zoldyck", 	weight=30, 	attack=60.0, 	health=450.0),
		Hero(name="Itachi Uchiha", 		weight=30, 	attack=70.0, 	health=450.0),
		Hero(name="Yato", 				weight=30, 	attack=60.0, 	health=500.0),
		Hero(name="Saitama", 			weight=30, 	attack=80.0, 	health=450.0),
		Hero(name="Shoto Todoroki", 	weight=30, 	attack=70.0, 	health=500.0),

		Hero(name="Ichigo Kurosaki",	weight=15, 	attack=70.0, 	health=550.0),
		Hero(name="Naruto", 			weight=15, 	attack=70.5, 	health=600.0),
		Hero(name="Monkey D. Luffy", 	weight=15, 	attack=70.5, 	health=600.0),
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
