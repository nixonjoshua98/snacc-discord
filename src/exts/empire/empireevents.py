import random

from collections import Counter

from src.common.models import EmpireM, BankM

from . import units


async def ambush_event(ctx):
	units_lost = await _lose_units_event(ctx)

	s = []
	for unit, n in units_lost:
		s.append(f"{n}x {unit.display_name}")

		await EmpireM.sub_unit(ctx.bot.pool, ctx.author.id, unit, n)

	await ctx.send(f"You was ambushed and lost **{', '.join(s) or 'nothing'}**!")


async def stolen_event(ctx):
	async with ctx.bot.pool.acquire() as con:
		bank = await con.fetchrow(BankM.SELECT_ROW, ctx.author.id)

		money = bank[BankM.MONEY]

		money_stolen = random.randint(min(2_500, money // 20), min(10_000, money // 10))

		if money_stolen > 0:
			await ctx.bot.pool.execute(BankM.SUB_MONEY, ctx.author.id, money_stolen)

	s = f"{money_stolen:,}" if money_stolen > 0 else "nothing"

	await ctx.send(f"A thief broke into your empire and stole **${s}**")


async def treaure_event(ctx):
	items = ("tiny ruby", "pink diamond", "small emerald", "holy sword", "demon sword", "iron shield")

	async with ctx.bot.pool.acquire() as con:
		bank = await con.fetchrow(BankM.SELECT_ROW, ctx.author.id)

		money = bank[BankM.MONEY]

		money_gained = random.randint(max(500, money // 50), max(1_500, money // 100))

		await ctx.bot.pool.execute(BankM.ADD_MONEY, ctx.author.id, money_gained)

	await ctx.send(f"You found a **{random.choice(items)}** which sold for **${money_gained:,}**")


async def _lose_units_event(ctx):
	async with ctx.bot.pool.acquire() as con:
		empire = await con.fetchrow(EmpireM.SELECT_ROW, ctx.author.id)

		units_owned = [unit for unit in units.ALL if empire[unit.db_col] > 0]

		units_lost = []

		if units_owned:
			total_units_owned = sum(map(lambda u: empire[u.db_col], units_owned))

			num_units_lost = random.randint(1, max(1, min(5, total_units_owned // 15)))

			weights = [i * 25 for i in range(len(units_owned), 0, -1)]

			temp_units_lost = random.choices(units_owned, weights=weights, k=num_units_lost)

			units_lost = [(unit, min(amount, empire[unit.db_col])) for unit, amount in Counter(temp_units_lost).items()]

	return units_lost
