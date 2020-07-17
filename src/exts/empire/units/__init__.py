

from src.common.models import EmpireM

from .groups import _UnitGroup, _MoneyUnitGroup, _MilitaryUnitGroup, UnitGroupType
from .units import _MoneyUnit, _MilitaryUnit


UNIT_GROUPS = {
	UnitGroupType.MONEY:
		_MoneyUnitGroup("Money Making Units", [
			_MoneyUnit(income_hour=10, db_col=EmpireM.FARMERS,		base_cost=250),
			_MoneyUnit(income_hour=20, db_col=EmpireM.BUTCHERS,		base_cost=500),
			_MoneyUnit(income_hour=30, db_col=EmpireM.BAKERS,		base_cost=750),
			_MoneyUnit(income_hour=40, db_col=EmpireM.COOKS,		base_cost=1000),
			_MoneyUnit(income_hour=50, db_col=EmpireM.WINEMAKERS, 	base_cost=1500),
		]
						),

	UnitGroupType.MILITARY:
		_MilitaryUnitGroup("Military Units", [
		]
						),
}

ALL = [unit for _, group in UNIT_GROUPS.items() for unit in group.units]