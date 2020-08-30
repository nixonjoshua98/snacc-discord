import random
import asyncio


def net_income(units, levels) -> int:
	from src.data import Military, Workers

	hourly_income = Workers.get_total_hourly_income(units, levels)
	hourly_upkeep = Military.get_total_hourly_upkeep(units, levels)

	return hourly_income - hourly_upkeep


def get_random_name() -> str:
	items = (
		"small ruby", 		"pink diamond", 	"tiny emerald",
		"torn bible", 		"wooden sword", 	"dragon scale",
		"golden egg", 		"magic scroll", 	"holy sword",
		"sword hilt",		"rusty sword",		"small dagger",
		"crossbow",			"gold nugget",		"blood vial"
	)

	return random.choice(items).title()


async def wait_for_reaction(*, bot, check, timeout):
	try:
		react, user = await bot.wait_for("reaction_add", timeout=timeout, check=check)

	except asyncio.TimeoutError:
		return None, None

	return react, user
