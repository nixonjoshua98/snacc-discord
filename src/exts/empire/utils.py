import math
import random
import itertools

from src.data import MilitaryGroup, MoneyGroup


def get_hourly_money_change(empire, upgrades, *, hours: float = 1.0):
	total_hourly_income = MoneyGroup.get_total_hourly_income(empire, upgrades)
	total_hourly_upkeep = MilitaryGroup.get_total_hourly_upkeep(empire, upgrades)

	return math.floor((total_hourly_income - total_hourly_upkeep) * hours)


def get_win_chance(atk_power, def_power):
	return max(0.15, min(0.85, ((atk_power / max(1, def_power)) / 2.0)))


async def calculate_units_lost(military, workers, upgrades):
	units_lost = dict()
	units_lost_cost = 0

	hourly_income = max(0, MoneyGroup.get_total_hourly_income(workers, upgrades))

	available_units = list(itertools.filterfalse(lambda u: military.get(u.key, 0) == 0, MilitaryGroup.units))

	available_units.sort(key=lambda u: u.price(upgrades, military.get(u.key, 0)), reverse=False)

	for unit in available_units:
		owned = military.get(unit.key, 0)

		for i in range(1, owned + 1):
			price = unit.price(upgrades, owned - i, i)

			if (price + units_lost_cost) < hourly_income:
				units_lost[unit] = i

			units_lost_cost = sum([u.get_price(owned - n, n) for u, n in units_lost.items()])

	return units_lost


async def calculate_money_lost(bank):
	return random.randint(max(1, int(bank.get("usd", 0) * 0.025)), max(1, int(bank.get("usd", 0) * 0.05)))