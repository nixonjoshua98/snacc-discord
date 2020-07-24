
from src.structs.purchasable import Purchasable


class _Upgrade(Purchasable):
	def __init__(self, *, db_col, base_cost, **kwargs):
		super(_Upgrade, self).__init__(db_col=db_col, base_cost=base_cost, **kwargs)


ALL_UPGRADES = [
	_Upgrade(db_col="extra_units", display_name="Extra Unit Slots", base_cost=10_000, exponent=1.25)
]
