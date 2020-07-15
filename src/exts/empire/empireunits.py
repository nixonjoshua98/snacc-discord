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
	Unit(0, "Peasants", 	"peasants", 	100, 	25),
	Unit(1, "Farmers", 		"farmers", 		150, 	50),
	Unit(2, "Butchers", 	"butchers", 	300, 	100),
	Unit(3, "Bakers", 		"bakers", 		1_000, 	250),
	Unit(4, "Winemakers", 	"winemakers", 	4_500, 	750),
)