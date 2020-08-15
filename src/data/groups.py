import discord

from .units import MilitaryUnit, MoneyUnit

from src.structs.textpage import TextPage


class UnitGroup:
	units = tuple()

	@classmethod
	def get(cls, **kwargs): return discord.utils.get(cls.units, **kwargs)


class MoneyGroup(UnitGroup):
	units = (
		MoneyUnit(income_hour=15, key="farmers", 		base_cost=350),
		MoneyUnit(income_hour=20, key="stonemason", 	base_cost=400),
		MoneyUnit(income_hour=25, key="butchers", 		base_cost=550),
		MoneyUnit(income_hour=30, key="weaver", 		base_cost=650),
		MoneyUnit(income_hour=35, key="tailors", 		base_cost=700),
		MoneyUnit(income_hour=40, key="bakers", 		base_cost=800),
		MoneyUnit(income_hour=45, key="blacksmiths", 	base_cost=950),
		MoneyUnit(income_hour=50, key="cooks", 			base_cost=1250),
		MoneyUnit(income_hour=55, key="winemakers", 	base_cost=1500),
		MoneyUnit(income_hour=60, key="shoemakers", 	base_cost=1750),
		MoneyUnit(income_hour=65, key="falconers", 		base_cost=2500)
	)

	@classmethod
	def get_total_hourly_income(cls, units: dict, upgrades: dict):
		return int(sum(map(lambda u: u.hourly_income(upgrades, amount=units.get(u.key, 0)), cls.units)))

	@classmethod
	def create_units_page(cls, units: dict, upgrades: dict):
		page = TextPage(title="Money Making Units", headers=["ID", "Unit", "Owned", "Income", "Cost"])

		for unit in cls.units:
			units_owned = units.get(unit.key, 0)

			max_units = unit.max_amount(upgrades)

			if units_owned < max_units:
				hourly_income = unit.hourly_income(upgrades)

				owned = f"{units_owned}/{max_units}"
				price = f"${unit.price(upgrades, units_owned):,}"

				row = [unit.id, unit.display_name, owned, f"${hourly_income}", price]

				page.add_row(row)

		page.set_footer("No units available to hire" if len(page.rows) == 0 else None)

		return page


class MilitaryGroup(UnitGroup):
	units = (
			MilitaryUnit(upkeep_hour=25, 	power=1, 	key="peasants", base_cost=250),
			MilitaryUnit(upkeep_hour=35, 	power=3, 	key="soldiers", base_cost=500),
			MilitaryUnit(upkeep_hour=50, 	power=5, 	key="spearmen", base_cost=750),
			MilitaryUnit(upkeep_hour=75, 	power=7, 	key="warriors", base_cost=1_250),
			MilitaryUnit(upkeep_hour=85, 	power=10, 	key="archers", 	base_cost=1_500),
			MilitaryUnit(upkeep_hour=100, 	power=14, 	key="knights", 	base_cost=2_000),
	)

	@classmethod
	def get_total_hourly_upkeep(cls, units: dict, upgrades: dict):
		return int(sum(map(lambda u: u.hourly_upkeep(upgrades, amount=units.get(u.key, 0)), cls.units)))

	@classmethod
	def get_total_power(cls, units: dict):
		return int(sum(map(lambda u: u.power() * units.get(u.key, 0), cls.units)))

	@classmethod
	def create_units_page(cls, units: dict, upgrades: dict):
		page = TextPage(title="Military Units", headers=["ID", "Unit", "Owned", "Power", "Upkeep", "Cost"])

		for unit in cls.units:
			units_owned = units.get(unit.key, 0)

			max_units = unit.max_amount(upgrades)

			if units_owned < max_units:
				unit_hourly_upkeep = unit.hourly_upkeep(upgrades)

				owned = f"{units_owned}/{max_units}"
				price = f"${unit.price(upgrades, units_owned):,}"

				row = [unit.id, unit.display_name, owned, unit.power(), f"${unit_hourly_upkeep}", price]

				page.add_row(row)

		page.set_footer("No units available to hire" if len(page.rows) == 0 else None)

		return page

