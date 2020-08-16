import math


class Unit:
	__unit_id = 1

	def __init__(self, *, key, base_cost, **kwargs):
		self.key = key
		self.id = Unit.__unit_id

		self._base_cost = base_cost

		self._base_max_amount = 15
		self._max_price = kwargs.get("max_price", 100_000)
		self._exponent = kwargs.get("exponent", 1.15)

		self.display_name = kwargs.get("display_name", self.key.title().replace("_", " "))

		Unit.__unit_id += 1

	def calc_max_amount(self, level):
		return self._base_max_amount + level

	def calc_price(self, owned: int, buying: int, level):
		base_cost = self._calculate_base_cost(owned, buying)

		return int(base_cost * (1.0 - (level * 0.0025)))

	def _calculate_base_cost(self, owned, buying):
		price = 0

		for i in range(owned, owned + buying):
			p = self._base_cost * pow(self._exponent, i)

			if self._max_price is not None:
				p = min(self._max_price, p)

			price += p

		return math.ceil(price)


class MoneyUnit(Unit):
	def __init__(self, *, key, base_cost, **kwargs):
		super(MoneyUnit, self).__init__(key=key, base_cost=base_cost, **kwargs)

		self._hourly_income = kwargs.get("income_hour", 0)

	def calc_hourly_income(self, amount, level):
		base_income = self._hourly_income * amount

		return int(base_income * (1.0 + (level * 0.025)))


class MilitaryUnit(Unit):
	def __init__(self, *, key, base_cost, **kwargs):
		super(MilitaryUnit, self).__init__(key=key, base_cost=base_cost, **kwargs)

		self._power = kwargs.get("power", 0)
		self._hourly_upkeep = kwargs.get("upkeep_hour", 0)

	def calc_hourly_upkeep(self, amount, level):
		return int(self._hourly_upkeep * (1.0 - (level * 0.025)) * amount)

	def calc_power(self):
		return self._power









