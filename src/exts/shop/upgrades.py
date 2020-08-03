
from src.structs.purchasable import Purchasable


class _Upgrade(Purchasable):
	__id = 1  # PRIVATE

	def __init__(self, *, db_col, base_cost, **kwargs):
		super(_Upgrade, self).__init__(db_col=db_col, base_cost=base_cost, **kwargs)

		self.max_amount = kwargs.get("max_amount", 10)

		self.id = _Upgrade.__id

		_Upgrade.__id += 1


ALL_UPGRADES = [
	_Upgrade(db_col="extra_money_units", display_name="Extra Money Unit Slots", base_cost=10_000, exponent=1.25),
	_Upgrade(db_col="extra_military_units", display_name="Extra Military Unit Slots", base_cost=10_000, exponent=1.25),
	_Upgrade(db_col="less_upkeep", display_name="Reduced Upkeep", base_cost=15_000, exponent=1.50, max_amount=5),
	_Upgrade(db_col="more_income", display_name="Increased Income", base_cost=35_000, exponent=1.50, max_amount=5),
]
