import math

from src.exts.empire.groups import (
	UnitGroupType,

	_MoneyUnitGroup,
	_MilitaryUnitGroup
)


class _Unit:
	__unit_id = 1  # PRIVATE

	def __init__(self, *, db_col, base_cost, **kwargs):
		self.display_name = kwargs.get("display_name", db_col.title().replace("_", " "))

		self.id = _Unit.__unit_id
		self.db_col = db_col
		self.base_price = base_cost

		self.power = kwargs.get("power", 0)
		self.exponent = kwargs.get("exponent", 1.15)
		self.income_hour = kwargs.get("income_hour", 0)
		self.upkeep_hour = kwargs.get("upkeep_hour", 0)
		self.max_amount = kwargs.get("max_amount", 15)

		# Increment the internal ID for the next unit
		_Unit.__unit_id += 1

	def get_price(self, total_owned: int, total_buying: int = 1) -> int:
		""" Get the total cost of the units brought. """

		price = 0

		for i in range(total_owned, total_owned + total_buying):
			price += self.base_price * pow(self.exponent, i)

		return math.ceil(price)

	def get_delta_money(self, total, delta_time):
		income = math.ceil((self.income_hour * total) * delta_time)
		upkeep = math.ceil((self.upkeep_hour * total) * delta_time) * -1

		return income + upkeep


UNIT_GROUPS = {
	UnitGroupType.MONEY:
		_MoneyUnitGroup("Money Making Units", [
			_Unit(income_hour=25, db_col="farmers",		base_cost=250),
			_Unit(income_hour=40, db_col="butchers",	base_cost=500),
			_Unit(income_hour=50, db_col="bakers",		base_cost=750),
			_Unit(income_hour=60, db_col="cooks",		base_cost=1000),
			_Unit(income_hour=75, db_col="winemakers", 	base_cost=1250),
		]
						),

	UnitGroupType.MILITARY:
		_MilitaryUnitGroup("Military Units", [
			_Unit(upkeep_hour=25, power=1, db_col="peasants", base_cost=250),
			_Unit(upkeep_hour=50, power=3, db_col="soldiers", base_cost=750),
			_Unit(upkeep_hour=75, power=5, db_col="warriors", base_cost=1500),

		]
						),
}

# Flatterned list of all units
ALL_UNITS = [unit for _, group in UNIT_GROUPS.items() for unit in group.units]











