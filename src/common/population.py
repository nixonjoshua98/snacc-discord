import math
import discord

from src.structs import TextPage

from src.common import UnitValues


class UnitGroup:
	units = tuple()

	@classmethod
	def get(cls, **kwargs):
		unit = discord.utils.get(cls.units, **kwargs)

		return unit


class Unit:
	__unit_id = 1

	__unit_keys = set()

	def __init__(self, *, key, base_cost, **kwargs):
		self.key = key
		self.id = Unit.__unit_id

		self._base_cost = base_cost

		self._base_max_amount = 15
		self._max_price = kwargs.get("max_price", 50_000)
		self._exponent = kwargs.get("exponent", 1.15)

		self.display_name = kwargs.get("display_name", self.key.title().replace("_", " "))

		Unit.__unit_id += 1

		if self.key in Unit.__unit_keys:
			raise KeyError(f"Key '{self.key}' is not unique.")

		Unit.__unit_keys.add(self.key)

	def _calc_price(self, owned, buying):
		price = 0

		for i in range(owned, owned + buying):
			p = self._base_cost * pow(self._exponent, i)

			if self._max_price is not None:
				p = min(self._max_price, p)

			price += p

		return math.ceil(price)

	def calc_max_amount(self, unit_entry: dict):
		return min(UnitValues.MAX_UNITS, self._base_max_amount + unit_entry.get("level", 0))

	def calc_price(self, owned: int, buying: int):
		return self._calc_price(owned, buying)


class WorkerUnit(Unit):
	__worker_id = 1

	def __init__(self, *, key, **kwargs):
		self.income_per_unit = kwargs.get("income", 0)

		base_cost = math.floor(self.income_per_unit * max(16.0, (24.0 + (0.5 * (WorkerUnit.__worker_id - 1)))))

		super(WorkerUnit, self).__init__(key=key, base_cost=base_cost, **kwargs)

		WorkerUnit.__worker_id += 1

	def calc_income_per_unit(self, unit_entry: dict):
		level = unit_entry.get("level", 0)

		return math.ceil(self.income_per_unit * (1.0 + (level * 0.05)))

	def calc_hourly_income(self, unit_entry: dict):
		return self.calc_income_per_unit(unit_entry) * unit_entry.get("owned", 0)


class MilitaryUnit(Unit):
	__military_id = 1

	def __init__(self, *, key, **kwargs):
		self._upkeep = kwargs.get("upkeep", 0)

		base_cost = math.floor(self._upkeep * max(16.0, (24.0 - (0.5 * (MilitaryUnit.__military_id - 1)))))

		super(MilitaryUnit, self).__init__(key=key, base_cost=base_cost, **kwargs)

		self.power_per_unit = self._base_cost / max(450, (600 - ((MilitaryUnit.__military_id - 1) * 25)))

		# - Military units are cheaper
		self._exponent = 1.10

		MilitaryUnit.__military_id += 1

	def calc_hourly_upkeep(self, unit_entry):
		return math.floor(self._upkeep * (1.0 - (unit_entry.get("level", 0) * 0.05)) * unit_entry.get("owned", 0))

	def calc_power_per_unit(self, _: dict):
		return round(self.power_per_unit, 1)

	def calc_power(self, unit_entry):
		return round(self.power_per_unit * unit_entry.get("owned", 0), 1)

	def calc_hourly_upkeep_per_unit(self, unit_entry: dict):
		return math.floor(self._upkeep * (1.0 - (unit_entry.get("level", 0) * 0.05)))


