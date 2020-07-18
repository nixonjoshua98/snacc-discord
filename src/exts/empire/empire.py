

# Module imports
import math
import asyncio
import random

import datetime as dt

from discord.ext import tasks, commands

# Src imports
from src import inputs
from src.common import checks
from src.common.models import BankM, EmpireM, PopulationM
from src.common.converters import EmpireUnit, Range

from src.exts.empire import events
from src.exts.empire.units import UNIT_GROUPS
from src.exts.empire.groups import UnitGroupType


class Empire(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.start_income_loop()

	def start_income_loop(self):
		""" Start the background loop assuming that Snaccman is the owner. """

		async def predicate():
			if await self.bot.is_snacc_owner():
				print("Starting loop: Income")

				self.income_loop.start()

		asyncio.create_task(predicate())

	@checks.no_empire()
	@commands.command(name="create")
	@commands.max_concurrency(1, commands.BucketType.user)
	async def create_empire(self, ctx):
		""" Establish an empire under your name. """

		await ctx.bot.pool.execute(EmpireM.INSERT_ROW, ctx.author.id)
		await ctx.bot.pool.execute(PopulationM.INSERT_ROW, ctx.author.id)

		await ctx.send(f"Your empire has been established! You can rename your empire using `!rename`")

		await self.show_empire(ctx)

	@checks.has_empire()
	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="battle")
	async def battle(self, ctx):
		""" Attack a rival empire. """

		military_group = UNIT_GROUPS[UnitGroupType.MILITARY]

		empire = await ctx.bot.pool.fetchrow(PopulationM.SELECT_ROW, ctx.author.id)

		power = 0

		for unit in military_group.units:
			power += unit.power * empire[unit.db_col]

		await ctx.send(f"Power rating: {power}")

	@checks.has_empire()
	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="empireevent", aliases=["ee"])
	async def empire_event(self, ctx):
		""" Trigger an empire event. """

		options = (events.attacked_event, events.loot_event, events.stolen_event)
		weights = (20, 70, 30)

		chosen_events = random.choices(options, weights=weights, k=1)

		for event in chosen_events:
			await event(ctx)

		if random.randint(0, 4) == 0:
			self.empire_event.reset_cooldown(ctx)

			await ctx.send("Good news! Your cooldown has been reset.")

	@checks.has_empire()
	@commands.command(name="empire")
	async def show_empire(self, ctx):
		""" View your empire. """

		population = await ctx.bot.pool.fetchrow(PopulationM.SELECT_ROW, ctx.author.id)

		pages = [group.create_empire_page(population).get() for group in UNIT_GROUPS.values()]

		await inputs.send_pages(ctx, pages)

	@checks.has_empire()
	@commands.command(name="rename")
	async def rename_empire(self, ctx, *, new_name):
		""" Rename your established empire. """

		await EmpireM.set(ctx.bot.pool, ctx.guild.id, name=new_name)

		await ctx.send(f"Your empire has been renamed to `{new_name}`")

	@checks.has_empire()
	@commands.command(name="units")
	async def show_units(self, ctx):
		""" Show all the possible units which you can buy. """

		population = await ctx.bot.pool.fetchrow(PopulationM.SELECT_ROW, ctx.author.id)

		pages = [group.create_units_page(population).get() for group in UNIT_GROUPS.values()]

		await inputs.send_pages(ctx, pages)

	@checks.has_empire()
	@commands.command(name="fire")
	@commands.max_concurrency(1, commands.BucketType.user)
	async def fire_unit(self, ctx, unit: EmpireUnit(), amount: Range(1, 100) = 1):
		""" Fire a new unit. """

		async with ctx.bot.pool.acquire() as con:
			empire_population = await con.fetchrow(PopulationM.SELECT_ROW, ctx.author.id)

			if amount > empire_population[unit.db_col]:
				await ctx.send(f"You do not have **{amount}x {unit.display_name}** avilable to fire.")

			else:
				await PopulationM.sub_unit(con, ctx.author.id, unit, amount)

				await ctx.send(f"You have fired **{amount}x {unit.display_name}**")

	@checks.has_empire()
	@commands.command(name="hire")
	@commands.max_concurrency(1, commands.BucketType.user)
	async def hire_unit(self, ctx, unit: EmpireUnit(), amount: Range(1, 100) = 1):
		""" Hire a new unit. """

		async with ctx.bot.pool.acquire() as con:
			empire_population = await con.fetchrow(PopulationM.SELECT_ROW, ctx.author.id)

			row = await BankM.get_row(con, ctx.author.id)

			# Cost of upgrading from current -> (current + amount)
			price = unit.get_price(empire_population[unit.db_col], amount)

			user_money = row["money"]

			if price > user_money:
				await ctx.send(f"You can't afford to hire **{amount}x {unit.display_name}**")

			elif empire_population[unit.db_col] + amount > unit.max_amount:
				await ctx.send(f"You may only have a maximum of **{unit.max_amount}** of this unit")

			else:
				await con.execute(BankM.SUB_MONEY, ctx.author.id, price)

				await PopulationM.add_unit(con, ctx.author.id, unit, amount)

				await ctx.send(f"Bought **{amount}x {unit.display_name}** for **${price:,}**!")

	@tasks.loop(hours=1.0)
	async def income_loop(self):
		""" Background income & upkeep loop. """

		async with self.bot.pool.acquire() as con:
			rows = await con.fetch(EmpireM.SELECT_ALL_AND_POPULATION)

			for empire in rows:
				now = dt.datetime.utcnow()

				# Hours since the user was last updated
				delta_time = (now - empire["last_update"]).total_seconds() / 3600

				money_change = src.exts.empire.utils.get_total_money_delta(empire, delta_time)

				# We do not want decimals
				money_change = math.ceil(money_change)

				# No need to update the database if the user gained nothing
				if money_change != 0:
					await con.execute(BankM.ADD_MONEY, empire["empire_id"], money_change)

				await EmpireM.set(con, empire["empire_id"], last_update=now)
