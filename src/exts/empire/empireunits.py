import math

from src.common.models import EmpireM


class _Unit:
	exponent: float = 1.15

	def __init__(self, id_, *, db_col, base_cost, **kwargs):
		self.display_name = db_col.title().replace("_", " ")

		self.id = id_
		self.db_col = db_col
		self.base_price = base_cost

		self.max_amount = kwargs.get("max_amount", 10)

	def __str__(self):
		return f"_Unit(self.id={self.id}, self.display_name={self.display_name})"

	def get_price(self, total_owned: int, total_buying: int = 1) -> int:
		price = 0

		for i in range(total_owned, total_owned + total_buying):
			price += self.base_price * pow(self.exponent, i)

		return math.ceil(price)


class _MoneyUnit(_Unit):
	def __init__(self, unit_id, *, income_hour, **kwargs):
		super().__init__(unit_id, **kwargs)

		self.income_hour = income_hour

	def __str__(self):
		return f"_Unit(self.id={self.id}, self.display_name={self.display_name})"


MONEY_UNITS = (
	_MoneyUnit(1, income_hour=10, db_col=EmpireM.FARMERS,		base_cost=250),
	_MoneyUnit(2, income_hour=20, db_col=EmpireM.BUTCHERS,		base_cost=500),
	_MoneyUnit(3, income_hour=30, db_col=EmpireM.BAKERS,		base_cost=750),
	_MoneyUnit(4, income_hour=40, db_col=EmpireM.COOKS,			base_cost=1000),
	_MoneyUnit(5, income_hour=50, db_col=EmpireM.WINEMAKERS, 	base_cost=1500),
)

ALL = MONEY_UNITS
