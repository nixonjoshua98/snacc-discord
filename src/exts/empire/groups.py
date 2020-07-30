import enum

from src.structs.textpage import TextPage


class UnitGroupType(enum.IntEnum):
	""" [Enum] Unit group. """

	MONEY = enum.auto()
	MILITARY = enum.auto()


class _UnitGroup:
	""" [Abstract] Defines some generic methods for each unit. """

	def __init__(self, unit_type: UnitGroupType, name: str, units: list):
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

	def get_total_hourly_income(self, empire, upgrades):
		return sum(map(lambda u: u.get_hourly_income(empire[u.db_col], upgrades), self.units))

	def get_total_hourly_upkeep(self, empire, upgrades):
		return sum(map(lambda u: u.get_hourly_upkeep(empire[u.db_col], upgrades), self.units))

	def get_total_power(self, empire):
		return sum(map(lambda u: u.power * empire[u.db_col], self.units), self.units)


class _MoneyUnitGroup(_UnitGroup):
	def __init__(self, name, units):
		super().__init__(UnitGroupType.MONEY, name, units)

	def create_empire_page(self, empire, upgrades):
		page = TextPage(title=empire["name"], headers=["Unit", "Owned", "Income"])

		total_hourly_income = 0

		for unit in self.units:
			units_owned = empire[unit.db_col]

			unit_hourly_income = unit.get_hourly_income(units_owned, upgrades)

			total_hourly_income += unit_hourly_income

			owned = f"{units_owned}/{unit.get_max_amount(upgrades)}"

			row = [unit.display_name, owned, f"${unit_hourly_income:,}"]

			page.add_row(row)

		page.set_footer(f"Hourly Income: ${total_hourly_income:,}")

		return page

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


class _MilitaryUnitGroup(_UnitGroup):
	def __init__(self, name, units):
		super().__init__(UnitGroupType.MILITARY, name, units)

	def create_empire_page(self, empire, upgrades):
		page = TextPage(title=empire["name"], headers=["Unit", "Owned", "Power", "Upkeep"])

		total_upkeep = 0

		for unit in self.units:
			units_owned = empire[unit.db_col]

			hourly_upkeep = unit.get_hourly_upkeep(units_owned, upgrades)

			total_upkeep += hourly_upkeep

			upkeep, power = f"${hourly_upkeep:,}", unit.power * units_owned

			row = [unit.display_name, f"{units_owned}/{unit.get_max_amount(upgrades)}", power, upkeep]

			page.add_row(row)

		page.set_footer(f"Hourly Upkeep: ${total_upkeep:,}")

		return page

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
