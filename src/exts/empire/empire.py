import math
import asyncio

from discord.ext import commands, tasks

from datetime import datetime

from src.common import checks
from src.common.queries import EmpireSQL, BankSQL
from src.structs.textpage import TextPage
from src.common.converters import EmpireUnit, Range

from . import empireunits as units


class Empire(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.last_income = datetime.utcnow()

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

		await ctx.bot.pool.execute(EmpireSQL.CREATE_EMPIRE, ctx.author.id, empire_name)

		await ctx.send(f"Your empire named `{empire_name}` has been established!")

		await self.show_empire(ctx)

	@checks.has_empire()
	@commands.command(name="empire")
	async def show_empire(self, ctx):
		""" View your empire. """

		empire = await ctx.bot.pool.fetchrow(EmpireSQL.SELECT_USER, ctx.author.id)

		page = TextPage()

		page.set_title(f"The '{empire['name']}' Empire")
		page.set_headers(["Unit", "Total", "$/hour"])

		ttoal_income = 0
		for unit in units.ALL:
			ttoal_income += unit.income_hour * empire[unit.db_col]

			page.add_row([unit.display_name, empire[unit.db_col], f"${unit.income_hour * empire[unit.db_col]:,}"])

		page.set_footer(f"${ttoal_income:,}/hour")

		await ctx.send(page.get())

	@checks.has_empire()
	@commands.command(name="rename")
	async def rename_empire(self, ctx, *, empire_name):
		""" Rename your established empire. """

		await ctx.bot.pool.execute(EmpireSQL.UPDATE_NAME, ctx.author.id, empire_name)
		await ctx.send(f"Your empire has been renamed to `{empire_name}`")

	@checks.has_empire()
	@commands.command(name="units")
	async def show_units(self, ctx):
		""" Show all the possible units which you can buy. """

		empire = await ctx.bot.pool.fetchrow(EmpireSQL.SELECT_USER, ctx.author.id)

		page = TextPage()

		page.set_title(f"Units for Hire")
		page.set_headers(["ID", "Unit", "$/hour", "Price"])

		for unit in units.ALL:
			page.add_row(
				[
					unit.id,
					unit.display_name,
					f"${unit.income_hour:,}",
					f"${unit.get_price(empire[unit.db_col]):,}",
				]
			)

		await ctx.send(page.get())

	@commands.command(name="hire")
	@commands.max_concurrency(1, commands.BucketType.user)
	@checks.has_empire()
	async def hire_unit(self, ctx, unit: EmpireUnit(), amount: Range(1, 100) = 1):
		""" Hire a new unit. """

		money_cog = ctx.bot.get_cog("Money")

		bal = await money_cog.get_balance(ctx.author)
		empire = await ctx.bot.pool.fetchrow(EmpireSQL.SELECT_USER, ctx.author.id)

		price = unit.get_price(empire[unit.db_col], amount)

		if price > bal["money"]:
			diff = price - bal['money']

			return await ctx.send(f"You need another **${diff:,}** to buy **{amount}x {unit.display_name}**")

		elif empire[unit.db_col] + amount > 250:
			return await ctx.send(f"You may only have a maximum of **250** of each unit.")

		await ctx.bot.pool.execute(BankSQL.SUB_MONEY, ctx.author.id, price)
		await ctx.bot.pool.execute(EmpireSQL.add_unit(unit), ctx.author.id, amount)

		await ctx.send(f"Bought **{amount}x {unit.display_name}** for **${price:,}**!")

	@tasks.loop(hours=1.0)
	async def income_loop(self):
		now = datetime.utcnow()

		delta_time = (now - self.last_income).total_seconds() / 3600

		self.last_income = now

		async with self.bot.pool.acquire() as con:
			async with con.transaction():
				empires = await con.fetch(EmpireSQL.SELECT_ALL)

				for emp in empires:
					income = 0

					for unit, total in {u: emp[u.db_col] for u in units.ALL}.items():
						income += (unit.income_hour * total) * delta_time

					income = math.ceil(income)

					if income > 0:
						await con.execute(BankSQL.ADD_MONEY, emp["user_id"], income)