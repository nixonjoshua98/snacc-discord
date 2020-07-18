import random

from collections import Counter

from src.common.models import BankM, PopulationM

from . import units, utils


async def attacked_event(ctx):
	""" Empire was attacked event (-units). """

	units_lost = []

	async with ctx.bot.pool.acquire() as con:
		population = await con.fetchrow(PopulationM.SELECT_ROW, ctx.author.id)

		units_owned = [unit for unit in units.ALL if population[unit.db_col] > 0]

		if units_owned:
			total_units_owned = sum(map(lambda u: population[u.db_col], units_owned))

			num_units_lost = random.randint(1, max(1, min(5, total_units_owned // 15)))

			weights = [i ** 2 for i in range(len(units_owned), 0, -1)]

			temp_units_lost = random.choices(units_owned, weights=weights, k=num_units_lost)

			for unit, amount in Counter(temp_units_lost).items():
				units_lost.append((unit, min(amount, population[unit.db_col])))

		s = []
		for unit, n in units_lost:
			s.append(f"{n}x {unit.display_name}")

			await PopulationM.sub_unit(ctx.bot.pool, ctx.author.id, unit, n)

	await ctx.send(f"Your empire was attacked and lost **{', '.join(s) or 'nothing'}**!")


async def assassinated_event(ctx):
	""" Single unit is killed. """

	async with ctx.bot.pool.acquire() as con:
		population = await con.fetchrow(PopulationM.SELECT_ROW, ctx.author.id)

		units_owned = [unit for unit in units.ALL if population[unit.db_col] > 0]

		if units_owned:
			weights = [i ** 2 for i in range(len(units_owned), 0, -1)]

			unit_killed = random.choices(units_owned, weights=weights, k=1)[0]

			await PopulationM.sub_unit(ctx.bot.pool, ctx.author.id, unit_killed, 1)

			await ctx.send(f"One of your {unit_killed.display_name} was assassinated.")

		else:
			await ctx.send("An assassin from a rival empire was found dead in your empire")


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

		money_gained = random.randint(max(500, hourly_income // 5), max(1_000, hourly_income))

		await ctx.bot.pool.execute(BankM.ADD_MONEY, ctx.author.id, money_gained)

	await ctx.send(f"You found a **{random.choice(items)}** which sold for **${money_gained:,}**")