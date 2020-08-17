import math
import discord

from .units import MilitaryUnit, WorkerUnit


class UnitGroup:
	units = tuple()

	@classmethod
	def get(cls, **kwargs): return discord.utils.get(cls.units, **kwargs)


class Workers(UnitGroup):
	units = (
		WorkerUnit(hourly_income=15, key="farmer"),
		WorkerUnit(hourly_income=20, key="stonemason"),
		WorkerUnit(hourly_income=25, key="butcher"),
		WorkerUnit(hourly_income=30, key="weaver"),
		WorkerUnit(hourly_income=35, key="tailor"),
		WorkerUnit(hourly_income=40, key="baker"),
		WorkerUnit(hourly_income=45, key="blacksmith"),
		WorkerUnit(hourly_income=50, key="cook"),
		WorkerUnit(hourly_income=55, key="winemaker"),
		WorkerUnit(hourly_income=60, key="shoemaker"),
		WorkerUnit(hourly_income=65, key="falconer"),
		WorkerUnit(hourly_income=70, key="carpenter"),
	)

	@classmethod
	def get_total_hourly_income(cls, units: dict, levels: dict):
		return sum(map(lambda u: u.calc_hourly_income(units.get(u.key, 0), levels.get(u.key, 0)), cls.units))


class Military(UnitGroup):
	units = (
			MilitaryUnit(upkeep_hour=25, 	key="peasant"),
			MilitaryUnit(upkeep_hour=35, 	key="soldier"),
			MilitaryUnit(upkeep_hour=50, 	key="spearman"),
			MilitaryUnit(upkeep_hour=60, 	key="cavalry"),
			MilitaryUnit(upkeep_hour=75, 	key="warrior"),
			MilitaryUnit(upkeep_hour=85, 	key="archer"),
			MilitaryUnit(upkeep_hour=100,	key="knight"),
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
