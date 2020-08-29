
from src.data import Military, Workers


def net_income(units, levels) -> int:

	hourly_income = Workers.get_total_hourly_income(units, levels)
	hourly_upkeep = Military.get_total_hourly_upkeep(units, levels)

	return hourly_income - hourly_upkeep
