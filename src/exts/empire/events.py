import random

from src.common.models import BankM, PopulationM

from . import utils

from .units import UNIT_GROUPS, UnitGroupType


async def assassinated_event(ctx):
	""" Single unit is killed. """

	async with ctx.bot.pool.acquire() as con:
		population = await con.fetchrow(PopulationM.SELECT_ROW, ctx.author.id)

		units_owned = [unit for unit in UNIT_GROUPS[UnitGroupType.MONEY].units if population[unit.db_col] > 0]

		if units_owned:
			unit_killed = min(units_owned, key=lambda u: u.get_price(population[u.db_col]))

			await PopulationM.sub_unit(ctx.bot.pool, ctx.author.id, unit_killed, 1)

			await ctx.send(f"One of your **{unit_killed.display_name}** was assassinated.")

		else:
			await ctx.send("An assassin from a rival empire was found dead in your empire")


async def stolen_event(ctx):
	""" Empire was stolen from event (-money). """

	async with ctx.bot.pool.acquire() as con:
		population = await con.fetchrow(PopulationM.SELECT_ROW, ctx.author.id)

		hourly_income = utils.get_total_money_delta(population, 1.0)

		money_stolen = random.randint(max(250, hourly_income // 2), max(1_000, hourly_income))

		# Only update the database if any money was stolen
		if money_stolen > 0:
			await ctx.bot.pool.execute(BankM.SUB_MONEY, ctx.author.id, money_stolen)

	s = f"{money_stolen:,}" if money_stolen > 0 else "nothing"

	await ctx.send(f"A thief broke into your empire and stole **${s}**")


async def loot_event(ctx):
	""" Empire finds loot event (+money). """

	items = ("tiny ruby", "pink diamond", "small emerald", "holy sword", "demon sword", "iron shield", "wooden sword")

	async with ctx.bot.pool.acquire() as con:
		population = await con.fetchrow(PopulationM.SELECT_ROW, ctx.author.id)

		hourly_income = utils.get_total_money_delta(population, 1.0)

		money_gained = random.randint(max(500, hourly_income // 2), max(1_000, int(hourly_income * 0.75)))

		await ctx.bot.pool.execute(BankM.ADD_MONEY, ctx.author.id, money_gained)

	await ctx.send(f"You found **- {random.choice(items)} -** which sold for **${money_gained:,}**")