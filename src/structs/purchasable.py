import math


class Purchasable:

	def __init__(self, *, key, base_cost, **kwargs):
		self.key = key

		self._base_cost = base_cost

		self._max_amount = kwargs.get("max_amount", 15)
		self._max_price = kwargs.get("max_price", None)
		self._exponent = kwargs.get("exponent", 1.15)

		self.display_name = kwargs.get("display_name", self.key.title().replace("_", " "))

	def get_price(self, total_owned: int, total_buying: int = 1) -> int:
		""" Get the total cost of the units brought. """

		price = 0

		for i in range(total_owned, total_owned + total_buying):
			p = self._base_cost * pow(self._exponent, i)

			if self._max_price is not None:
				p = min(self._max_price, p)

			price += p

		return math.ceil(price)
