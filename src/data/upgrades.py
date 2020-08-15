import discord

from src.structs.purchasable import Purchasable


class _Upgrade(Purchasable):
	__id = 1

	def __init__(self, *, key, base_cost, **kwargs):
		super(_Upgrade, self).__init__(key=key, base_cost=base_cost, **kwargs)

		self._max_amount = kwargs.get("max_amount", 10)
		self._exponent = kwargs.get("exponent", 1.25)

		self.id = _Upgrade.__id

		_Upgrade.__id += 1


class EmpireUpgrades:
	upgrades = [
		_Upgrade(key="extra_money_units", display_name="Money Maker Slots", base_cost=12_500),
		_Upgrade(key="extra_military_units", display_name="Military Slots", base_cost=10_000, max_amount=15),
		_Upgrade(key="less_upkeep", display_name="Reduced Upkeep", base_cost=20_000, exponent=1.50, max_amount=5),
		_Upgrade(key="more_income", display_name="Increased Income", base_cost=30_000, exponent=1.50, max_amount=5),
		_Upgrade(key="quicker_quests", display_name="Faster Quests", base_cost=12_500),
		_Upgrade(key="more_quest_money", base_cost=15_000),
		_Upgrade(key="cheaper_money_units", display_name="Cheaper Money Makers", base_cost=7_500, max_amount=10),
		_Upgrade(key="cheaper_military_units", display_name="Cheaper Military", base_cost=7_500, max_amount=10)
	]

	@classmethod
	def get(cls, **kwargs): return discord.utils.get(cls.upgrades, **kwargs)
