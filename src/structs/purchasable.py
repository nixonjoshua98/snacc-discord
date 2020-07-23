import math


class Purchasable:
	__id = 1  # PRIVATE

	def __init__(self, *, db_col, base_cost, **kwargs):
		self.display_name = kwargs.get("display_name", db_col.title().replace("_", " "))

		self.id = Purchasable.__id
		self.db_col = db_col
		self.base_price = base_cost

		self.max_amount = kwargs.get("max_amount", 10)
		self.exponent = kwargs.get("exponent", 1.15)

		Purchasable.__id += 1

	def get_price(self, total_owned: int, total_buying: int = 1) -> int:
		""" Get the total cost of the units brought. """

		price = 0

		for i in range(total_owned, total_owned + total_buying):
			price += self.base_price * pow(self.exponent, i)

		return math.ceil(price)