import random

from src.common.models import PopulationM

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
	upgrades = await ctx.bot.mongo.find_one("upgrades", {"_id": ctx.author.id})

	population = await PopulationM.fetchrow(ctx.bot.pool, ctx.author.id)

	hourly_income = max(0, MoneyGroup.get_total_hourly_income(population, upgrades))

	money_stolen = random.randint(max(250, hourly_income // 2), max(1_000, hourly_income))

	await ctx.bot.mongo.decrement_one("bank", {"_id": ctx.author.id}, {"usd": money_stolen})

	s = f"${money_stolen:,}" if money_stolen > 0 else "nothing"

	await ctx.send(f"A thief broke into your empire and stole **{s}**")


async def loot_event(ctx):
	""" Empire finds loot event. """

	items = (
		"tiny ruby", 		"pink diamond", 	"small emerald",
		"holy sword", 		"demon sword", 		"iron shield",
		"wooden sword",		"dragon scale",		"golden egg",
		"treasure map",		"rare scroll",		"recursive bow"
	)

	upgrades = await ctx.bot.mongo.find_one("upgrades", {"_id": ctx.author.id})

	population = await PopulationM.fetchrow(ctx.bot.pool, ctx.author.id)

	hourly_income = max(0, MoneyGroup.get_total_hourly_income(population, upgrades))

	money_gained = random.randint(max(500, hourly_income // 2), max(1_000, int(hourly_income * 0.75)))

	await ctx.bot.mongo.increment_one("bank", {"_id": ctx.author.id}, {"usd": money_gained})

	await ctx.send(f"You found **- {random.choice(items)} -** which sold for **${money_gained:,}**")


async def recruit_unit(ctx):
	""" Empire gains a unit or gains money. """

	author_population = await PopulationM.fetchrow(ctx.bot.pool, ctx.author.id)

	upgrades = await ctx.bot.mongo.find_one("upgrades", {"_id": ctx.author.id})

	units = MilitaryGroup.units + MoneyGroup.units

	units = list(filter(lambda u: author_population[u.db_col] < u.get_max_amount(upgrades), units))

	if units:
		unit_recruited = sorted(units, key=lambda u: u.get_price(author_population[u.db_col]))[0]

		await PopulationM.increment(ctx.bot.pool, ctx.author.id, field=unit_recruited.db_col, amount=1)

		await ctx.send(f"You recruited a rogue **{unit_recruited.display_name}!**")

	else:
		await loot_event(ctx)
