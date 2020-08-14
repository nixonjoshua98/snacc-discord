import math
import discord

from src.structs.textpage import TextPage
from src.structs.purchasable import Purchasable


class _Unit(Purchasable):
	__unit_id = 1  # PRIVATE

	def __init__(self, *, db_col, base_cost, **kwargs):
		super(_Unit, self).__init__(db_col=db_col, base_cost=base_cost, **kwargs)

		self.id = _Unit.__unit_id

		self.max_price = kwargs.get("max_price", 50_000)

		# Increment the internal ID for the next unit
		_Unit.__unit_id += 1


class _MoneyUnit(_Unit):
	def __init__(self, *, db_col, base_cost, **kwargs):
		super(_MoneyUnit, self).__init__(db_col=db_col, base_cost=base_cost, **kwargs)

		self.max_amount = kwargs.get("max_amount", 15)
		self.income_hour = kwargs.get("income_hour", 0)

	def get_max_amount(self, upgrades: dict):
		return self.max_amount + upgrades["extra_money_units"]

	def get_hourly_income(self, total, upgrades):
		income = self.income_hour * total
		income = income * (1.0 + (upgrades["more_income"] * 0.05))

		return math.floor(income)

	def calculate_price(self, upgrades, total_owned: int, total_buying: int = 1) -> int:
		cost = self.get_price(total_owned, total_buying)

		return math.floor(cost * (1.0 - (upgrades['cheaper_money_units'] * 0.005)))


class _MilitaryUnit(_Unit):
	def __init__(self, *, db_col, base_cost, **kwargs):
		super(_MilitaryUnit, self).__init__(db_col=db_col, base_cost=base_cost, **kwargs)

		self.power = kwargs.get("power", 0)
		self.max_amount = kwargs.get("max_amount", 10)
		self.upkeep_hour = kwargs.get("upkeep_hour", 0)

	def get_max_amount(self, upgrades: dict):
		return self.max_amount + upgrades["extra_military_units"]

	def get_hourly_upkeep(self, total, upgrades):
		return self.upkeep_hour * total * (1.0 - (upgrades["less_upkeep"] * 0.05))

	def get_power(self, total, upgrades):
		return (self.power * total) * (1.0 + (upgrades.get("more_power", 0) * 0.01))

	def calculate_price(self, upgrades, total_owned: int, total_buying: int = 1) -> int:
		cost = self.get_price(total_owned, total_buying)

		return math.floor(cost * (1.0 - (upgrades['cheaper_military_units'] * 0.005)))


class _MoneyGroup(type):
	_UNITS = [
			_MoneyUnit(income_hour=15, db_col="farmers",		base_cost=350),
			_MoneyUnit(income_hour=20, db_col="stonemason",		base_cost=400),
			_MoneyUnit(income_hour=25, db_col="butchers",		base_cost=550),
			_MoneyUnit(income_hour=30, db_col="weaver",			base_cost=650),
			_MoneyUnit(income_hour=35, db_col="tailors",		base_cost=700),
			_MoneyUnit(income_hour=40, db_col="bakers",			base_cost=800),
			_MoneyUnit(income_hour=45, db_col="blacksmiths",	base_cost=950),
			_MoneyUnit(income_hour=50, db_col="cooks",			base_cost=1250),
			_MoneyUnit(income_hour=55, db_col="winemakers", 	base_cost=1500),
			_MoneyUnit(income_hour=60, db_col="shoemakers", 	base_cost=1750),
			_MoneyUnit(income_hour=65, db_col="falconers", 		base_cost=2500)
		]

	def create_units_page(self, empire, upgrades):
		page = TextPage(title="Money Making Units", headers=["ID", "Unit", "Owned", "Income", "Cost"])

		for unit in self._UNITS:
			units_owned = empire[unit.db_col]

			if units_owned < unit.get_max_amount(upgrades):
				unit_hourly_income = unit.get_hourly_income(1, upgrades)

				owned = f"{units_owned}/{unit.get_max_amount(upgrades)}"
				price = f"${unit.calculate_price(upgrades, units_owned):,}"

				row = [unit.id, unit.display_name, owned, f"${unit_hourly_income}", price]

				page.add_row(row)

		page.set_footer("No units available to hire" if len(page.rows) == 0 else None)

		return page

	def get_total_hourly_income(self, empire, upgrades):
		return sum(map(lambda u: u.get_hourly_income(empire[u.db_col], upgrades), self.units))

	@property
	def units(self): return self._UNITS

	def get(self, **kwargs): return discord.utils.get(self._UNITS, **kwargs)


class _MilitaryGroup(type):
	_UNITS = [
			_MilitaryUnit(upkeep_hour=25, 	power=1, 	db_col="peasants", 	base_cost=250),
			_MilitaryUnit(upkeep_hour=35, 	power=3, 	db_col="soldiers", 	base_cost=500),
			_MilitaryUnit(upkeep_hour=50, 	power=5, 	db_col="spearmen", 	base_cost=750),
			_MilitaryUnit(upkeep_hour=75, 	power=7, 	db_col="warriors", 	base_cost=1_250),
			_MilitaryUnit(upkeep_hour=85, 	power=10, 	db_col="archers", 	base_cost=1_500),
			_MilitaryUnit(upkeep_hour=100, 	power=14, 	db_col="knights", 	base_cost=2_000),
		]

	def create_units_page(self, empire, upgrades):
		page = TextPage(title="Military Units", headers=["ID", "Unit", "Owned", "Power", "Upkeep", "Cost"])

		for unit in self._UNITS:
			units_owned = empire[unit.db_col]

			if units_owned < unit.get_max_amount(upgrades):
				hourly_upkeep = unit.get_hourly_upkeep(1, upgrades)

				owned = f"{units_owned}/{unit.get_max_amount(upgrades)}"
				price = f"${unit.calculate_price(upgrades, units_owned):,}"

				row = [unit.id, unit.display_name, owned, unit.power, f"${hourly_upkeep}", price]

				page.add_row(row)

		page.set_footer("No units available to hire" if len(page.rows) == 0 else None)

		return page

	def get_total_hourly_upkeep(self, empire, upgrades):
		return math.floor(sum(map(lambda u: u.get_hourly_upkeep(empire.get(u.db_col, 0), upgrades), self.units)))

	def get_total_power(self, empire, upgrades):
		return math.floor(sum(map(lambda u: u.get_power(empire.get(u.db_col, 0), upgrades), self.units)))

	@property
	def units(self): return self._UNITS

	def get(self, **kwargs): return discord.utils.get(self._UNITS, **kwargs)


class MilitaryGroup(metaclass=_MilitaryGroup):
	pass


class MoneyGroup(metaclass=_MoneyGroup):
	pass










