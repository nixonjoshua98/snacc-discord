import math

from src.data import MilitaryGroup, MoneyGroup


def get_hourly_money_change(empire, upgrades, *, hours: float = 1.0):
	total_hourly_income = MoneyGroup.get_total_hourly_income(empire, upgrades)
	total_hourly_upkeep = MilitaryGroup.get_total_hourly_upkeep(empire, upgrades)

	return math.floor((total_hourly_income - total_hourly_upkeep) * hours)
