import enum

from src.common.models import EmpireM
from src.structs.textpage import TextPage


class UnitGroupType(enum.IntEnum):
	MONEY = enum.auto()
	MILITARY = enum.auto()


class _UnitGroup:
	def __init__(self, unit_type, name, units):
		self.name = name
		self.units = units
		self.unit_type = unit_type

	def create_empire_page(self, empire):
		page = TextPage()

		page.add_rows(*(unit.create_empire_row(empire[unit.db_col]) for unit in self.units))

		return page

	def create_units_page(self, empire):
		page = TextPage()

		for unit in self.units:
			if empire[unit.db_col] >= unit.max_amount:
				continue

			page.add_row(unit.create_units_row(empire[unit.db_col]))

		return page


class _MoneyUnitGroup(_UnitGroup):
	def __init__(self, name, units):
		super().__init__(UnitGroupType.MONEY, name, units)

	def create_empire_page(self, empire):
		page = super(_MoneyUnitGroup, self).create_empire_page(empire)

		page.set_title(f"The '{empire[EmpireM.NAME]}' Empire")
		page.set_headers(["Unit", "Owned", "Income"])

		total_income = sum(unit.get_delta_money(empire[unit.db_col], 1.0) for unit in self.units)

		page.set_footer(f"Hourly Income: ${total_income:,}")

		return page

	def create_units_page(self, empire):
		page = super(_MoneyUnitGroup, self).create_units_page(empire)

		page.set_title(self.name)
		page.set_headers(["ID", "Unit", "Owned", "Income", "Cost"])

		page.set_footer("No units available to hire" if len(page.rows) == 0 else None)

		return page


class _MilitaryUnitGroup(_UnitGroup):
	def __init__(self, name, units):
		super().__init__(UnitGroupType.MILITARY, name, units)

	def create_empire_page(self, empire):
		page = super().create_empire_page(empire)

		page.set_title(f"The '{empire[EmpireM.NAME]}' Empire")
		page.set_headers(["Unit", "Owned", "Power", "Upkeep"])

		total_income = sum(unit.get_delta_money(empire[unit.db_col], 1.0) for unit in self.units)

		page.set_footer(f"Hourly Upkeep: ${total_income:,}")

		return page

	def create_units_page(self, empire):
		page = super().create_units_page(empire)

		page.set_title(self.name)
		page.set_headers(["ID", "Unit", "Owned", "Power", "Upkeep", "Cost"])

		page.set_footer("No units available to hire" if len(page.rows) == 0 else None)

		return page
