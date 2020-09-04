import discord
import asyncio
import itertools
import random

from src.common.population import Military, Workers


def get_random_name() -> str:
	items = (
		"small ruby", 		"pink diamond", 	"tiny emerald",
		"torn bible", 		"wooden sword", 	"dragon scale",
		"golden egg", 		"magic scroll", 	"holy sword",
		"sword hilt",		"rusty sword",		"small dagger",
		"crossbow",			"gold nugget",		"blood vial"
	)

	return random.choice(items).title()


def random_colour() -> discord.Color:
	COLOURS = (
		discord.Color.orange(), 		discord.Color.purple(), 		discord.Color.teal(),
		discord.Color.green(),			discord.Color.dark_green(), 	discord.Color.blue(),
		discord.Color.dark_blue(), 		discord.Color.dark_purple(),	discord.Color.magenta(),
		discord.Color.dark_magenta(), 	discord.Color.gold(),

		discord.Color.from_rgb(248, 255, 0), 	discord.Color.from_rgb(179, 0, 255),
		discord.Color.from_rgb(255, 29, 174), 	discord.Color.from_rgb(179, 0, 255),
		discord.Color.from_rgb(193, 255, 72), 	discord.Color.from_rgb(74, 255, 1),
		discord.Color.from_rgb(0, 246, 255)
	)

	return random.choice(COLOURS)


async def wait_for_reaction(*, bot, check, timeout):
	try:
		react, user = await bot.wait_for("reaction_add", timeout=timeout, check=check)

	except asyncio.TimeoutError:
		return None, None

	return react, user


def net_income(empire) -> int:
	hourly_income = Workers.get_total_hourly_income(empire)
	hourly_upkeep = Military.get_total_hourly_upkeep(empire)

	return hourly_income - hourly_upkeep


def grouper(iterable, n, fill=None):
	args = [iter(iterable)] * n

	return itertools.zip_longest(*args, fillvalue=fill)
