import math

from src.exts.empire.groups import (
	UnitGroupType,

	_MoneyUnitGroup,
	_MilitaryUnitGroup
)


class _Unit:
	__unit_id = 1  # PRIVATE

	def __init__(self, *, db_col, base_cost, **kwargs):
		self.display_name = db_col.title().replace("_", " ")

		self.id = _Unit.__unit_id
		self.db_col = db_col
		self.base_price = base_cost

		self.max_amount = kwargs.get("max_amount", 10)
		self.exponent = kwargs.get("exponent", 1.10)

		# Increment the internal ID for the next unit
		_Unit.__unit_id += 1

	def get_price(self, total_owned: int, total_buying: int = 1) -> int:
		""" Get the total cost of the units brought. """

		price = 0

		for i in range(total_owned, total_owned + total_buying):
			price += self.base_price * pow(self.exponent, i)

		return math.ceil(price)


class _MoneyUnit(_Unit):
	def __init__(self, *, income_hour, **kwargs):
		super().__init__(**kwargs)

		self.income_hour = income_hour

	def get_delta_money(self, total, delta_time):
		""" Gets the total INCOME this unit has generated for the delta_time. """

		return math.ceil((self.income_hour * total) * delta_time)


class _MilitaryUnit(_Unit):
	def __init__(self, *, upkeep_hour, power, **kwargs):
		super().__init__(**kwargs)

		self.power = power
		self.upkeep_hour = upkeep_hour

	def get_delta_money(self, total, delta_time):
		""" Gets the total UPKEEP this unit has generated for the delta_time. """

		return math.ceil((self.upkeep_hour * total) * delta_time) * -1


"""
We store all the unit types in a dictionary <UnitGroupType, _UnitType> here.
This should NEVER be edited during runtime
"""
UNIT_GROUPS = {
	UnitGroupType.MONEY:
		_MoneyUnitGroup("Money Making Units", [
			_MoneyUnit(income_hour=25, db_col="farmers",	base_cost=250),
			_MoneyUnit(income_hour=40, db_col="butchers",	base_cost=500),
			_MoneyUnit(income_hour=50, db_col="bakers",		base_cost=750),
			_MoneyUnit(income_hour=60, db_col="cooks",		base_cost=1000),
			_MoneyUnit(income_hour=75, db_col="winemakers", base_cost=1250),
		]
						),

	UnitGroupType.MILITARY:
		_MilitaryUnitGroup("Military Units", [
			_MilitaryUnit(upkeep_hour=0, power=5, db_col="peasants", base_cost=750),

		]
						),
}

# Flatterned list of all units
ALL = [unit for _, group in UNIT_GROUPS.items() for unit in group.units]