class Workers(UnitGroup):
	units = (
		WorkerUnit(income=5, 	key="beggar"),
		WorkerUnit(income=10, 	key="farmer"),
		WorkerUnit(income=15, 	key="stonemason"),
		WorkerUnit(income=20, 	key="butcher"),
		WorkerUnit(income=25, 	key="weaver"),
		WorkerUnit(income=35, 	key="tailor"),
		WorkerUnit(income=40, 	key="maid"),
		WorkerUnit(income=45, 	key="baker"),
		WorkerUnit(income=50, 	key="blacksmith"),
		WorkerUnit(income=60, 	key="cook"),
		WorkerUnit(income=65, 	key="winemaker"),
		WorkerUnit(income=70, 	key="shoemaker"),
		WorkerUnit(income=75, 	key="falconer"),
		WorkerUnit(income=80, 	key="carpenter"),
		WorkerUnit(income=85, 	key="merchant"),
	)

	@classmethod
	def get_total_hourly_income(cls, empire: dict):
		units = empire.get("units", dict())

		return sum(map(lambda u: u.calc_hourly_income(units.get(u.key, dict())), cls.units))

	@classmethod
	def shop_page(cls, empire):
		page = TextPage(title="Workers", headers=["ID", "Unit", "Lvl", "Owned", "Income", "Price"])

		all_units = empire.get("units", dict()) if empire is not None else dict()

		for unit in cls.units:
			unit_entry = all_units.get(unit.key, dict())

			owned = unit_entry.get("owned", 0)
			level = unit_entry.get("level", 0)

			max_units = unit.calc_max_amount(unit_entry)

			row = [unit.id, unit.display_name, level]

			if owned >= max_units:
				if level >= UnitValues.MAX_UNIT_MERGE:
					continue

				row.append("Mergeable")

				page.add(row)

				continue

			price = unit.calc_price(owned, 1)

			income_per_unit = unit.calc_income_per_unit(unit_entry)

			row.extend([f"{owned}/{max_units}", f"${income_per_unit:,}", f"${price:,}"])

			page.add(row)

		return page


class Military(UnitGroup):
	units = (
		MilitaryUnit(upkeep=10, 	key="scout"),
		MilitaryUnit(upkeep=15, 	key="peasant"),
		MilitaryUnit(upkeep=25, 	key="soldier"),
		MilitaryUnit(upkeep=35, 	key="thief"),
		MilitaryUnit(upkeep=40, 	key="spearman"),
		MilitaryUnit(upkeep=45, 	key="cavalry"),
		MilitaryUnit(upkeep=55, 	key="warrior"),
		MilitaryUnit(upkeep=65, 	key="archer"),
		MilitaryUnit(upkeep=70,		key="knight"),
	)

	@classmethod
	def get_total_hourly_upkeep(cls, empire: dict):
		units = empire.get("units", dict())

		return sum(map(lambda u: u.calc_hourly_upkeep(units.get(u.key, dict())), cls.units))

	@classmethod
	def calc_total_power(cls, empire):
		power = 0

		units = empire.get("units", dict())

		for u in cls.units:
			power += u.calc_power(units.get(u.key, dict()))

		return round(power, 1)

	@classmethod
	def shop_page(cls, empire):
		page = TextPage(title="Military", headers=["ID", "Unit", "Lvl", "Owned", "Power", "Upkeep", "Price"])

		all_units = empire.get("units", dict()) if empire is not None else dict()

		for unit in cls.units:
			unit_entry = all_units.get(unit.key, dict())

			owned = unit_entry.get("owned", 0)
			level = unit_entry.get("level", 0)

			max_units = unit.calc_max_amount(unit_entry)

			row = [unit.id, unit.display_name, level]

			if owned >= max_units:
				if level >= UnitValues.MAX_UNIT_MERGE:
					continue

				row.append("Mergeable")

				page.add(row)

				continue

			price = unit.calc_price(owned, 1)

			upkeep_per_unit = unit.calc_hourly_upkeep_per_unit(unit_entry)
			power_per_unit = unit.calc_power_per_unit(unit_entry)

			row.extend([f"{owned}/{max_units}", power_per_unit, f"${upkeep_per_unit:,}", f"${price:,}"])

			page.add(row)

		return page