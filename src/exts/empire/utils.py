import itertools

from src.data import Military, Workers


def get_win_chance(atk_power, def_power):
	return max(0.15, min(0.85, ((atk_power / max(1, def_power)) / 2.0)))


async def calculate_units_lost(units, levels):
	units_lost = dict()
	units_lost_cost = 0

	hourly_income = max(0, Workers.get_total_hourly_income(units, levels))

	hourly_upkeep = max(0, Military.get_total_hourly_upkeep(units, levels))

	hourly_income = hourly_income - hourly_upkeep

	all_units = Military.units + Workers.units

	available_units = list(itertools.filterfalse(lambda u: units.get(u.key, 0) == 0, all_units))

	available_units.sort(key=lambda u: u.calc_price(units.get(u.key, 0), 1), reverse=False)

	for unit in available_units:
		owned = units.get(unit.key, 0)

		for i in range(1, owned + 1):
			price = unit.calc_price(owned - i, i)

			if (price + units_lost_cost) < hourly_income:
				units_lost[unit] = i

			units_lost_cost = sum([unit.calc_price(owned - n, n) for u, n in units_lost.items()])

	return units_lost
