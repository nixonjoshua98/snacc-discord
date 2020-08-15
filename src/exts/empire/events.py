import random

from src.data import MilitaryGroup, MoneyGroup


async def assassinated_event(ctx):
	""" Single unit is killed. """

	# - Load the relevant data
	military = await ctx.bot.mongo.find_one("military", {"_id": ctx.author.id})

	# - List of all military units which have an owned amount greater than 0
	units_owned = [unit for unit in MilitaryGroup.units if military.get(unit.key, 0) > 0]

	if len(units_owned) > 0:
		# - Select the cheapest unit to replace for the user
		unit_killed = min(units_owned, key=lambda u: u.get_price(military.get(u.key, 0)))

		# - Remove the unit from the empire
		await ctx.bot.mongo.decrement_one("military", {"_id": ctx.author.id}, {unit_killed.key: 1})

		await ctx.send(f"One of your **{unit_killed.display_name}** was assassinated.")

	else:
		# - The user has no units so we send a generic message and do not do anything
		await ctx.send("An assassin from a rival empire was found dead in your empire")


async def stolen_event(ctx):
	""" Empire was stolen from event. """

	# - Load the data
	upgrades = await ctx.bot.mongo.find_one("upgrades", {"_id": ctx.author.id})
	workers = await ctx.bot.mongo.find_one("workers", {"_id": ctx.author.id})

	hourly_income = max(0, MoneyGroup.get_total_hourly_income(workers, upgrades))

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

	# - Query the database
	upgrades = await ctx.bot.mongo.find_one("upgrades", {"_id": ctx.author.id})
	workers = await ctx.bot.mongo.find_one("workers", {"_id": ctx.author.id})

	hourly_income = max(0, MoneyGroup.get_total_hourly_income(workers, upgrades))

	money_gained = random.randint(max(500, hourly_income // 2), max(1_000, int(hourly_income * 0.75)))

	await ctx.bot.mongo.increment_one("bank", {"_id": ctx.author.id}, {"usd": money_gained})

	await ctx.send(f"You found **- {random.choice(items)} -** which sold for **${money_gained:,}**")


async def recruit_unit(ctx):
	""" Empire gains a unit or gains money. """

	military = await ctx.bot.mongo.find_one("military", {"_id": ctx.author.id})
	upgrades = await ctx.bot.mongo.find_one("upgrades", {"_id": ctx.author.id})

	units = list(filter(lambda u: military.get(u.key, 0) < u._max_amount(upgrades), MilitaryGroup.units))

	if units:
		unit_recruited = min(units, key=lambda u: u.get_price(military.get(u.key, 0)))

		await ctx.bot.mongo.increment_one("military", {"_id": ctx.author.id}, {unit_recruited.key: 1})

		await ctx.send(f"You recruited a rogue **{unit_recruited.display_name}!**")

	else:
		await loot_event(ctx)
