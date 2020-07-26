import math

from src.exts.empire.groups import (
	UnitGroupType,

	_MoneyUnitGroup,
	_MilitaryUnitGroup
)

from src.structs.purchasable import Purchasable


class _Unit(Purchasable):
	__unit_id = 1  # PRIVATE

	def __init__(self, *, db_col, base_cost, **kwargs):
		super(_Unit, self).__init__(db_col=db_col, base_cost=base_cost, **kwargs)

		self.id = _Unit.__unit_id

		self.power = kwargs.get("power", 0)

		self.income_hour = kwargs.get("income_hour", 0)
		self.upkeep_hour = kwargs.get("upkeep_hour", 0)

		# Increment the internal ID for the next unit
		_Unit.__unit_id += 1

	def __str__(self):
		return self.display_name

	def get_delta_money(self, total, delta_time):
		income = math.ceil((self.income_hour * total) * delta_time)
		upkeep = math.ceil((self.upkeep_hour * total) * delta_time) * -1

		return income + upkeep


UNIT_GROUPS = {
	UnitGroupType.MONEY:
		_MoneyUnitGroup("Money Making Units", [
			_Unit(income_hour=25, db_col="farmers",		base_cost=250),
			_Unit(income_hour=40, db_col="butchers",	base_cost=500),
			_Unit(income_hour=45, db_col="taylors",		base_cost=650),
			_Unit(income_hour=50, db_col="bakers",		base_cost=750),
			_Unit(income_hour=55, db_col="blacksmiths",	base_cost=875),
			_Unit(income_hour=60, db_col="cooks",		base_cost=1000),
			_Unit(income_hour=75, db_col="winemakers", 	base_cost=1250),
		]
						),

	UnitGroupType.MILITARY:
		_MilitaryUnitGroup("Military Units", [
			_Unit(upkeep_hour=25, power=1, db_col="peasants", base_cost=250),
			_Unit(upkeep_hour=35, power=2, db_col="spearmen", base_cost=500),
			_Unit(upkeep_hour=50, power=3, db_col="soldiers", base_cost=750),
			_Unit(upkeep_hour=75, power=5, db_col="warriors", base_cost=1250),

		]
						),
}

# Flatterned list of all units
ALL_UNITS = [unit for _, group in UNIT_GROUPS.items() for unit in group.units]











