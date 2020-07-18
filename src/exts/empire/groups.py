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

	def filter_units(self, population):
		units = []

		for unit in self.units:
			units_owned = population[unit.db_col]

			if units_owned < unit.max_amount:
				units.append(unit)

		return units


class _MoneyUnitGroup(_UnitGroup):
	def __init__(self, name, units):
		super().__init__(UnitGroupType.MONEY, name, units)

	def create_empire_page(self, empire):
		page = TextPage(title="Your Empire")

		page.set_headers(["Unit", "Owned", "Income"])

		for unit in self.units:
			units_owned = empire[unit.db_col]

			row = [unit.display_name, f"{units_owned}/{unit.max_amount}", f"${unit.income_hour * units_owned:,}"]

			page.add_row(row)

		# Total income the user would get after 1 hour
		total_income = sum(unit.get_delta_money(empire[unit.db_col], 1.0) for unit in self.units)

		page.set_footer(f"Hourly Income: ${total_income:,}")

		return page

	def create_units_page(self, empire):
		page = TextPage(title=self.name, headers=["ID", "Unit", "Owned", "Income", "Cost"])

		for unit in self.filter_units(empire):
			units_owned = empire[unit.db_col]

			owned, price = f"{units_owned}/{unit.max_amount}", f"${unit.get_price(units_owned):,}"

			row = [unit.id, unit.display_name, owned, f"${unit.income_hour}", price]

			page.add_row(row)

		page.set_footer("No units available to hire" if len(page.rows) == 0 else None)

		return page


class _MilitaryUnitGroup(_UnitGroup):
	def __init__(self, name, units):
		super().__init__(UnitGroupType.MILITARY, name, units)

	def create_empire_page(self, empire):
		page = TextPage(title="Your Empire", headers=["Unit", "Owned", "Power", "Upkeep"])

		for unit in self.units:
			units_owned = empire[unit.db_col]

			upkeep, power = f"${unit.upkeep_hour * units_owned:,}", unit.power * units_owned

			row = [unit.display_name, f"{units_owned}/{unit.max_amount}", power, upkeep]

			page.add_row(row)

		# Total hourly upkeep of all military units
		total_upkeep = sum(unit.get_delta_money(empire[unit.db_col], 1.0) for unit in self.units)

		page.set_footer(f"Hourly Upkeep: ${total_upkeep * -1:,}")

		return page

	def create_units_page(self, empire):
		page = TextPage(title=self.name, headers=["ID", "Unit", "Owned", "Power", "Upkeep", "Cost"])

		for unit in self.filter_units(empire):
			units_owned = empire[unit.db_col]

			owned, price = f"{units_owned}/{unit.max_amount}", f"${unit.get_price(units_owned):,}"

			row = [unit.id, unit.display_name, owned, unit.power, f"${unit.upkeep_hour}", price]

			page.add_row(row)

		page.set_footer("No units available to hire" if len(page.rows) == 0 else None)

		return page
