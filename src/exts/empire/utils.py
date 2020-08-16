import random
import itertools

from src.data import Military, Workers


def get_win_chance(atk_power, def_power):
	return max(0.15, min(0.85, ((atk_power / max(1, def_power)) / 2.0)))


async def calculate_units_lost(units, levels):
	units_lost = dict()
	units_lost_cost = 0

	hourly_income = max(0, Workers.get_total_hourly_income(units, levels))

	available_units = list(itertools.filterfalse(lambda u: units.get(u.key, 0) == 0, Military.units))

	def f(u):
		return u.calc_price(units.get(u.key, 0), 1, levels.get(u.key, 0))

	available_units.sort(key=lambda u: f(u), reverse=False)

	for unit in available_units:
		owned = units.get(unit.key, 0)

		unit_level = levels.get(unit.key, 0)

		for i in range(1, owned + 1):
			price = unit.calc_price(owned - i, i, unit_level)

			if (price + units_lost_cost) < hourly_income:
				units_lost[unit] = i

			units_lost_cost = sum([unit.calc_price(owned - n, n, unit_level) for u, n in units_lost.items()])

	return units_lost


async def calculate_money_lost(bank):
	return random.randint(max(1, int(bank.get("usd", 0) * 0.025)), max(1, int(bank.get("usd", 0) * 0.05)))
