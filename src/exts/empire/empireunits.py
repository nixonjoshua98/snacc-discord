import math
import enum

from src.common.models import EmpireM
from src.structs.textpage import TextPage


class UnitGroupType(enum.IntEnum):
	MONEY = enum.auto()


class _Unit:
	__unit_id = 1

	exponent: float = 1.15

	def __init__(self, *, db_col, base_cost, **kwargs):
		self.display_name = db_col.title().replace("_", " ")

		self.id = _Unit.__unit_id
		self.db_col = db_col
		self.base_price = base_cost

		self.max_amount = kwargs.get("max_amount", 10)

		_Unit.__unit_id += 1

	def get_price(self, total_owned: int, total_buying: int = 1) -> int:
		price = 0

		for i in range(total_owned, total_owned + total_buying):
			price += self.base_price * pow(self.exponent, i)

		return math.ceil(price)


class _MoneyUnit(_Unit):
	def __init__(self, *, income_hour, **kwargs):
		super().__init__(**kwargs)

		self.income_hour = income_hour

	def create_empire_row(self, units_owned: int) -> list:
		return [self.display_name, f"{units_owned}/{self.max_amount}", f"${self.income_hour * units_owned:,}"]

	def create_units_row(self, units_owned: int) -> list:
		owned, price = f"{units_owned}/{self.max_amount}", f"${self.get_price(units_owned):,}"

		return [self.id, self.display_name, owned, f"${self.income_hour}", price]


class _UnitGroup:
	def __init__(self, unit_type, name, units):
		self.name = name
		self.units = units
		self.unit_type = unit_type


class _MoneyUnitGroup(_UnitGroup):
	def __init__(self, name, units):
		super(_MoneyUnitGroup, self).__init__(UnitGroupType.MONEY, name, units)

	def create_empire_page(self, empire):
		page = TextPage(f"The '{empire[EmpireM.NAME]}' Empire", headers=["Unit", "Owned", "$/hour"])

		total_income = 0

		for unit in self.units:
			total_income += unit.income_hour * empire[unit.db_col]

			page.add_row(unit.create_empire_row(empire[unit.db_col]))

		page.set_footer(f"${total_income:,}/hour")

		return page


def get_group(key: UnitGroupType):
	""" Helper function to get a unit group. """
	return UNIT_GROUPS[key]


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
}

ALL = [unit for _, group in UNIT_GROUPS.items() for unit in group.units]
