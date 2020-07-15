import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Unit:
	id: int
	display_name: str
	db_col: str
	base_price: int
	income_hour: int

	def get_price(self, total_owned: int, total_buying: int = 1) -> int:
		price = 0

		for i in range(total_buying):
			price += self.base_price * pow(1.05, total_owned + i)

		return math.ceil(price)


ALL = (
	Unit(0, "Peasant", 		"peasants", 	100, 	15),
	Unit(1, "Farmer", 		"farmers", 		150, 	25),
	Unit(2, "Butcher", 		"butchers", 	300, 	50),
	Unit(3, "Baker", 		"bakers", 		500, 	100),
	Unit(4, "Cook", 		"cooks", 		750, 	175),
	Unit(5, "Winemaker", 	"winemakers", 	1_500, 	250),
	Unit(6, "Tanner", 		"tanners", 		2_500, 	350),
	Unit(7, "Blacksmith", 	"blacksmiths", 	5_000, 	500),
)
