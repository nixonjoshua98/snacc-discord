import discord

from src.structs.purchasable import Purchasable


class _Upgrade(Purchasable):
	__id = 1

	def __init__(self, *, db_col, base_cost, **kwargs):
		super(_Upgrade, self).__init__(db_col=db_col, base_cost=base_cost, **kwargs)

		self.max_amount = kwargs.get("max_amount", 10)
		self.exponent = kwargs.get("exponent", 1.25)

		self.id = _Upgrade.__id

		_Upgrade.__id += 1


class _EmpireUpgrades(type):
	_UPGRADES = [
		_Upgrade(db_col="extra_money_units", display_name="Money Unit Slots", base_cost=12_500),
		_Upgrade(db_col="extra_military_units", display_name="Military Unit Slots", base_cost=10_000, max_amount=15),
		_Upgrade(db_col="less_upkeep", display_name="Reduced Upkeep", base_cost=20_000, exponent=1.50, max_amount=5),
		_Upgrade(db_col="more_income", display_name="Increased Income", base_cost=30_000, exponent=1.50, max_amount=5),
		_Upgrade(db_col="quicker_quests", display_name="Faster Quests", base_cost=12_500),
		_Upgrade(db_col="more_quest_money", base_cost=15_000),
		_Upgrade(db_col="cheaper_money_units", base_cost=15_000, max_amount=10),
		_Upgrade(db_col="cheaper_military_units", base_cost=15_000, max_amount=10),
	]

	def get(self, **kwargs): return discord.utils.get(self._UPGRADES, **kwargs)

	@property
	def upgrades(self): return self._UPGRADES


class EmpireUpgrades(metaclass=_EmpireUpgrades):
	pass
