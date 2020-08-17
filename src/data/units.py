import math

from src.common import EmpireConstants


class Unit:
	__unit_id = 1

	__unit_keys = set()

	def __init__(self, *, key, base_cost, **kwargs):
		self.key = key
		self.id = Unit.__unit_id

		self._base_cost = base_cost

		self._base_max_amount = 15
		self._max_price = kwargs.get("max_price", 100_000)
		self._exponent = kwargs.get("exponent", 1.15)

		self.display_name = kwargs.get("display_name", self.key.title().replace("_", " "))

		Unit.__unit_id += 1

		if self.key in Unit.__unit_keys:
			raise KeyError(f"Key '{self.key}' is not unique.")

		Unit.__unit_keys.add(self.key)

	def _calc_price(self, owned, buying):
		price = 0

		for i in range(owned, owned + buying):
			p = self._base_cost * pow(self._exponent, i)

			if self._max_price is not None:
				p = min(self._max_price, p)

			price += p

		return math.ceil(price)

	def calc_max_amount(self, level):
		return self._base_max_amount + level

	def calc_price(self, owned: int, buying: int):
		return self._calc_price(owned, buying)


class MoneyUnit(Unit):
	def __init__(self, *, key, base_cost, **kwargs):
		super(MoneyUnit, self).__init__(key=key, base_cost=base_cost, **kwargs)

		self._hourly_income = kwargs.get("income_hour", 0)

	def calc_hourly_income(self, amount, level):
		return math.floor(self._hourly_income * amount * (1.0 + (level * 0.05)))

	def calc_next_merge_stats(self, amount, level):
		income = self.calc_hourly_income(amount, level)
		unit_income = self.calc_hourly_income(1, level)
		slots = self.calc_max_amount(level)

		new_income = self.calc_hourly_income(amount - EmpireConstants.MAX_UNIT_MERGE, level + 1)
		new_unit_income = self.calc_hourly_income(1, level + 1)
		new_slots = self.calc_max_amount(level + 1)

		return {
			"Hourly Income": f"${income:,} -> ${new_income:,}",
			"Slots": f"{slots:,} -> {new_slots:,}",
			"Unit Income": f"${unit_income:,} -> ${new_unit_income:,}"
		}


class MilitaryUnit(Unit):
	def __init__(self, *, key, base_cost, **kwargs):
		super(MilitaryUnit, self).__init__(key=key, base_cost=base_cost, **kwargs)

		self._power = kwargs.get("power", 0)
		self._hourly_upkeep = kwargs.get("upkeep_hour", 0)

	def calc_hourly_upkeep(self, amount, level):
		return math.floor(self._hourly_upkeep * (1.0 - (level * 0.05)) * amount)

	def calc_power(self, amount):
		return self._power * amount

	def calc_next_merge_stats(self, amount, level):
		upkeep = self.calc_hourly_upkeep(amount, level)
		slots = self.calc_max_amount(level)
		unit_upkeep = self.calc_hourly_upkeep(1, level)
		power = self.calc_power(amount)

		new_upkeep = self.calc_hourly_upkeep(amount - EmpireConstants.MAX_UNIT_MERGE, level + 1)
		new_slots = self.calc_max_amount(level + 1)
		new_unit_upkeep = self.calc_hourly_upkeep(1, level + 1)
		new_power = self.calc_power(amount)

		return {
			"Hourly Upkeep": f"${upkeep:,} -> ${new_upkeep:,}",
			"Slots": f"{slots:,} -> {new_slots:,}",
			"Unit Upkeep": f"${unit_upkeep:,} -> ${new_unit_upkeep:,}",
			"Unit Power": f"{power:,} -> {new_power:,}"
		}









