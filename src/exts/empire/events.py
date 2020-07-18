import random

from collections import Counter

from src.common.models import BankM, PopulationM

from . import units, utils


async def attacked_event(ctx):
	""" Empire was attacked event (-units). """

	units_lost = await _lose_units_event(ctx)

	s = []
	for unit, n in units_lost:
		s.append(f"{n}x {unit.display_name}")

		await PopulationM.sub_unit(ctx.bot.pool, ctx.author.id, unit, n)

	await ctx.send(f"Your empire was attacked and lost **{', '.join(s) or 'nothing'}**!")


async def stolen_event(ctx):
	""" Empire was stolen from event (-money). """

	async with ctx.bot.pool.acquire() as con:
		bank = await con.fetchrow(BankM.SELECT_ROW, ctx.author.id)

		money = bank["money"]

		# min(2_500, 2% money) - min(10_000, 5% money)
		money_stolen = random.randint(min(2_500, money // 50), min(10_000, money // 20))

		# Only update the database if any money was stolen
		if money_stolen > 0:
			await ctx.bot.pool.execute(BankM.SUB_MONEY, ctx.author.id, money_stolen)

	s = f"{money_stolen:,}" if money_stolen > 0 else "nothing"

	await ctx.send(f"A thief broke into your empire and stole **${s}**")


async def loot_event(ctx):
	""" Empire finds loot event (+money). """

	items = ("tiny ruby", "pink diamond", "small emerald", "holy sword", "demon sword", "iron shield")

	async with ctx.bot.pool.acquire() as con:
		population = await con.fetchrow(PopulationM.SELECT_ROW, ctx.author.id)

		hourly_income = utils.get_total_money_delta(population, 1.0)

		money_gained = random.randint(max(100, hourly_income // 5), max(250, hourly_income // 2))

		await ctx.bot.pool.execute(BankM.ADD_MONEY, ctx.author.id, money_gained)

	await ctx.send(f"You found a **{random.choice(items)}** which sold for **${money_gained:,}**")


async def _lose_units_event(ctx):
	""" Generic lose troops function. """

	async with ctx.bot.pool.acquire() as con:
		population = await con.fetchrow(PopulationM.SELECT_ROW, ctx.author.id)

		# List of all unit types the empire has
		units_owned = [unit for unit in units.ALL if population[unit.db_col] > 0]

		units_lost = []

		if units_owned:
			# Total number of units
			total_units_owned = sum(map(lambda u: population[u.db_col], units_owned))

			# 1 - Clamp(1, 5, units // 15)
			num_units_lost = random.randint(1, max(1, min(5, total_units_owned // 15)))

			# TODO: Sort by `.power`
			weights = [i * 25 for i in range(len(units_owned), 0, -1)]

			# List of units (with duplicates) which were killed
			temp_units_lost = random.choices(units_owned, weights=weights, k=num_units_lost)

			# Final list of units which were killed with amount killed of each type
			for unit, amount in Counter(temp_units_lost).items():
				units_lost.append((unit, min(amount, population[unit.db_col])))

	return units_lost
