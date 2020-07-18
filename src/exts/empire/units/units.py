import math


class _Unit:
	__unit_id = 1  # PRIVATE

	def __init__(self, *, db_col, base_cost, **kwargs):
		self.display_name = db_col.title().replace("_", " ")

		self.id = _Unit.__unit_id
		self.db_col = db_col
		self.base_price = base_cost

		self.max_amount = kwargs.get("max_amount", 10)
		self.exponent = kwargs.get("exponent", 1.25)

		# Increment the internal ID for the next unit
		_Unit.__unit_id += 1

	def get_price(self, total_owned: int, total_buying: int = 1) -> int:
		"""
		Get the total cost of the units brought.

		Example:
			get_price(1)		-> 	250		(+1 units)
			get_price(0, 1) 	-> 	250 	(+1 units)
			get_price(1, 10) 	-> 1,567	(+9 units)
		"""

		price = 0

		for i in range(total_owned, total_owned + total_buying):
			price += self.base_price * pow(self.exponent, i)

		return math.ceil(price)


class _MoneyUnit(_Unit):
	def __init__(self, *, income_hour, **kwargs):
		super().__init__(**kwargs)

		self.income_hour = income_hour

	def get_delta_money(self, total, delta_time):
		"""
		Gets the total INCOME this unit has generated for the delta_time.

		:param total: Number of this unit.
		:param delta_time: Number of hours to simulate.
		:return int: Money earned
		"""
		return math.ceil((self.income_hour * total) * delta_time)

	def create_empire_row(self, units_owned: int) -> list:
		""" Create the row which will be presented on `!empire`. """

		return [self.display_name, f"{units_owned}/{self.max_amount}", f"${self.income_hour * units_owned:,}"]

	def create_units_row(self, units_owned: int) -> list:
		""" Create the row which will be displayed on `!units`. """

		owned, price = f"{units_owned}/{self.max_amount}", f"${self.get_price(units_owned):,}"

		return [self.id, self.display_name, owned, f"${self.income_hour}", price]


class _MilitaryUnit(_Unit):
	def __init__(self, *, upkeep_hour, power, **kwargs):
		super().__init__(**kwargs)

		self.power = power
		self.upkeep_hour = upkeep_hour

	def get_delta_money(self, total, delta_time):
		"""
		Gets the total UPKEEP this unit has generated for the delta_time.

		:param total: Number of this unit.
		:param delta_time: Number of hours to simulate.
		:return int: Money earned
		"""
		return math.ceil((self.upkeep_hour * total) * delta_time) * -1

	def create_empire_row(self, units_owned: int) -> list:
		""" Create the row which will be presented on `!empire`. """

		upkeep, power = f"${self.upkeep_hour * units_owned:,}", self.power * units_owned

		return [self.display_name, f"{units_owned}/{self.max_amount}", power, upkeep]

	def create_units_row(self, units_owned: int) -> list:
		""" Create the row which will be displayed on `!units`. """

		owned, price = f"{units_owned}/{self.max_amount}", f"${self.get_price(units_owned):,}"

		return [self.id, self.display_name, owned, self.power, f"${self.upkeep_hour}", price]
