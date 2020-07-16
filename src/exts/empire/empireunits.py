import math

from dataclasses import dataclass

from src.common.models import EmpireM


@dataclass(frozen=True)
class _Unit:
	id: int
	display_name: str
	db_col: str
	base_price: int
	income_hour: int

	max_amount: int = 10
	exponent: float = 1.1

	def get_price(self, total_owned: int, total_buying: int = 1) -> int:
		price = 0

		for i in range(total_buying):
			price += self.base_price * pow(self.exponent, total_owned + i)

		return math.ceil(price)


ALL = (
	_Unit(1, "Farmer", 		EmpireM.FARMERS, 	100, 	10),
	_Unit(2, "Butcher", 	EmpireM.BUTCHERS, 	250, 	25),
	_Unit(3, "Baker", 		EmpireM.BAKERS, 	500, 	35),
	_Unit(4, "Cook", 		EmpireM.COOKS, 		750, 	45),
	_Unit(5, "Winemaker", 	EmpireM.WINEMAKERS, 1000, 	50),
)
