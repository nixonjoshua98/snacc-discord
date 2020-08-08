import enum
import math

from src.structs.textpage import TextPage
from src.structs.purchasable import Purchasable


class _UnitGroupType(enum.IntEnum):
	MONEY = enum.auto()
	MILITARY = enum.auto()


class _UnitGroup:
	def __init__(self, unit_type, name: str, units: list):
		self.name = name
		self.units = units
		self.unit_type = unit_type

	def filter_units(self, population, upgrades):
		units = []

		for unit in self.units:
			units_owned = population[unit.db_col]

			if units_owned < unit.get_max_amount(upgrades):
				units.append(unit)

		return units


class _MoneyUnitGroup(_UnitGroup):
	def __init__(self, name, units):
		super().__init__(_UnitGroupType.MONEY, name, units)

	def create_units_page(self, empire, upgrades):
		page = TextPage(title=self.name, headers=["ID", "Unit", "Owned", "Income", "Cost"])

		for unit in self.filter_units(empire, upgrades):
			units_owned = empire[unit.db_col]

			unit_hourly_income = unit.get_hourly_income(1, upgrades)

			owned = f"{units_owned}/{unit.get_max_amount(upgrades)}"
			price = f"${unit.get_price(units_owned):,}"

			row = [unit.id, unit.display_name, owned, f"${unit_hourly_income}", price]

			page.add_row(row)

		page.set_footer("No units available to hire" if len(page.rows) == 0 else None)

		return page

	def get_total_hourly_income(self, empire, upgrades):
		return sum(map(lambda u: u.get_hourly_income(empire[u.db_col], upgrades), self.units))


class _MilitaryUnitGroup(_UnitGroup):
	def __init__(self, name, units):
		super().__init__(_UnitGroupType.MILITARY, name, units)

	def create_units_page(self, empire, upgrades):
		page = TextPage(title=self.name, headers=["ID", "Unit", "Owned", "Power", "Upkeep", "Cost"])

		for unit in self.filter_units(empire, upgrades):
			units_owned = empire[unit.db_col]

			hourly_upkeep = unit.get_hourly_upkeep(1, upgrades)

			owned = f"{units_owned}/{unit.get_max_amount(upgrades)}"
			price = f"${unit.get_price(units_owned):,}"

			row = [unit.id, unit.display_name, owned, unit.power, f"${hourly_upkeep}", price]

			page.add_row(row)

		page.set_footer("No units available to hire" if len(page.rows) == 0 else None)

		return page

	def get_total_hourly_upkeep(self, empire, upgrades):
		return sum(map(lambda u: u.get_hourly_upkeep(empire[u.db_col], upgrades), self.units))

	def get_total_power(self, empire):
		return sum(map(lambda u: u.power * empire[u.db_col], self.units))


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

	def get_hourly_upkeep(self, total, upgrades):
		upkeep = self.upkeep_hour * total
		upkeep = upkeep * (1.0 - (upgrades["less_upkeep"] * 0.05))

		return math.floor(upkeep)

	def get_hourly_income(self, total, upgrades):
		income = self.income_hour * total
		income = income * (1.0 + (upgrades["more_income"] * 0.05))

		return math.floor(income)


class _MoneyUnit(_Unit):
	def get_max_amount(self, upgrades: dict):
		return self.max_amount + upgrades["extra_money_units"]


class _MilitaryUnit(_Unit):
	def get_max_amount(self, upgrades: dict):
		return self.max_amount + upgrades["extra_military_units"]


_UNIT_GROUPS = {
	_UnitGroupType.MONEY:
		_MoneyUnitGroup("Money Making Units", [
			_MoneyUnit(income_hour=15, db_col="farmers",		base_cost=350),
			_MoneyUnit(income_hour=20, db_col="stonemason",		base_cost=400),
			_MoneyUnit(income_hour=25, db_col="butchers",		base_cost=550),
			_MoneyUnit(income_hour=30, db_col="weaver",			base_cost=650),
			_MoneyUnit(income_hour=35, db_col="tailers",		base_cost=700),
			_MoneyUnit(income_hour=40, db_col="bakers",			base_cost=800),
			_MoneyUnit(income_hour=45, db_col="blacksmiths",	base_cost=950),
			_MoneyUnit(income_hour=50, db_col="cooks",			base_cost=1250),
			_MoneyUnit(income_hour=55, db_col="winemakers", 	base_cost=1500),
			_MoneyUnit(income_hour=60, db_col="shoemakers", 	base_cost=1750),
			_MoneyUnit(income_hour=65, db_col="falconers", 		base_cost=2500)
		]
						),

	_UnitGroupType.MILITARY:
		_MilitaryUnitGroup("Military Units", [
			_MilitaryUnit(upkeep_hour=10, 	power=1, 	db_col="peasants", 	base_cost=250, 	max_amount=10),
			_MilitaryUnit(upkeep_hour=35, 	power=3, 	db_col="soldiers", 	base_cost=500, 	max_amount=10),
			_MilitaryUnit(upkeep_hour=50, 	power=5, 	db_col="spearmen", 	base_cost=750, 	max_amount=10),
			_MilitaryUnit(upkeep_hour=75, 	power=10, 	db_col="warriors", 	base_cost=1250, max_amount=10),
			_MilitaryUnit(upkeep_hour=100, power=15, db_col="knights", base_cost=2000, max_amount=10, exponent=1.25),
		]
						),
}

# - Flatterned list of all units
ALL_UNITS = [unit for _, group in _UNIT_GROUPS.items() for unit in group.units]

# - Groups
MilitaryGroup = _UNIT_GROUPS[_UnitGroupType.MILITARY]
MoneyGroup = _UNIT_GROUPS[_UnitGroupType.MONEY]










