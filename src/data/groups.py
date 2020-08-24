import math
import discord

from .units import MilitaryUnit, WorkerUnit

from src.common import EmpireConstants

from src.structs import TextPage


class UnitGroup:
	units = tuple()

	@classmethod
	def get(cls, **kwargs):
		unit = discord.utils.get(cls.units, **kwargs)

		return unit


class Workers(UnitGroup):
	units = (
		WorkerUnit(hourly_income=5, 	key="farmer"),
		WorkerUnit(hourly_income=10, 	key="stonemason"),
		WorkerUnit(hourly_income=15, 	key="butcher"),
		WorkerUnit(hourly_income=20, 	key="weaver"),
		WorkerUnit(hourly_income=25, 	key="tailor"),
		WorkerUnit(hourly_income=30, 	key="baker"),
		WorkerUnit(hourly_income=35, 	key="blacksmith"),
		WorkerUnit(hourly_income=40, 	key="cook"),
		WorkerUnit(hourly_income=45, 	key="winemaker"),
		WorkerUnit(hourly_income=50, 	key="shoemaker"),
		WorkerUnit(hourly_income=55, 	key="falconer"),
		WorkerUnit(hourly_income=60, 	key="carpenter"),
	)

	@classmethod
	def get_total_hourly_income(cls, units: dict, levels: dict):
		return sum(map(lambda u: u.calc_hourly_income(units.get(u.key, 0), levels.get(u.key, 0)), cls.units))

	@classmethod
	def shop_page(cls, units_owned, unit_levels):
		page = TextPage(title="Workers", headers=["ID", "Unit", "Lvl", "Owned", "Income", "Price"])

		for unit in cls.units:
			unit_level = unit_levels.get(unit.key, 0)
			owned = units_owned.get(unit.key, 0)

			max_units = unit.calc_max_amount(unit_level)

			row = [unit.id, unit.display_name, unit_level]

			if owned >= max_units:
				if unit_level >= EmpireConstants.MAX_UNIT_MERGE:
					continue

				row.append("Mergeable")

				page.add(row)

				continue

			price = unit.calc_price(owned, 1)
			income = unit.calc_hourly_income(1, unit_level)

			row.extend([f"{owned}/{max_units}", f"${income:,}", f"${price:,}"])

			page.add(row)

		return page


class Military(UnitGroup):
	units = (
		MilitaryUnit(upkeep_hour=10, 	key="scout"),
		MilitaryUnit(upkeep_hour=15, 	key="peasant"),
		MilitaryUnit(upkeep_hour=25, 	key="soldier"),
		MilitaryUnit(upkeep_hour=40, 	key="thief"),
		MilitaryUnit(upkeep_hour=45, 	key="spearman"),
		MilitaryUnit(upkeep_hour=60, 	key="cavalry"),
		MilitaryUnit(upkeep_hour=65, 	key="warrior"),
		MilitaryUnit(upkeep_hour=80, 	key="archer"),
		MilitaryUnit(upkeep_hour=90,	key="knight"),
	)

	@classmethod
	def get_total_hourly_upkeep(cls, units: dict, levels: dict):
		return sum(map(lambda u: u.calc_hourly_upkeep(units.get(u.key, 0), levels.get(u.key, 0)), cls.units))

	@classmethod
	def get_total_power(cls, units: dict):
		def round_up(n, decimals=0):
			multiplier = 10 ** decimals

			return math.ceil(n * multiplier) / multiplier

		return round_up(sum(map(lambda u: u.calc_power(units.get(u.key, 0)), cls.units)), 1)

	@classmethod
	def shop_page(cls, units_owned, unit_levels):
		page = TextPage(title="Workers", headers=["ID", "Unit", "Lvl", "Owned", "Power", "Upkeep", "Price"])

		for unit in cls.units:
			unit_level = unit_levels.get(unit.key, 0)

			owned = units_owned.get(unit.key, 0)

			max_units = unit.calc_max_amount(unit_level)

			row = [unit.id, unit.display_name, unit_level]

			if owned >= max_units:
				if unit_level >= EmpireConstants.MAX_UNIT_MERGE:
					continue

				row.append("Mergeable")

				page.add(row)

				continue

			price = unit.calc_price(owned, 1)
			power = unit.calc_power(1)
			upkeep = unit.calc_hourly_upkeep(1, unit_level)

			row.extend([f"{owned}/{max_units}", power, f"${upkeep:,}", f"${price:,}"])

			page.add(row)

		return page
