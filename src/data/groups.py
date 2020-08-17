import discord

from .units import MilitaryUnit, MoneyUnit


class UnitGroup:
	units = tuple()

	@classmethod
	def get(cls, **kwargs): return discord.utils.get(cls.units, **kwargs)


class Workers(UnitGroup):
	units = (
		MoneyUnit(income_hour=15, key="farmer", 		base_cost=350),
		MoneyUnit(income_hour=20, key="stonemason", 	base_cost=400),
		MoneyUnit(income_hour=25, key="butcher", 		base_cost=550),
		MoneyUnit(income_hour=30, key="weaver", 		base_cost=650),
		MoneyUnit(income_hour=35, key="tailor", 		base_cost=700),
		MoneyUnit(income_hour=40, key="baker", 			base_cost=800),
		MoneyUnit(income_hour=45, key="blacksmith", 	base_cost=950),
		MoneyUnit(income_hour=50, key="cook", 			base_cost=1250),
		MoneyUnit(income_hour=55, key="winemaker", 		base_cost=1500),
		MoneyUnit(income_hour=60, key="shoemaker", 		base_cost=1750),
		MoneyUnit(income_hour=65, key="falconer", 		base_cost=2500)
	)

	@classmethod
	def get_total_hourly_income(cls, units: dict, levels: dict):
		return int(sum(map(lambda u: u.calc_hourly_income(units.get(u.key, 0), levels.get(u.key, 0)), cls.units)))


class Military(UnitGroup):
	units = (
			MilitaryUnit(upkeep_hour=25, 	power=1, 	key="peasant", 	base_cost=250),
			MilitaryUnit(upkeep_hour=35, 	power=3, 	key="soldier", 	base_cost=500),
			MilitaryUnit(upkeep_hour=50, 	power=5, 	key="spearman", base_cost=750),
			MilitaryUnit(upkeep_hour=75, 	power=7, 	key="warrior", 	base_cost=1_250),
			MilitaryUnit(upkeep_hour=85, 	power=10, 	key="archer", 	base_cost=1_500),
			MilitaryUnit(upkeep_hour=100, 	power=14, 	key="knight", 	base_cost=2_000),
	)

	@classmethod
	def get_total_hourly_upkeep(cls, units: dict, levels: dict):
		return int(sum(map(lambda u: u.calc_hourly_upkeep(units.get(u.key, 0), levels.get(u.key, 0)), cls.units)))

	@classmethod
	def get_total_power(cls, units: dict):
		return int(sum(map(lambda u: u.calc_power(units.get(u.key, 0)), cls.units)))
