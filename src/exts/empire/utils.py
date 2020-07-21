
from .units import UNIT_GROUPS, UnitGroupType


def get_total_money_delta(population, delta_time):
	money_change = 0

	for _, group in UNIT_GROUPS.items():
		for unit in group.units:
			money_change += unit.get_delta_money(population[unit.db_col], delta_time)

	return money_change


def get_total_power(population):
	power = 0

	for unit in UNIT_GROUPS[UnitGroupType.MILITARY].units:
		power += unit.power * population[unit.db_col]

	return power
