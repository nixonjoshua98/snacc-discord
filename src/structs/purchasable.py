import math


class Purchasable:

	def __init__(self, *, db_col, base_cost, **kwargs):
		self.db_col = db_col
		self.base_price = base_cost

		self.max_amount = kwargs.get("max_amount", 15)
		self.max_price = kwargs.get("max_price", None)
		self.exponent = kwargs.get("exponent", 1.15)
		self.display_name = kwargs.get("display_name", db_col.title().replace("_", " "))

	def get_price(self, total_owned: int, total_buying: int = 1) -> int:
		""" Get the total cost of the units brought. """

		price = 0

		for i in range(total_owned, total_owned + total_buying):
			p = self.base_price * pow(self.exponent, i)

			if self.max_price is not None:
				p = min(self.max_price, p)

			price += p

		return math.ceil(price)
