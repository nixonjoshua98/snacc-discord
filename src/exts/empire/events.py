import random

from src.common.models import BankM, PopulationM, UserUpgradesM

from . import utils

from src.data import MilitaryGroup, MoneyGroup


async def assassinated_event(ctx):
	""" Single unit is killed. """

	# - Load the relevant data
	author_population = await PopulationM.fetchrow(ctx.bot.pool, ctx.author.id)

	# - List of all military units which have an owned amount greater than 0
	units_owned = [unit for unit in MilitaryGroup.units if author_population[unit.db_col] > 0]

	if len(units_owned) > 0:
		# - Select the cheapest unit to replace for the user
		unit_killed = min(units_owned, key=lambda u: u.get_price(author_population[u.db_col]))

		# - Remove the unit from the empire
		await PopulationM.decrement(ctx.bot.pool, ctx.author.id, field=unit_killed.db_col, amount=1)

		await ctx.send(f"One of your **{unit_killed.display_name}** was assassinated.")

	else:
		# - The user has no units so we send a generic message and do not do anything
		await ctx.send("An assassin from a rival empire was found dead in your empire")


async def stolen_event(ctx):
	""" Empire was stolen from event. """

	# - Load the data
	author_upgrades = await UserUpgradesM.fetchrow(ctx.bot.pool, ctx.author.id)
	author_population = await PopulationM.fetchrow(ctx.bot.pool, ctx.author.id)

	hourly_income = utils.get_hourly_money_change(author_population, author_upgrades)

	money_stolen = random.randint(max(250, hourly_income // 2), max(1_000, hourly_income))

	await BankM.decrement(ctx.bot.pool, ctx.author.id, field="money", amount=money_stolen)

	s = f"${money_stolen:,}" if money_stolen > 0 else "nothing"

	await ctx.send(f"A thief broke into your empire and stole **{s}**")


async def loot_event(ctx):
	""" Empire finds loot event. """

	items = ("tiny ruby", "pink diamond", "small emerald", "holy sword", "demon sword", "iron shield", "wooden sword")

	# - Load the data
	author_upgrades = await UserUpgradesM.fetchrow(ctx.bot.pool, ctx.author.id)
	author_population = await PopulationM.fetchrow(ctx.bot.pool, ctx.author.id)

	hourly_income = utils.get_hourly_money_change(author_population, author_upgrades)

	money_gained = random.randint(max(500, hourly_income // 2), max(1_000, int(hourly_income * 0.75)))

	await BankM.increment(ctx.bot.pool, ctx.author.id, field="money", amount=money_gained)

	await ctx.send(f"You found **- {random.choice(items)} -** which sold for **${money_gained:,}**")


async def recruit_unit(ctx):
	""" Empire find gains a unit regardless of cap. """

	author_population = await PopulationM.fetchrow(ctx.bot.pool, ctx.author.id)

	units = MilitaryGroup.units + MoneyGroup.units

	unit_recruited = min(units, key=lambda u: u.get_price(author_population[u.db_col]))

	await PopulationM.increment(ctx.bot.pool, ctx.author.id, field=unit_recruited.db_col, amount=1)

	await ctx.send(f"You recruited a rogue **{unit_recruited.display_name}!**")
