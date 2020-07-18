

def get_total_money_delta(population, delta_time):
	# Circular dependancy otherwise
	from . import UNIT_GROUPS

	money_change = 0

	for _, group in UNIT_GROUPS.items():
		for unit in group.units:
			money_change += unit.get_delta_money(population[unit.db_col], delta_time)

	return money_change
