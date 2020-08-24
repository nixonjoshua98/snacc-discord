import math
import discord
import random
import dataclasses


@dataclasses.dataclass(frozen=True)
class _Quest:
	id: int
	name: str
	power: int
	reward: int
	duration: int

	def get_avg_reward(self, upgrades):
		return math.floor(self.reward * (1.0 + (upgrades.get("more_quest_money", 0) * 0.01)))

	def get_reward(self, upgrades): return math.floor(random.uniform(0.9, 1.1) * self.get_avg_reward(upgrades))

	def get_duration(self, upgrades):
		return self.duration * (1.0 - (upgrades.get("quicker_quests", 0) * 0.01))

	def success_rate(self, author_power): return round(max(0.01, min(author_power / self.power, 0.99)), 2)


class EmpireQuests:
	quests = [
		_Quest(id=1, 	name="Herb Collection", 		power=10, 	reward=500, 	duration=1),  # 500
		_Quest(id=2, 	name="Spider Cave", 			power=45, 	reward=1_500, 	duration=2),  # 750
		_Quest(id=3, 	name="Ogre Subjugation", 		power=75, 	reward=2_700, 	duration=3),  # 900
		_Quest(id=4, 	name="The Dragon", 				power=125, 	reward=5_000,	duration=4),  # 1250
		_Quest(id=5, 	name="Kill the Traitors", 		power=170, 	reward=7_000, 	duration=5),  # 1400
		_Quest(id=6, 	name="Sabotage the Enemy", 		power=225, 	reward=9_900, 	duration=6),  # 1650
		_Quest(id=7, 	name="Search for Durandel", 	power=290, 	reward=13_300, 	duration=7),  # 1900
		_Quest(id=8, 	name="The Abyss Stares Back", 	power=350, 	reward=18_000, 	duration=8)   # 2250
	]

	@classmethod
	def get(cls, **kwargs): return discord.utils.get(cls.quests, **kwargs)

