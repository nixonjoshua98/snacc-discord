import discord


class _Quest:
	def __init__(self, *, id_, name, power, duration):
		self.id = id_
		self.name = name
		self.power = power
		self.duration = duration


class _EmpireQuests(type):
	_QUESTS = [
		_Quest(id_=0, name="Beginner Dungeon", power=50, duration=1),
	]

	def get(self, **kwargs): return discord.utils.get(self._QUESTS, **kwargs)

	@property
	def quests(self): return self._QUESTS


class EmpireQuests(metaclass=_EmpireQuests):
	pass

