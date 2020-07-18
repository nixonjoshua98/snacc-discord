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

	def create_empire_page(self, empire):
		""" [Overridable] ..."""

		page = TextPage()

		for unit in self.units:
			page.add_row(unit.create_empire_row(empire[unit.db_col]))

		return page

	def create_units_page(self, empire):
		""" [Overridable] ..."""

		page = TextPage()

		for unit in self.units:
			# Do not show units which we have the maximum number allowed
			if empire[unit.db_col] >= unit.max_amount:
				continue

			page.add_row(unit.create_units_row(empire[unit.db_col]))

		page.set_footer("No units available to hire" if len(page.rows) == 0 else None)

		return page


class _MoneyUnitGroup(_UnitGroup):
	def __init__(self, name, units):
		super().__init__(UnitGroupType.MONEY, name, units)

	def create_empire_page(self, empire):
		page = super().create_empire_page(empire)

		page.set_headers(["Unit", "Owned", "Income"])

		# Total income the user would get after 1 hour
		total_income = sum(unit.get_delta_money(empire[unit.db_col], 1.0) for unit in self.units)

		page.set_footer(f"Hourly Income: ${total_income:,}")

		return page

	def create_units_page(self, empire):
		page = super().create_units_page(empire)

		page.set_title(self.name)
		page.set_headers(["ID", "Unit", "Owned", "Income", "Cost"])

		return page


class _MilitaryUnitGroup(_UnitGroup):
	def __init__(self, name, units):
		super().__init__(UnitGroupType.MILITARY, name, units)

	def create_empire_page(self, empire):
		page = super().create_empire_page(empire)

		page.set_headers(["Unit", "Owned", "Power", "Upkeep"])

		# Total hourly upkeep of all military units
		total_upkeep = sum(unit.get_delta_money(empire[unit.db_col], 1.0) for unit in self.units)

		page.set_footer(f"Hourly Upkeep: ${total_upkeep:,}")

		return page

	def create_units_page(self, empire):
		page = super().create_units_page(empire)

		page.set_title(self.name)
		page.set_headers(["ID", "Unit", "Owned", "Power", "Upkeep", "Cost"])

		return page
