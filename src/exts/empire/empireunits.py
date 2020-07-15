import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Unit:
	id: int
	display_name: str
	db_col: str
	base_price: int
	income_hour: int

	max_amount: int = 25
	exponent: float = 1.1

	def get_price(self, total_owned: int, total_buying: int = 1) -> int:
		price = 0

		for i in range(total_buying):
			price += self.base_price * pow(self.exponent, total_owned + i)

		return math.ceil(price)


ALL = (
	Unit(1, "Farmer", 		"farmers", 		100, 	10),
	Unit(2, "Butcher", 		"butchers", 	250, 	25),
	Unit(3, "Baker", 		"bakers", 		500, 	35),
	Unit(4, "Cook", 		"cooks", 		750, 	45),
	Unit(5, "Winemaker", 	"winemakers", 	1000, 	50),
)
