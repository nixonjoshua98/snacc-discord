

from .groups import (
	UnitGroupType,

	_MoneyUnitGroup,
	_MilitaryUnitGroup
)

from .units import (
	_MoneyUnit,
	_MilitaryUnit
)


"""
We store all the unit types in a dictionary <UnitGroupType, _UnitType> here.
This should NEVER be edited during runtime
"""
UNIT_GROUPS = {
	UnitGroupType.MONEY:
		_MoneyUnitGroup("Money Making Units", [
			_MoneyUnit(income_hour=10, db_col="farmers",	base_cost=250),
			_MoneyUnit(income_hour=20, db_col="butchers",	base_cost=500),
			_MoneyUnit(income_hour=30, db_col="bakers",		base_cost=750),
			_MoneyUnit(income_hour=40, db_col="cooks",		base_cost=1000),
			_MoneyUnit(income_hour=50, db_col="winemakers", base_cost=1500),
		]
						),

	UnitGroupType.MILITARY:
		_MilitaryUnitGroup("Military Units", [

		]
						),
}

# Flatterned list of all units
ALL = [unit for _, group in UNIT_GROUPS.items() for unit in group.units]