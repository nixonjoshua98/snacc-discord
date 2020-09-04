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

		self.icon = self._get_icon()
		self.grade = self._get_grade()

		Hero.__hero_id += 1

	def _get_icon(self):
		config = ConfigParser()

		config.read(os.path.join(os.getcwd(), "data", "heroes.ini"))

		return config.get("icons", self.name, fallback=None)

	def _get_grade(self):
		grades = {"A": 65, "B": 50, "C": 40, "D": 30}

		rating = self.base_attack + self.base_health

		for k, v in grades.items():
			if rating >= v:
				return k

		return "F"




class ChestHeroes:
	ALL_HEROES = (
		Hero(name="Light Yagami", 		weight=65, 	attack=3.0, 	health=45.0),
		Hero(name="Itachi Uchiha", 		weight=25, 	attack=7.5, 	health=45.0),
		Hero(name="Killua Zoldyck", 	weight=25, 	attack=6.0, 	health=55.0),
		Hero(name="Naruto", 			weight=20, 	attack=7.0, 	health=60.0),
		Hero(name="Levi Ackerman", 		weight=45, 	attack=4.5, 	health=50.0),
		Hero(name="Monkey D. Luffy", 	weight=25, 	attack=7.0, 	health=60.0),
		Hero(name="Saitama", 			weight=45, 	attack=9.0, 	health=40.0),
		Hero(name="Edward Elric", 		weight=55, 	attack=6.5, 	health=35.0),
		Hero(name="Natsu Dragneel", 	weight=55, 	attack=7.0, 	health=45.0),
		Hero(name="Kirigaya Kazuto",	weight=65, 	attack=3.5, 	health=30.0),
		Hero(name="Death The Kid", 		weight=35, 	attack=5.0, 	health=45.0),
		Hero(name="Ichigo Kurosaki",	weight=20, 	attack=7.0, 	health=55.0),
		Hero(name="Yato", 				weight=30, 	attack=5.5, 	health=45.0),
		Hero(name="Shoto Todoroki", 	weight=40, 	attack=5.0, 	health=50.0),
		Hero(name="Rias Gremory", 		weight=15, 	attack=5.0, 	health=45.0),
	)

	@classmethod
	def get(cls, **kwargs): return discord.utils.get(cls.ALL_HEROES, **kwargs)


weights = sum([hero.weight for hero in ChestHeroes.ALL_HEROES])

for hero in ChestHeroes.ALL_HEROES:
	print(
		f"{hero.name: <16} "
		f"{str(round((hero.weight / weights) * 100, 2)) + '%': <6} "
		f"Rating: {hero.base_health + hero.base_attack}"
	)
