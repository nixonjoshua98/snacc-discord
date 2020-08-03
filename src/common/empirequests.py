import math
import discord
import random


class _Quest:
	def __init__(self, *, id_, name, power, reward, duration):
		self.id = id_
		self.name = name
		self.power = power
		self.duration = duration

		self.reward = reward

	def get_reward(self): return math.floor(random.uniform(0.9, 1.1) * self.reward)

	def success_rate(self, author_power): return min(math.floor(author_power / self.power), 0.99)


class _EmpireQuests(type):
	_QUESTS = [
		_Quest(id_=1, name="Herb Collection", 		power=50, 	reward=350, 	duration=1),
		_Quest(id_=2, name="Spider Cave", 			power=100, 	reward=900, 	duration=2),
		_Quest(id_=3, name="Enemy Empire Raid", 	power=150, 	reward=1_700, 	duration=3),
		_Quest(id_=4, name="Ogre Subjugation", 		power=200, 	reward=2_500, 	duration=4),
		_Quest(id_=5, name="Enemy Empire Raid", 	power=250, 	reward=4_000, 	duration=5),
	]

	def get(self, **kwargs): return discord.utils.get(self._QUESTS, **kwargs)

	@property
	def quests(self): return self._QUESTS


class EmpireQuests(metaclass=_EmpireQuests):
	pass

