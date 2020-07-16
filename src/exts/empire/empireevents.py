import random

from src.common.models import EmpireM, BankM

from . import empireunits as units


async def ambush_event(ctx):
	units_lost = await _lose_units_event(ctx)

	s = []
	for unit, n in units_lost:
		s.append(f"{n}x {unit.display_name}")

		await EmpireM.sub_unit(ctx.bot.pool, ctx.author.id, unit, n)

	await ctx.send(f"You was ambushed and lost **{', '.join(s) or 'nothing'}**!")


async def treaure_event(ctx):
	items = ("tiny ruby", "pink diamond", "small emerald", "holy sword", "demon sword", "dead slave")

	async with ctx.bot.pool.acquire() as con:
		bank = await con.fetchrow(BankM.SELECT_ROW, ctx.author.id)

		money = bank[BankM.MONEY]

		money_gained = random.randint(max(250, money // 50), max(1_000, money // 25))

		await ctx.bot.pool.execute(BankM.ADD_MONEY, ctx.author.id, money_gained)

	await ctx.send(f"You found a **{random.choice(items)}** which sold for **${money_gained}**")


async def _lose_units_event(ctx):
	async with ctx.bot.pool.acquire() as con:
		empire = await con.fetchrow(EmpireM.SELECT_ROW, ctx.author.id)

		units_owned = [unit for unit in units.ALL if empire[unit.db_col] > 0]

		units_lost = []

		if units_owned:
			num_units_lost = random.randint(1, max(1, len(units_owned) // 5))

			target_units = units_owned.copy()

			for i in range(num_units_lost):
				unit = random.choice(target_units)

				amount_lost = random.randint(1, max(1, empire[unit.db_col] // 4))

				units_lost.append((unit, amount_lost))

				target_units.remove(unit)

	return units_lost
