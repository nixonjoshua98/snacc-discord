import math
import asyncio
import random

from discord.ext import commands, tasks

from datetime import datetime

from src.common import checks
from src.common.models import BankM, EmpireM
from src.structs.textpage import TextPage
from src.common.converters import EmpireUnit, Range

from . import empireunits as units
from . import empireevents as events


class Empire(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.start_income_loop()

	def start_income_loop(self):
		async def predicate():
			if await self.bot.is_snacc_owner():
				print("Starting 'Empire.start_income_loop' loop.")

				self.income_loop.start()

		asyncio.create_task(predicate())

	@checks.no_empire()
	@commands.command(name="create")
	@commands.max_concurrency(1, commands.BucketType.user)
	async def create_empire(self, ctx, *, empire_name: str):
		""" Establish an empire under your name. """

		await ctx.bot.pool.execute(EmpireM.INSERT_ROW, ctx.author.id, empire_name)

		await ctx.send(f"Your empire named `{empire_name}` has been established!")

		await self.show_empire(ctx)

	@checks.has_empire()
	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="battle")
	async def battle(self, ctx):
		""" Attack a rival empire. """

		await ctx.send("Not yet")

	@checks.has_empire()
	@commands.cooldown(1, 60 * 60 * 3, commands.BucketType.user)
	@commands.command(name="empireevent", aliases=["ee"])
	async def empire_event(self, ctx):
		""" Trigger an empire event. """

		options = (events.ambush_event, events.treaure_event)
		weights = (50, 50)

		chosen_events = random.choices(options, weights=weights)

		for event in chosen_events:
			await event(ctx)

	@checks.has_empire()
	@commands.command(name="empire")
	async def show_empire(self, ctx):
		""" View your empire. """

		empire = await ctx.bot.pool.fetchrow(EmpireM.SELECT_ROW, ctx.author.id)

		page = TextPage()

		page.set_title(f"The '{empire['name']}' Empire")
		page.set_headers(["Unit", "Owned", "$/hour"])

		ttoal_income = 0
		for unit in units.ALL:
			ttoal_income += unit.income_hour * empire[unit.db_col]

			page.add_row(
				[
					unit.display_name,
					f"{empire[unit.db_col]}/{unit.max_amount}",
					f"${unit.income_hour * empire[unit.db_col]:,}"
				]
			)

		page.set_footer(f"${ttoal_income:,}/hour")

		await ctx.send(page.get())

	@checks.has_empire()
	@commands.command(name="rename")
	async def rename_empire(self, ctx, *, empire_name):
		""" Rename your established empire. """

		await ctx.bot.pool.execute(EmpireM.UPDATE_NAME, ctx.author.id, empire_name)
		await ctx.send(f"Your empire has been renamed to `{empire_name}`")

	@checks.has_empire()
	@commands.command(name="units")
	async def show_units(self, ctx):
		""" Show all the possible units which you can buy. """

		empire = await ctx.bot.pool.fetchrow(EmpireM.SELECT_ROW, ctx.author.id)

		page = TextPage()

		page.set_title(f"Units for Hire")
		page.set_headers(["ID", "Unit", "Owned", "$/hour", "Cost"])

		for unit in units.ALL:
			if empire[unit.db_col] >= unit.max_amount:
				continue

			price = unit.get_price(empire[unit.db_col])

			page.add_row(
				[
					unit.id,
					unit.display_name,
					f"{empire[unit.db_col]}/{unit.max_amount}",
					f"${unit.income_hour:,}",
					f"${price:,}"
				]
			)

		page.set_footer("No units available to hire" if len(page.rows) == 0 else None)

		await ctx.send(page.get())

	@checks.has_empire()
	@commands.command(name="hire")
	@commands.max_concurrency(1, commands.BucketType.user)
	async def hire_unit(self, ctx, unit: EmpireUnit(), amount: Range(1, 100) = 1):
		""" Hire a new unit. """

		async with ctx.bot.pool.acquire() as con:
			empire = await con.fetchrow(EmpireM.SELECT_ROW, ctx.author.id)

			row = await BankM.get_row(con, ctx.author.id)

			price = unit.get_price(empire[unit.db_col], amount)

			user_money = row[BankM.MONEY]

			# User cannot afford the units
			if price > user_money:
				await ctx.send(f"You need another **${price - user_money:,}** to buy **{amount}x {unit.display_name}**")

			# Buying the units will make the user go over the purchase limit
			elif empire[unit.db_col] + amount > unit.max_amount:
				await ctx.send(f"You may only have a maximum of **{unit.max_amount}** of this unit.")

			# Everything is OK :)
			else:
				await con.execute(BankM.SUB_MONEY, ctx.author.id, price)

				await EmpireM.add_unit(con, ctx.author.id, unit, amount)

				await ctx.send(f"Bought **{amount}x {unit.display_name}** for **${price:,}**!")

	@tasks.loop(hours=1.0)
	async def income_loop(self):
		async with self.bot.pool.acquire() as con:
			rows = await con.fetch(EmpireM.SELECT_ALL)

			for row in rows:
				now = datetime.utcnow()

				delta_time = (now - row[EmpireM.LAST_INCOME]).total_seconds() / 3600

				income = 0

				for unit, total in {u: row[u.db_col] for u in units.ALL}.items():
					income += (unit.income_hour * total) * delta_time

				income = math.ceil(income)

				if income > 0:
					await con.execute(BankM.ADD_MONEY, row[EmpireM.USER_ID], income)

				await con.execute(EmpireM.UPDATE_LAST_INCOME, row[EmpireM.USER_ID], now)
