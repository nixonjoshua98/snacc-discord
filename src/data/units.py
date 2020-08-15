
from src.structs.purchasable import Purchasable


class Unit(Purchasable):
	__unit_id = 1  # PRIVATE

	def __init__(self, *, collection, key, base_cost, **kwargs):
		super(Unit, self).__init__(key=key, base_cost=base_cost, **kwargs)

		self.id = Unit.__unit_id

		self.collection = collection

		Unit.__unit_id += 1


class MoneyUnit(Unit):
	def __init__(self, *, key, base_cost, **kwargs):
		super(MoneyUnit, self).__init__(collection="workers", key=key, base_cost=base_cost, **kwargs)

		self._max_price = kwargs.get("max_price", 100_000)
		self._hourly_income = kwargs.get("income_hour", 0)

	def max_amount(self, upgrades: dict):
		return self._max_amount + upgrades.get("extra_money_units", 0)

	def hourly_income(self, upgrades: dict, *, amount: int = 1):
		return int(self._hourly_income * (1.0 + (upgrades.get("more_income", 0) * 0.05)) * amount)

	def price(self, upgrades: dict, owned: int, buying: int = 1):
		return int(self.get_price(owned, buying) * (1.0 - (upgrades.get("cheaper_money_units", 0) * 0.005)))


class MilitaryUnit(Unit):
	def __init__(self, *, key, base_cost, **kwargs):
		super(MilitaryUnit, self).__init__(collection="military", key=key, base_cost=base_cost, **kwargs)

		self._power = kwargs.get("power", 0)
		self._max_price = kwargs.get("max_price", 75_000)
		self._hourly_upkeep = kwargs.get("upkeep_hour", 0)

	def max_amount(self, upgrades: dict):
		return self._max_amount + upgrades.get("extra_military_units", 0)

	def hourly_upkeep(self, upgrades: dict, *, amount: int = 1):
		return int(self._hourly_upkeep * (1.0 - (upgrades.get("less_upkeep", 0) * 0.05)) * amount)

	def power(self):
		return self._power

	def price(self, upgrades: dict, owned: int, buying: int = 1):
		return int(self.get_price(owned, buying) * (1.0 - (upgrades.get("cheaper_military_units", 0) * 0.005)))










