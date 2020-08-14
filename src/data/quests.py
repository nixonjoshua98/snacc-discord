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

	def get_avg_reward(self, upgrades): return math.floor(self.reward * (1.0 + (upgrades["more_quest_money"] * 0.01)))

	def get_reward(self, upgrades): return math.floor(random.uniform(0.9, 1.1) * self.get_avg_reward(upgrades))

	def get_duration(self, upgrades): return self.duration * (1.0 - (upgrades["quicker_quests"] * 0.01))

	def success_rate(self, author_power): return round(max(0.01, min(author_power / self.power, 0.99)), 2)


class _EmpireQuests(type):
	_QUESTS = [
		_Quest(id=0, 	name="__TEST__", 				power=0, 	reward=0, 		duration=0),
		_Quest(id=1, 	name="Herb Collection", 		power=50, 	reward=500, 	duration=1),
		_Quest(id=2, 	name="Spider Cave", 			power=100, 	reward=1_250, 	duration=2),
		_Quest(id=3, 	name="Enemy Empire Raid", 		power=165, 	reward=2_000, 	duration=3),
		_Quest(id=4, 	name="Ogre Subjugation", 		power=225, 	reward=3_000, 	duration=4),
		_Quest(id=5, 	name="Enemy Empire Raid", 		power=260, 	reward=4_500, 	duration=5),
		_Quest(id=6, 	name="The Dragon", 				power=380, 	reward=5_500,	duration=6),
		_Quest(id=7, 	name="Kill the Traitors", 		power=475, 	reward=7_000, 	duration=7),
		_Quest(id=8, 	name="Sabotage the Enemy", 		power=550, 	reward=8_250, 	duration=8),
		_Quest(id=9, 	name="Search for Durandel", 	power=650, 	reward=9_500, 	duration=9),
		_Quest(id=10, 	name="The Abyss Stares Back", 	power=700, 	reward=11_000, 	duration=10),
	]

	def get(self, **kwargs): return discord.utils.get(self._QUESTS, **kwargs)

	@property
	def quests(self): return self._QUESTS


class EmpireQuests(metaclass=_EmpireQuests):
	pass

