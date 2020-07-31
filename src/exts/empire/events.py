import random

from src.common.models import BankM, PopulationM, UserUpgradesM

from . import utils

from .units import MilitaryGroup


async def assassinated_event(ctx):
	""" Single unit is killed. """

	population, upgrades = ctx.population_["author"], ctx.upgrades_["author"]

	units_owned = [unit for unit in MilitaryGroup.units if population[unit.db_col] > 0]

	if units_owned:
		unit_killed = min(units_owned, key=lambda u: u.get_price(population[u.db_col]))

		await PopulationM.decrement(ctx.bot.pool, ctx.author.id, field=unit_killed.db_col, amount=1)

		await ctx.send(f"One of your **{unit_killed.display_name}** was assassinated.")

	else:
		await ctx.send("An assassin from a rival empire was found dead in your empire")


async def stolen_event(ctx):
	""" Empire was stolen from event (-money). """

	population, upgrades = ctx.population_["author"], ctx.upgrades_["author"]

	hourly_money_change = utils.get_hourly_money_change(population, upgrades)

	money_stolen = random.randint(max(250, hourly_money_change // 2), max(1_000, hourly_money_change))

	await BankM.decrement(ctx.bot.pool, ctx.author.id, field="money", amount=money_stolen)

	s = f"{money_stolen:,}" if money_stolen > 0 else "nothing"

	await ctx.send(f"A thief broke into your empire and stole **${s}**")


async def loot_event(ctx):
	""" Empire finds loot event (+money). """

	items = ("tiny ruby", "pink diamond", "small emerald", "holy sword", "demon sword", "iron shield", "wooden sword")

	population, upgrades = ctx.population_["author"], ctx.upgrades_["author"]

	hourly_income = utils.get_hourly_money_change(population, upgrades)

	money_gained = random.randint(max(500, hourly_income // 2), max(1_000, int(hourly_income * 0.75)))

	await BankM.increment(ctx.bot.pool, ctx.author.id, field="money", amount=money_gained)

	await ctx.send(f"You found **- {random.choice(items)} -** which sold for **${money_gained:,}**")